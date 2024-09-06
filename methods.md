# Methods

## Description

To model the future price change of a stock, a [metalog distribution](https://en.wikipedia.org/wiki/Metalog_distribution) is fit to the previous $N$ changes (typically $N>100$). For an individual stock, we can randomly sample from this fitted distribution $M$ times, aggregate the samples, and have a model for the price change over the next $M$ time periods.

However, for a collection of stocks, we must take into account that their changes may be correlated with each other. For this we sample from a [multivariate normal distribution](https://en.wikipedia.org/wiki/Multivariate_normal_distribution) with $\vec{\mu}=0$ and the covariance matrix being the correlation matrix computed from the stocks' changes over the past $N$ time periods. We use the correlation matrix here to allow us to easily convert the sample vector to percentiles using the univariate normal CDF. We then have a vector of percentiles roughly correlated according to the correlation matrix of the stocks, which we can use to easily sample from each stock's metalog distribution.

## Mathematical Representation

Let $\{X_1,X_2,...,X_n\}$ be a collection of $N$ dimensional vectors containing the log price changes of each stock over the past $N$ time periods.

Apply a metalog fit to each price change vector.

$$
Metalog(X_i)\rightarrow M_i
$$

Here $M_i$ represents the metalog quantile function associated with the fitted metalog distribution of $X_i$. Conveniently, this is the easiest form of the metalog distribution to acheive by [fitting data](https://en.wikipedia.org/wiki/Metalog_distribution#Fitting_to_data).

Compute the correlation matrix for the set of price change vectors.

$$
S=Corr(\{X_1,X_2,...,X_n\})
$$

Now sample from the multivate normal distribution

$$
Y\sim MultiNorm(\mu=\vec{0},\ \Sigma=S)
$$

Apply the univariate normal CDF, element-wise, to $Y$ to get a percentile vector.

$$
Z=NormCDF(Y)
$$

For any stock $i$ associated with $X_i$, a random sample is $M_i(Z_i)$.


