
FROM python:2.7

RUN mkdir -p /server
WORKDIR /server

RUN apt-get update
RUN apt-get install -y autoconf automake libtool curl make g++ unzip vim


RUN pip install pip --upgrade  \
  && pip install ga4gh

RUN wget https://github.com/ga4gh/server/releases/download/data/ga4gh-example-data_4.6.tar \
  && tar -xvf ga4gh-example-data_4.6.tar \
  && cd ga4gh-example-data \
  && wget https://raw.githubusercontent.com/The-Sequence-Ontology/SO-Ontologies/master/so-xp-dec.obo

RUN cd /server \
  && ga4gh_repo add-ontology ga4gh-example-data/registry.db  ga4gh-example-data/so-xp-dec.obo -n so-xp


RUN mkdir -p /server/ga4gh-example-data/cgd \
 && cd /server/ga4gh-example-data/cgd \
 && wget https://raw.githubusercontent.com/ohsu-comp-bio/ohsu-server-util/master/cgd-08-09-2016.ttl
RUN cd /server \
 && ga4gh_repo add-featureset -R  GRCh37-subset -O so-xp  -C PhenotypeAssociationFeatureSet ga4gh-example-data/registry.db  1kg-p3-subset  ga4gh-example-data/cgd   \
 && ga4gh_repo add-phenotypeassociationset ga4gh-example-data/registry.db  1kg-p3-subset  ga4gh-example-data/cgd   -n cgd


WORKDIR /server
CMD ga4gh_server -H 0.0.0.0
