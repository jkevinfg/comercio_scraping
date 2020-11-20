import requests
from bs4 import BeautifulSoup
import pandas as pd


def main(url):
    link_secciones = scrap_sections(url)
    link_notes = scrap_section(link_secciones)
    data = obtener_data(link_notes)
    save_data(data)


def scrap_sections(url):
    try:
        p12 = requests.get(url)
        if p12.status_code == 200:
            s = BeautifulSoup(p12.text, 'lxml')
            secciones = s.find('ul', attrs={
                'class': 'main-sections'
            }).find_all('li')
            link_secciones = [seccion.a.get('href') for seccion in secciones]
            return link_secciones
        else:
            print('No se pudo obtener la seccion', seccion)
    except:
        print('No se pudo obtener la seccion', seccion)


def scrap_section(link_secciones):
    allnotes = []
    for seccion in link_secciones:
        try:
            sec = requests.get(seccion)
            if sec.status_code == 200:
                s_section = BeautifulSoup(sec.text, 'html.parser')

                top_content = s_section.find('section', attrs={
                    'id': 'top-content'
                }).find('article').h2.a.get('href')

                list_content = s_section.find('section', attrs={
                    'id': 'list-content'
                }).find_all('article')

                links_list_content = [listc.find('div', attrs={'class': 'article-item__header'}).a.get('href') for listc in list_content]
                links_list_content.append(top_content)
                allnotes = allnotes + links_list_content
            else:
                print('No se pudo obtener la seccion', seccion)
        except:
            print('No se pudo obtener la seccion', seccion)

    return allnotes


def obtener_data(link_notes):
    data = []
    for i, nota in enumerate(link_notes):
        print(f'Scrapeando nota {i+1}/{len(link_notes)}')
        data.append(scrap_nota(nota))
    return data


def scrap_nota(url):
    try:
        nota = requests.get(url)
        if nota.status_code == 200:
            s_nota = BeautifulSoup(nota.text, 'html.parser')
            ret_dict = obtener_info(s_nota)
            ret_dict['url'] = url
            return ret_dict
        else:
            print('No se pudo obtener la nota', url)
    except Exception as e:
        print(f'Error {e}')

def obtener_info(s_nota):
    ret_dict = {}

    # Extraemos la fecha
    fecha = s_nota.find('span', attrs={'pubdate': 'pubdate'})
    if fecha:
        ret_dict['fecha'] = fecha.get('datetime')
    else:
        ret_dict['fecha'] = None

    # Extraemos el titulo
    titulo = s_nota.find('h1', attrs={'class': 'article-title'})
    if titulo:
        ret_dict['titulo'] = titulo.text
    else:
        ret_dict['titulo'] = None

    # Extraer la volanda
    volanta = s_nota.find('h2', attrs={'class': 'article-prefix'})
    if volanta:
        ret_dict['volanta'] = volanta.get_text()
    else:
        ret_dict['volanta'] = None

    # Extraer copete
    copete = s_nota.find('div', attrs={'class': 'article-summary'})
    if copete:
        ret_dict['copete'] = copete.get_text()
    else:
        ret_dict['copete'] = None

    # Extraer autor
    autor = s_nota.find('div', attrs={'class': 'article-author'})
    if autor:
        ret_dict['autor'] = autor.get_text()
    else:
        ret_dict['autor'] = None

    # Extraer imagen

    imagenes = s_nota.find('div', attrs={'class': 'article-main-media-image'}).find_all('img')
    if len(imagenes) == 0:
        print('no se encontraron imagenes')
    else:
        imagen = imagenes[len(imagenes) - 1]
        imagen_src = imagen.get('data-src')
        try:
            img_req = requests.get(imagen_src)
            if img_req.status_code == 200:
                ret_dict['imagen'] = imagen_src
            else:
                ret_dict['imagen'] = None
        except:
            print('No se pudo obtener la imagen')


    # Extraerel  cuerpo
    cuerpo = s_nota.find('div', attrs={'class': 'article-text'})
    if cuerpo:
        ret_dict['cuerpo'] = cuerpo.get_text()
    else:
        ret_dict['cuerpo'] = None

    return ret_dict


def save_data(data):
    df = pd.DataFrame(data)
    df.to_csv('Notas_pagina12.csv')

    return df


if __name__ == "__main__":
    url = 'https://www.pagina12.com.ar/'
    main(url)
