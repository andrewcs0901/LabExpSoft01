import pandas as pd
df = pd.read_csv('result_main_query.txt.csv')

result_df = df.drop_duplicates(subset=['url'], keep='first')
result_df.to_csv('result.csv')