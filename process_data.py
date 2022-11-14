import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")

bitcoin =  pd.read_csv('./storage/bitcoin.csv')


#####################################
short = 30
long = 100
#####################################

bitcoin['short'] = bitcoin['BTC-USD'].rolling(window=short).mean()
bitcoin['long'] = bitcoin['BTC-USD'].rolling(window=long).mean()
bitcoin = bitcoin[bitcoin['long'].notnull()]
bitcoin.set_index('Date',inplace=True)

# Algoritmo

def buy_sell(signal):
  sigPriceBuy = []
  sigPriceSell = []
  flag = -1
  for i in range(0,len(signal)):
      if signal['short'][i] > signal['long'][i]:
        if flag != 1:
          sigPriceBuy.append(signal['BTC-USD'][i])
          sigPriceSell.append(np.nan)
          flag = 1
        else:
          sigPriceBuy.append(np.nan)
          sigPriceSell.append(np.nan)
        #print('Buy')
      elif signal['short'][i] < signal['long'][i]:
        if flag != 0:
          sigPriceSell.append(signal['long'][i])
          sigPriceBuy.append(np.nan)
          flag = 0
        else:
          sigPriceBuy.append(np.nan)
          sigPriceSell.append(np.nan)
        #print('sell')
      else: #Handling nan values
        sigPriceBuy.append(np.nan)
        sigPriceSell.append(np.nan)
  
  return (sigPriceBuy, sigPriceSell)

# Aplicamos algoritmo
signal = bitcoin.copy()

x = buy_sell(signal)
signal['Buy_Signal_Price'] = x[0]
signal['Sell_Signal_Price'] = x[1]

# # Generamos historicos resumido y completo

primer_compra = signal[signal['Buy_Signal_Price'].notnull()].index.min()
simul_inv = signal[signal.index >= primer_compra]
simul_inv['Buy_Signal_Price'] = simul_inv['Buy_Signal_Price']*(-1)
simul_inv = simul_inv[['Buy_Signal_Price','Sell_Signal_Price']]

# Me guardo copia de la versión completa para usar más adeleante, avanzo con versión resumida
simul_inv_completa = simul_inv.copy()

# Sigo con el anterior
simul_inv = simul_inv[ (simul_inv['Buy_Signal_Price'].notnull()) | (simul_inv['Sell_Signal_Price'].notnull()) ]
simul_inv = simul_inv.fillna(0)
simul_inv['ganancia'] = simul_inv['Buy_Signal_Price'] + simul_inv['Sell_Signal_Price']
simul_inv['ganancia_acumulada'] = simul_inv['ganancia']
simul_inv['ganancia_acumulada'] = simul_inv['ganancia_acumulada'].cumsum()

simul_inv.reset_index(inplace=True)
simul_inv['Date'] = pd.to_datetime(simul_inv['Date'])
simul_inv['Periodo'] = simul_inv['Date'].diff().dt.days
simul_inv.set_index('Date',inplace=True)

simul_inv['ganancia'] = round(simul_inv['ganancia'],2)
simul_inv['ganancia_acumulada'] = round(simul_inv['ganancia_acumulada'],2)

# Vuelvo a versión completa

simul_inv_completa = simul_inv_completa.fillna(0)

simul_inv_completa['ganancia'] = simul_inv_completa['Buy_Signal_Price'] + simul_inv_completa['Sell_Signal_Price']
simul_inv_completa['ganancia_acumulada'] = simul_inv_completa['ganancia']
simul_inv_completa['ganancia_acumulada'] = simul_inv_completa['ganancia_acumulada'].cumsum()

simul_inv_completa['ganancia'] = round(simul_inv_completa['ganancia'],2)
simul_inv_completa['ganancia_acumulada'] = round(simul_inv_completa['ganancia_acumulada'],2)

simul_inv_completa['Operacion'] = ''
conditions = [
    simul_inv_completa['ganancia'] < 0,
    simul_inv_completa['ganancia'] > 0
]
values = ['Mantengo activo comprado','Mantengo cash']
simul_inv_completa['Operacion'] = np.select(conditions,values)

simul_inv_completa['Operacion'] = np.where(simul_inv_completa['Operacion']=='0',np.nan,simul_inv_completa['Operacion'])
simul_inv_completa['Operacion'] = simul_inv_completa['Operacion'].fillna(method = 'ffill')

simul_inv_completa['position'] = ''

conditions = [
    simul_inv_completa['ganancia'] > 0,
    simul_inv_completa['ganancia'] < 0
]

values = ['vendo','compro']
simul_inv_completa['position'] = np.select(conditions,values)
simul_inv_completa['position'] = np.where(simul_inv_completa['position']=='0',np.nan,simul_inv_completa['position'])
simul_inv_completa['position'][0] = 'compra inicial'
simul_inv_completa['position'] = np.where(simul_inv_completa['position'].isna(), simul_inv_completa['Operacion'],simul_inv_completa['position'])
simul_inv_completa.drop('Operacion',axis=1,inplace=True)

simul_inv.reset_index(inplace=True)
simul_inv_completa.reset_index(inplace=True)


simul_inv['Date'] = simul_inv['Date'].astype(str)

simul_inv = simul_inv.merge(simul_inv_completa[['Date','position']],left_on='Date',right_on='Date',how='left')

simul_inv['Buy_Signal_Price'] = round(simul_inv['Buy_Signal_Price'],2)
simul_inv['Sell_Signal_Price'] = round(simul_inv['Sell_Signal_Price'],2)

simul_inv_completa['Buy_Signal_Price'] = round(simul_inv_completa['Buy_Signal_Price'],2)
simul_inv_completa['Sell_Signal_Price'] = round(simul_inv_completa['Sell_Signal_Price'],2)

simul_inv_completa.to_csv('./storage/simul_inv_completa.csv')
simul_inv.to_csv('./storage/simul_inv.csv')