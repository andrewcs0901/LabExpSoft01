import csv
from datetime import date, datetime
import requests

currentDate = date(2021, 8, 31)
txt_query = 'main_query.txt'
token = open('env', 'r').read()
total_count = 0
previous_cursor = 'null'
output = open(f'result_{txt_query}.csv', 'w')


def format_data(key, value):
    if key == 'createdAt' or key == 'updatedAt':
        date_row = datetime.fromisoformat(value.replace('Z', '+00:00')).date()
        return f"{(currentDate - date_row).days},"
    return f"{value},"


def read_json_to_csv(res_json, separator=''):
    str_acc = ''
    for key in res_json:
        values = res_json[key]
        str_acc += format_data(key, values) \
            if not isinstance(values, dict) \
            else read_json_to_csv(values)
    return f"{str_acc[:-1]}\n" if separator == '\n' else str_acc


def read_json(res_json, dict_keys: set, total_count:int):
    str_acc = ''
    for node in res_json:
        if not node['url'] in dict_keys:
            dict_keys.add(node['url'])
            total_count += 1
            str_acc += read_json_to_csv(node, '\n')
    output.write(str_acc)
    return total_count


def create_csv_rows(json_row, aux=''):
    str_acc = aux
    for key in json_row.keys():
        str_acc += f"{key}," \
            if not isinstance(json_row[key], dict) \
            else create_csv_rows(json_row[key], f"{key}_")
    return f"{str_acc[:-1]}\n" if len(aux) == 0 else str_acc


def write_csv_rows(json_row):
    output.write(create_csv_rows(json_row[0]))

def graph_query(first = 100, page = 0, previous_cursor = previous_cursor, total_count = total_count):
    print('starting github graphql query...')
    query = open(txt_query, 'r').read()
    query = query.replace('first: 100', f'first: {first}')
    headers = dict(Authorization=f'bearer {token}')
    dict_keys:set = set()

    while page < 10:
        r = requests.post('https://api.github.com/graphql', headers=headers, json={'query': query})
        if r.status_code == 200:
            print(f'page: {page}')
            res_json = r.json()['data']['search']
            nodes = res_json['nodes']
            end_cursor = res_json['pageInfo']['endCursor']
            print(previous_cursor)
            print(end_cursor)
            if page == 0:
                write_csv_rows(nodes)
                query = query.replace(previous_cursor, f'"{end_cursor}"')
            else:
                query = query.replace(previous_cursor, end_cursor)
            previous_cursor = end_cursor
            total_count = read_json(nodes, dict_keys,total_count)
            page += 1
    print('query executed')
    return total_count,previous_cursor


total_count,previous_cursor = graph_query()

if total_count != 1000:
    remain = 1000 - total_count
    print(f'found {remain} duplicates')
    first = remain % 100
    graph_query(first, 9,previous_cursor,total_count)
    first = remain - first
    if remain != 0:
        while(first != 0):
            graph_query(100, 9, previous_cursor,total_count)
            first = first - 100
