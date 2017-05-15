from __future__ import print_function
import sys
import json
from kafka import KafkaProducer

# module level funtions


def _eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def populate_args(argparser):
    """add arguments we expect """
    argparser.add_argument('--kafka_topic', '-kt',
                           help='''kafka_topic''',
                           default='smmart.g2p')

    argparser.add_argument('--kafka_bootstrap', '-kb',
                           help='''kafka host:port''',
                           default='localhost:9092')


class KafkaSilo:
    """ A silo is where we store stuff that has been harvested.
        Store features in kafka"""

    def __init__(self, args):
        """ initialize, set endpoint & index name """
        self._kafka_bootstrap = args.kafka_bootstrap
        self._producer = KafkaProducer(bootstrap_servers=self._kafka_bootstrap)
        self._kafka_topic = args.kafka_topic

    def __str__(self):
        return "KafkaSilo bootstrap_servers:{} topic:{}".format(
                self._kafka_bootstrap, self._kafka_topic)

    def delete_all(self):
        """delete index"""
        # noop
        pass

    def delete_source(self, source):
        """ delete source from index """
        # noop
        pass

    def save(self, feature_association):
        """ write dict to kafka """
        self._producer.send(self._kafka_topic, json.dumps(feature_association))
        self._producer.flush()
        # _eprint(self._kafka_topic, len(json.dumps(feature_association)))
