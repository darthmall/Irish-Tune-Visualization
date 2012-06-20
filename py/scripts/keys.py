#!/usr/bin/env python

import sys
sys.path.append('..')

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tune_viz.settings')

from django.db.models import Count
from tune_viz.models import *
import numpy
import matplotlib.pyplot as plt


def main():
    total_measures = Measure.objects.count()
    data = [(m['chord'], float(m['frequency']) / total_measures) for m in Measure.objects.values('chord').annotate(frequency=Count('chord'))]
    labels = [m[0].split()[0] for m in data]
    probabilities = [m[1] for m in data]
    width = 6.0
    x = numpy.arange(len(labels))

    plt.pie(probabilities, labels=labels)
    plt.show()

if __name__ == '__main__':
    main()