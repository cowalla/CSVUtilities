import datetime

from csv_utilities.csv import CSV


FILE_PRICES = 'bitcoin_price.csv'


btc_csv = CSV(FILE_PRICES)


# date_format = "Mar 10, 2020"


date_format = '\"%b %d %Y\"'
dt = datetime.datetime.strptime(btc_csv.rows[0][0], date_format)
to_format = '%Y-%m-%d'


def _to_new_format(datestring):
    return datetime.datetime.strptime(datestring, dateformat).strftime(to_format)


rows = []

btc_prices = {
    _to_new_format(d[0]): float(d[1])
    for d in btc_csv.rows
}

