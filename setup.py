try:
    from setuptools import setup
except ImportError:
    from distutilts.core import setup

config = {
    'description': 'Boothy: a wedding photobooth',
    'author': 'Andy Smith & Josh Quick',
    'url': 'https://github.com/aresti/boothy',
    'version': '0.1',
    'install_requires': ['nose'],
    'packages': ['boothy'],
    'scripts': [],
    'name': 'boothy'
}

setup(**config)
