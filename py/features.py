#!/usr/bin/env python

from music21 import converter, features


def featureImplemented(feature):
    return (feature and feature in features.jSymbolic.featureExtractors)


def featuresByCategory(categories):
    feature_list = []
    fs = features.jSymbolic.extractorsById

    for category in categories:
        feature_list += filter(featureImplemented, fs[category])

    return feature_list


if __name__ == '__main__':
    import sys
    sys.path.append('..')

    import os
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tune_viz.settings')

    from itertools import chain, izip
    from progress_bar import ProgressBar
    from tune_viz.models import *
    import argparse, csv
    
    # Set up some argument parsing. Wee!
    parser = argparse.ArgumentParser(description='Extract features from tunes')
    parser.add_argument('-a', '--accidentals', dest='accidentals', type=int, default=2)
    parser.add_argument('-t', '--type', dest='type', type=str, default='jig')
    parser.add_argument('categories', metavar='CATEGORY', type=str, nargs='+')
    parser.add_argument('output', metavar='FILE', type=str)

    args = parser.parse_args()

    # Get the tunes from the database
    tunes = Tune.objects.filter(rhythm=args.type, key__number_of_accidentals=args.accidentals, key__accidentals='s')
    tune_count = tunes.count()

    # Get the features from music21
    feature_list = featuresByCategory(args.categories)
    feature_count = len(feature_list)

    # Set up a CSV writer
    fieldnames = ['id'] + list(chain(*[feature().getAttributeLabels() for feature in feature_list]))
    writer = csv.DictWriter(open(args.output, 'wb'), fieldnames=fieldnames)

    # A little progress checking
    progressbar = ProgressBar(tune_count * len(feature_list))

    # Store a count by feature name of all the errors, so that if one feature is particularly
    # troublesome, we can skip it when computing the singular value decomposition
    errors = 0

    print('Extracting {} features from {} tunes'.format(len(feature_list), tunes.count()))

    for  i, tune in enumerate(tunes.values('id', 'title', 'raw_abc')):
        try:
            score = converter.parseData(tune['raw_abc'], format='abc')
            
            row = {'id': tune['id']}

            for j, feature in enumerate(feature_list):
                try:
                    fe = feature(score)
                    f = fe.extract()

                    row.update(izip(fe.getAttributeLabels(), f.vector))
                except:
                    errors += 1
                    row = None
                    break

                progressbar.update_time((i * feature_count) + j + 1)
                print progressbar, '{: >3d} / {} features'.format(j + 1, feature_count), '{: >5,d} / {: <5,d} tunes'.format(i, tune_count), 'Errors: {:,d}'.format(errors), chr(27) + '[A'

            if row:
                writer.writerow(row)
            
        except:
            errors += 1

    print progressbar, '{: >3d} / {} features'.format(j + 1, feature_count), '{: >5,d} / {: <5,d} tunes'.format(i, tune_count), 'Errors: {:,d}'.format(errors)
    