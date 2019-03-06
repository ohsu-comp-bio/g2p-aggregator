from __future__ import print_function
import json
import os
import logging


# module level funtions


def populate_args(argparser):
    """add arguments we expect """
    argparser.add_argument('--file_output_dir', '-o',
                           help='''Bulk, line delimited JSON ndjson''',
                           default='.')


class FileSilo:
    """ A silo is where we store stuff that has been harvested.
        Store features in a file"""

    def __init__(self, args):
        """ initialize, set endpoint & index name """
        self._file_output_dir = args.file_output_dir

    def __str__(self):
        return "FileSilo file_output:{}".format(
                self._file_output_dir)

    def delete_all(self):
        """delete index"""
        logging.info("file silo: delete_all not supported, skipping")
        # noop
        pass

    def delete_source(self, source):
        """ delete source from index """
        try:
            os.remove(
                os.path.join(
                    self._file_output_dir, '{}.json'.format(source)))
        except Exception as e:
            logging.info("file silo: delete failed {}".format(e))

    def save_bulk(self, feature_association_generator, mode=None):
        """ write to file """
        for feature_association in feature_association_generator:
            self.save(feature_association, mode)

    def save(self, feature_association, mode=None):
        """ write dict to file """
        source = feature_association['source']
        if mode is None:
            path = os.path.join(self._file_output_dir, '{}.json'.format(source))
        else:
            path = os.path.join(self._file_output_dir, '{}.{}.json'.format(source, mode))
        with open(path, 'w') as the_file:
            try:
                out_s = json.dumps(feature_association, separators=(',', ':'))
            except UnicodeDecodeError:
                out_s = json.dumps(feature_association, separators=(',', ':'), encoding='ISO-8859-1').encode('UTF-8')
            the_file.write(out_s)
            the_file.write('\n')
