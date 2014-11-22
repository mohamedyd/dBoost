#! /usr/bin/env python3
import dboost
import sys
import utils
import features
import argparse
import cli
from utils.autoconv import autoconv
from utils.print import print_rows

dataset = []
row_length = None

parser = cli.get_sdtin_parser()
args, models, rules = cli.parsewith(parser)

for line in args.input:
    line = line.strip().split(args.fs)
    
    if row_length != None and len(line) != row_length:
        sys.stderr.write("Discarding {}\n".format(line))

    row_length = len(line)
    dataset.append(tuple(autoconv(field) for field in line))

for model in models:
    outliers = dboost.outliers_static(dataset, model, rules)

    if len(outliers) == 0:
        print("   All clean!")
    else:
        print_rows(outliers, model, features.descriptions(rules), args.verbosity)
