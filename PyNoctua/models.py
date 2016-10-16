#!/usr/bin/python
# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, DateTime, SmallInteger, BigInteger
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Avatares(Base):
    __tablename__ = "avatares"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(20))

    def __unicode__(self):
        return self.nombre


class Paises(Base):
    __tablename__ = "paises"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50))
    idioma = Column(SmallInteger)

    def __unicode__(self):
        return self.nombre


class Ciudades(Base):
    __tablename__ = "ciudades"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50))
    pais = Column(Integer, ForeignKey(Paises.id))

    def __unicode__(self):
        return self.nombre


class Empresas(Base):
    __tablename__ = "empresas"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50))
    ciudad = Column(Integer, ForeignKey(Ciudades.id))
    direccion = Column(String(75))
    poblacion = Column(String(50))
    codpos = Column(String(5))
    latitud = Column(Float)
    longitud = Column(Float)
    web = Column(String(50))
    telefonos = Column(String(30))
    email = Column(String(50))
    facebook = Column(String(50))
    twitter = Column(String(50))
    descripcion = Column(Text)
    logo = Column(String(64))
    tipo = Column(String(2))
    password = Column(String(9))

    def __unicode__(self):
        return self.nombre


class Administradores(Base):
    __tablename__ = "administradores"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(75))
    tipo = Column(String(2))
    usuario = Column(String(30))
    password = Column(String(32))
    email = Column(String(75))
    empresa = Column(Integer)
    imagen = Column(String(75))
    token = Column(String(500))

    def __unicode__(self):
        return self.nombre


class Ofertas(Base):
    __tablename__ = "ofertas"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50))
    inicio = Column(DateTime)
    fin = Column(DateTime)
    descripcion = Column(Text)
    tipo = Column(String(1))
    imagen = Column(String(64))
    empresa = Column(Integer, ForeignKey(Empresas.id))
    cantidad = Column(SmallInteger)
    
    def __unicode__(self):
        return self.nombre


class Usuarios(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(75))
    usuario = Column(String(30))
    password = Column(String(64))
    email = Column(String(50))
    edad = Column(SmallInteger)
    genero = Column(String(1))
    facebook = Column(String(20))
    so = Column(String(1))
    dispositivo = Column(String(75))
    gcm = Column(String(250))
    apn = Column(String(64))
    token = Column(String(200))
    imagen = Column(String(128))
    baja = Column(String(1))
    fechaact = Column(DateTime)

    def __unicode__(self):
        return self.nombre


class OfertasUsuarios(Base):
    __tablename__ = "ofertasusuarios"
    id = Column(Integer, primary_key=True, autoincrement=True)
    oferta = Column(Integer, ForeignKey(Ofertas.id))
    usuario = Column(Integer, ForeignKey(Usuarios.id))
    adquirida = Column(DateTime)

    def __unicode__(self):
        return self.estado


class ImagenesEmpresa(Base):
    __tablename__ = "imagenesempresa"
    id = Column(Integer, primary_key=True, autoincrement=True)
    empresa = Column(Integer, ForeignKey(Empresas.id))
    archivo = Column(String(64))
    descripcion = Column(Text)
 
    def __unicode__(self):
        return self.archivo


class Favoritos(Base):
    __tablename__ = "favoritos"
    id = Column(Integer, primary_key=True, autoincrement=True)
    empresa = Column(Integer, ForeignKey(Empresas.id))
    usuario = Column(Integer, ForeignKey(Usuarios.id))
    fecha = Column(DateTime)


class ComprasPaypal(Base):
    __tablename__ = "paypal"
    id = Column(Integer, primary_key=True, autoincrement=True)
    fecha = Column(DateTime)
    empresa = Column(Integer, ForeignKey(Empresas.id))
    importe = Column(Float)
    transaccion = Column(String(30))


class Mensajes(Base):
    __tablename__ = "mensajes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    empresa = Column(Integer, ForeignKey(Empresas.id))
    usuario = Column(Integer, ForeignKey(Usuarios.id))
    fecha = Column(DateTime)


class LineasMensajes(Base):
    __tablename__ = "lineasmensajes"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    mensaje = Column(Integer, ForeignKey(Mensajes.id))
    texto = Column(Text)
    fecha = Column(DateTime)
    tipo = Column(String(1))

    def __unicode__(self):
        return self.texto


class Amigos(Base):
    __tablename__ = "amigos"
    id = Column(Integer, primary_key=True, autoincrement=True)
    solicita = Column(Integer, ForeignKey(Usuarios.id))
    solicitado = Column(Integer, ForeignKey(Usuarios.id))
    fecha = Column(DateTime)
    aceptado = Column(String(1))

