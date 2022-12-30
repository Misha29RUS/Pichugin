import pandas as pd
import sqlite3


df = pd.read_csv("exchange_rate_currency.csv")
connect = sqlite3.connect("data_base_3.5.1.sqlite")
cursor = connect.cursor()
df.to_sql(name="data_base_3.5.1.sqlite", con=connect, if_exists='replace', index=False)
connect.commit()
