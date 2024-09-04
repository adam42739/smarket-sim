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
        "git+https://github.com/adam42739/yf-scraper.git#egg=yfscraper",
        "numpy>=2.1.1",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Licesnse :: MIT License",
        "Operating System :: OS Independent",
    ],
)
