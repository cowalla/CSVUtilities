import copy

from csv_utilities.csv import CSV


FILE_PATH = "t.csv"


csv = CSV(FILE_PATH)
grouped = csv.group_by("Instrument")
grouped_buy_sells = {}

for g, items_list in grouped.items():
    grouped_buy_sells[g] = []

    for item in items_list:
        quantity = item['Quantity']

        if 'sell' in item['Side']:
            quantity = '-' + quantity

        t_id = item['Id']
        date = item['Date']
        price = item['Price']
        grouped_buy_sells[g].append({
            'quantity': quantity,
            'date': date,
            'price': price,
            'id': t_id,
        })

    grouped_buy_sells[g] = sorted(grouped_buy_sells[g], key=lambda x: x['date'])

grouped_buy_sells.pop('')
outfile = 'parsed.csv'


def find_item_from_list_with_id(l, l_id):
    for i in range(len(l)):
        if l[i]['id'] == l_id:
            return i
    return -1


def remove_item_from_list_with_id(l, l_id):
    idx = find_item_from_list_with_id(l, l_id)

    if idx > 0:
        l.pop(idx)
        return idx
    else:
        return -1


gains = []
sell_gains = {}

for group, items_list in grouped_buy_sells.items():
    buys = [item for item in items_list if float(item['quantity']) > 0]
    sells = [item for item in items_list if float(item['quantity']) < 0]

    for sell in sells:
        sell_gs = []
        relevant_buys = [
            b
            for b in buys
            if b['date'] <= sell['date']
        ]

        sell_quantity = float(sell['quantity'][1:]) # remove negative sign
        sell_date = sell['date']

        while sell_quantity > 0:
            last_buy = relevant_buys.pop(0)
            last_buy_id = last_buy['id']
            last_buy_quantity = float(last_buy['quantity'])
            gain = {
                'date': sell_date,
                'quantity': 0.0,
                'gain': 0.0,
                'sell_id': sell['id'],
                'asset': group,
                'buy_id': last_buy_id,
            }

            if last_buy_quantity < sell_quantity:
                gain['quantity'] = last_buy_quantity
                remove_item_from_list_with_id(buys, last_buy_id)
            else:
                gain['quantity'] = sell_quantity
                buy_idx = find_item_from_list_with_id(buys, last_buy_id)
                buys[buy_idx]['quantity'] = str(float(buys[buy_idx]['quantity']) - sell_quantity)

            gain['gain'] = (float(sell['price']) - float(last_buy['price'])) * gain['quantity']
            gains.append(gain)
            sell_gs.append(gain)
            sell_quantity -= last_buy_quantity

        sell_gains[int(sell['id'])] = sell_gs
        sell_gs = []


gains_2019 = [g for g in gains if g['date'] > '2019-01-01 00:00:00 GMT']
total_gains_2019 = sum([g['gain'] for g in gains_2019])


# add in btc_price, gain, gain (USD) columns

btc_prices_column = []
gain_btc_column = []
gain_usd_column = []
buy_ids = []


from parse_btc import btc_prices, _to_new_format

# 2019-10-20 20:00:24 GMT
# d_format = "%Y-%m-%d "

for row in csv.rows:
    # get date of row
    row_date = row[csv.header_indices['Date']].split(' ')[0]
    btc_price = float(btc_prices[row_date])
    # get sell id
    t_id = int(row[csv.header_indices['Id']])
    is_sell = 'sell' in row[csv.header_indices['Side']]
    buy_id_str = ''
    total_gain = 0.0  # usd
    gain_btc = 0.0

    if is_sell:
        gains = sell_gains[t_id]
        # import pdb
        # pdb.set_trace()

        for gain in gains:
            buy_id_str += str(gain['buy_id']) + ';'
            gain_btc += float(gain['gain'])
            total_gain += btc_price * gain['gain']

    btc_prices_column.append(str(btc_price))
    gain_btc_column.append(str(gain_btc))
    gain_usd_column.append(str(total_gain))
    buy_ids.append(buy_id_str)


csv.add_column('btc price', btc_prices_column)
csv.add_column('gain btc', gain_btc_column)
csv.add_column('gain usd', gain_usd_column)
csv.add_column('buy ids', buy_ids)

csv.save('/Users/connor/Desktop/deribit_gains_2018_2019.csv')


# with open('deribit.csv', 'w') as f:
#     f.write('product,date,price,quantity\n')
#
#     for group, items_list in grouped_buy_sells.items():
#         for item in items_list:
#             l = '%s,%s,%s,%s\n' % (group, item['date'], item['price'], item['quantity'])
#             f.write(l)

