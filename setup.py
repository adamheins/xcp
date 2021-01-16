from setuptools import setup

install_requires = ['colorama', 'pyyaml']
test_requires = ['pytest']

with open('README.md') as f:
    long_description = f.read()

setup(name='xcp-tool',
      version='0.1.1',
      description='Command line tool for cutting, copying, and pasting files.',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/adamheins/xcp',
      author='Adam Heins',
      author_email='mail@adamheins.com',
      install_requires=install_requires,
      test_requires=test_requires,
      license='MIT',
      packages=['xcp'],
      scripts=['bin/xcp'],
      python_requires='>=3.5',
      zip_safe=False)
