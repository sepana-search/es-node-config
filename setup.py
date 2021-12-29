
from setuptools import setup

setup(
    name='sepanactl',
    entry_points={
        'console_scripts': ['sepanactl=sepana:app'],
    },
    version='0.1',
    description='Sepana node config cli',
    author='Kolawole Tajudee',
    author_email='kolawole@teza.ai',
    install_requires=[
        "typer",
        "requests",
        "pyyaml"
    ]
)
