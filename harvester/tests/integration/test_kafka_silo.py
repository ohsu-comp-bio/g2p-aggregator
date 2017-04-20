#!/usr/bin/python

import sys
import argparse
sys.path.append('silos')  # NOQA

from kafka_silo import KafkaSilo
import kafka_silo
from kafka import KafkaConsumer
import time
import json


""" elastic should be up and running """


def test_populate_args():
    """ test that module static method populate_args works """
    argparser = argparse.ArgumentParser()
    kafka_silo.populate_args(argparser)
    args = argparser.parse_args(['--kafka_topic', 'foo',
                                 '--kafka_bootstrap', 'bar'])
    assert args.kafka_topic == 'foo'
    assert args.kafka_bootstrap == 'bar'


def test_init():
    silo = _make_silo()
    assert 'localhost' in str(silo)
    assert 'bar' in str(silo)


def test_save():
    """ assert no errors and message round trip works"""
    silo = _make_silo()
    assert silo
    current_time = int(round(time.time() * 1000))

    silo.save({'source': 'testing', 'time': current_time})
    msg = _consume_messages()
    assert current_time == msg['time']


def _make_silo():
    argparser = argparse.ArgumentParser()
    kafka_silo.populate_args(argparser)
    args = argparser.parse_args(['--kafka_bootstrap', 'localhost:9092',
                                 '--kafka_topic', 'bar'])
    silo = KafkaSilo(args)
    return silo


def _consume_messages():
    # To consume latest messages and auto-commit offsets
    # random consumer id, to ensure we get all messages
    current_milli_time = int(round(time.time() * 1000))
    consumer = KafkaConsumer(group_id='my-group-{}'.format(current_milli_time),
                             auto_offset_reset='earliest',
                             bootstrap_servers=['localhost:9092'],
                             consumer_timeout_ms=50)
    consumer.subscribe(['bar'])
    for message in consumer:
        # # message value and key are raw bytes -- decode if necessary!
        # # e.g., for unicode: `message.value.decode('utf-8')`
        # # j = json.loads(message.value)
        # print ("consume_smmart %s:%d:%d: key=%s value=%s" %
        #        (message.topic, message.partition,
        #         message.offset, message.key, message.value))

        pass  # just no-op to get to last message
    return json.loads(message.value)
