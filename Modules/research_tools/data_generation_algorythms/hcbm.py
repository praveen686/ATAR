"""
Implementation of the Hierarchical Correlation Block Model (HCBM) matrix.
"Clustering financial time series: How long is enough?" by Marti, G., Andler, S., Nielsen, F. and Donnat, P.
https://www.ijcai.org/Proceedings/16/Papers/367.pdf
"""
import numpy as np
import pandas as pd
from statsmodels.sandbox.distributions.multivariate import multivariate_t_rvs


def _hcbm_mat_helper(mat, n_low=0, n_high=214, rho_low=0.1, rho_high=0.9, blocks=4, depth=4):
    """
    Helper function for `generate_hcmb_mat` that recursively places rho values to HCBM matrix
    given as an input.

    By using a uniform distribution we select the start and end locations of the blocks in the
    matrix. For each block, we recurse depth times and repeat splitting up the sub-matrix into
    blocks. Each depth level has a unique correlation (rho) values generated from a uniform
    distributions, and bounded by `rho_low` and `rho_high`. This function works as a
    side-effect to the `mat` parameter.

    It is reproduced with modifications from the following paper:
    `Marti, G., Andler, S., Nielsen, F. and Donnat, P., 2016.
    Clustering financial time series: How long is enough?. arXiv preprint arXiv:1603.04017.
    <https://www.ijcai.org/Proceedings/16/Papers/367.pdf>`_

    :param mat: (np.array) Parent HCBM matrix.
    :param n_low: (int) Start location of HCMB matrix to work on.
    :param n_high: (int) End location of HCMB matrix to work on.
    :param rho_low: (float) Lower correlation bound of the matrix. Must be greater or equal
    to 0.
    :param rho_high: (float) Upper correlation bound of the matrix. Must be less or equal to 1.
    :param blocks: (int) Maximum number of blocks to generate per level of depth.
    :param depth: (int) Depth of recursion for generating new blocks.
    """

    # First, we check if we have reached the maximum depth of recursion. If so, we return.
    if depth == 0:
        return

    # We select the number of blocks to generate for this level of recursion.
    n_blocks = np.random.randint(1, blocks + 1)

    # We select the start and end locations of the blocks.
    block_starts = np.random.randint(n_low, n_high, n_blocks)
    block_ends = np.random.randint(n_low, n_high, n_blocks)

    # We sort the start and end locations of the blocks.
    block_starts.sort()
    block_ends.sort()

    # We generate a correlation value for each block.
    block_rhos = np.random.uniform(rho_low, rho_high, n_blocks)

    # We iterate over the blocks and place the correlation values in the HCBM matrix.
    for i in range(n_blocks):
        # We select the start and end locations of the current block.
        start = block_starts[i]
        end = block_ends[i]

        # We select the correlation value of the current block.
        rho = block_rhos[i]

        # We place the correlation value in the HCBM matrix.
        mat[start:end, start:end] = rho

        # We recurse on the current block.
        _hcbm_mat_helper(mat, start, end, rho_low, rho_high, blocks, depth - 1)

    return


def generate_hcmb_mat(t_samples, n_size, rho_low=0.1, rho_high=0.9, blocks=4, depth=4, permute=False):
    """
    Generates a Hierarchical Correlation Block Model (HCBM) matrix  of correlation values.

    By using a uniform distribution we select the start and end locations of the blocks in the
    matrix. For each block, we recurse depth times and repeat splitting up the sub-matrix into
    blocks. Each depth level has a unique correlation (rho) values generated from a uniform
    distributions, and bounded by `rho_low` and `rho_high`.

    It is reproduced with modifications from the following paper:
    `Marti, G., Andler, S., Nielsen, F. and Donnat, P., 2016.
    Clustering financial time series: How long is enough?. arXiv preprint arXiv:1603.04017.
    <https://www.ijcai.org/Proceedings/16/Papers/367.pdf>`_

    :param t_samples: (int) Number of HCBM matrices to generate.
    :param n_size: (int) Size of HCBM matrix.
    :param rho_low: (float) Lower correlation bound of the matrix. Must be greater or equal to 0.
    :param rho_high: (float) Upper correlation bound of the matrix. Must be less or equal to 1.
    :param blocks: (int) Number of blocks to generate per level of depth.
    :param depth: (int) Depth of recursion for generating new blocks.
    :param permute: (bool) Whether to permute the final HCBM matrix.
    :return: (np.array) Generated HCBM matrix of shape (t_samples, n_size, n_size).
    """

    # We generate the HCBM matrix.
    mat = np.zeros((t_samples, n_size, n_size))
    for i in range(t_samples):
        _hcbm_mat_helper(mat[i], 0, n_size, rho_low, rho_high, blocks, depth)

    # We permute the HCBM matrix if required.
    if permute:
        mat = np.random.permutation(mat)

    return mat


def time_series_from_dist(corr, t_samples=1000, dist="normal", deg_free=3):
    """
    Generates a time series from a given correlation matrix.

    It uses multivariate sampling from distributions to create the time series. It supports
    normal and student-t distributions. This method relies and acts as a wrapper for the
    `np.random.multivariate_normal` and
    `statsmodels.sandbox.distributions.multivariate.multivariate_t_rvs` modules.
    `<https://numpy.org/doc/stable/reference/random/generated/numpy.random.multivariate_normal.html>`_
    `<https://www.statsmodels.org/stable/sandbox.html?highlight=sandbox#module-statsmodels.sandbox>`_

    It is reproduced with modifications from the following paper:
    `Marti, G., Andler, S., Nielsen, F. and Donnat, P., 2016.
    Clustering financial time series: How long is enough?. arXiv preprint arXiv:1603.04017.
    <https://www.ijcai.org/Proceedings/16/Papers/367.pdf>`_

    :param corr: (np.array) Correlation matrix.
    :param t_samples: (int) Number of samples in the time series.
    :param dist: (str) Type of distributions to use.
        Can take the values ["normal", "student"].
    :param deg_free: (int) Degrees of freedom. Only used for student-t distribution.
    :return: (pd.DataFrame) The resulting time series of shape (len(corr), t_samples).
    """

    # We generate the time series.
    if dist == "normal":
        ts = np.random.multivariate_normal(np.zeros(len(corr)), corr, t_samples)
    elif dist == "student":
        ts = multivariate_t_rvs(np.zeros(len(corr)), corr, size=t_samples, df=deg_free)
    else:
        raise ValueError("Distribution not supported.")

    return pd.DataFrame(ts)
