# #!/usr/bin/env python3
#
# from statsmodels.distributions.empirical_distribution import ECDF
# import itertools as itr
# import seaborn as sns
#
# import matplotlib.pyplot as plt
# import pandas as pd
# import numpy as np
# import datetime
# import math
#
# sharpe_ratio = lambda r: r.mean() / (r.std()+0.0000001) * (365 ** 0.5)
#
# class CSCV(object):
#     """Combinatorially symmetric cross-validation algorithm.
#     Calculate backtesting about overfitting probability distribution and performance degradation.
#     Attributes:
#         n_bins:A int of CSCV algorithm bin size to control overfitting calculation.Default is 10.
#         objective:A function of in sample(is) and out of sample(oos) return benchmark algorithm.Default is lambda r:r.mean().
#     """
#     def __init__(self, n_bins=10, objective=sharpe_ratio):
#         self.n_bins = n_bins
#         self.objective = objective
#         self.bins_enumeration = [set(x) for x in itr.combinations(np.arange(10), 10 // 2)]
#
#         self.Rs = [pd.Series(dtype=float) for i in range(len(self.bins_enumeration))]
#         self.R_bars = [pd.Series(dtype=float) for i in range(len(self.bins_enumeration))]
#
#     def add_daily_returns(self, daily_returns):
#         """Add daily_returns in algorithm.
#         Args:
#           daily_returns: A dataframe of trading daily_returns.
#         """
#         bin_size = daily_returns.shape[0] // self.n_bins
#         bins = [daily_returns.iloc[i*bin_size: (i+1) * bin_size] for i in range(self.n_bins)]
#
#         for set_id, is_set in enumerate(self.bins_enumeration):
#             oos_set = set(range(self.n_bins)) - is_set
#             is_returns = pd.concat([bins[i] for i in is_set])
#             oos_returns = eturns = pd.concat([bins[i] for i in oos_set])
#             R = self.objective(is_returns)
#             R_bar = self.objective(oos_returns)
#             self.Rs[set_id] = self.Rs[set_id].append(R)
#             self.R_bars[set_id] = self.R_bars[set_id].append(R_bar)
#
#     def estimate_overfitting(self, plot=False):
#         """Estimate overfitting probability.
#         Generate the result on Combinatorially symmetric cross-validation algorithm.
#         Display related analysis charts.
#         Args:
#           plot: A bool of control plot display. Default is False.
#         Returns:
#           A dict of result include:
#           pbo_test: A float of overfitting probability.
#           logits: A float of estimated logits of OOS rankings.
#           R_n_star: A list of IS performance of th trategies that has the best ranking in IS.
#           R_bar_n_star: A list of find the OOS performance of the strategies that has the best ranking in IS.
#           dom_df: A dataframe of optimized_IS, non_optimized_OOS data.
#         """
#         # calculate strategy performance in IS(R_df) and OOS(R_bar_df)
#         R_df = pd.DataFrame(self.Rs)
#         R_bar_df = pd.DataFrame(self.R_bars)
#
#         # calculate ranking of the strategies
#         R_rank_df = R_df.rank(axis=1, ascending=False, method='first')
#         R_bar_rank_df = R_bar_df.rank(axis=1, ascending=False, method='first')
#
#         # find the IS performance of th trategies that has the best ranking in IS
#         r_star_series = (R_df * (R_rank_df == 1)).unstack().dropna()
#         r_star_series = r_star_series[r_star_series != 0].sort_index(level=-1)
#
#         # find the OOS performance of the strategies that has the best ranking in IS
#         r_bar_star_series = (R_bar_df * (R_rank_df == 1)).unstack().dropna()
#         r_bar_star_series = r_bar_star_series[r_bar_star_series != 0].sort_index(level=-1)
#
#         # find the ranking of strategies which has the best ranking in IS
#         r_bar_rank_series = (R_bar_rank_df * (R_rank_df == 1)).unstack().dropna()
#         r_bar_rank_series = r_bar_rank_series[r_bar_rank_series != 0].sort_index(level=-1)
#
#         # probability of overfitting
#
#         # estimate logits of OOS rankings
#         logits = (1-((r_bar_rank_series)/(len(R_df.columns)+1))).map(lambda p: math.log(p/(1-p)))
#         prob = (logits < 0).sum() / len(logits)
#
#         # stochastic dominance
#
#         # caluclate
#         if len(r_bar_star_series) != 0:
#             y = np.linspace(
#                 min(r_bar_star_series), max(r_bar_star_series), endpoint=True, num=1000
#             )
#
#             # build CDF performance of best candidate in IS
#             R_bar_n_star_cdf = ECDF(r_bar_star_series.values)
#             optimized = R_bar_n_star_cdf(y)
#
#             # build CDF performance of average candidate in IS
#             R_bar_mean_cdf = ECDF(R_bar_df.median(axis=1).values)
#             non_optimized = R_bar_mean_cdf(y)
#
#             #
#             dom_df = pd.DataFrame(
#                 dict(optimized_IS=optimized, non_optimized_OOS=non_optimized)
#             , index=y)
#             dom_df["SD2"] = -(dom_df.non_optimized_OOS - dom_df.optimized_IS).cumsum()
#         else:
#             dom_df = pd.DataFrame(columns=['optimized_IS', 'non_optimized_OOS', 'SD2'])
#
#         ret = {
#             'pbo_test': (logits < 0).sum() / len(logits),
#             'logits': logits.to_list(),
#             'R_n_star': r_star_series.to_list(),
#             'R_bar_n_star': r_bar_star_series.to_list(),
#             'dom_df': dom_df,
#         }
#
#         if plot:
#             # probability distribution
#             plt.title('Probability Distribution')
#             plt.hist(x=[l for l in ret['logits'] if l > -10000], bins='auto')
#             plt.xlabel('Logits')
#             plt.ylabel('Frequency')
#             plt.show()
#
#             # performance degradation
#             plt.title('Performance degradation')
#             plt.scatter(ret['R_n_star'], ret['R_bar_n_star'])
#             plt.xlabel('In-sample Performance')
#             plt.ylabel('Out-of-sample Performance')
#
#             # first and second Stochastic dominance
#             plt.title('Stochastic dominance')
#             ret['dom_df'].plot(secondary_y=['SD2'])
#             plt.xlabel('Performance optimized vs non-optimized')
#             plt.ylabel('Frequency')
#             plt.show()
#
#         return ret


import itertools as itr
import math
import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import ray
# !/usr/bin/env python3
from logger_tt import logger
from statsmodels.distributions.empirical_distribution import ECDF

sharpe_ratio = lambda r: r.mean() / (r.std() + 0.0000001) * (365 ** 0.5)
# sharpe_ratio = lambda r: r.mean() / (r.std() + 0.0000001) * (252 ** 0.5)

"""The CSCV algorithm is a backtesting method used to estimate overfitting probability and performance degradation. 
It works by dividing a dataset into in-sample (IS) and out-of-sample (OOS) sets, then calculating the ranking of each 
strategy in the IS set. The performance of the strategies that have the best ranking in the IS set is then compared to 
the average performance of all strategies in the OOS set. The overfitting probability is then estimated based on the 
difference in rankings between the IS and OOS sets. The performance degradation is estimated by calculating the 
difference in performance between the IS and OOS sets. Finally, the stochastic dominance of the best-performing 
strategy in the IS set is calculated and compared to the average performance of all strategies in the OOS set.

# Here's what the below class is doing:
# 1. It splits the data into N (10) bins.
# 2. It then takes 9 of those bins and uses them as in-sample (IS) data, and the remaining bin is used as out-of-sample (OOS) data.
# 3. This process is repeated for all possible combinations of IS/OOS bins.
# 4. For each IS/OOS combination, the strategy is 'trained' on the IS data and then tested on the OOS data.
# 5. The results are stored in a list of lists (self.Rs). Each sub-list contains the performance of the strategy for one IS/OOS combination.
# 6. The results are then used to calculate the probability of overfitting (PBO).
# 6.1 This is done by ranking the performance of each strategy for each IS/OOS combination.
# 6.2 The best performing strategy in IS is then identified, and its OOS performance is recorded.
# 6.3 This process is repeated for all IS/OOS combinations.
# 6.4 A logit function is used to estimate the probability of overfitting.
# 6.5 The PBO is then calculated as the number of logits that are less than zero, divided by the total number of logits.
# 7. The results are also used to calculate the performance degradation.
# 7.1 This is done by plotting the IS and OOS performance of the best performing strategy in IS for each IS/OOS combination.
# 8. The results are also used to calculate stochastic dominance (SD).
# 8.1 This is done by plotting the cumulative distribution function (CDF) of the IS and OOS performance of the best performing strategy in IS for each IS/OOS combination.
# 8.2 The first SD is calculated as the area under the curve where the CDF of the IS performance is greater than that of the OOS performance.
# 8.3 The second SD is calculated as the area under the curve where the CDF of the IS performance is less than that of the OOS performance.


"""


# Todo
#   Get high-quality data that reflects your cause-effect relationship idea, prepare it accordingly, formulate hypotheses and metrics
#   Train models, evaluate feature importance, ensure that there is a consistent signal using the right techniques
#   Build a trading strategy and evaluate “big picture” metrics from the distributional point of view
#   Estimate strategy risks and the probability of failure using the CSCV algorithm and the risk-free rate of return.



class CSCV(object):
    """Combinatorially symmetric cross-validation algorithm.
    Calculate backtesting about overfitting probability distribution and performance degradation.
    Attributes:
        n_bins:A int of CSCV algorithm bin size to control overfitting calculation.Default is 10.
        objective:A function of in sample(is) and out of sample(oos) return benchmark algorithm.Default is lambda r:r.mean().
    """

    def __init__(self, study_dir, n_bins=10, objective=sharpe_ratio):
        self.study_dir = study_dir
        self.n_bins = n_bins
        self.objective = objective

        self.bins_enumeration = [set(x) for x in itr.combinations(np.arange(10), 10 // 2)]

        self.Rs = [pd.Series(dtype=float) for i in range(len(self.bins_enumeration))]
        self.R_bars = [pd.Series(dtype=float) for i in range(len(self.bins_enumeration))]

    def add_daily_returns(self, daily_returns):
        """Add daily_returns in algorithm.
        Args:
          daily_returns: A dataframe of trading daily_returns.
        """

        bin_size = daily_returns.shape[0] // self.n_bins

        bins = [daily_returns.iloc[i * bin_size: (i + 1) * bin_size] for i in range(self.n_bins)]

        warnings.simplefilter(action='ignore', category=FutureWarning)
        logger.info("Splitting into IS and OS Returns")

        for set_id, is_set in enumerate(self.bins_enumeration):
            oos_set = set(range(self.n_bins)) - is_set

            is_returns = pd.concat([bins[i] for i in is_set])
            oos_returns = pd.concat([bins[i] for i in oos_set])

            R = self.objective(is_returns)
            R_bar = self.objective(oos_returns)

            # is_returns_ = is_returns.vbt.returns(freq='d')
            # # oos_returns = oos_returns.vbt.returns(freq='d')
            #
            # logger.info(f'{is_returns = }')
            # logger.info(f'{is_returns_= }')
            # logger.info(f'{is_returns_.total()= }')
            #
            # exit()
            self.Rs[set_id] = self.Rs[set_id].append(R)
            self.R_bars[set_id] = self.R_bars[set_id].append(R_bar)

    @staticmethod
    @ray.remote
    def add_daily_returns_for_remote(objective, bins, n_bins, set_id, is_set):
        oos_set = set(range(n_bins)) - is_set

        is_returns = pd.concat([bins[i] for i in is_set])
        oos_returns = pd.concat([bins[i] for i in oos_set])

        R = objective(is_returns)
        R_bar = objective(oos_returns)

        return [set_id, R, R_bar]

    def remote_add_daily_returns(self, daily_returns):
        """Add daily_returns in algorithm.
                Args:
                  daily_returns: A dataframe of trading daily_returns.
                """

        bin_size = daily_returns.shape[0] // self.n_bins

        bins = [daily_returns.iloc[i * bin_size: (i + 1) * bin_size] for i in range(self.n_bins)]

        warnings.simplefilter(action='ignore', category=FutureWarning)
        from logger_tt import logger
        logger.info(f'{len(self.bins_enumeration) = }')

        result = ray.get(
            [self.add_daily_returns_for_remote.remote(self.objective, bins, self.n_bins, set_id, is_set) for
             set_id, is_set in
             enumerate(self.bins_enumeration)])

        # self.Rs[set_id] = self.Rs[set_id].append(R)
        # self.R_bars[set_id] = self.R_bars[set_id].append(R_bar)
        result = np.array(result)
        result = result.transpose()
        set_id, R, R_bar = result

        # print(R.shape)
        # print(R.size)
        # # exit()
        # return R
        # logger.info(f'{set_id = }')
        # logger.info(f'{R = }')
        # logger.info(f'{R_bar = }')
        # exit()
        #

        #
        #     type(oos_set) = <class 'set'>
        # type(is_returns) = <class 'pandas.core.frame.DataFrame'>
        # type(oos_returns) = <class 'pandas.core.frame.DataFrame'>
        # type(R) = <class 'pandas.core.series.Series'>
        # type(R_bar) = <class 'pandas.core.series.Series'>
        # type(self.Rs) = <class 'list'>
        # type(self.R_bars) = <class 'list'>

    def estimate_overfitting(self, plot=False):
        """Estimate overfitting probability.
        Generate the result on Combinatorially symmetric cross-validation algorithm.
        Display related analysis charts.
        Args:
          plot: A bool of control plot display. Default is False.
        Returns:
          A dict of result include:
          pbo_test: A float of overfitting probability.
          logits: A float of estimated logits of OOS rankings.
          R_n_star: A list of IS performance of th trategies that has the best ranking in IS.
          R_bar_n_star: A list of find the OOS performance of the strategies that has the best ranking in IS.
          dom_df: A dataframe of optimized_IS, non_optimized_OOS data.
        """
        # calculate strategy performance in IS(R_df) and OOS(R_bar_df)

        R_df = pd.DataFrame(self.Rs)
        R_bar_df = pd.DataFrame(self.R_bars)

        # calculate ranking of the strategies
        R_rank_df = R_df.rank(axis=1, ascending=False, method='first')
        R_bar_rank_df = R_bar_df.rank(axis=1, ascending=False, method='first')

        # find the IS performance of the strategies that has the best ranking in IS
        r_star_series = (R_df * (R_rank_df == 1)).unstack().dropna()
        r_star_series = r_star_series[r_star_series != 0].sort_index(level=-1)

        # find the OOS performance of the strategies that has the best ranking in IS
        r_bar_star_series = (R_bar_df * (R_rank_df == 1)).unstack().dropna()
        r_bar_star_series = r_bar_star_series[r_bar_star_series != 0].sort_index(level=-1)

        logger.info(f'{len(r_star_series) = }')
        logger.info(f'{len(r_bar_star_series) = }')

        # find the ranking of strategies which has the best ranking in IS
        r_bar_rank_series = (R_bar_rank_df * (R_rank_df == 1)).unstack().dropna()
        r_bar_rank_series = r_bar_rank_series[r_bar_rank_series != 0].sort_index(level=-1)

        # probability of overfitting

        # estimate logits of OOS rankings
        logits = (1 - ((r_bar_rank_series) / (len(R_df.columns) + 1))).map(lambda p: math.log(p / (1 - p)))
        prob = (logits < 0).sum() / len(logits)

        # stochastic dominance

        # calculate
        if len(r_bar_star_series) != 0:
            y = np.linspace(
                min(r_bar_star_series), max(r_bar_star_series), endpoint=True, num=1000
            )

            # build CDF performance of best candidate in IS
            R_bar_n_star_cdf = ECDF(r_bar_star_series.values)
            optimized = R_bar_n_star_cdf(y)

            # build CDF performance of average candidate in IS
            R_bar_mean_cdf = ECDF(R_bar_df.median(axis=1).values)
            non_optimized = R_bar_mean_cdf(y)

            #
            dom_df = pd.DataFrame(
                dict(optimized_IS=optimized, non_optimized_OOS=non_optimized)
                , index=y)
            dom_df["SD2"] = -(dom_df.non_optimized_OOS - dom_df.optimized_IS).cumsum()
        else:
            dom_df = pd.DataFrame(columns=['optimized_IS', 'non_optimized_OOS', 'SD2'])

        ret = {
            'pbo_test': (logits < 0).sum() / len(logits),
            'logits': logits.to_list(),
            'R_n_star': r_star_series.to_list(),
            'R_bar_n_star': r_bar_star_series.to_list(),
            'dom_df': dom_df,
        }
        print(f'PBO: {round(ret["pbo_test"] * 100)} %')

        if plot:
            # probability distribution
            plt.title('Probability Distribution')
            plt.hist(x=[l for l in ret['logits'] if l > -10000], bins='auto')
            plt.xlabel('Logits')
            plt.ylabel('Frequency')
            plt.savefig(f'{self.study_dir}/probability_distribution.png')
            plt.show()
            #
            # performance degradation
            plt.title('Performance degradation')
            assert len(ret['R_n_star']) == len(ret['R_bar_n_star'])
            plt.scatter(ret['R_n_star'], ret['R_bar_n_star'])
            plt.xlabel('In-sample Performance')
            plt.ylabel('Out-of-sample Performance')
            plt.savefig(f'{self.study_dir}/performance_degradation.png')
            # plt.show()
            #
            # first and second Stochastic dominance
            plt.title('Stochastic dominance')
            ret['dom_df'].plot(secondary_y=['SD2'])
            plt.xlabel('Performance optimized vs non-optimized')
            plt.ylabel('Frequency')
            plt.savefig(f'{self.study_dir}/stochastic_dominance.png')
            plt.show()

        return ret


def test_cscv():
    nstrategy = 10
    nreturns = 4001
    returns = pd.DataFrame({'s' + str(i): np.random.normal(0, 0.02, size=nreturns) for i in range(nstrategy)})
    returns['s1'] += 0.02

    study_dir = '.'
    cscv = CSCV(study_dir)
    cscv.add_daily_returns(returns)
    results = cscv.estimate_overfitting(plot=True)

    assert results['pbo_test'] == 0

    returns = pd.DataFrame({'s' + str(i): np.random.normal(0, 0.02, size=nreturns) for i in range(nstrategy)})

    cscv = CSCV(study_dir)
    cscv.add_daily_returns(returns)
    results = cscv.estimate_overfitting(plot=True)

    assert (results['pbo_test'] > 0) == True


if __name__ == '__main__':
    test_cscv()
