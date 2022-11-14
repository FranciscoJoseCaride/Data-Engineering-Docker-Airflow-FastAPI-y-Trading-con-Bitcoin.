# To run: streamlit run dashboard.py

import streamlit as st

import pandas as pd
from pandas_datareader.data import DataReader
from datetime import date 
import matplotlib as plt
import matplotlib.pyplot as plt
import numpy as np

import warnings
warnings.filterwarnings("ignore")

st.write("""
    # Estrategia de inversión Dual Moving Average Crossover (DMAC) para Bitcoins
    ## Francisco José Caride
""")

st.markdown("""<div style="text-align: justify"> 
    En este tablero se muestra el resultado para un DMAC con Bitcoins. La estrategia consiste en calcular una media móvil de "corto plazo" y otra de "largo plazo" con las cuales, de acuerdo que cuerva esté por encima de la otra (corto y medio), conviene vender o comprar. Básicamente hay dos enfoques, técnico y de valor. En este trabajo nos manejamos por el enfoque técnico el cual establece que cuando la curva de corto está por encima de la de largo compras (y mantenes) tu activo, y cuando estan al reves vendes tu activo y te mantenes con el cash. En este link hay una MUY buena explicación de la estrategia de inversión DMAC: https://people.duke.edu/~charvey/Teaching/BA453_2002/CCAM/CCAM.htm
    </div>""" , unsafe_allow_html=True)

data = ['ETH-USD','BTC-USD'] 
cripto = DataReader(data, 'yahoo', start=date(2014,9,17))
bitcoin = pd.DataFrame(cripto['Close']['BTC-USD'])

#####################################
#####################################
short = 30
long = 100
#####################################
#####################################

estrategia = pd.DataFrame(index=['strategy'],columns=['short','long'])
estrategia['short'] = [short]
estrategia['long'] = [long]

st.markdown(""" <br>""" , unsafe_allow_html=True) 
st.markdown("""<div style="text-align: justify"> 
    En esta caso vamos a usar la siguiente estrategia para long y short (podes cambiar la estrategia de short y long desde el código del tablero!):
    </div>""" , unsafe_allow_html=True)
st.markdown(""" <br>""" , unsafe_allow_html=True) 
st.dataframe(estrategia)

st.markdown("""<div style="text-align: justify"> 
    Aplicamos el algoritmo y gráficamente nos quedaría:
    </div>""" , unsafe_allow_html=True)

bitcoin['short'] = bitcoin['BTC-USD'].rolling(window=short).mean()
bitcoin['long'] = bitcoin['BTC-USD'].rolling(window=long).mean()
bitcoin = bitcoin[bitcoin['long'].notnull()]

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
   
st.markdown(""" <br>""" , unsafe_allow_html=True) 
# Graficamos
my_stocks = signal
fig1 = plt.figure(figsize=(25,8)) 
plt.scatter(my_stocks.index, my_stocks['Buy_Signal_Price'], color = 'green', label='Buy Signal', marker = '^', alpha = 1)
plt.scatter(my_stocks.index, my_stocks['Sell_Signal_Price'], color = 'red', label='Sell Signal', marker = 'v', alpha = 1)
plt.plot( my_stocks['BTC-USD'],  label='BTC-USD', alpha = 0.3)
plt.plot( my_stocks['short'],  label='short', alpha = 1)
plt.plot( my_stocks['long'],  label='long', alpha = 1)
plt.title('Bitcoin Dual Moving Average Crossover investment strategy',fontsize=35)
plt.xlabel('Date',fontsize=25)
plt.ylabel('Adj. Close Price USD ($)',fontsize=25)
plt.legend( loc='upper left',fontsize='xx-large')
plt.xticks(fontsize=15)
plt.yticks(fontsize=15)
st.pyplot(fig1)


# Generamos historicos resumido y completo

primer_compra = signal[signal['Buy_Signal_Price'].notnull()].index.min()
simul_inv = signal[signal.index >= primer_compra]
simul_inv['Buy_Signal_Price'] = simul_inv['Buy_Signal_Price']*(-1)
simul_inv = simul_inv[['Buy_Signal_Price','Sell_Signal_Price']]

# Me guardo copia de la versión completa para usar más adeleante, avanzo con versión resumida
simul_inv_completa = simul_inv.copy()

#Sigo con el anterior
simul_inv = simul_inv[ (simul_inv['Buy_Signal_Price'].notnull()) | (simul_inv['Sell_Signal_Price'].notnull()) ]
simul_inv = simul_inv.fillna(0)
simul_inv['ganancia'] = simul_inv['Buy_Signal_Price'] + simul_inv['Sell_Signal_Price']
simul_inv['ganancia_acumulada'] = simul_inv['ganancia']
simul_inv['ganancia_acumulada'] = simul_inv['ganancia_acumulada'].cumsum()

simul_inv.reset_index(inplace=True)
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

simul_inv = simul_inv.merge(simul_inv_completa[['position']],left_index=True,right_index=True,how='left')

dias = simul_inv.reset_index()
dias = dias['Date'].max().to_numpy() - dias['Date'].min().to_numpy()
dias = dias.astype('timedelta64[D]')
dias = dias / np.timedelta64(1, 'D')
anios = round(dias / 365,2)

st.write('Durante la ventana de tiempo desde',simul_inv_completa.index.min().to_pydatetime().date(),'hasta',simul_inv_completa.index.max().to_pydatetime().date(),'tuve que reponer de mis ganancias usd',round(simul_inv['ganancia_acumulada'][simul_inv['ganancia_acumulada'] < 0].sum(),2), 'porque la estrategia de inversión no reporto ganancia en algunos periodos, sin embargo la ganancia neta total fue de usd', simul_inv['ganancia_acumulada'][-1],'en',round(dias,0),'días, por ende una ganacia promedio por anio de (aprox):' ,round(simul_inv['ganancia_acumulada'][-1]/anios,2),'. De',len(simul_inv),'intervenciones de compra/venta en el mercado, en',len(simul_inv[simul_inv['ganancia_acumulada'] < 0]),'tuve pérdidas. La peor pérdida fue de usd:',simul_inv['ganancia_acumulada'][simul_inv['ganancia_acumulada'] < 0].min(),'y la ronda que más se gano fue de usd:',simul_inv['ganancia_acumulada'][simul_inv['ganancia_acumulada'] > 0].max(),'. Esta estrategia implica un short de',short,'días y un long de',long,'días.')

st.markdown(""" <br>""" , unsafe_allow_html=True) 
st.markdown("""<div style="text-align: justify"> 
    Esta es mi posición consolidad de los últimos 30 días:
    </div>""" , unsafe_allow_html=True)

st.dataframe(simul_inv_completa.tail(30))


st.markdown("""<div style="text-align: justify"> 
    Esta es mi posición resumida:
    </div>""" , unsafe_allow_html=True)
st.dataframe(simul_inv)