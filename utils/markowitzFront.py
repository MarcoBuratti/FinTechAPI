import numpy as np
import matplotlib.pyplot as plt
import cvxopt as opt
from cvxopt import blas, solvers
import pandas as pd


import plotly
import cufflinks

# (*) To communicate with Plotly's server, sign in with credentials file
#import chart_studio.plotly as py

# (*) Useful Python/Plotly tools
import plotly.tools as tls   

# (*) Graph objects to piece together plots
import plotly.express as px


## NUMBER OF ASSETS
n_assets = 4
## NUMBER OF OBSERVATIONS
n_obs = 1000
return_vec = np.random.randn(n_assets, n_obs)

def rand_weights(n):
    ''' Produces n random weights that sum to 1 '''
    k = np.random.rand(n)
    return k / sum(k)

def random_portfolio(returns):
    ''' 
    Returns the mean and standard deviation of returns for a random portfolio
    '''

    p = np.asmatrix(np.mean(returns, axis=1))
    w = np.asmatrix(rand_weights(returns.shape[0]))
    C = np.asmatrix(np.cov(returns))
    
    mu = w * p.T
    sigma = np.sqrt(w * C * w.T)
    
    # This recursion reduces outliers to keep plots pretty
    if sigma > 2:
        return random_portfolio(returns)
    return mu, sigma

n_portfolios = 500
means, stds = np.column_stack([
    random_portfolio(return_vec) for _ in range(n_portfolios)
])

#fig = plt.figure()
#plt.plot(stds, means, 'o', markersize=5)
#plt.xlabel('std')
#plt.ylabel('mean')
#plt.title('Mean and standard deviation of returns of randomly generated portfolios')
#plt.px(fig, filename='mean_std', strip_style=True)

media = [ elem[0] for elem in means]
stdVar = [ elem[0] for elem in stds]
fig = px.scatter(y=media, x=stdVar)
fig.show()
