from setuptools import setup, find_packages

setup(
    name='aocref',
    version='2.0.4',
    description='Age of Empires reference data',
    url='https://github.com/siegeengineers/aoc-reference-data',
    packages=find_packages(),
    package_data={'aocref': [
        'data/datasets/*',
        'data/constants.json'
    ]},
    install_requires=[
        'requests>=2.22.0',
        'ruamel.yaml>=0.16.12',
        'pycountry>=20.7.3'
    ]
)
