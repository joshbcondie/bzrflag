import numpy as np

c = 0 #For transition matrix
posnoise = 5
delta_t = 0.5
plot_estimate = False
print_mu_sigma_t = False
print_estimate_vs_actual = False

# Initial estimate covariance matrix
sigma_t = np.matrix(
    [[100, 0, 0, 0, 0, 0],
    [0, 0.1, 0, 0, 0, 0],
    [0, 0, 0.1, 0, 0, 0],
    [0, 0, 0, 100, 0, 0],
    [0, 0, 0, 0, 0.1, 0],
    [0, 0, 0, 0, 0, 0.1]]
)

# Covariance in process noise
sigma_x = np.matrix(
    [[0.1, 0, 0, 0, 0, 0],
    [0, 0.1, 0, 0, 0, 0],
    [0, 0, 100, 0, 0, 0],
    [0, 0, 0, 0.1, 0, 0],
    [0, 0, 0, 0, 0.1, 0],
    [0, 0, 0, 0, 0, 100]]
)
