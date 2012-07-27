#!/usr/bin/env python

import sys
sys.path.append("..")

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tune_viz.settings")

from tune_viz.models import *
import re

KEY_PATTERN = r'^[A-G][#b]?(?:m|Mix|Dor|Phr|Lyd|Loc)?$'

def main():
    normal = []
    abnormal = []

    for key in Tune.objects.all().distinct('key').values_list('key', flat=True):
        m = re.match(KEY_PATTERN, key)

        if m:
            normal.append(key)
        else:
            abnormal.append(key)

    print("Normalized keys")
    for key in normal:
        print(key)

    replace = {}
    print("\nAbnormal keys")
    for key in abnormal:
        replace[key] = raw_input(u"Replace {} with: ".format(key))

    for k,v in replace.iteritems():
        for t in Tune.objects.filter(key=k):
            print(u"{} {} => {}".format(t.title, k, v))
            t.key = v
            t.save()

if __name__ == '__main__':
    main()