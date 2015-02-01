#! /usr/bin/env python3
import sys
import utils
import features
from utils import tupleops
from utils.print import debug
from itertools import chain
from analyzers import statistical

def expand_field(f, rules):
    rls = rules[type(f)]
    return tuple(chain.from_iterable(rule(f) for rule in rls))

def expand(x, rules):
    return tuple(expand_field(f, rules) for f in x)

def expand_hints(X, hints):
    expanded_hints = tupleops.deepmap(lambda h: X[h[0]][h[1]], hints)
    return (expanded_hints,) + X

def expand_stream(generator, rules, keep_x, hints, maxrecords = float("+inf")):
    for id, x in enumerate(generator()):
        if id >= maxrecords:
            break
        X = expand(x, rules)
        if hints != None:
            X = expand_hints(X, hints)
        yield (x, X) if keep_x else X

def outliers(trainset_generator, testset_generator, analyzer, model, rules, maxrecords = float("+inf")):
    debug(">> Finding correlations")
    analyzer.fit(expand_stream(trainset_generator, rules, False, None, maxrecords))
    # debug(analyzer.hints)

    debug(">> Building model...")
    analyzer.expand_stats()
    model.fit(expand_stream(trainset_generator, rules, False, analyzer.hints, maxrecords), analyzer)

    debug(">> Finding outliers...")
    for index, (x, X) in enumerate(expand_stream(testset_generator, rules,
                                                 True, analyzer.hints, maxrecords)):
        discrepancies = model.find_discrepancies(X, index)
        if len(discrepancies) > 0:
            yield index, (x, X, discrepancies)
