import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('sqlite:///currency_values_03_22.db', echo=False)
data = pd.read_csv('currency_from_2003_to_2022.csv')
data.to_sql(name='currency_values_03_22', con=engine)
