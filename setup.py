#!/usr/bin/env python
import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages

setup(
    name = "Dextrose",
    description = "Dextrose web application framework",
    version = version,
    packages = find_packages(),
    entry_points = {
        'console_scripts': ['dx = dextrose.cli:main']
    },
    install_requires = [
        'Werkzeug==0.6.2',
        'Jinja2==2.5.5',
        'mongoengine==0.4',
        'redis==2.2.2',
        'python-postmark==0.2.2',
        'PyYAML==3.09',
        'argparse',
        'celery'
    ],
)
