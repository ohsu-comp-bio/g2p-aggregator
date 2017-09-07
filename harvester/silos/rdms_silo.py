'''
A silo in a relational database management system (RDMS) such as SQLite or PostGreSQL.
Currently only SQLite is enabled.
'''

from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

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
    deleted = Column(Boolean)
    deleted_at = Column(DateTime)
    description = Column(String)
    ensembl_version = Column(String)
    gene_id = Column(Integer, ForeignKey('Gene.id'))

    gene = relationship('Gene', back_populates='variants')

# module level funtions

def populate_args(argparser):
    """add arguments we expect """
    argparser.add_argument('--database', '-db', help='''SQLite database''')


class RDMSSilo(object):
    """ A silo is where we store stuff that has been harvested.
        Store features in a relational database management system using SQLAlchemy """

    def __init__(self, args):
        """ initialize, set endpoint & index name """
        self._database_file = args.database
        # echo=True will echo all SQL statements issued by SQLAlchemy.
        self._engine = create_engine('sqlite:///g2p.sqlite3', echo=False)

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

        # Create genes.
        for gene_name in feature_association['genes']:
            gene = get_or_create(session, Gene, name=gene_name)

        # Create variant.

        # Create drug.

        # Create association.

        session.commit()
