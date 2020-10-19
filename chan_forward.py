from datetime import datetime
import pandas as pd
import json
from typing import Dict

from pandas.core.frame import DataFrame

with open('result.json') as rf:
    result = json.load(rf)

# dataset.date.dt.day

messages = pd.DataFrame(result.get("messages", []))
messages = messages[messages['type'] == "message"]
messages = messages[["id", "date"]]
messages['date'] = pd.to_datetime(messages['date'])
messages = messages.set_index("date")
messages = messages[messages.index.year != datetime.now().year]
years = messages.groupby(pd.Grouper(freq='Y'))


def get_messages_for_day_month(day: int, month: int) -> Dict[int, pd.DataFrame]:
    ret = {}

    for date_end_year, msgs in years:
        ret[date_end_year.year] = msgs[(msgs.index.day == day) & (msgs.index.month == month)]
    return ret

def get_convs_from_messages(messages: pd.DataFrame):
    convs = []
    if len(messages) == 0:
        return convs
    last_date = messages.index[0]
    conv = []
    for index, message in messages.iterrows():
        # Se sta iniziando una nuova conversazione (sono passati 5+ minuti)
        if (index - last_date).total_seconds() >  5 * 60:
            # "Sposta" conv in convs, e crea una nuova conversazione
            convs.append(conv)
            conv = []
        # In ogni caso appendi il messaggio alla conv attuale e registra la data
        conv.append(message.id)
        last_date = index
    convs.append(conv)
    return convs

def get_convs_for_day_month(day, month):
    messages_for_years = get_messages_for_day_month(day, month) # Dict{ anno: messaggi }
    convs = {}
    for year, messages_for_year in messages_for_years.items():
        convs[year] = get_convs_from_messages(messages_for_year)
    return convs
