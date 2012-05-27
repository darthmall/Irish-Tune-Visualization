#!/usr/bin/env python

# Set up the environment for using Django's ORM
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tune_viz.settings")

from abc_parser import parse_string
from bs4 import BeautifulSoup
from httplib import HTTPConnection

def main():
    cnxn = HTTPConnection('www.thesession.org')
    cnxn.request('GET', '/tunes/display/2')
    response = cnxn.getresponse()

    if response.status is 200:
        soup = BeautifulSoup(response.read())
        abc = soup.find(id="abc").select('div.box > p')[0].get_text()
        print(abc)
        results = parse_string(abc)
        print('{} ({})'.format(results.title, results.ref_number))
        print(''.join(results.body))


if __name__ == '__main__':
    main()
