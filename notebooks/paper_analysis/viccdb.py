from definitions import *
import json
from collections import defaultdict
import pickle
import pyupset as pyu
import pandas as pd
import matplotlib as mpl


class ViccAssociation(dict):

    def __hash__(self):
        source = self['source']
        if source == 'civic':
            assert len(self['association']['evidence']) == 1  # we currently import 1 evidence per association.
            k = 'civic:{}'.format(self['association']['evidence'][0]['evidenceType']['id'])
        elif source == 'molecularmatch':
            k = 'mm:{}'.format(self['raw']['hashKey'])
        elif source == 'brca':
            k = 'brca:{}'.format(self['raw']['id'])
        elif source == 'pmkb':
            t = [self['raw']['variant']['id'], self['raw']['tumor']['id']] + [x['id'] for x in self['raw']['tissues']]
            k = 'pmkb:{}'.format('-'.join([str(x) for x in t]))  # There's no interpretation ID, made compound ID from components
        elif source == 'oncokb':
            pre = self['raw']['clinical']
            t = [pre['cancerType'], pre['drug'], pre['gene'], pre['variant']['name'], pre['level']]
            k = 'oncokb:{}'.format('-'.join(t))
        elif source == 'jax':
            k = 'jax:{}'.format(self['raw']['id'])
        elif source == 'cgi':
            t = [self['raw']['Drug full name'], self['raw']['Primary Tumor type'],
                 self['raw']['Alteration'], self['raw']['Source']] + self['raw']['individual_mutation']
            k = 'cgi:{}'.format('-'.join(t))
        else:
            raise NotImplementedError("No hash routine defined for source '{}'".format(source))
        return hash(k)

    def __eq__(self, other):
        return hash(self) == hash(other)


class ViccDb:

    DEFAULT_CACHE = PROJECT_ROOT / 'association_cache.pkl'

    def __init__(self, associations=None, load_cache=False, cache_path=DEFAULT_CACHE):
        if load_cache:
            with open(str(cache_path), 'rb') as f:
                self.associations = pickle.load(f)
            self._index_associations()
        elif associations is not None:
            self.associations = associations
            self._index_associations()
        else:
            self.load_data()

    def load_data(self, data_dir=(DATA_ROOT / '0.10')):
        resource_paths = list(data_dir.glob('*.json'))
        if resource_paths:
            self._load_local(resource_paths)
        else:
            self._load_s3()

    def _load_local(self, resource_paths):
        self.associations_by_source = dict()
        self.associations = list()
        for path in resource_paths:
            source = path.parts[-1].split('.')[0]
            with path.open() as json_data:
                associations = list()
                for line in json_data:
                    association = ViccAssociation(json.loads(line))
                    association['raw'] = association.pop(source)
                    associations.append(association)
                    self.associations.append(association)

                self.associations_by_source[source] = associations
        print('Loaded {} associations'.format(len(self.associations)))

    def _load_s3(self, cache):
        raise NotImplementedError

    def _index_associations(self):
        associations_by_source = defaultdict(list)
        for association in self.associations:
            source = association['source']
            associations_by_source[source].append(association)
        self.associations_by_source = dict(associations_by_source)

    def select(self, filter_function):
        associations = filter(filter_function, self.associations)
        return ViccDb(list(associations))

    def report_groups(self, superset=None):
        if superset is None:
            total = len(self)
            for group in sorted(self.associations_by_source):
                count = len(self.associations_by_source[group])
                print("{}: {} ({:.1f}% of total)".format(group, count, count / total * 100))
            print("{} total associations".format(total))
        else:
            for group in sorted(self.associations_by_source):
                count = len(self.associations_by_source[group])
                # intended: below will raise error if key doesn't exit in superset, should be actual superset of self.
                superset_count = len(superset.associations_by_source[group])
                print("{}: {} ({:.1f}% of superset)".format(group, count, count / superset_count * 100))
            print("Total: {} ({:.1f}% of superset)".format(len(self.associations),
                                                           len(self.associations) / len(superset.associations) * 100))

    def cache_data(self, cache_path=DEFAULT_CACHE):
        with open(str(cache_path), 'wb') as f:
            pickle.dump(self.associations, f)

    def __len__(self):
        return len(self.associations)

    def __iter__(self):
        return iter(self.associations)

    def plot_overlap(self, map_function, by='source'):
        if by == 'source':
            input_dict = self.associations_by_source
        else:
            raise NotImplementedError
        d = {group: pd.DataFrame(set().update(map(map_function, input_dict[group]))) for group in input_dict}
        pyu.plot(d, inters_size_bounds=(3, 10000000))