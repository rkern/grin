import os
from setuptools import setup

kwds = {}

# Read the long description from the README.txt
thisdir = os.path.abspath(os.path.dirname(__file__))
f = open(os.path.join(thisdir, 'README.txt'))
kwds['long_description'] = f.read()
f.close()


setup(
    name = 'grin',
    version = '1.2.1',
    author = 'Robert Kern',
    author_email = 'robert.kern@enthought.com',
    description = "A grep program configured the way I like it.",
    license = "BSD",
    classifiers = [
        "License :: OSI Approved :: BSD License",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Utilities",
    ],

    py_modules = ["grin"],
    entry_points = dict(
        console_scripts = [
            "grin = grin:grin_main",
            "grind = grin:grind_main",
        ],
    ),
    install_requires = [
        'argparse >= 1.1',
    ],
    tests_require = [
        'nose >= 0.10',
    ],
    test_suite = 'nose.collector',
    **kwds
)
