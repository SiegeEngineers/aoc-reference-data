from setuptools import setup, find_packages

setup(
    name='aocref',
    version='2.0.24',
    description='Age of Empires reference data',
    url='https://github.com/siegeengineers/aoc-reference-data',
    packages=find_packages(exclude=["scripts*"]),
    package_data={'aocref': [
        'data/datasets/*',
        'data/constants.json'
    ]},
    install_requires=[
    ]
)
