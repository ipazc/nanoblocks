#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from setuptools import setup, setuptools
from nanoblocks import __version__

__author__ = "Iván de Paz Centeno"


def readme():
    with open('README.rst', encoding="UTF-8") as f:
        return f.read()


if sys.version_info < (3, 4, 1):
    sys.exit('Python < 3.4.1 is not supported!')


setup(name='nanoblocks',
      version=__version__,
      description='Another unofficial Python package for managing Nano Cryptocurrency',
      long_description=readme(),
      url='http://github.com/ipazc/nanoblocks',
      author='Iván de Paz Centeno',
      author_email='ipazc@unileon.es',
      license='MIT',
      packages=setuptools.find_packages(exclude=["tests.*", "tests"]),
      install_requires=[
          "requests>=2.18.4",
          "qrcode[pil]>=6.1",
          "pandas>=1.1.0",
          "numpy>=1.18.1",
          "tzlocal>=2.1",
      ],
      classifiers=[
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: Education',
          'Intended Audience :: Science/Research',
          'Natural Language :: English',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
      ],
      test_suite='nose.collector',
      tests_require=['nose'],
      include_package_data=True,
      keywords="nano protocol cryptocurrency python package wrapper nanoblocks",
      zip_safe=False)
