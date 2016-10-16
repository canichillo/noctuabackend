#!/usr/bin/python
# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager

from django.conf import settings

# Establece la configuración de la base de datos
configbd = 'default'

# Nuestro motor de base de datos
engine = create_engine('postgresql://' + settings.DATABASES[configbd]['USER'] + ':' +
                       settings.DATABASES[configbd]['PASSWORD'] + '@' +
                       settings.DATABASES[configbd]['HOST'] + '/' +
                       settings.DATABASES[configbd]['NAME'], convert_unicode=True)

# Nuestra sesión
Session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

@contextmanager
def transaction_context():
    session = Session()
    try:
        yield session
    except:
        raise
    finally:
        Session.remove()


Base = declarative_base()
Base.query = Session.query_property()