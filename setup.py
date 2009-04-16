from setuptools import setup, find_packages

setup(
    name = "basecampreporting",
    version = "0.5",
    url = 'http://github.com/cmheisel/basecampreporting',
    license = 'MIT',
    description = "Read-only interface to Basecamp projects, with support for Scrum concepts like sprints and backlogs.",
    author = 'Chris Heisel',
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    install_requires = ['setuptools'],
)
