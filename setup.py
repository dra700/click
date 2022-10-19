from setuptools import setup

setup(
    name="cli",
    version="0.1",
    author="dra700",
    install_requires=[
        "click",
    ],
    entry_points='''
        [console_scripts]
        jira_cli=cli.main:cli
    ''',
)
