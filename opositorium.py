# __author__ = TomeuKuma
# Este software obtiene y muestra ordenadamente la información de los consursos y opociones públicos,
# publicados en el BOE, BOIB, Boletin Oficial del Consell y Ayuntamientos de Mallorca.

from bs4 import BeautifulSoup
import requests
import pandas as pd
import datetime
import numpy as np


# cuenta días que han transcurrido desde 1 de enero de 2019 (fecha de referencia) hasta la fecha actual:
def contar_dias():
    fecha_actual = datetime.date.today()
    fecha_referencia = datetime.date(2019, 1, 1)
    dias_transcurridos = fecha_actual - fecha_referencia
    return dias_transcurridos.days


# Definimos las variables para crear la Url del BOIB actual
num_BOIB_actual = int(10922 + contar_dias() / 7 * 3)
año_actual = datetime.date.today().year

# Creamos listas vacías para guardar los elementos escrapeados por categoría
lista_boletin = []
lista_entidades = []
lista_resoluciones = []
lista_registros = []
lista_links_pdf = []
lista_fechas = []

# Cremos las URLS de los últimos 20 BOIBs publicados desde la fecha actual para scrapear sobre cada uno
for urls in range(20):
    url_BOIB_actual = 'http://www.caib.es/eboibfront/ca/' + str(año_actual) + '/' + str(
        num_BOIB_actual) + '/seccio-ii-autoritats-i-personal/473'
    num_BOIB_actual -= 1

    # Obtiene el html de la web 'url' en formato texto
    BOIB_html = requests.get(url_BOIB_actual)
    BOIB_status = BOIB_html.status_code  # comprueba el estado de la web, si hay conexión, devuelve 200

    # Creamos el objeto BeautifulSoup para dividir el texto html en Tags
    soup = BeautifulSoup(BOIB_html.text, 'lxml')

    # Si la web es accesible (la respuesta es 200), la transformamos en objeto BeautifulSoup)
    if BOIB_status == 200:
        # Creamos el objeto BeautifulSoup para dividir el texto html en Tags
        soup = BeautifulSoup(BOIB_html.text, 'lxml')

        # Filtramos por Tags en la Sopa:
        # Tabla completa de datos de la sección segunda del BOIB
        sec_seg = soup.find_all('ul', {'class': 'entitats'})

        # Comprobamos si existe la subsección primera, y si no, coprobamos si existe la subsección segunda y retornamos la información de la subsección segunda
        # Filtramos la subsección segunda de la sección segunda BOIB
        comprobador = soup.find_all('ul', {'class': 'llistat'})
        if str(comprobador[0]).find(
                'Subsecció primera.') >= 0:  # Retronaría -1 en el caso de que la palabra buscada no existiera en el string html
            sec_seg_sub_seg = sec_seg[1]
        else:
            if str(comprobador[0]).find(
                    'Subsecció segona.') >= 0:  # Si no existe la subsección primera, buscará la subsección segunda en el primer índice de la lista o retornará una string informativa
                sec_seg_sub_seg = sec_seg[0]
            else:
                print('No hay oposiciones/convocatorias este día')

        # Filtramos por anuncio
        anuncios = sec_seg_sub_seg.find_all('div', {'class': 'caja'})

        # fecha_publicacion = "1/1/2019" #cambiar a dinámico dependiendo del nº de BOIB con Xpath
        fecha_publicacion_html = soup.find_all('li', {'class': 'primerElemento'})
        fecha_publicacion = str(fecha_publicacion_html)[154:171]

        # Filtra por cada uno de los anuncios en la sección segunda y guarda los datos scrapeados en listas
        for anuncio in anuncios:

            # Obtiene el nombre del boletín en el que se publica el anuncio
            lista_boletin.append("BOIB")

            # Obtiene la fecha de las publicaciones del BOIB del día de referencia y los guarda en una lista
            lista_fechas.append(fecha_publicacion)

            # Obtiene las entidades que emiten de las publicaciones del BOIB y los guarda en una lista
            entidades_bs4 = BeautifulSoup(anuncio.find('h3', {'class': 'organisme'}).text, 'lxml')
            entidades_text = entidades_bs4.get_text().strip('\n')
            lista_entidades.append(entidades_text)

            # Obtiene la descripción parseada de las resoluciones publicadas en el BOIB y los guarda en una lista
            resoluciones_bs4 = BeautifulSoup(anuncio.find('ul', {'class': 'resolucions'}).text, 'lxml')
            resoluciones_text = resoluciones_bs4.get_text().replace('\r', ' ').replace('\n', '').replace('\t',
                                                                                                         '').split(
                'Número')
            lista_resoluciones.append(resoluciones_text[0])

            # Obtiene los links de las publicaciones del BOIB en formato pdf y los guarda en una lista
            links_pdf_bs4 = anuncio.findAll('a', href=True)
            for link in links_pdf_bs4:
                if link['href'].find('pdf') != -1:  # si no encuentra la palabra pdf en el link, devuelve -1
                    link_completo = "https://www.caib.es" + link['href']
                    lista_links_pdf.append(link_completo)
                else:
                    continue

            # Obtiene el numero de registro de las publicaciones del BOIB y los guarda en una lista
            registros_bs4 = BeautifulSoup(anuncio.find('p', {'class': 'registre'}).text, 'lxml')
            registros_text = registros_bs4.get_text()[19:24]
            lista_registros.append(registros_text)

        # Creamos un objeto DataFrame de la librería 'pandas' para unificar las listas que contienen los datos escrapeados.
        fusion_listas = {'Boletín': lista_boletin, 'Fecha': lista_fechas, 'Entidad': lista_entidades,
                         'Resolución': lista_resoluciones, 'Enlace': lista_links_pdf, 'Nº Registro': lista_registros}
        datos_scrapeados = pd.DataFrame(data=fusion_listas)
        pd.set_option('display.max_columns', None)  # Muestra la información del dataframe sin truncar
        datos_scrapeados.to_csv('DataBase.csv')
        print(datos_scrapeados)

        # Comprobamos que obtenemos los datos solicitados
        print("---------------------------------------------------")
        print("-------------------BOIB hackeado con éxito-------------------")
        print("--------------Información extraida y almacenada--------------")

    else:
        print("---------------El BOIB no carga--------------")


