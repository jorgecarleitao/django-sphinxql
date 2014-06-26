from setuptools import setup, find_packages

setup(name='Django-SphinxQL',
      version='0.0.1',
      description='Sphinx search on Django',
      long_description=open('README.md').read(),
      author='Jorge C. Leitão',
      author_email='jorgecarleitao@gmail.com',
      packages=find_packages(),
      install_requires=["Django >= 1.4"],
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'Environment :: Web Environment',
          'Framework :: Django',
          'Intended Audience :: Developers',
          'Operating System :: Unix',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Topic :: Utilities',
      ],
)
