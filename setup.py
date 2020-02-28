from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='interactive_input',
    packages=['interactive_input'],
    version='0.4.3',
    license='MIT',
    python_requires='>=3.6',
    install_requires=[],
    author='0Delta',
    author_email='0deltast@gmail.com',
    url='https://github.com/0Delta/py-interactive_input',
    description='curses based interactive value input',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords='interactive_input 0Delta',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Development Status :: 3 - Alpha',
        'Environment :: Console :: Curses'
    ],
)
