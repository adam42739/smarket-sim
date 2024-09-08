# smarket-sim

## Introduction

smarket-sim uses historical stock price data to simulate the volatility and correlation of stocks in the future. This can be useful for determining riskiness of a portfolio since it depends on volatility and correlation.

For more information about how smarket-sim works, please see [methods](methods.md).

## Installation

Ensure [yf-scraper](https://github.com/adam42739/yf-scraper) is installed before proceeding.

```python
pip install git+https://github.com/adam42739/smarket-sim.git#egg=smarketsim
```

## Usage

### Simulating a portfolio

Create the portfolio object.

```python
port = smarketsim.Portfolio()
```

Initalize the portfolio with stock data.

```python
port.init_sim(
    "base/",
    {
        "aapl": 0.5
        "msft": 0.25
        "amzn": 0.25
    },
    datetime.datetime(2024, 9, 1)
)
```

Run the simulation

```python
port.sim_models()
```

View the simulation results.

```python
port.sim_summarize()
```

Output:

```console
Analysis: Next 20 Days:
    Volatility:  8.77 %
    Bottom 5% Performance:  -11.15 %
    Top 5% Performance:  17.00 %
Analysis: Next 100 Days:
    Volatility:  15.92 %
    Bottom 5% Performance:  -21.63 %
    Top 5% Performance:  26.94 %
Analysis: Next 400 Days:
    Volatility:  38.56 %
    Bottom 5% Performance:  -40.91 %
    Top 5% Performance:  72.93 %
Analysis: Next 1200 Days:
    Volatility:  78.26 %
    Bottom 5% Performance:  -63.09 %
    Top 5% Performance:  155.36 %
```

### Writing simulation results to a file

Write to a file.

```python
port.to_file("sim_files/", "sim1")
```

Read from a file.

```python
port.from_file("sim_files/", "sim1")
```
