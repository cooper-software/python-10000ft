from setuptools import setup, find_packages
execfile('tenthousandfeet/version.py')

setup(
    name = 'tenthousandfeet',
    version = __version__,
    packages = find_packages(),
    description = 'A client for the 10000ft.com service (http://10kft.github.io/api-documentation/).',
    author = 'Elisha Fitch-Cook',
    author_email = 'elisha@cooper.com',
    url = 'https://github.com/cooper-software/python-10000ft',
    install_requires = ['requests', 'python-dateutil'],
    tests_require = ['httmock', 'mock']
)
