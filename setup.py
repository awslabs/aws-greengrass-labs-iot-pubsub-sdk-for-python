# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0.

import os
import codecs
from setuptools import setup, find_packages

PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))

def _load_readme():
    readme_path = os.path.join(PROJECT_DIR, 'README.md')
    with codecs.open(readme_path, 'r', 'utf-8') as f:
        return f.read()

setup(
    name='awsgreengrasspubsubsdk',
    version='0.1.5',  
    description='AWS Greengrass IoT Pubsub SDK for Python',
    long_description=_load_readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/awslabs/aws-greengrass-labs-iot-pubsub-sdk-for-python',
    author='Dean Colcott',
    author_email='dean.colcott@gmail.com',
    license='License :: OSI Approved :: MIT License',
    packages=find_packages(include=['awsgreengrasspubsubsdk*']),
    install_requires=['awsiotsdk'],
    python_requires='>=3.6',
    classifiers=[
        "Programming Language :: Python :: 3",
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        "Operating System :: OS Independent"
    ]
)
