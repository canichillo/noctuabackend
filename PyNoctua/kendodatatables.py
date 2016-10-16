#!/usr/bin/python
# -*- coding: utf-8 -*-

from sqlalchemy.sql.expression import asc, desc
from sqlalchemy.sql import and_
import sys
from PyNoctua.models import *


class KendoDataTables:
    def __init__(self, arguments, query, columnas):
        self.query = query
        self.columnas = columnas

        if '$filter' in arguments:
            self.filtering(arguments['$filter'])

        if '$orderby' in arguments:
            self.sorting(arguments['$orderby'])

    def filtering(self, filtrado):
        filters = filtrado.split(' and ')

        for filter in filters:
            if 'startswith' in filter:
                parametros = filter.replace("startswith", "").replace("tolower", "").\
                    replace("(", "").replace(")", "").split(",")
                nombre = parametros[0]
                valor = parametros[1].encode('utf-8')
                self.query = self.query.filter(getattr(getattr(sys.modules[__name__],
                                                               self.columnas[nombre].split('.')[0]),
                                                       self.columnas[nombre].split('.')[1])
                                               .ilike("{0}%".format(valor.replace("'", ""))))

            if 'endswith' in filter:
                parametros = filter.replace("endswith", "").replace("tolower", "").\
                    replace("(", "").replace(")", "").split(",")
                nombre = parametros[0]
                valor = parametros[1].encode('utf-8')
                self.query = self.query.filter(getattr(getattr(sys.modules[__name__],
                                                               self.columnas[nombre].split('.')[0]),
                                                       self.columnas[nombre].split('.')[1])
                                               .ilike("%{0}".format(valor.replace("'", ""))))

            if 'substringof' in filter:
                parametros = filter.replace("substringof", "").\
                    replace("(", "").replace(")", "").split(",")
                nombre = parametros[1]
                valor = parametros[0].encode('utf-8')
                self.query = self.query.filter(getattr(getattr(sys.modules[__name__],
                                                               self.columnas[nombre].split('.')[0]),
                                                       self.columnas[nombre].split('.')[1])
                                               .like("%{0}%".format(valor.replace("'", ""))))

            if ' ne ' in filter:
                parametros = filter.split(' ne ')
                nombre = parametros[0]
                valor = parametros[1].encode('utf-8').replace("datetime", "")
                self.query = self.query.filter(getattr(getattr(sys.modules[__name__],
                                                               self.columnas[nombre].split('.')[0]),
                                                       self.columnas[nombre].split('.')[1]) != valor.replace("'", ""))

            if ' eq ' in filter:
                parametros = filter.split(' eq ')
                nombre = parametros[0]
                valor = parametros[1].encode('utf-8')

                if 'datetime' in valor:
                    if 'T' in valor:
                        inicio = valor.replace("datetime", "").split("T")[0] + " 00:00"
                        fin = valor.replace("datetime", "").split("T")[0] + " 23:59"
                        self.query = self.query.filter(and_(getattr(getattr(sys.modules[__name__],
                                                                       self.columnas[nombre].split('.')[0]),
                                                               self.columnas[nombre].split('.')[1]) >= inicio,
                                                       getattr(getattr(sys.modules[__name__],
                                                                       self.columnas[nombre].split('.')[0]),
                                                               self.columnas[nombre].split('.')[1]) <= fin))
                    else:
                        self.query = self.query.filter(getattr(getattr(sys.modules[__name__],
                                                                       self.columnas[nombre].split('.')[0]),
                                                               self.columnas[nombre].split('.')[1]) == valor.replace("'", ""))
                else:
                    self.query = self.query.filter(getattr(getattr(sys.modules[__name__],
                                                                   self.columnas[nombre].split('.')[0]),
                                                           self.columnas[nombre].split('.')[1]) == valor.replace("'", ""))

            if ' gt ' in filter:
                parametros = filter.split(' gt ')
                nombre = parametros[0]
                valor = parametros[1].encode('utf-8').replace("datetime", "")
                self.query = self.query.filter(getattr(getattr(sys.modules[__name__],
                                                               self.columnas[nombre].split('.')[0]),
                                                       self.columnas[nombre].split('.')[1]) > valor)

            if ' lt ' in filter:
                parametros = filter.split(' lt ')
                nombre = parametros[0]
                valor = parametros[1].encode('utf-8').replace("datetime", "")
                self.query = self.query.filter(getattr(getattr(sys.modules[__name__],
                                                               self.columnas[nombre].split('.')[0]),
                                                       self.columnas[nombre].split('.')[1]) < valor)

            if ' ge ' in filter:
                parametros = filter.split(' ge ')
                nombre = parametros[0]
                valor = parametros[1].encode('utf-8').replace("datetime", "")
                self.query = self.query.filter(getattr(getattr(sys.modules[__name__],
                                                               self.columnas[nombre].split('.')[0]),
                                                       self.columnas[nombre].split('.')[1]) >= valor)

            if ' le ' in filter:
                parametros = filter.split(' le ')
                nombre = parametros[0]
                valor = parametros[1].encode('utf-8').replace("datetime", "")
                self.query = self.query.filter(getattr(getattr(sys.modules[__name__],
                                                               self.columnas[nombre].split('.')[0]),
                                                       self.columnas[nombre].split('.')[1]) <= valor)

    def sorting(self, ordenacion):
        sorts = ordenacion.split(',')

        for sort in sorts:
            if ' ' in sort:
                self.query = self.query.order_by(asc(self.columnas[sort.split(' ')[0]]) if sort.split(' ')[1] == 'asc'
                                                 else desc(self.columnas[sort.split(' ')[0]]))
            else:
                self.query = self.query.order_by(asc(self.columnas[sort.split(' ')[0]]))


    def filtro(self):
        return self.query