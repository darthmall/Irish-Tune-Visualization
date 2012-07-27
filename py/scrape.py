#!/usr/bin/env python

# Set up the environment for using Django's ORM
import sys
sys.path.append("..")

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tune_viz.settings")

from bs4 import BeautifulSoup
from django.db.models import Max
from httplib import HTTPConnection
from pyparsing import ParseException
from music21 import *
from tune_viz.models import *

ABC_METADATA = {
    "C": "composer",
    "M": "meter",
    "L": "unit_note_length",
    "R": "rhythm",
    "K": "key",
    "Q": "tempo",
    "O": "origin"
}

def print_abc(abc):
    for i, line in enumerate(abc.splitlines()):
        print(u"{:>2}: {}".format(i, line))

def main(tune_ids=None, batchsize=10):
    cnxn = HTTPConnection('www.thesession.org')

    if not tune_ids or len(tune_ids) < 1:
        last_id = (Tune.objects.all().aggregate(Max('reference'))['reference__max'] or 0) + 1
        tune_ids = range(last_id, last_id + batchsize)

    for i in tune_ids:
        cnxn.request('GET', '/tunes/display/{}'.format(i))
        response = cnxn.getresponse()

        if response.status is 200:
            soup = BeautifulSoup(response.read())
            abcStr = soup.find(id="abc").select('div.box > p')[0].get_text()
            abcStr = '\n'.join(filter(len, map(unicode.strip, abcStr.splitlines())))

            try:
                ah = abc.ABCHandler()
                ah.process(abcStr)

                tune = Tune(reference=i, title=ah.getTitle(), raw_abc=abcStr)

                for metadata in filter(lambda tok: (type(tok) == abc.base.ABCMetadata), ah.tokens):
                    if metadata.tag in ABC_METADATA:
                        setattr(tune, ABC_METADATA[metadata.tag], metadata.data)

                tune.save()

                try:
                    print('Saved: {} ({})'.format(tune.title, tune.reference))
                except UnicodeEncodeError:
                    print("Saved: ({})".format(tune.reference))
            except abc.base.ABCHandlerException as e:
                print("Failed to parse ABC data for id {}:".format(i))
                try:
                    print_abc(abcStr)
                except UnicodeEncodeError:
                    print("Unable to print ABC String due to unicode characters")

                print(e)

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser("Scrape tune data from thesession.org")
    parser.add_argument("-s", "--batchsize", default=10, type=int, dest="batchsize")
    parser.add_argument("tune_ids", metavar="ID", type=int, nargs="*")
    args = parser.parse_args()

    main(args.tune_ids, args.batchsize)
