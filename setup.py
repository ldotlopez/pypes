# -*- encoding: utf-8 -*-

from distutils.core import setup

setup(
    name='pypes',
    version='0.0.0.20140318.1',
    author='L. López',
    author_email='ldotlopez@gmail.com',
    packages=['pypes', 'pypes.tests'],
    scripts=[],
    url='https://github.com/ldotlopez/pypes',
    license='LICENSE.txt',
    description='Flow-based programming for Python 3',
    long_description=open('README').read(),
    install_requires=[
    ],
)
