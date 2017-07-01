from setuptools import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='jarviscli',
    version='1.0',
    description='Personal Assistant for Linux',
    url='https://github.com/sukeesh/Jarvis',
    author='Sukeesh',
    author_email='vsukeeshbabu@gmail.com',
    keywords=['linux','personal-assistant'],
    license='MIT',
    packages=['jarviscli'],
    classifiers=['Programming Language :: Python :: 2.7','License :: OSI Approved :: MIT License'],
    install_requires=required
)
