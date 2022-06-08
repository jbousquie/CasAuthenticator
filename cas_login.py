#!/usr/bin/python3

# pip3 install urllib3
# pip3 install lxml 
# pip3 install bs4

import sys
import urllib3
from bs4 import BeautifulSoup


CAS_URL = 'https://cas.ut-capitole.fr/cas/login'
ORIGIN = 'https://cas.ut-capitole.fr'
HOST = 'cas.ut-capitole.fr'
COOKIE_TGC = 'CASTGC='
GET_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br', 
    'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7', 
    'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.2 Safari/605.1.15',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive'
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
    'Referer': CAS_URL,
    }

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
    p = http.request_encode_body('POST', post_url, fields=fields, headers=post_headers, encode_multipart=False)
    tgc_cookie = p.getheader('Set-Cookie')
    tmp = tgc_cookie.split(COOKIE_TGC)[1]   # à droite de COOKIE_TGC
    tgc = tmp.split(';')[0]                 # à gauche de ";"
    return tgc

def main():
    ret = get_tgc(sys.argv[1], sys.argv[2])
    print(ret)

if __name__ == '__main__':
    sys.exit(main())