import pandas as pd
from datetime import date, datetime
import requests


currentDate = date(2021, 8, 31)
txt_query = 'main_query.txt'
token = open('env', 'r').read()
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


def read_json(res_json):
    str_acc = ''
    for node in res_json:
        str_acc += read_json_to_csv(node, '\n')
    output.write(str_acc)


def create_csv_rows(json_row, aux=''):
    str_acc = aux
    for key in json_row.keys():
        str_acc += f"{key}," \
            if not isinstance(json_row[key], dict) \
            else create_csv_rows(json_row[key], f"{key}_")
    return f"{str_acc[:-1]}\n" if len(aux) == 0 else str_acc


def write_csv_rows(json_row):
    output.write(create_csv_rows(json_row[0]))

def drop_duplicates():
    print('Dropping duplicated rows')
    df = pd.read_csv('result_main_query.txt.csv')
    result_df = df.drop_duplicates(subset=['url'], keep='first')
    result_df.to_csv('final_result.csv')
    return result_df


def process_csv():
    print('starting github graphql query...')
    query = open(txt_query, 'r').read()
    page = 0
    previous_cursor = 'null'
    headers = dict(Authorization=f'bearer {token}')
    while page < 10:
        r = requests.post('https://api.github.com/graphql', headers=headers, json={'query': query})
        if r.status_code == 200:
            print(f'page: {page}')
            resJson = r.json()['data']['search']
            nodes = resJson['nodes']
            end_cursor = resJson['pageInfo']['endCursor']
            if page == 0:
                write_csv_rows(nodes)
                query = query.replace(previous_cursor, f'"{end_cursor}"')
            else:
                query = query.replace(previous_cursor, end_cursor)
            previous_cursor = end_cursor
            read_json(nodes)
            page += 1
    print('query executed')



def main_process():
    process_csv()
    result_df = drop_duplicates()
    quantityOfRowsInNotDuplicatedFile = result_df['stargazerCount'].count()
    print(f"Quantity of rows in dropped csv: {quantityOfRowsInNotDuplicatedFile}")

if __name__ == '__main__':
    main_process()
