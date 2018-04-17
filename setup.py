""" PIP module declaration for clouds-aws """
from os import environ

from setuptools import setup, find_packages

try:
    SNAPSHOT = 'dev%s' % environ['BUILD_NUMBER']
except KeyError:
    SNAPSHOT = ''

setup(
    name='clouds-aws',

    version='0.3.0-1%s' % SNAPSHOT,

    description='A tool for easy handling of AWS Cloudformation stacks as code.',
    long_description='For detailed usage instructions see '
                     'https://github.com/elias5000/clouds-aws/blob/master/README.md',

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

    install_requires=['boto3', 'PyYAML', 'tabulate']
)
