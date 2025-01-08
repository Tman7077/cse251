from setuptools import setup

setup(
    name='cse251',
    version='1.0.0',
    description='This package contains common classes and helper methods for the CSE 251 course at BYU-I.',
    url='https://github.com/byui-cse/cse251-py-package',
    author='Luc Comeau, Hunter Wilhelm, and Christopher Keers',
    license='MIT',
    packages=['cse251'],
    install_requires=['matplotlib', 'numpy', 'pillow', 'opencv-python', 'requests'],
    zip_safe=False
)