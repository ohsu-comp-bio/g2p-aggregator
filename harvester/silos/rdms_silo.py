'''
A silo in a relational database management system (RDMS) such as SQLite or PostGreSQL.
Currently only SQLite is enabled.
'''

from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

######### Module level funtions

def populate_args(argparser):
    """add arguments we expect """
    argparser.add_argument('--database', '-db', help='''SQLite database''', default='g2p.sqlite3')

def evidence_direction_to_int(direction):
    res_type = {
        'resistant': -1,
        'sensitive': 1,
        'no benefit': 0
    }
    return res_type.get(direction, -2)

# Taken from https://stackoverflow.com/questions/2546207/does-sqlalchemy-have-an-equivalent-of-djangos-get-or-create
def get_or_create(session, model, **kwargs):
    '''
    Get or create models based on kwargs.
    '''
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance

######### Declarative definitions for objects and corresponding tables.

Base = declarative_base()

class Source(Base):
    '''
    Source of association.
    '''
    __tablename__ = 'Source'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    source_evidence_associations = relationship('SourceVariantEvidenceItem')

class Gene(Base):
    '''
    A gene found in the genome.
    '''
    __tablename__ = 'Gene'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    deleted = Column(Boolean)
    deleted_at = Column(DateTime)
    official_name = Column(String)
    entrez_id = Column(Integer)
    description = Column(String)
    clinical_description = Column(String)

    variants = relationship('Variant', back_populates='gene')

    def __repr__(self):
        return "<Gene(name='%s', official_name='%s', entrez_id='%s')>" % (
            self.name, self.official_name, self.entrez_id)

class Variant(Base):
    '''
    A genomic variant.
    '''
    __tablename__ = 'Variant'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    chromosome = Column(String)
    chromosome2 = Column(String)
    start = Column(Integer)
    stop = Column(Integer)
    ref = Column(String)
    alt = Column(String)
    deleted = Column(Boolean)
    deleted_at = Column(DateTime)
    description = Column(String)
    ensembl_version = Column(String)
    gene_id = Column(Integer, ForeignKey('Gene.id'))

    gene = relationship('Gene', back_populates='variants')
    evidence_associations = relationship('VariantEvidenceItemAssociation')

    def __repr__(self):
        return "<Variant(chromosome='%s', start='%s', ref='%s', alt='%s', gene='%s')>" % (
            self.chromosome, self.start, self.ref, self.alt, self.gene)

class Drug(Base):
    '''
    A drug.
    '''
    __tablename__ = 'Drug'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    evidence_items = relationship('EvidenceItem', back_populates='drug')

    def __repr__(self):
        return "<Drug(name='%s')>" % (self.name)

class Article(Base):
    '''
    PubMed Articles
    '''
    __tablename__ = 'Article'

    id = Column(Integer, primary_key=True)
    pubmed_id = Column(Integer)
    link = Column(String)

    article_variant_evidence_items = relationship('ArticleVariantEvidenceItem', back_populates='article')

    def __rep__(self):
        return "<PubMed(name='%s')>" % (self.pubmed_id)

class Disease(Base):
    '''
    A disease.
    '''
    __tablename__ = 'Disease'

    id = Column(Integer, primary_key=True)
    doid = Column(String)
    name = Column(String)
    family = Column(String)

    evidence_items = relationship('EvidenceItem', back_populates='disease')

    def __repr__(self):
        return "<Disease(name='%s', doid='%s', family='%s')>" % (
            self.name, self.doid, self.family)

class EvidenceItem(Base):
    '''
    Evidence items.
    '''
    __tablename__ = 'EvidenceItem'

    id = Column(Integer, primary_key=True)
    evidence_level = Column(Integer)
    evidence_direction = Column(Integer)
    drug_id = Column(Integer, ForeignKey('Drug.id'))
    disease_id = Column(Integer, ForeignKey('Disease.id'))

    drug = relationship('Drug', back_populates='evidence_items')
    disease = relationship('Disease', back_populates='evidence_items')

    def __repr__(self):
        return "<EvidenceItem(evidence_level='%i', evidence_direction='%i', drug='%s', disease='%s')>" % (
            self.evidence_level, self.evidence_direction, self.drug, self.disease)

class VariantEvidenceItemAssociation(Base):
    '''
    Association between variants and evidence items.
    '''
    __tablename__ = 'VariantEvidenceItemAssociation'

    id = Column(Integer, primary_key=True)
    variant_id = Column(Integer, ForeignKey('Variant.id'))
    evidence_item_id = Column(Integer, ForeignKey('EvidenceItem.id'))

    evidence_item = relationship('EvidenceItem')
    variant = relationship('Variant')

class SourceVariantEvidenceItem(Base):
    '''
    Association between variants, evidence items, and sources of evidence
    '''
    __tablename__ = 'SourceVariantEvidenceItem'

    source_id = Column(Integer, ForeignKey('Source.id'), primary_key=True)
    variant_ei_id = Column(Integer, ForeignKey('VariantEvidenceItemAssociation.id'), primary_key=True)

    source = relationship('Source')
    evidence_associations = relationship('VariantEvidenceItemAssociation')

class ArticleVariantEvidenceItem(Base):
    '''
    Association between Articles and Variant-EvidenceItem Associations
    '''
    __tablename__ = 'ArticleVariantEvidenceItem'

    article_id = Column(Integer, ForeignKey('Article.id'), primary_key=True)
    variant_ei_id = Column(Integer, ForeignKey('VariantEvidenceItemAssociation.id'), primary_key=True)

    article = relationship('Article')
    evidence_associations = relationship('VariantEvidenceItemAssociation')

class RDMSSilo(object):
    """ A silo is where we store stuff that has been harvested.
        Store features in a relational database management system using SQLAlchemy """

    def __init__(self, args):
        """ initialize, set endpoint & index name """
        self._database_file = args.database
        # echo=True will echo all SQL statements issued by SQLAlchemy.
        self._engine = create_engine('sqlite:///%s' % self._database_file, echo=False)

        # Create all tables associated with classes.
        Base.metadata.create_all(self._engine)

    def __str__(self):
        return "RDMSSilo _database_file:{}".format(self._database_file)

    def delete_all(self):
        """ Delete all tables. """
        Base.metadata.delete_all(self._engine)

    def delete_source(self, source):
        """ Delete source from index. """
        pass

    def _stringify_sources(self, feature_association):
        pass

    def save(self, feature_association):
        """ Write to database """

        # Create session.
        Session = sessionmaker(bind=self._engine)
        Session.configure(bind=self._engine)
        session = Session()

        # Add source.
        source = get_or_create(session, Source, name=feature_association['source'])

        # Add genes.
        for gene_name in feature_association['genes']:
            gene = get_or_create(session, Gene, name=gene_name)

        # Add variants.
        variants = [ \
                    get_or_create(session, Variant,
                                  chromosome=feature.get('chromosome', ''),
                                  start=feature.get('start', -1),
                                  ref=feature.get('ref', ''),
                                  alt=feature.get('alt', ''),
                                  gene_id=gene.id) \
                    for feature in feature_association['features']
                   ]

        # Add drugs.
        association = feature_association['association']
        drugs = []
        if 'drug_labels' in association:
            drugs = association['drug_labels'].split(',')
            drugs = [get_or_create(session, Drug, name=drug_name.decode('utf-8')) for drug_name in drugs]

        # Add disease.
        phenotype = association['phenotype']
        disease = get_or_create(session, Disease,
                                doid=phenotype.get('id', ''),
                                name=phenotype.get('description', ''),
                                family=phenotype.get('family', ''))

        # Add articles.
        if len(association['evidence']) > 1:
            print 'ERROR: more than one "evidence"'
        article = association['evidence'][0]['info']['publications']
        articles = [get_or_create(session, Article, 
                                  link=article_link, 
                                  pubmed_id=article_link.lstrip('http://www.ncbi.nlm.nih.gov/pubmed/')) \
                    for article_link in article]

        # Add evidence items and associations b/t variants and evidence items.
        for drug in drugs:
            evidence = association['evidence']
            evidence = get_or_create(session, EvidenceItem,
                                    evidence_level=association['evidence_level'],
                                    evidence_direction=evidence_direction_to_int(association['response_type']),
                                    drug_id=drug.id,
                                    disease_id=disease.id)

            # Create associations between variants and evidence items.
            for variant in variants:
                get_or_create(session, VariantEvidenceItemAssociation,
                              variant_id=variant.id,
                              evidence_item_id=evidence.id)

        # Add source_variant_evidence_item associations
        # Add article_variant_eviden_item associations
