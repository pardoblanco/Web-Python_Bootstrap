import os

from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import sys, json, db
from sqlalchemy import and_, or_, text
from models import Criptomoneda, Exchange, Categoria
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import sqlite3

app = Flask(__name__)

@app.route("/")
def home():

    return render_template("index.html")

@app.route("/exchanges")
def exchange():
    def tablaVisitasExchanges():
        con = sqlite3.connect('database/criptomonedas.db')
        df_exchanges = pd.read_sql_query('SELECT nombre, volumen_usd, visitas_semanales from exchange;', con)
        df = df_exchanges.sort_values('visitas_semanales', ascending=False)
        return df.to_numpy()

    return render_template("exchanges.html", data_rows=tablaVisitasExchanges())

@app.route("/criptomonedas")
def criptomoneda():
    def tablaCriptomonedas():
        con = sqlite3.connect('database/criptomonedas.db')
        df_exchanges = pd.read_sql_query('SELECT nombre, simbolo, cmc_rank, precio_usd, pares from criptomoneda;', con)
        df = df_exchanges.sort_values('cmc_rank')
        return df.to_numpy()

    return render_template("criptomonedas.html", data_rows=tablaCriptomonedas())


@app.route("/criptomonedas/crear_criptomoneda", methods=["POST"])
def crearCriptomoneda():
    criptomoneda = Criptomoneda(nombre=request.form['nombre_criptomoneda'], simbolo=request.form['simbolo_criptomoneda'], cmc_rank=request.form['ranking_criptomoneda'],
                                precio_usd=request.form['precio_criptomoneda'], pares=request.form['pares_criptomoneda'])
    db.session.add(criptomoneda)
    db.session.commit()

    return redirect(url_for('criptomoneda'))

@app.route("/criptomonedas/eliminar_criptomoneda", methods=["POST"])
def eliminarCriptomoneda():
    db.session.query(Criptomoneda).filter_by(nombre=request.form['nombre_criptomoneda']).delete()
    db.session.commit()
    return redirect(url_for('criptomoneda'))

@app.route("/criptomonedas/modificar_criptomoneda", methods=["POST"])
def modificarCriptomoneda():
    nombre = request.form['nombre_criptomoneda_modificar']
    cripto = db.session.query(Criptomoneda).filter(Criptomoneda.nombre == nombre).first()
    print(cripto)

    if cripto is None:
        print("La criptomoneda indicada no existe")
    else:
        nuevo_nombre = request.form['nuevo_nombre']
        cripto.nombre = nuevo_nombre

        nuevo_simbolo = request.form['nuevo_simbolo']
        cripto.simbolo = nuevo_simbolo

        nuevo_ranking = request.form['nuevo_ranking']
        cripto.cmc_rank = nuevo_ranking

        nuevo_precio = request.form['nuevo_precio']
        cripto.precio_usd = nuevo_precio

        nuevo_pares = request.form['nuevo_pares']
        cripto.pares = nuevo_pares

    db.session.commit()
    print("Criptomoneda ACTUALIZADA")

    return redirect(url_for('criptomoneda'))

@app.route("/ecosistemas")
def ecosistema():
    def tablaEcosistemas():
        con = sqlite3.connect('database/criptomonedas.db')
        df_exchanges = pd.read_sql_query('SELECT nombre, numero_tokens, cap_mercado from categoria;', con)
        df = df_exchanges.sort_values('numero_tokens', ascending=False).head(5)
        return df.to_numpy()

    return render_template("ecosistemas.html", data_rows=tablaEcosistemas())


# A CONTINUECION NOS CONECTAMOS A LA API DE CMC Y DESCARGAMOS LOS FICHEROS JSON QUE METEREMOS EN LA BD
def descargarJSONCriptomonedas(cantidad):
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    parameters = {
        'start': '1',
        'limit': cantidad,
        'convert': 'USD'
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': 'f265fb6b-6418-47ce-abaf-31252144cf23',
    }

    session = Session()
    session.headers.update(headers)

    try:
        response = session.get(url, params=parameters)
        data = json.loads(response.text)
        # print(data)
        with open('database/criptomonedas.json', 'w') as op:
            json.dump(data, op)
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)

def descargarJSONExchanges():
    url = 'https://pro-api.coinmarketcap.com/v1/exchange/info'
    parameters = {
        'slug': 'binance,kucoin,kraken,hotbit,bitfinex'
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': 'f265fb6b-6418-47ce-abaf-31252144cf23',
    }

    session = Session()
    session.headers.update(headers)

    try:
        response = session.get(url, params=parameters)
        data = json.loads(response.text)
        print(data)
        with open('database/exchanges.json', 'w') as op:
            json.dump(data, op)
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)

def descargarJSONCategorias():
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/categories'
    parameters = {
        'start': '2',
        'limit': '200'
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': 'f265fb6b-6418-47ce-abaf-31252144cf23',
    }

    session = Session()
    session.headers.update(headers)

    try:
        response = session.get(url, params=parameters)
        data = json.loads(response.text)
        print(data)
        with open('database/categorias_cmc.json', 'w') as op:
            json.dump(data, op)
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)


# CREAMOS LAS FUNCIONES QUE CREARAN LAS TABLAS DE LA BD
def crearTablasCriptomonedas(ruta):
    with open(ruta) as contenido:
        datos = json.load(contenido)

        for elemento in datos['data']:
            # print(elemento['name']) PARA DEBUG
            c = Criptomoneda(nombre=elemento['name'], simbolo=elemento['symbol'], cmc_rank=elemento['cmc_rank'],
                             precio_usd=elemento['quote']['USD']['price'],
                             pares=elemento['num_market_pairs'])
            db.session.add(c)
            db.session.commit()
        db.session.close()

def crearTablasExchanges(ruta):
    with open(ruta) as contenido:
        datos = json.load(contenido)

        for dato in datos['data']:

            e = Exchange(datos['data'][dato]['id'], datos['data'][dato]['name'], datos['data'][dato]['description'],
                         datos['data'][dato]['spot_volume_usd'], datos['data'][dato]['weekly_visits'])
            db.session.add(e)
            db.session.commit()
        db.session.close()

def crearTablasCategorias(ruta):
    with open(ruta) as contenido:
        datos = json.load(contenido)

        for elemento in datos['data']:
            c = Categoria(id=elemento['id'], nombre=elemento['name'], descripcion=elemento['description'],
                          numero_tokens=elemento['num_tokens'], cap_mercado=elemento['market_cap'],
                          cambio_cap_mercado=elemento['market_cap_change'], volumen=elemento['volume'],
                          cambio_volumen=elemento['volume_change'])
            db.session.add(c)
            db.session.commit()
        db.session.close()

# A PARTIR DE AQUI ESTARAN LAS FUNCIONES PARA CREAR LAS IMG DE LOS GRAFICOS.

# GRAFICOS DE LA TABLA DE EXCHANGES

def graficoTrataVolumenUsdExchanges(): # grafico de tarta del volumen de USD de cada exchange
    volumen = []
    nombres = []
    colores = ['#008fd5', '#fc4f30', '#e5ae37', '#6d904f', '#1abc9c', '#616a6b']
    result = db.session.query(Exchange).all()
    for exchange in result:
        nombres.append(exchange.nombre)
        volumen.append(exchange.volumen_usd)


    plt.pie(volumen, labels=nombres, colors= colores, wedgeprops={'edgecolor': 'black'})
    plt.title('Volumen de USD manejado por cada exchange')
    plt.savefig('static/img/grafico_tarta_volumen_exchanges.jpg')
    plt.clf()


def graficoBarrasVisitasSemanalesExchanges(): # Grafico de barras de visitas semanales por exchange
    nombres = []
    visitas = []
    colores = ['#008fd5', '#fc4f30', '#e5ae37', '#6d904f', '#1abc9c', '#616a6b']
    result = db.session.query(Exchange).all()
    for exchange in result:
        nombres.append(exchange.nombre)
        visitas.append(exchange.visitas_semanales)


    plt.bar(nombres, visitas)
    plt.xlabel('Exchange')
    plt.ylabel('Visitas semanales')
    plt.title('Visitas semanales por exchange')
    plt.savefig('static/img/grafico_barras_visitas_exchanges.jpg')
    plt.clf() # Con esto limpiamos el grafico para que no se superpongan con los otros graficos

# GRAFICOS DE LA TABLA DE CRIPTOMONEDAS

def graficosCriptomonedasPares():
    pares = []
    simbolos = []

    result = db.session.query(Criptomoneda).limit(10)
    for cripto in result:
        pares.append(cripto.pares)
        simbolos.append(cripto.simbolo)

    plt.bar(simbolos, pares)
    plt.title('Numero de pares por criptomoneda')
    plt.xlabel('Criptomoneda')
    plt.ylabel('Nº de pares')
    plt.savefig('static/img/grafico_barras_criptomonedas_pares.jpg')
    plt.clf()  # Con esto limpiamos el grafico para que no se superpongan con los otros graficos

def graficoVolumenVisitas():
    exchange_nombre = []
    volumen = []
    visitas = []
    volumen_visitas = []

    result = db.session.query(Exchange).all()
    for exchange in result:
        exchange_nombre.append(exchange.nombre)
        volumen.append(exchange.volumen_usd)
        visitas.append(exchange.visitas_semanales)
        volumen_visitas.append((exchange.volumen_usd) / (exchange.visitas_semanales))

    bar_color = ['#495875']
    plt.bar(exchange_nombre, volumen_visitas, color=bar_color)
    plt.title('Volumen medio de USD por cada visita')
    plt.xlabel('Exchange')
    plt.ylabel('Volumen')
    plt.savefig('static/img/grafico_volumen_visitas_exchange.jpg')
    plt.clf()  # Con esto limpiamos el grafico para que no se superpongan con los otros graficos



if __name__ == "__main__":
    descargarJSONCriptomonedas(30)
    descargarJSONExchanges()
    descargarJSONCategorias()

    # RUTAS DE DONDE SACA LA BBDD LOS DATOS DE LOS JSON
    rutaJsonExchanges = 'database/exchanges.json'
    rutaJsonCriptomonedas = "database/criptomonedas.json"
    rutaJsonCategorias = 'database/categorias_cmc.json'

    if os.path.isfile('database/criptomonedas.db'):

    # CREAMOS LOS GRAFICOS
        graficoTrataVolumenUsdExchanges()
        graficoBarrasVisitasSemanalesExchanges()
        graficoVolumenVisitas()
        graficosCriptomonedasPares()

    # SI EXISTE YA LA BASE DE DATOS
        app.run(debug=True)

    else:
    # SI NO EXISTE LA BASE DE DATOS
        # CREAMOS LA BD, LAS TABLAS, E INTRODUCIMOS LOS DATOS
        db.Base.metadata.create_all(db.engine)
        crearTablasCriptomonedas(rutaJsonCriptomonedas)
        crearTablasExchanges(rutaJsonExchanges)
        crearTablasCategorias(rutaJsonCategorias)

        # CREAMOS LOS GRAFICOS
        graficoTrataVolumenUsdExchanges()
        graficoBarrasVisitasSemanalesExchanges()
        graficoVolumenVisitas()
        graficosCriptomonedasPares()

        app.run(debug=True)