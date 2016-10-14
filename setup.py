import os
from setuptools import setup

PACKAGE = 'clickutil'


def readme():
    with open('README.rst') as f:
        return f.read()


def get_version_str():
    ver_file = os.path.join(PACKAGE, 'version.py')
    with open(ver_file, 'r') as fid:
        version = fid.read()
    version = version.split("= ")
    version = version[1].strip()
    version = version.strip('"')
    version = version.strip("'")
    return version


# NOTE: I suspect zip_safe should actually be True, but I haven't
# had time to investigate yet.
setup(name=PACKAGE,
      version=get_version_str(),
      description=(
          'Tools for working with container types, command data operations, '
          'and concise exception handling'
      ),
      long_description=readme(),
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2.7',
      ],
      keywords='',
      url='https://github.com/stroxler/clickutil',
      author='Steven Troxler',
      author_email='steven.troxler@gmail.com',
      license='MIT',
      packages=[PACKAGE],
      install_requires=['click>=6.6', 'tdx>=0.0.1'],
      tests_require=['pytest'],
      include_package_data=True,
      zip_safe=False)
