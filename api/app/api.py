#pip install fastapi
#pip install "uvicorn[standard]"
# para levantar el webserver: uvicorn nombre_archivo:app --reload el nombre del archivo va sin .py
# para este caso uvicorn api:api --reload


import numpy as np
import pandas as pd

from fastapi import FastAPI
#from fastapi.encoders import jsonable_encoder

api = FastAPI() #-----> mi servicio se va a llamar api, si la llamo pepe cuando la levante va a ser nombre_archivo:pepe

# Precio historico
@api.get('/bitcoin_price_complete/')
async def bitcoin():
    bitcoin = pd.read_csv('storage/bitcoin.csv')
    bitcoin = bitcoin.to_dict(orient='index')
    return bitcoin


# Precio historico filtrado por fecha -- Format to request AAAA-MM-DD with numers, for example: 2014-11-19
@api.get('/bitcoin_price/{data_from}/{data_to}')
async def data(data_from: str,data_to: str):
    bitcoin = pd.read_csv('storage/bitcoin.csv')
    bitcoin['Date'] = pd.to_datetime(bitcoin['Date'])
    bitcoin = bitcoin[ (bitcoin['Date'] >= data_from) & (bitcoin['Date'] <= data_to) ]
    bitcoin = bitcoin.to_dict(orient='index')
    return bitcoin

# Simulación de inversión completa
@api.get('/full_investment_simulation/')
async def full_simul():
    simul_inv_completa = pd.read_csv('storage/simul_inv_completa.csv')
    simul_inv_completa.drop('Unnamed: 0',axis=1,inplace=True)
    simul_inv_completa = simul_inv_completa.to_dict(orient='index')
    return simul_inv_completa

@api.get('/investment_simulation/')
async def simul():
    simul_inv = pd.read_csv('storage/simul_inv.csv')
    simul_inv['Periodo'][0] = '0'
    simul_inv.drop('Unnamed: 0',axis=1,inplace=True)
    simul_inv = simul_inv.to_dict(orient='index')
    return simul_inv

    