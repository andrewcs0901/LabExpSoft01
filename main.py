import csv
from datetime import date, datetime
import requests
currentDate = date(2021, 8, 31)
queries = ['main_query.txt', 'closed_issues.txt']
token = open('env', 'r').read()


def read_json_tocsv(res_json, str_acc=''):
    for key in res_json:
        values = res_json[key]
        if not isinstance(values, dict):
            if key == 'createdAt' or key == 'updatedAt':
                dateRow = datetime.fromisoformat(values.replace('Z', '+00:00')).date()
                str_acc += f"{(currentDate - dateRow).days},"
            else:
                str_acc += f"{values},"
        else:
            for val in values.values():
                if isinstance(val, dict):
                    read_json_tocsv(val.values(), str_acc)
                else:
                    str_acc += f"{val},"
    str_acc = f"{str_acc[:-1]}\n"
    output.write(str_acc)


def read_json(res_json):
    for node in res_json:
        read_json_tocsv(node)


def create_csv_rows(json_row, str_acc=''):
    for key in json_row.keys():
        if not isinstance(json_row[key], dict):
            str_acc += f"{key},"
        else:
            for key2 in json_row[key].keys():
                if isinstance(json_row[key][key2], dict):
                    str_acc += f"{key2}_"
                    create_csv_rows(json_row[key][key2], str_acc)
                else:
                    str_acc += f"{key}_{key2},"
    str_acc = f"{str_acc[:-1]}\n"
    output.write(str_acc)

print('starting github graphql query...')
for txt_query in queries:
    query = open(txt_query, 'r').read()
    output = open(f'result_{txt_query}.csv', 'w')
    csvwriter = csv.writer(output)
    headers = dict(Authorization=f'bearer {token}')
    r = requests.post('https://api.github.com/graphql', headers=headers, json={'query': query})
    if r.status_code == 200:
        resJson = r.json()['data']['search']['nodes']
        create_csv_rows(resJson[0])
        read_json(resJson)
print('Query executed')
