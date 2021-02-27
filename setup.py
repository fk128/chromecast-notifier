#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('requirements.txt') as requirements_file:
    requirements = requirements_file.read().splitlines()


setup(name='chromecast_notifier',
      version='0.1',
      description='',
      author='F. K.',
      keywords='chromecast',
      license='Apache License 2.0',
      long_description=readme,
      classifiers=['Intended Audience :: Developers',
                   'Intended Audience :: Education',
                   'License :: OSI Approved :: Apache Software License',
                   'Operating System :: POSIX :: Linux',
                   'Operating System :: MacOS :: MacOS X',
                   'Operating System :: Microsoft :: Windows',
                   'Programming Language :: Python :: 3.7'],
      install_requires=requirements,
      )
