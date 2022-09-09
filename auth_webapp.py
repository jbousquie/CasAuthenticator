#!/usr/bin/python3
# -*- coding: utf-8 -*-


# $ ./auth_webapp.py urlService loginCAS passwordCAS allowRedirect
# ex : ./auth_webapp.py https://ohris.ut-capitole.fr/fr/  https://ohris.ut-capitole.fr/time/punch/add_virtual jbousqui maudePasse
# loginCAS, passwordCAS et redirect optionnels, demandés par prompt si non passés

import sys
import getpass
from pprint import pp
from cas_login import get_tgc, send_tgc, send_cookies

# Exécute l'action d'un service CASsifié
# service = URL du service CASsifié ex : https://ohris.ut-capitole.fr/fr/
# action_url = URL de l'action dans une des pages du site CASsifié ex : https://ohris.ut-capitole.fr/time/punch/add_virtual
# login / password : credentials CAS
# Cette fonction réalise une authentification CAS du service, puis exécute une action de ce service.
def auth_action(service, action_url, login, password):
    service_response = auth_service(service, login, password, False)
    action_response = exec_authenticated_action(action_url, service_response)
    return action_response


# Émet un GET sur l'action du service CASsifié souhaitée
# action_url : URL du GET de la page du service à invoquer
# service_response = la réponse du service, contenant ses cookies, à la réception du ticket CAS https://service?ticket=ticketCAS
# Cette fonction exécute une action du service CASsifié après authentification
def exec_authenticated_action(action_url, service_response):
    http_response = send_cookies(action_url, service_response)
    return http_response


# Retourne l'objet Response urllib3 à la requête sur l'URL service, authentifiée par CAS avec les credentials passés
# Le paramètre redirect (True/False) autorise le suivi d'éventuelles redirections (code 302). La redirection ne transporte pas les éventuels cookies.
# Cette fonction réalise l'authentification CAS du service CASsifié
def auth_service(service, login, password, redirect):
    tgc = get_tgc(login, password)
    response = send_tgc(service, tgc, redirect)
    return response



def main():
    redirect = False
    l = len(sys.argv)
    if l < 3:
        print("Erreur nb parametres. Usage : auth_webapp.py urlService urlAction loginCAS passwordCAS")
        print("ou au minimum : auth_webapp.py urlService urlAction  [ loginCAS | passwordCAS ]")
        return -1

    redirect_string = ''
    service = sys.argv[1]
    action_url = sys.argv[2]
    
    if l < 4:
        login = input('Entrer le login CAS : ')
    else:
        login = sys.argv[3]
    if l < 5:      
        password = getpass.getpass(prompt='Entrer le password CAS : ')
    else:
        password = sys.argv[4]

    response = auth_action(service, action_url, login, password)
    #print(response.data.decode('utf-8'))
    #pp(response.getheaders())
    print(response.status)
    print(response.geturl())



if __name__ == '__main__':
    sys.exit(main())