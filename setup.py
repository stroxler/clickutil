from setuptools import setup

setup(name='clickutil',
      version='0.0.1',
      description='Template for python development',
      long_description="",
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Programming Language :: Python :: 2.7',
      ],
      entry_points={
          "console_scripts": [
          ]
      },
      keywords='',
      url='https://github.com/stroxler/clickutil',
      author='Steven Troxler',
      author_email='steven.troxler@gmail.com',
      license='BSD',
      packages=['clickutil'],
      install_requires=[
          'click',
      ],
      include_package_data=True,
      zip_safe=False)
