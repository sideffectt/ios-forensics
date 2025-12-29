"""Setup configuration for iOS Forensics Toolkit."""

from setuptools import setup, find_packages

setup(
    name='ios-forensics',
    version='1.0.0',
    description='Forensic toolkit for parsing iOS device artifacts',
    author='sideffectt',
    python_requires='>=3.7',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'ios-forensics=cli:main'
        ]
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Topic :: Security',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ]
)
