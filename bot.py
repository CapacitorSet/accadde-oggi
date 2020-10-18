import logging
import random
logging.basicConfig(level=logging.INFO)

from config import CHANNEL_FROM_ID, TO_GROUP_ID, TELEGRAM_BOT_TOKEN, SENTRY_URL
from datetime import datetime
import sentry_sdk
from sentry_sdk import configure_scope, add_breadcrumb, Scope, capture_exception
sentry_sdk.init(SENTRY_URL)
from telegram import Update, CallbackQuery, Bot, InlineKeyboardMarkup, InlineKeyboardButton, ParseMode
from telegram.ext import Updater, CallbackContext, CommandHandler
from chan_forward import get_convs_for_day_month


# Default: sceglie un anno a caso
# Con un argomento usa quell'anno
# Manda una conversazione a caso, ne manda massimo 5 messaggi, e manda il link al primo messaggio
def accadde(update: Update, context):
    # Blacklist: chat diverse da ritaly, o TARS come autore
    if (update.message.chat.id != TO_GROUP_ID) or (update.message.from_user.id == 75818507):
        return
    if len(context.args) == 3:
        # Anno mese giorno
        convs_years = get_convs_for_day_month(int(context.args[2]), int(context.args[1]))
        if not convs_years:
            update.message.reply_text(f"Non è successo niente quel giorno.")
            return
        selected_year = int(context.args[0])
        if selected_year not in convs_years.keys():
            update.message.reply_text(f"Non è successo niente quel giorno.")
            return
    elif len(context.args) == 2:
        # Mese Giorno
        convs_years = get_convs_for_day_month(int(context.args[1]), int(context.args[0]))
        if not convs_years:
            update.message.reply_text(f"Non è successo niente quel giorno.")
            return
        selected_year = random.choice(list(convs_years.keys()))
    elif len(context.args) == 1:
        # Anno
        now = datetime.now()
        convs_years = get_convs_for_day_month(now.day, now.month)
        if not convs_years:
            update.message.reply_text(f"Non è successo niente oggi ma in quell'anno.")
            return
        selected_year = int(context.args[0])
    elif len(context.args) == 0:
        # Random
        now = datetime.now()
        convs_years = get_convs_for_day_month(now.day, now.month)
        if not convs_years:
            update.message.reply_text(f"Non è successo niente gli anni precedenti.")
            return

        selected_year = random.choice(list(convs_years.keys()))
    else:
        update.message.reply_text("Sintassi: /accadde [(anno [mese giorno]|mese giorno)]")
        return

    convs = convs_years[selected_year]
    selected_conv = random.choice(convs)
    update.message.reply_text(f"Nel <b>{selected_year}</b> accadeva questo (<a href='https://t.me/c/1026518516/{selected_conv[0]}'>link</a>)", parse_mode=ParseMode.HTML)
    for message_id in selected_conv[:5]:
        update.message.bot.forward_message(chat_id=update.message.chat.id, from_chat_id=CHANNEL_FROM_ID, message_id=str(message_id))

logging.info("Configuring bot...")
updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
updater.dispatcher.add_handler(CommandHandler("accadde", accadde))

#git_commit = subprocess.check_output(["git", "describe", "--always"]).strip()
#sentry_sdk.init(SENTRY_URL, release=str(git_commit, "utf-8"), environment=updater.bot.get_me().username)

logging.info("Polling...")
updater.start_polling()
updater.idle()
