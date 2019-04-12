"""AoC Reference Data setup."""
from setuptools import setup, find_packages

setup(
    name='aocref',
    version='0.0.2',
    description='Age of Empires II reference data.',
    url='https://github.com/siegeengineers/aoc-reference-data/',
    license='MIT',
    author='happyleaves',
    author_email='happyleaves.tfr@gmail.com',
    packages=find_packages(),
    package_data={'aocref': [
        'data/events/events.json',
        'data/events/series.json',
        'data/datasets/*.json',
        'data/constants.json',
        'data/platforms.json'
    ]},
    install_requires=[
        'iso8601>=0.1.12',
        'networkx>=2.2',
        'requests>=2.20.1',
        'requests-cache>=0.4.13',
        'SQLAlchemy>=1.2.14'
    ],
    entry_points = {
        'console_scripts': ['aocref=aocref.__main__:setup'],
    },
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
    ]
)
