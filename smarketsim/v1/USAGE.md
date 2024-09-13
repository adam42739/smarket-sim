# Usage

## Simulating a portfolio

```python
import smarketsim.v1 as smarketsim
```

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

## Writing simulation results to a file

Write to a file.

```python
port.to_file("sim_files/", "sim1")
```

Read from a file.

```python
port.from_file("sim_files/", "sim1")
```
