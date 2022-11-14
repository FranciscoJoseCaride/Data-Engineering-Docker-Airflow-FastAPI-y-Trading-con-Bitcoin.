import pandas as pd
from pandas_datareader.data import DataReader
from datetime import date 


import warnings
warnings.filterwarnings("ignore")

data = ['ETH-USD','BTC-USD'] 
cripto = DataReader(data, 'yahoo', start=date(2014,9,17))
bitcoin = pd.DataFrame(cripto['Close']['BTC-USD'])

bitcoin.to_csv('./storage/bitcoin.csv')