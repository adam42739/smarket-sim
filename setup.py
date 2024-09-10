from setuptools import setup

setup(
    name="smarketsim",
    version="0.1.0",
    description="Tool for risk analysis and stock market analysis",
    url="https://github.com/adam42739/smarket-sim",
    author="Adam Lynch",
    author_email="aclynch@umich.edu",
    license="MIT License",
    packages=["smarketsim"],
    install_requires=[
        "yfscraper",
        "numpy>=2.1.1",
        "scipy>=1.14.1",
        "fastparquet>=2024.5.0",
        "scikit-learn>=1.5.1"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Licesnse :: MIT License",
        "Operating System :: OS Independent",
    ],
)
