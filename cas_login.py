#!/usr/bin/python3
# -*- coding: utf-8 -*-

# signature : cas_login.py loginCAS passwordCAS
# procède à une authentification CAS et renvoie le ticket CAS TGC

# pip3 install urllib3
# pip3 install lxml 
# pip3 install bs4

from base64 import encode
import sys
import urllib3
from bs4 import BeautifulSoup

import config


CAS_URL = config.CAS_URL
REFERER = config.REFERER
ORIGIN = config.ORIGIN


HOST = config.HOST
COOKIE_TGC = config.COOKIE_TGC



GET_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br', 
    'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7', 
    'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.2 Safari/605.1.15',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Host': HOST
}

post_headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br', 
    'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7', 
    'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.2 Safari/605.1.15',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Host': HOST,
    'Origin': ORIGIN,
    'Referer': REFERER,
    }

# Retourne le ticket CAS après authentification selon les credentials passés
def get_tgc(login, password):
    http = urllib3.PoolManager()
    
    g = http.request('GET', CAS_URL, headers=GET_HEADERS)
    # récupération du cookie contenant JSESSIONID
    cookie = g.getheader('Set-Cookie')
    jsessionid = cookie.split(';')[0]    # en espérant que ce soit toujours le premier
    post_headers['Cookie'] = jsessionid


    # récupération du formulaire fm1
    html_response = g.data.decode('utf-8')
    data_soup = BeautifulSoup(html_response, 'lxml')
    form_tag = data_soup.find(id='fm1')
    form_action = form_tag.get('action')

    # récupération de tous les balises input hidden du formulaire et ajout des crédentials
    fields = {'username': login, 'password': password, 'submit': 'SE CONNECTER'}
    input_tags = form_tag.find_all('input', attrs={'type':'hidden'})
    for input_tag in input_tags:
        name = input_tag.get('name')
        value = input_tag.get('value')
        fields[name] = value


    # requête POST d'envoi des credentials
    post_url = ORIGIN + form_action
    p = http.request_encode_body('POST', post_url, fields=fields, headers=post_headers, encode_multipart=False, redirect=False)
    tgc_cookie = p.getheader('Set-Cookie')
    tmp = tgc_cookie.split(COOKIE_TGC)[1]   # à droite de COOKIE_TGC
    tgc = tmp.split(';')[0]                 # à gauche de ";"
    return tgc

# envoie le ticket TGC au service CASsifié demandé
def send_tgc(service, tgc, redirect):

    # Étape 1 : https://cas.ut-capitole.fr/cas/login?service=paramService  + TGC en cookie
    # récupération de la redirection et du ticket ST
    auth_url = CAS_URL + '?service=' + service
    http = urllib3.PoolManager()
    cookie_string = post_headers['Cookie'] + ';CASTGC=' + tgc
    post_headers['Cookie'] = cookie_string
    post_headers.pop('Content-Type', None)
    g_cas = http.request_encode_url('GET', auth_url, headers=post_headers, redirect=False)
    redirection_url = g_cas.getheader('Location')

    # Étape 2 : https://service/?ticket=serviceTicket  avec les headers corrects
    u = urllib3.util.parse_url(service)
    post_headers['Host'] = u.host
    post_headers['Referer'] = ORIGIN
    post_headers.pop('Origin', None)
    post_headers.pop('Cookie', None)
    g_service = http.request('GET', redirection_url, post_headers, redirect=redirect)

    return g_service

def main():
    login = sys.argv[1]
    password = sys.argv[2]
    ret = get_tgc(login, password)
    print(ret)

if __name__ == '__main__':
    sys.exit(main())