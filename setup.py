""" PIP module declaration for clouds-aws """
from os import environ

from setuptools import setup, find_packages

setup(
    name='clouds-aws',

    version='0.3.9',

    description='A tool for easy handling of AWS CloudFormation stacks as code.',
    long_description="""Clouds-aws a CLI tool easy handling if CloudFormation stacks as code.

Clouds-aws represents CF stacks on the local disk as files (template + parameters).
It can create or update existing stacks in AWS with a single,
easy command from local files or dump an existing stack to files.
Clouds-aws is also suitable for usage in automation.""",

    url='https://github.com/elias5000/clouds-aws',

    author='Frank Wittig',
    author_email='frank@e5k.de',

    license='Apache License, Version 2.0',

    classifiers=[
        'Development Status :: 5 - Production/Stable',

        'Environment :: Console',

        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',

        'License :: OSI Approved :: Apache Software License',

        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Operating System :: Unix',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',

        'Topic :: System :: Installation/Setup',
        'Topic :: Utilities'
    ],

    keywords='aws cloudformation devops',

    packages=find_packages('src'),
    package_dir={'': 'src'},

    entry_points={
        'console_scripts': [
            'clouds=clouds_aws:main'
        ]
    },

    install_requires=('boto3', 'PyYAML', 'tabulate', 'scandir')
)
