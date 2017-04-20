#!/usr/bin/python

import sys
import argparse
sys.path.append('silos')  # NOQA

from elastic_silo import ElasticSilo
import elastic_silo

""" elastic should be up and running """


def test_args():
    argparser = argparse.ArgumentParser()
    elastic_silo.populate_args(argparser)
    args = argparser.parse_args(['--elastic_search', 'foo',
                                 '--elastic_index', 'bar'])
    assert args.elastic_search == 'foo'
    assert args.elastic_index == 'bar'


def test_init():
    silo = _make_silo()
    assert 'localhost' in str(silo)
    assert 'bar' in str(silo)


def test_save():
    """ assert no errors """
    silo = _make_silo()
    silo.save({'source': 'testing'})


def test_delete_all():
    """ assert no errors """
    silo = _make_silo()
    silo.save({'source': 'testing'})
    silo.delete_all()


def test_delete_source():
    """ assert no errors """
    silo = _make_silo()
    silo.save({'source': 'testing'})
    silo.delete_source('testing')


def _make_silo():
    argparser = argparse.ArgumentParser()
    elastic_silo.populate_args(argparser)
    args = argparser.parse_args(['--elastic_search', 'localhost',
                                 '--elastic_index', 'bar'])
    silo = ElasticSilo(args)
    return silo
