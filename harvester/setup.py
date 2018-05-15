from setuptools import setup
from pip.req import parse_requirements

# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_reqs = parse_requirements('./requirements.txt')

# reqs is a list of requirement
# e.g. ['django==1.5.1', 'mezzanine==1.4.6']
reqs = [str(ir.req) for ir in install_reqs]


setup(
   name='g2p_harvester',
   version='1.0',
   description='harvest and normalize g2p data',
   author='Brian Walsh',
   author_email='walsbr@ohsu.edu.com',
   packages=['g2p_harvester'],  # same as name
   install_requires=reqs,  # external packages as dependencies
)
