import re
from os.path import join as join_path

import setuptools

with open(join_path("bandlab_master", "__init__.py"), encoding="utf8") as f:
    version = re.search(r'__version__ = "(.*?)"', f.read()).group(1)

setuptools.setup(
    name='bandlab-master',
    version=version,
    author='Zeke Marffy',
    author_email='zmarffy@yahoo.com',
    packages=setuptools.find_packages(),
    url='https://github.com/zmarffy/bandlab-master',
    license='MIT',
    description='Master a song with BandLab',
    python_requires='>=3.6',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    install_requires=[
        'selenium',
        'webdriver-extended>=1.1',
        'zmtools>=1.4.0'
    ],
    entry_points={
        'console_scripts': [
            'bandlab-master = bandlab_master.__main__:main',
        ],
    },
)
