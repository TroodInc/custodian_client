from os.path import join, dirname

from setuptools import setup, find_packages

setup(
    name='custodian_client',
    version=0.1,
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    include_package_data=True,
    packages=find_packages(),
    author='Trood CIS',
    url='',
    install_requires=[
        u'requests==2.18.4',
        'dateparser'
    ]
)
