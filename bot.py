import logging
import random
logging.basicConfig(level=logging.INFO)

from config import CHANNEL_FROM_ID, TO_GROUP_ID, TELEGRAM_BOT_TOKEN, SENTRY_URL
from datetime import datetime
import sentry_sdk

sentry_sdk.init(SENTRY_URL)
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler
from chan_forward import get_convs_for_day_month


# Default: sceglie un anno a caso
# Con un argomento usa quell'anno
# Manda una conversazione a caso, ne manda massimo 5 messaggi, e manda il link al primo messaggio
def accadde(update: Update, context):
    # Blacklist: chat diverse da ritaly, o TARS come autore
    if (update.message.chat.id != TO_GROUP_ID) or (update.message.from_user.id == 75818507):
        return
    if len(context.args) > 3:
        update.message.reply_text("Sintassi: /accadde [(anno [mese giorno]|mese giorno)]")
        return

    if len(context.args) == 3:
        # Anno mese giorno
        month = int(context.args[1])
        day = int(context.args[2])
    elif len(context.args) == 2:
        # Mese Giorno
        month = int(context.args[0])
        day = int(context.args[1])
    else:
        now = datetime.now()
        month = now.month
        day = now.day

    convs_years = get_convs_for_day_month(day, month)
    if not convs_years:
        update.message.reply_text(f"Non è successo niente quel giorno.")
        return

    if len(context.args) == 3 or len(context.args) == 1:
        selected_year = int(context.args[0])
        if selected_year not in convs_years.keys():
            update.message.reply_text(f"Non è successo niente quel giorno.")
            return
    else:
        selected_year = random.choice(list(convs_years.keys()))

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
