#!/usr/bin/python
from __future__ import print_function
import sys
import argparse
sys.path.append('silos')  # NOQA

import json
import argparse

from elastic_tagger import ElasticTagger
import elastic_tagger


def main():

    argparser = argparse.ArgumentParser()

    elastic_tagger.populate_args(argparser)
    args = argparser.parse_args()

    _eprint("elastic_search: %r" % args.elastic_search)
    _eprint("genes: %r" % args.genes)
    _eprint("tag_property: %r" % args.tag_property)
    _eprint("tag_name: %r" % args.tag_name)

    tagger = ElasticTagger(args)
    _eprint("tagger: %r" % str(tagger))
    tagger.tag_all()


def _eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


if __name__ == '__main__':
    main()
