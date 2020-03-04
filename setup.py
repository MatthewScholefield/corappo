from setuptools import setup

setup(
    name='corappo',
    version='0.2.1',
    description='A tool to automatically generate CMake projects',
    url='https://github.com/matthewscholefield/corappo',
    author='Matthew D. Scholefield',
    author_email='matthew331199@gmail.com',
    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='corappo',
    packages=['corappo'],
    install_requires=[],
    entry_points={
        'console_scripts': [
            'corappo=corappo.__main__:main'
        ],
    }
)
