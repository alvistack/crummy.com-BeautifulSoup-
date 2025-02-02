# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='beautifulsoup4',
    version='4.13.3',
    description='Screen-scraping library',
    author_email='Leonard Richardson <leonardr@segfault.org>',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Markup :: HTML',
        'Topic :: Text Processing :: Markup :: SGML',
        'Topic :: Text Processing :: Markup :: XML',
    ],
    install_requires=[
        'soupsieve>1.2',
        'typing-extensions>=4.0.0',
    ],
    extras_require={
        'cchardet': [
            'cchardet',
        ],
        'chardet': [
            'chardet',
        ],
        'charset-normalizer': [
            'charset-normalizer',
        ],
        'html5lib': [
            'html5lib',
        ],
        'lxml': [
            'lxml',
        ],
    },
    packages=[
        'bs4',
        'bs4.builder',
        'bs4.tests',
    ],
)
