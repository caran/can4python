#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

# Read version string. See
# http://stackoverflow.com/questions/458550/standard-way-to-embed-version-into-python-package
exec(open('can4python/version.py').read())

setup(
    name='can4python',
    version=__version__,
    description="A package for handling CAN bus signals on Linux SocketCAN, for Python 3.3 and later.",
    long_description=readme + '\n\n' + history,
    author="Jonas Berg",
    author_email='caranopensource@semcon.com',
    url='https://github.com/caran/can4python',
    packages=['can4python'],
    package_dir={'can4python': 'can4python'},
    include_package_data=True,
    install_requires=[],
    license="BSD",
    zip_safe=False,
    keywords='can4python',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Embedded Systems',
        'Topic :: Software Development :: Libraries',
        'Topic :: System :: Hardware :: Hardware Drivers'
    ],
    test_suite='tests',
    tests_require=[]
)
