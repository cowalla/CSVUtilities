import datetime

from csv_utilities.csv import CSV


FILE_PRICES = 'bitcoin_price.csv'


btc_csv = CSV(FILE_PRICES, quotes_enabled=True)
# btc_csv._join_rows(1,2)


# date_format = "Mar 10, 2020"


date_format = '%b %d %Y'
dt = datetime.datetime.strptime(btc_csv.rows[0][0], date_format)
to_format = '%Y-%m-%d'


def _to_new_format(datestring, date_format):
    return datetime.datetime.strptime(datestring, date_format).strftime(to_format)


def decstring_to_float(s):
    return float(s.replace(',', ''))
#
#
rows = []

btc_prices = {
    _to_new_format(d[0], date_format): decstring_to_float(d[1])
    for d in btc_csv.rows
}

