from setuptools import setup, find_packages

setup(
    name='aocref',
    version='1.0.1',
    description='Age of Empires reference data',
    url='https://github.com/siegeengineers/aoc-reference-data',
    package_data={'': ['*']},
    install_requires=[
        'requests==2.22.0',
        'ruamel.yaml==0.16.12'
    ]
)
