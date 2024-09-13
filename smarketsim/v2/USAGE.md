# Usage

## Simulating a portfolio

```python
import smarketsim.v2 as smarketsim
```

Download stock price data to a base directory.

```python
import yfscraper.v2 as yfscraper
import datetime

BASE = "base/"

yfscraper.download_data(["AAPL", "MSFT", "AMZN"], BASE, datetime.datetime.today())
```

Build parq<sup>1</sup> data from the base directory.

```python
PARQ = "parq/"

smarketsim.build_parq(BASE, PARQ)
```

1. "parq data" refers to features computed from raw stock price data stored in [parquet](https://en.wikipedia.org/wiki/Apache_Parquet) format for each of use later on.

Create the simulation object.

```python
sim = smarketsim.Simulation()
```

Build the simulation object and pass a simulation begin date. The simulation begin date must be a market day.

```python
DATE = "2020-01-03"

sim.build(PARQ, ["AAPL", "MSFT", "AMZN"], DATE)
```

Run the simulation some amount of days

```python
DAYS = 25

sim.sim(DAYS)
```

If needed, write the simulation to disk for ease of access later on.

```python
SIM_DATA_FOLDER = "sims/"
SIM_UNIQUE_ID = "sim01"

sim.write_sim(SIM_DATA_FOLDER, SIM_UNIQUE_ID)
```

```python
sim = smarketsim.Simulation()
sim.read_sim(SIM_DATA_FOLDER, SIM_UNIQUE_ID)
```

Get the last $N$ number of simulated prices.

```python
N = 3

sim_data = sim.last_ntcloses(N)
print(sim_data)
```

```console
>>>                 AAPL        MSFT       AMZN
>>>Date                                                  
>>>2020-01-08  70.504647  157.146555  91.984244
>>>2020-01-07  70.509706  159.216697  94.778780
>>>2020-01-06  72.616016  158.769957  93.643120
```