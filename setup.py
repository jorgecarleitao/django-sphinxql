from setuptools import setup, find_packages

setup(name='django-sphinxql',
      version='0.1',
      description='Sphinx search on Django',
      long_description=open('README.md').read(),
      author='Jorge C. Leitão',
      author_email='jorgecarleitao@gmail.com',
      packages=find_packages(),
      install_requires=['Django >= 1.8rc1', 'pymysql'],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Web Environment',
          'Framework :: Django',
          'Intended Audience :: Developers',
          'Operating System :: Unix',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Topic :: Utilities',
      ],
)
