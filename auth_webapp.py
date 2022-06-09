#!/usr/bin/python3

import sys
from urllib.parse import urlencode
from cas_login import get_tgc

def auth_service(service, login, password):

    service_arg = {'service': service}
    encoded_service = '?' + urlencode(service_arg)
    #auth_url = CAS_URL + encoded_service



def main():
    service = sys.argv[1]
    login = sys.argv[2]
    password = sys.argv[3]
    tgc = get_tgc(login, password)
    print(tgc)

if __name__ == '__main__':
    sys.exit(main())