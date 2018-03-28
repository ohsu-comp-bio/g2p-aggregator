from definitions import *
import json
from collections import defaultdict
import pickle
import re
import pyupset as pyu
import pandas as pd


class Element:

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return str(other) == str(self)

    def __lt__(self, other):
        return str(self) < str(other)

    def __gt__(self, other):
        return str(self) > str(other)


class Gene(Element):

    def __init__(self, gene_name):
        self.gene_symbol = str(gene_name)  # Assumes gene_name is gene_symbol

    def __str__(self):
        return self.gene_symbol


class Publication(Element):

    pmid_re = re.compile(r'https?://.*pubmed/(\d+)$')

    def __init__(self, publication_string):
        pmid_match = Publication.pmid_re.match(publication_string)
        self.pmid = None
        self.publication_string = publication_string
        if pmid_match:
            self.pmid = int(pmid_match[1])

    def __str__(self):
        if self.pmid:
            return str(self.pmid)
        else:
            return self.publication_string


class RawAssociation(dict):

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
            try:
                pre = self['raw']['clinical']
                t = [pre['cancerType'], pre['drug'], pre['gene'], pre['variant']['name'], pre['level']]
                k = 'oncokb_clinical:{}'.format('-'.join(t))
            except KeyError:
                pre = self['raw']['biological']
                t = [pre['gene'], pre['variant']['name'], pre['oncogenic'], pre['mutationEffectPmids']]
                k = 'oncokb_biological:{}'.format('-'.join(t))
        elif source == 'jax':
            k = 'jax:{}'.format(self['raw']['id'])
        elif source == 'cgi':
            t = [self['raw']['Drug full name'], self['raw']['Primary Tumor type'],
                 self['raw']['Alteration'], self['raw']['Source']] + self['raw']['individual_mutation']
            k = 'cgi:{}'.format('-'.join(t))
        else:
            raise NotImplementedError("No hash routine defined for source '{}'".format(source))
        return hash(k)

    @property
    def publications(self):
        evidence = self['association']['evidence']
        all_pubs = list()
        for e in evidence:
            all_pubs += [Publication(p) for p in e['info']['publications'] if p]
        return all_pubs

    @property
    def genes(self):
        return [ Gene(g) for g in self['genes'] ]


    @property
    def source(self):
        return self['source']

    def __eq__(self, other):
        return hash(self) == hash(other)


class ViccAssociation(RawAssociation):

    pass


class ViccDb:

    DEFAULT_CACHE = PROJECT_ROOT / 'association_cache.pkl'

    def __init__(self, associations=None, load_cache=False, save_cache=False, cache_path=DEFAULT_CACHE):
        if load_cache and save_cache:
            raise ValueError('Can only load or save cache, not both.')
        if load_cache:
            with open(str(cache_path), 'rb') as f:
                self.associations = pickle.load(f)
        elif associations is not None:
            self.associations = associations
        else:
            self.load_data()
        self._index_associations()
        if save_cache:
            self.cache_data(cache_path)

    def load_data(self, data_dir=(DATA_ROOT / '0.10')):
        resource_paths = list(data_dir.glob('*.json'))
        if resource_paths:
            self._load_local(resource_paths)
        else:
            self._load_s3()

    def _load_local(self, resource_paths):
        self.associations = list()
        for path in resource_paths:
            source = path.parts[-1].split('.')[0]
            with path.open() as json_data:
                for line in json_data:
                    association = RawAssociation(json.loads(line))
                    association['raw'] = association.pop(source)
                    self.associations.append(association)


    def _load_s3(self):
        raise NotImplementedError

    def _index_associations(self):
        associations_by_source = defaultdict(list)
        hashed = defaultdict(list)
        for association in self.associations:
            source = association['source']
            associations_by_source[source].append(association)
            hashed[hash(association)].append(association)
        self.associations_by_source = dict(associations_by_source)
        self._hashed = hashed

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

    def __contains__(self, item):
        return hash(item) in self._hashed

    def __getitem__(self, item):
        return self.associations[item]

    def __sub__(self, other):
        for h, associations in other._hashed.items():
            assert len(associations) == 1
            assert len(self._hashed.get(h, [])) <= 1
            # these assertions assume that hash uniquely identifies an association.
            # Currently not true, but should be with harvester changes.
        return ViccDb([x for x in self if x not in other])

    def plot_element_by_source(self, element, filter_func=lambda x: True, min_bound=3, max_bound=1000000000):
        element_by_source = defaultdict(set)
        for association in self:
            element_by_source[association.source].update(getattr(association, element))

        df_dict = dict()
        column_name = ['attribute']
        for source in element_by_source:
            pubs = list(filter(filter_func, element_by_source[source]))
            df_dict[source] = pd.DataFrame(pubs, columns=column_name)
        x = pyu.plot(df_dict, unique_keys=column_name, inters_size_bounds=(min_bound, max_bound))
        x['input_data'] = element_by_source
        return x
