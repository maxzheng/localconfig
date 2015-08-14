#!/usr/bin/env python

import os
import setuptools


setuptools.setup(
  name='localconfig',
  version='0.4.2',

  author='Max Zheng',
  author_email='maxzheng.os @t gmail.com',

  description='A simplified interface to ConfigParser using dot notion with data type / comment support.',
  long_description=open('README.rst').read(),

  url='https://github.com/maxzheng/localconfig',

  install_requires=[
  ],

  license='MIT',

  package_dir={'': 'src'},
  packages=setuptools.find_packages('src'),
  include_package_data=True,

  setup_requires=['setuptools-git'],

#  scripts=['bin/cast-example'],

  classifiers=[
    'Development Status :: 5 - Production/Stable',

    'Intended Audience :: Developers',
    'Topic :: Software Development',

    'License :: OSI Approved :: MIT License',

    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
  ],

  keywords='configuration config ConfigParser data type support',
)
