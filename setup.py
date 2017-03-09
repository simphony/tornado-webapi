from setuptools import setup, find_packages

# Setup version
VERSION = '0.6.0.dev0'

# Read description

with open('README.rst', 'r') as readme:
    README_TEXT = readme.read()

def write_version_py():
    filename = os.path.join(
        os.path.dirname(__file__),
        'tornadowebapi',
        'version.py')
    ver = "__version__ = '{}'\n"
    with open(filename, 'w') as fh:
        fh.write("# Autogenerated by setup.py\n")
        fh.write(ver.format(VERSION))


write_version_py()

# main setup configuration class
setup(
    name='tornadowebapi',
    version=VERSION,
    author='SimPhoNy Project',
    license='BSD',
    description='Tornado-based WebAPI framework',
    install_requires=[
        "setuptools>=21.0",
        "tornado>=4.3"
    ],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False
    )
