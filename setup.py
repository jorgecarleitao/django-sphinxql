from setuptools import setup, find_packages

setup(name='django-sphinxql',
      version='1.1.0',
      description='Sphinx search on Django',
      long_description=open('README.md').read(),
      author='Jorge C. Leitão',
      author_email='jorgecarleitao@gmail.com',
      packages=find_packages(),
      install_requires=['Django >= 1.8', 'pymysql'],
      url='https://github.com/jorgecarleitao/django-sphinxql',
      license='GPLv2',
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Web Environment',
          'Framework :: Django',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
          'Operating System :: Unix',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Topic :: Utilities',
      ],
)
