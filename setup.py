from setuptools import setup

setup(
    name="cli",
    version="0.1.0",
    author="dra700",
    install_requires=[
        "click",
    ],
    entry_points='''
        [console_scripts]
        cli=cli.main:cli
    ''',
)
