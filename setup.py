#!/usr/bin/env python

import setuptools


setuptools.setup(
  name='localconfig',
  version='1.0.1',

  author='Max Zheng',
  author_email='maxzheng.os @t gmail.com',

  description='A simplified interface to ConfigParser using dot notion with data type / comment support.',
  long_description=open('README.rst').read(),

  url='https://github.com/maxzheng/localconfig',

  install_requires=[
  ],

  license='MIT',

  packages=setuptools.find_packages(),
  include_package_data=True,

  setup_requires=['setuptools-git'],

  classifiers=[
    'Development Status :: 5 - Production/Stable',

    'Intended Audience :: Developers',
    'Topic :: Software Development',

    'License :: OSI Approved :: MIT License',

    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.6',
  ],

  keywords='configuration config ConfigParser data type support',
)
