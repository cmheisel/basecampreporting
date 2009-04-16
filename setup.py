import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name = "basecampreporting",
    version = "0.5",
    url = 'http://github.com/cmheisel/basecampreporting',
    license = 'MIT',
    description = "Read-only interface to Basecamp projects, with support for Scrum concepts like sprints and backlogs.",
    long_description = read('README'),
    
    author = 'Chris Heisel',
    author_email = "chris@heisel.org",

    packages = find_packages('src'),
    package_dir = {'': 'src'},
    
    install_requires = ['setuptools', 'simplejson', 'elementtree'],

    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Office/Business :: Groupware',
        'Topic :: Office/Business :: Scheduling',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
