#!/usr/bin/python3
# -*- coding: utf-8 -*-


# $ ./auth_webapp.py urlService loginCAS passwordCAS allowRedirect
# ex : ./auth_webapp.py https://ohris.ut-capitole.fr/fr/  https://ohris.ut-capitole.fr/fr/time/punch/add_virtual jbousqui maudePasse
# loginCAS, passwordCAS et redirect optionnels, demandés par prompt si non passés

import sys
import time
import getpass
from pprint import pp
from .cas_login import CasAuthenticator, ServiceAuthenticator

# Exécute l'action d'un service CASsifié
# service authenticator = un objet ServiceAuthenticator ayant réussi une authentification
# action_url = URL de l'action dans une des pages du site CASsifié ex : https://ohris.ut-capitole.fr/time/punch/add_virtual
def exec_auth_action(service_authenticator, action_url, headers):
    action = service_authenticator.execAction(action_url, headers)
    return action



# Retourne l'objet ServiceAuthenticator à la requête sur l'URL service, authentifiée par CAS avec les credentials passés
# Cette fonction réalise l'authentification CAS du service CASsifié
def auth_service(service, login, password):
    
    # authentif et récupération du ticket CAS
    ca = CasAuthenticator()
    tgc = ca.get_tgc(login, password)
    redirection_url = ca.get_redirection_url(service)
    
    # authentif service avec le ticket CAS
    sa = ServiceAuthenticator(service)
    sa.getAuthenticatedService(redirection_url)
    
    return sa



def main():

    l = len(sys.argv)
    if l < 3:
        print("Erreur nb parametres. Usage : auth_webapp.py urlService urlAction loginCAS passwordCAS")
        print("ou au minimum : auth_webapp.py urlService urlAction  [ loginCAS | passwordCAS ]")
        return -1

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

    sa = auth_service(service, login, password)
    time.sleep(0.2)
    headers_punch = {
        'X-Requested-With': 'XMLHttpRequest',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin'
        }
    exec_auth_action(sa, action_url, headers_punch)





if __name__ == '__main__':
    sys.exit(main())