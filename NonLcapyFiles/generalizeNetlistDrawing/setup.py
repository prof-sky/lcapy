from setuptools import setup, find_packages

setup(
    name="generalize netlist drawing",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "lcapy",
        "networkx",
    ],
)