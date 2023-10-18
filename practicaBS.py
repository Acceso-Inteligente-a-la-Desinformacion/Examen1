import re

# IMPORTACIONES #

import sqlite3
import random
import datetime

from typing import List

class DbField:
    def __init__(self, name: str, type: str, min: int = 0, max: int = 1000):
        self.name = name.replace(' ', '_').upper()
        self.type = type
        self.min = min
        self.max = max
    
    def get(self):
        return f'{self.name.upper()} {self.type.upper()}'
    
    def exampleValue(self):
        if self.type.lower() == 'text':
            value = self.name.capitalize() + ' ' + str(random.randint(self.min, self.max))
        elif self.type.lower() == 'int':
            value = random.randint(self.min, self.max)
        elif self.type.lower() == 'date':
            value = datetime.datetime.now()

        return value
    
class DbTable:
    def __init__(self, name: str, fields: List[DbField]):
        self.name = name.lower().replace(' ', '_')
        self.fields = fields

class DB:
    def __init__(self, dbName: str, tables: List[DbTable] = [], enviorenment: str = 'prod'):

        self.dbName = dbName
        self.tables = tables
        
        self.connection = None

        self.enviorenment = enviorenment

        self.connect()
        self.createSchema()

    def getTable(self, tableName: str):
        for table in self.tables:
            if table.name == tableName:
                return table

    def rebuildSchema(self, env:str = 'dev'):
        for table in self.tables:
            if self.enviorenment == 'dev' and env == 'dev':
                self.dropTable(table.name, 'dev')
                self.createTable(table.name, 'dev')
                self.dummyData(table)

            self.dropTable(table.name)
            self.createTable(table.name)

    def createSchema(self):
        for table in self.tables:
            if self.enviorenment == 'dev':
                self.createTable(table.name, 'dev')
                self.dummyData(table)

            self.createTable(table.name)
        

    def dummyData(self, table: DbTable, quantity: int = 25):
        while(quantity > 0):
            data = []
            for field in table.fields:
                data.append(field.exampleValue())

            t = tuple(e for e in data)

            self.insert(table.name, t, 'dev')

            quantity -= 1

    def connect(self):
        connection = sqlite3.connect(self.dbName+'.db')
        connection.text_factory = str

        self.connection = connection

    def dropTable(self, tableName: str, env: str = 'prod'):
        table = self.getTable(tableName)

        if(env == 'dev'):
            appendName = f'_{env}'
        else:
            appendName = ''

        self.connection.execute("DROP TABLE IF EXISTS "+table.name+appendName)
        self.connection.commit()

    def closeConnection(self, env: str = 'prod'):
        self.connection.close()

    def exec(self, query: str, data: tuple = ()):

        #print(query)
        #print(data)

        if len(data):
            result = self.connection.execute(query, data)
        else:
            result = self.connection.execute(query)

        self.connection.commit()
        return result
    
    def createTable(self, tableName: str, env: str = 'prod'):
        table = self.getTable(tableName)
        
        if(env == 'dev'):
            appendName = f'_{env}'
        else:
            appendName = ''

        fieldsQuery = ""
        i = 1
        for field in table.fields:
            fieldsQuery += field.get() + (', ' if i<len(table.fields) else '')
            i += 1

        return self.exec("CREATE TABLE IF NOT EXISTS "+table.name+appendName+" ("+fieldsQuery+");")
    
    def insert(self, tableName: str, data: tuple, env: str = 'prod'):

        table = self.getTable(tableName)

        if(env == 'dev'):
            appendName = f'_{env}'
        else:
            appendName = ''
    
        variables = ''
        i = 1
        for field in table.fields:
            variables += '?' + (',' if i<len(table.fields) else '')
            i += 1

        return self.exec(f"INSERT INTO {table.name}{appendName} VALUES ({variables})", data)

    def countTable(self, tableName: str):
        return self.exec('SELECT COUNT(*) FROM '+tableName).fetchone()[0]
    

from tkinter import *
from tkinter import messagebox

from typing import List

class FormWindow:
    def __init__(self, title, components):
        self.components = components

        self.end = END

        self.entryComponents = []

        self.title = title

        self.root = Toplevel()

    def create(self):
        self.root.title(self.title)

        for c in self.components:
            # Parámetros opcionales
            if 'side' not in c.keys():
                c['side'] = LEFT

            if 'width' not in c.keys():
                c['width'] = 30

            if 'onChangeEvent' not in c.keys():
                c['onChangeEvent'] = True

            if 'func' not in c.keys():
                c['func'] = self.nullFunctionality

            # Función que devuelve el parámetro introducido en el input
            def create_func(component, entry):
                def func(param=None):
                    return component['func'](entry.get(), self)
                return func

            # Generador de formulario
            if c['type'] == 'label':
                entry = Label(self.root, text=c['text']).pack(side=c['side'])

            elif c['type'] == 'spinbox':
                entry = Spinbox(self.root, width=c['width'], values=c['values'])

                if c['onChangeEvent'] == True:
                    entry.configure(command=create_func(c, entry))

                entry.bind("<Return>", create_func(c, entry))
                entry.pack(side=LEFT)

            elif c['type'] == 'text':
                entry = Entry(self.root, width=c['width'])

                entry.bind("<Return>", create_func(c, entry))
                entry.pack(side=LEFT)

            elif c['type'] == 'entry':
                entry = Entry(self.root)
                entry.bind("<Return>", create_func(c, entry))
                entry.pack(side=LEFT)

            self.entryComponents.append(entry)

    def nullFunctionality(param, window):
        print('No has añadido ninguna funcionalidad a este componente')

class Component:
    def __init__(self, type, text, callback):
        self.type = type
        self.text = text
        self.callback = callback

# Elemento dentro de un menu
class MenuTabItem:
    def __init__(self, label, callback):
        self.label = label
        self.callback = callback

# Un nuevo apartado dentro del menu
class MenuTab:
    items = []

    def __init__(self, title, items: type(MenuTabItem) = []):
        self.title = title
        self.items = items

    def addTab(self, tab: type(MenuTabItem)):
        self.items.append(tab)

# Interfaz gráfica de la aplicación
class GUI:
    title = 'Untitled'

    def __init__(self):
        self.root = Tk()
        self.menubar = Menu(self.root)

    def addRootComponent(self, component):
        if component.type == 'frame':
            print('aunno')
        elif component.type == 'button':
            button = Button(self.root, text=component.text, command=component.callback)
            button.pack()

    def setTitle(self, title):
        self.title = title

    def addMenuTab(self, menutab: type(MenuTab)):
        menu = Menu(self.menubar)

        for item in menutab.items:
            menu.add_command(label=item.label, command=item.callback)

        self.menubar.add_cascade(label=menutab.title, menu=menu)

    def launch(self):
        self.root.title(self.title)
        self.root.config(menu=self.menubar)
        self.root.mainloop()

    def close(self):
        self.root.quit()

    def message(self, title, message):
        messagebox.showinfo(title, message)

    # Muestra en una nueva ventana con scroll el contenido
    def listScrollWindow(self, title, content: List[List[str]], width=150):
        v = Toplevel()
        v.title(title)
        sc = Scrollbar(v)
        sc.pack(side=RIGHT, fill=Y)
        lb = Listbox(v, width = 150, yscrollcommand=sc.set)

        for row in content:
            for r in row:
                lb.insert(END, r)
            lb.insert(END,"\n\n")

        lb.pack(side=LEFT,fill=BOTH)
        sc.config(command = lb.yview)

    def formWindow(self, title, components):
        return FormWindow(title, components)
    
from bs4 import BeautifulSoup
from urllib import request, parse

import ssl, os
if (not os.environ.get('PYTHONHTTPSVERIFY', '')and
    getattr(ssl,'_create_unverified_context', None)):
    ssl._create_default_https_context=ssl._create_unverified_context

class Scrapper:
    def __init__(self, url, type:str = "html.parser"):
        self.url = url
        self.type = type
    
    def post(self, data):
        data = parse.urlencode(data).encode()
        req =  request.Request(self.url, data=data)
        html = request.urlopen(req)
        self.soup = BeautifulSoup(html, self.type)
        
    def get(self):
        html = request.urlopen(self.url)
        self.soup = BeautifulSoup(html, self.type)

    def select(self, selector:str):
        return self.soup.select(selector)
    
    def selectOne(self, selector:str):
        return self.soup.select_one(selector)
    
    def find(self, element, className):
        return self.soup.find_all(element, {"class": className})
    
    def findOne(self, element, className):
        return self.soup.find(element, {"class": className})

class App:
    def __init__(self, title='Título del programa'):
    
        self.db = DB('dbExamen', [
            DbTable(
                name="noticias",
                fields = [
                    DbField(
                        'Categoria',
                        'text'
                    ),
                    DbField(
                        'Titular',
                        'text'
                    ),
                    DbField(
                        'Fecha Publicacion',
                        'date'
                    ),
                    DbField(
                        'Autor',
                        'text'
                    ),
                    DbField(
                        'Link Twitter',
                        'int'
                    ),
                    DbField(
                        'Etiquetas',
                        'text'
                    ),
                    DbField(
                        'Noticias Recomendadas',
                        'text'
                    )
                ]
            ),
            DbTable(
                name="etiquetas",
                fields = [
                    DbField(
                        'Titulo',
                        'text'
                    )
                ]
            )
        ]) # Inicializa la conexión a la base de datos

        self.gui = GUI() # Inicializa la interfaz gráfica
        self.gui.setTitle(title) # Asigna un título a la interfaz gráfica
        
        # Por cada elemento del menú en el método getMenu lo añade a la MenuBar de la interfaz gráfica
        for menutab in self.getMenu():
            self.gui.addMenuTab(menutab)

        # Por cada elemento definido en getMainComponents se añade un componente dentro de la ventana principal
        for component in self.getMainComponents():
            self.gui.addRootComponent(component)

        self.gui.launch() # Lanza la interfaz gráfica

    def getMenu(self):
        return [
            MenuTab(
                title = 'Datos',
                items = [
                    MenuTabItem(
                        label = 'Cargar',
                        callback = self.load
                    ),
                    MenuTabItem(
                        label = 'Salir',
                        callback = self.close
                    )
                ]
            ),
            MenuTab(
                title = 'Listar',
                items = [
                    MenuTabItem(
                        label = 'Noticias',
                        callback = self.listNoticias
                    ),
                    MenuTabItem(
                        label = 'Autores',
                        callback = self.listAutores
                    )
                ]
            ),
            MenuTab(
                title = 'Buscar',
                items = [
                    MenuTabItem(
                        label = 'Noticias por etiquetas',
                        callback = self.searchEtiqueta
                    ),
                    MenuTabItem(
                        label = 'Recomendación por titular',
                        callback = self.searchRecomendacion
                    ),
                    MenuTabItem(
                        label = 'Noticias por fecha',
                        callback = self.searchFecha
                    )
                ]
            )
        ]
    
    def getMainComponents(self):
        return []

    def close(self):
        self.db.closeConnection() # Cierra la conexión con la base de datos
        self.gui.close() # Cierra la interfaz gráfica

    def load(self):

        noticias = [] # Elemento que va a almacenar cada vino

        scrappy = Scrapper('https://as.com/baloncesto/') # Inicializa la clase de Scrapper
        scrappy.get() # Hace que el scrapper funcione en método GET

        noticiasHtml = scrappy.select('section.area article')

        allEtiquetas = []

        for noticia in noticiasHtml: # Recorre cada elemento de VINO. Aquí son objetos de tipo BEAUTIFULSOUP

            
            titular = noticia.select_one('h2 > a').text

            categoriaSelector =  noticia.select_one('.s__txt > .s__tl-wr > p.ki > a')
            if categoriaSelector != None:
                categoria = noticia.select_one('.s__txt > .s__tl-wr > p.ki > a').text
            else:
                categoria = ''

            
            fechaSelector = noticia.select_one('.s__date')
            if fechaSelector != None:
                fecha = datetime.datetime.fromisoformat(fechaSelector['datetime']).strftime("%Y-%m-%d %H:%M:%S")
            else:
                fecha = datetime.datetime.now()
            

            autorSelector = noticia.select_one('.s__au')
            if autorSelector != None:
                autor = autorSelector.text
            else:
                autor = ''

            linkNoticia = noticia.select_one('h2 > a')['href']


            scrappy2 = Scrapper(linkNoticia)
            scrappy2.get()


            linkTwitterSelector = scrappy2.selectOne('.art__au__lk')
            if linkTwitterSelector != None:
                linkTwitter = linkTwitterSelector['href']
            else:
                linkTwitter = ''

            etiquetas = scrappy2.select('.art__tags > ul > li > a')

            etiquetasArray = []
            for etiqueta in etiquetas:
                if etiqueta not in allEtiquetas:
                    allEtiquetas.append(etiqueta.text)

                etiquetasArray.append(etiqueta.text)
            

            recomendadas = scrappy2.select('aside.wdt-trends--recommended > ul > li > a')

            recomendadasArray = []
            for recomendada in recomendadas:
                recomendadasArray.append('https://as.com'+recomendada['href'])

            noticias.append((
                categoria,
                titular,
                fecha,
                autor,
                linkTwitter,
                ','.join(etiquetasArray),
                ','.join(recomendadasArray)
            ))

        # Reinicializa la tabla de la base de datos de VINOS
        self.db.rebuildSchema('prod')

        # Por cada tupla de vinos la añade a la tabla
        for noticia in noticias:
            self.db.exec('INSERT INTO NOTICIAS VALUES (?,?,?,?,?,?,?)', noticia)

        for eti in allEtiquetas:
            self.db.exec('INSERT INTO ETIQUETAS VALUES (?)', (eti,))

        partidoQuantity = self.db.countTable('NOTICIAs') # Cuenta la cantidad de vinos
        self.gui.message("Base de Datos", "Cantidad de noticias: "+str(partidoQuantity)) # Muestra un mensaje con la cantidad de elementos añadidos


    def listNoticias(self):
        cursor = self.db.exec('SELECT * FROM NOTICIAS') # Recoge todos los vinos de la tabla

        content = []

        for row in cursor:
            content.append([ 
                "    Categoria: "+ (row[0]),
                "    Titular: "+ (row[1]),
                "    Fecha Publicacion: "+ (row[2]),
                "    Autor: "+ str(row[3]),
                "    Etiquetas: "+ str(row[5])
            ])

        self.gui.listScrollWindow(title='Noticias', content=content)

    def listAutores(self):
        cursor = self.db.exec('SELECT * FROM NOTICIAS') # Recoge todos los vinos de la tabla

        content = []

        for row in cursor:
            content.append([ 
                "    Nombre Autor: "+ str(row[3]),
                "    Link Twitter del autor: "+ str(row[4])
            ])

        self.gui.listScrollWindow(title='Noticias', content=content)
    
    def searchEtiqueta(self):
        def search(param, window):
            cursor = self.db.exec("SELECT * FROM noticias WHERE ETIQUETAS LIKE ?", ('%'+param+'%',))

            content = []
            for row in cursor:
                content.append(["Titular: "+ (row[1] ),
                               "Fecha publicación: "+ str(row[2]),
                               "Categoria: "+str(row[0]),
                               "Link twitter del autor:  " + str(row[4]),
                               "Nombre del autor: " +(row[3]),
                               "Etiqueta: " +(row[5])])

            self.gui.listScrollWindow(title='Buscar jornada', content=content)


        cursor = self.db.exec('SELECT TITULO FROM ETIQUETAS') # Recoge cada denominación sin repetirla

        etiquetas = [d[0] for d in cursor]

        newWindow = self.gui.formWindow(title="Buscar por etiquetas", components = [{
            'type': 'label',
            'text': 'Seleccione una etiqueta: ',
            'side': 'left'
        }, {
            'type': 'spinbox',
            'values': etiquetas,
            'onChangeEvent': False,
            'func': search,
            'side': 'left',
            'width': 30
        }])

        newWindow.create()


    def searchRecomendacion(self):
        def search(param, window):
            cursor = self.db.exec("SELECT TITULAR,NOTICIAS_RECOMENDADAS FROM noticias WHERE TITULAR LIKE ?",('%'+param+'%',))

            bo=False
            if (param.isalnum()== bo):
                messagebox.showerror("Error", "No se permite introducir mas de una palabra")

            resultados = cursor.fetchall()
            content = []
            for c in resultados:
                content.append([
                    'Titular: '+c[0],
                    'Link a noticias recomendadas: '+c[1]
                ])


            self.gui.listScrollWindow(title='Noticias encontradas', content=content)


        newWindow = self.gui.formWindow(title="Buscar noticia", components = [{
            'type': 'label',
            'text': 'Introduce un término: ',
            'side': 'left'
        }, {
            'type': 'text',
            'func': search,
            'side': 'left',
            'width': 30
        }])

        newWindow.create()

    def searchFecha(self):
        def search(param, window):
            try:
                fecha = datetime.datetime.strptime(param, "%d/%m/%Y").strftime("%Y-%m-%d")
            except ValueError:
                self.gui.message(title="Error", message='La fecha introducida no es correcta. Sigue el formato "DD/MM/YYYY"')

            cursor = self.db.exec('SELECT * FROM NOTICIAS WHERE FECHA_PUBLICACION <= ?', (fecha,))

            content = []
            for c in cursor:
                content.append([
                    'Categoria: ' + c[0],
                    'Titular: ' + c[1],
                    'Autor: ' + c[3],
                    'Fecha de publicación: '+c[2],
                    'Etiqueta: '+c[5]
                ])

            self.gui.listScrollWindow(title='Buscar por fecha', content=content)



        newWindow = self.gui.formWindow(title="Buscar por fecha", components = [{
            'type': 'label',
            'text': 'Introduce una fecha: ',
            'side': 'left'
        }, {
            'type': 'entry',
            'func': search,
            'side': 'left',
            'width': 30
        }])

        newWindow.create()
        

# Lanza App
App()
