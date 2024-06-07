# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

from setuptools import setup, find_packages

setup(name='spectre',
      version='0.0.0',
      description='SPECTRE: Process, Explore and Capture Transient Radio Emissions',
      author='Jimmy Fitzpatrick',
      author_email= 'jcfitzpatrick12@gmail.com',
      packages=['client', 'spectre', 'cfg'],  
      install_requires=[
        'numpy==1.24.0',
        'scipy==1.12.0',
        'astropy==6.0.1',
        'matplotlib==3.5.0',
    ]
)