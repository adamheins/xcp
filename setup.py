from setuptools import setup

setup(name='xcp-tool',
      version='0.1',
      description='Command line tool for cutting, copying, and pasting files.',
      url='https://github.com/adamheins/xcp',
      author='Adam Heins',
      author_email='mail@adamheins.com',
      license='MIT',
      packages=['xcp'],
      scripts=['bin/xcp'],
      zip_safe=False)
