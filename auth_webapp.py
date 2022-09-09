#!/usr/bin/python3
# -*- coding: utf-8 -*-


# $ ./auth_webapp.py urlService loginCAS passwordCAS allowRedirect
# ex : ./auth_webapp.py https://econges.ut-capitole.fr/  jbousqui maudePasse True/False
# loginCAS, passwordCAS et redirect optionnels, demandés par prompt si non passés

import sys
import getpass
from pprint import pp
from cas_login import get_tgc, send_tgc


# Retourne l'objet Response urllib3 à la requête sur l'URL service, authentifiée par CAS avec les credentials passés
# Le paramètre redirect (True/False) autorise le suivi d'éventuelles redirections (code 302)
def auth_service(service, login, password, redirect):

    tgc = get_tgc(login, password)
    response = send_tgc(service, tgc, redirect)
    return response



def main():
    redirect = False
    l = len(sys.argv)
    if l < 2:
        print("Erreur nb parametres. Usage : auth_webapp.py urlService loginCAS passwordCAS redirect")
        print("ou au minimum : auth_webapp.py urlService  [ loginCAS | passwordCAS | redirect ]  (redirect=False par defaut)")
        return -1

    redirect_string = ''
    service = sys.argv[1]
    
    if l < 3:
        login = input('Entrer le login CAS : ')
    else:
        login = sys.argv[2]
    if l < 4:      
        password = getpass.getpass(prompt='Entrer le password CAS : ')
    else:
        password = sys.argv[3]
    if l < 5:
        redirect_string = input('Entrer le redirect True/False (defaul = False): ')
    else: 
        redirect_string = sys.argv[4]        

    if redirect_string == "True":
        redirect = True

    response = auth_service(service, login, password, redirect)
    #print(response.data.decode('utf-8'))
    pp(response.getheaders())
    print(response.status)
    print(response.geturl())



if __name__ == '__main__':
    sys.exit(main())