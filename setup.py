from codecs import open
from os import path, environ
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

try:
    snapshot = 'dev%s' % environ['BUILD_NUMBER']
except KeyError:
    snapshot = ''

setup(
    name='clouds-aws',

    version='0.2.3-4%s' % snapshot,

    description='A tool for easy handling of AWS Cloudformation stacks as code.',
    long_description='For detailed usage instructions see https://github.com/elias5000/clouds-aws/blob/master/README.md',

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

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',

        'Topic :: System :: Installation/Setup',
        'Topic :: Utilities'
    ],

    keywords='aws cloudformation devops',

    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'clouds=clouds_aws:main'
        ]
    },

    install_requires=['boto3', 'PyYAML']
)
