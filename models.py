from sqlalchemy import Column, Integer, String, Float
import db

class Criptomoneda(db.Base):
    __tablename__ = 'criptomoneda'
    __table_args__ = {'sqlite_autoincrement': True} # Habilitamos el autoincrement en la PK
    id_criptomoneda = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    simbolo = Column(String, nullable=False)
    cmc_rank = Column(Integer)
    precio_usd = Column(Float)
    pares = Column(Integer)


    def __init__(self, nombre, simbolo, cmc_rank, precio_usd, pares):
        self.nombre = nombre
        self.simbolo = simbolo
        self.cmc_rank = cmc_rank
        self.precio_usd = precio_usd
        self.pares = pares

    def __str__(self):
        return "Criptomoneda: {}, simbolo: {}".format(self.nombre, self.simbolo)


class Exchange(db.Base):
    __tablename__ = 'exchange'
    id_exchange = Column(Integer, nullable=False, primary_key=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(String)
    volumen_usd = Column(Float)
    visitas_semanales = Column(Integer)
    
    
    def __init__(self, id, nombre, descripcion, volumen_usd, visitas_semanales):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.volumen_usd = volumen_usd
        self.visitas_semanales = visitas_semanales

    def __str__(self):
        return "Exchange: {}, visitas semanales: {}".format(self.nombre, self.visitas_semanales)


class Categoria(db.Base):
    __tablename__ = 'categoria'
    id_categoria = Column(Integer, nullable=False, primary_key=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(String)
    numero_tokens = Column(Integer)
    cap_mercado = Column(Float)
    cambio_cap_mercado = Column(Float)
    volumen = Column(Float)
    cambio_volumen = Column(Float)

    def __init__(self, id, nombre, descripcion, numero_tokens, cap_mercado, cambio_cap_mercado,
                 volumen, cambio_volumen):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.numero_tokens = numero_tokens
        self.cap_mercado = cap_mercado
        self.cambio_cap_mercado = cambio_cap_mercado
        self.volumen = volumen
        self.cambio_volumen = cambio_volumen

    def __str__(self):
        return "Categoria: {}, numero de tokens: {}".format(self.nombre, self.numero_tokens)