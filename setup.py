import os

from setuptools import setup

kwds = {}

# Read the long description from the README.txt
thisdir = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(thisdir, 'README.rst')) as f:
    kwds['long_description'] = f.read()


setup(
    name='grin',
    version='1.3.0',
    author='Robert Kern',
    author_email='robert.kern@enthought.com',
    maintainer='Matthew Brett',
    maintainer_email='matthew.brett@gmail.com',
    description="A grep program configured the way I like it.",
    license="BSD",
    url='https://github.com/matthew-brett/grin',
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Utilities",
    ],
    py_modules=["grin"],
    entry_points=dict(
        console_scripts=[
            "grin = grin:grin_main",
            "grind = grin:grind_main",
        ],
    ),
    tests_require=[
        'nose >= 0.10',
    ],
    test_suite='nose.collector',
    **kwds
)
