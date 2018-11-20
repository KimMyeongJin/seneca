from setuptools import setup, find_packages
from setuptools.extension import Extension
from distutils.command.build_ext import build_ext
import os

major = 0

def get_version_number():
    if os.getenv('CIRCLECI'):
        minor, patch = divmod(int(os.getenv('CIRCLE_BUILD_NUM')), 180)
        ver = '{}.{}.{}'.format(major, minor, patch)
        return ver
    else:
        return '{}.3.32'.format(major)

__version__ = get_version_number()

print('#' * 128)
print('\n    VERSION = {}\n'.format(__version__))
print('#' * 128)

requirements = [
    'redis==2.10.6',
    'python-dotenv==0.9.1',
    'ujson==1.35'
]

class ve_build_ext(build_ext):
    """Build C extensions, but fail with a straightforward exception."""

    def run(self):
        """Wrap `run` with `BuildFailed`."""
        try:
            build_ext.run(self)
        except errors.DistutilsPlatformError:
            raise BuildFailed()

    def build_extension(self, ext):
        """Wrap `build_extension` with `BuildFailed`."""
        try:
            # Uncomment to test compile failure handling:
            #   raise errors.CCompilerError("OOPS")
            build_ext.build_extension(self, ext)
        except ext_errors:
            raise BuildFailed()
        except ValueError as err:
            # this can happen on Windows 64 bit, see Python issue 7511
            if "'path'" in str(err):    # works with both py 2/3
                raise BuildFailed()
            raise

setup(
    name='seneca',
    version=__version__,
    description='Python-based smart contract language and interpreter.',
    entry_points={
        'console_scripts': ['seneca=seneca.cli:main'],
    },
    packages=find_packages(),
    install_requires=requirements,
    url='https://github.com/Lamden/seneca',
    author='Lamden',
    author_email='team@lamden.io',
    classifiers=[
        'Programming Language :: Python :: 3.6',
    ],
    zip_safe=True,
    data_files=[
        ('./seneca/constants', ['seneca/constants/cu_costs.const']),
    ],
    ext_modules=[
        Extension('seneca.libs.metering.tracer', sources = ['seneca/libs/metering/tracer.c'])
    ],
    cmdclass={
        'build_ext': ve_build_ext,
    },
)
