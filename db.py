from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# El engine permite a SQLAlchemy comunicarse con la base de datos
# https://docs.sqlalchemy.org/en/14/core/engines.html
engine = create_engine('sqlite:///database/criptomonedas.db', connect_args={'check_same_thread': False})
# Advertencia, crear el engine no conecta directamente a la base de datos, eso lo hacemos mas adelante

# Ahora creamos la sesion, lo que nos permite realizar operaciones dentro de nuestra BD
Session = sessionmaker(bind=engine)
session = Session()

# Ahora vamos al fichero models.py y en los modelos (clases) donde queramos que se transformen en tablas le añadiremos esta
# variable, y esta se encargara de mapear y vincular la variable a la tabla.
Base = declarative_base()