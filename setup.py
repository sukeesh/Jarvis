from setuptools import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='Jarvis',
    version='',
    description='Personal Assistant for Linux',
    url='https://github.com/sukeesh/Jarvis',
    author='Sukeesh',
    author_email='vsukeeshbabu@gmail.com',
    keywords=['linux','personal-assistant'],
    license='MIT',
    packages=['Jarvis'],
    classifiers=['Programming Language :: Python :: 2.7','License :: MIT License'],
    install_requires=required
)
