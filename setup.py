
from setuptools import setup

setup(
    name='sepanactl',
    entry_points={
        'console_scripts': ['sepana-start=sepana:start', 'sepana-register=sepana:register', 'sepana-stop=sepana:stop', 'sepana-init=sepana:init'],
    },
    version='0.1',
    description='Sepana node config cli',
    author='Kolawole Tajudee',
    author_email='kolawole@teza.ai',
)
