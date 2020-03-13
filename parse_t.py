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

for group, items_list in grouped_buy_sells.items():
    buys = [item for item in items_list if float(item['quantity']) > 0]
    sells = [item for item in items_list if float(item['quantity']) < 0]

    for sell in sells:
        relevant_buys = [
            b
            for b in buys
            if b['date'] <= sell['date']
        ]

        sell_quantity = float(sell['quantity'][1:]) # remove negative sign
        sell_date = sell['date']

        while sell_quantity > 0:
            gain = {'date': sell_date, 'quantity': 0.0, 'gain': 0.0, 'sell_id': sell['id'], 'asset': group}
            last_buy = relevant_buys.pop(0)
            last_buy_id = last_buy['id']
            last_buy_quantity = float(last_buy['quantity'])

            if last_buy_quantity < sell_quantity:
                gain['quantity'] = last_buy_quantity
                remove_item_from_list_with_id(buys, last_buy_id)
            else:
                gain['quantity'] = sell_quantity
                buy_idx = find_item_from_list_with_id(buys, last_buy_id)
                buys[buy_idx]['quantity'] = str(float(buys[buy_idx]['quantity']) - sell_quantity)

            gain['gain'] = (float(sell['price']) - float(last_buy['price'])) * gain['quantity']
            gains.append(gain)
            sell_quantity -= last_buy_quantity


gains_2019 = [g for g in gains if g['date'] > '2019-01-01 00:00:00 GMT']
total_gains_2019 = sum([g['gain'] for g in gains_2019])


with open(outfile, 'w') as f:
    f.write('product,date,price,quantity\n')

    for group, items_list in grouped_buy_sells.items():
        for item in items_list:
            l = '%s,%s,%s,%s\n' % (group, item['date'], item['price'], item['quantity'])
            f.write(l)

