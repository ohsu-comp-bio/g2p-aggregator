from setuptools import setup

try:  # for pip >= 10
    from pip._internal.req import parse_requirements
except ImportError:  # for pip <= 9.0.3
    from pip.req import parse_requirements

print 'start'

# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_reqs = parse_requirements('smmartnotebook/requirements.txt', session=False)

# reqs is a list of requirement
# e.g. ['django==1.5.1', 'mezzanine==1.4.6']
reqs = [str(ir.req) for ir in install_reqs]

print reqs

setup(
   name='smmartnotebook',
   version='1.0',
   description='create pandas dataset from g2p data',
   author='Brian Walsh',
   author_email='walsbr@ohsu.edu',
   packages=['smmartnotebook'],  # same as name
   install_requires=reqs,  # external packages as dependencies
)
