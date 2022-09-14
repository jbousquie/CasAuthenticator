#!/usr/bin/python3
# -*- coding: utf-8 -*-

# signature : cas_login.py loginCAS passwordCAS
# procède à une authentification CAS et renvoie le ticket CAS TGC

# pip3 install urllib3
# pip3 install requests
# pip3 install lxml 
# pip3 install bs4

import time
import sys
import requests
from bs4 import BeautifulSoup
from pprint import pp


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
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.2 Safari/605.1.15',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Host': HOST
}

post_headers = {
    'Accept': 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br', 
    'Accept-Language': 'fr-FR,fr;q=0.8,en-US;q=0.5,en;q=0.3', 
    'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64; rv:104.0) Gecko/20100101 Firefox/104.0',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Host': HOST,
    'Origin': ORIGIN,
    'Referer': REFERER,
    }

proxy = { 
    'http': 'http://cache.iut-rodez.fr:8080', 
    'https': 'http://cache.iut-rodez.fr:8080' 
    }


# CAS Authenticator
class CasAuthenticator:

    # constructeur
    def __init__(self):
        self.cas_session = requests.Session()
        self.tgc = ''

    # Retourne le ticket CAS après authentification selon les credentials passés
    def get_tgc(self, login, password):

        # récupération du cookie contenant JSESSIONID
        cas_session = self.cas_session
        g = cas_session.get(CAS_URL, headers=GET_HEADERS, proxies=proxy)
        
        # récupération du formulaire fm1
        html_response = g.text
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
        p = cas_session.post(post_url, data=fields, headers=post_headers, allow_redirects=False, proxies=proxy)
        tgc_cookie = p.cookies['CASTGC']
        self.tgc = str(tgc_cookie)
        return tgc_cookie


    # renvoie l'URL de redirection avec le service ticket
    def get_redirection_url(self, service):

        # envoi de https://cas.ut-capitole.fr/cas/login?service=paramService  + TGC en cookie
        auth_url = CAS_URL + '?service=' + service  
        post_headers.pop('Content-Type', None)
        cas_session = self.cas_session
        g_cas = cas_session.get(auth_url, headers=post_headers, allow_redirects=False, proxies=proxy)
        redirection_url = g_cas.headers.get('location')
        return redirection_url


class ServiceAuthenticator:

    # constructeur
    def __init__(self, service):
        self.service = service
        self.service_session = requests.Session()
        self.authenticated_response = ''


    # Retourne l'objet Response après toutes les redirections à la requête https://service/?ticket=serviceTicket
    def getAuthenticatedService(self, redirection_url):
        self.redirection_url = redirection_url
        service = self.service

        u = requests.utils.urlparse(service)
        post_headers['Host'] = u.netloc
        post_headers['Referer'] = REFERER
        post_headers.pop('Origin', None)
        post_headers.pop('Cookie', None)
        post_headers.pop('Content-Type', None)
        post_headers.pop('Cache-Control')

        service_session = self.service_session
        g_service = service_session.get(redirection_url, headers=post_headers, allow_redirects=True, proxies=proxy)
        self.authenticated_response = g_service
        return g_service



def main():
    login = sys.argv[1]
    password = sys.argv[2]
    ca = CasAuthenticator()
    ret = ca.get_tgc(login, password)
    print(ret)

if __name__ == '__main__':
    sys.exit(main())