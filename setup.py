""" setup.py """
from pathlib import Path
from setuptools import setup

this_directory = Path(__file__).parent
long_description = (this_directory / 'README.md').read_text()

setup(name='delapp_helper',
    version='0.0.1',
    description='a small wrapper for the penny-del api',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/grindsa/delapp_helper',
    author='grindsa',
    author_email='grindelsack@gmail.com',
    license='GPL',
    packages=['delapphelper'],
    platforms='any',
    install_requires=[
        'requests',
    ],
    classifiers = [
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'Natural Language :: German',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules'
        ],
    zip_safe=False,
    test_suite="test")
