#!/usr/bin/env python3

import warnings

import matplotlib
import numpy as np
import pandas as pd
import ray
from logger_tt import setup_logging, logger

from Overfitting_Genie.CSCV import CSCV
from post_processing_genie_main_ import load_pf_file

# import pandas as pd

matplotlib.use('TkAgg')
warnings.filterwarnings(
    'ignore',
    category=ResourceWarning,
    message='ResourceWarning: unclosed'
)


def test_overfitting():
    nstrategy = 10
    nreturns = 120
    returns_test = pd.DataFrame({'s' + str(i): np.random.normal(0, 0.02, size=nstrategy) for i in range(nreturns)})
    #
    returns = returns_test.__deepcopy__()
    returns['s1'] += 0.02
    test_dir = '.'
    cscv = CSCV(test_dir)
    cscv.add_daily_returns(returns)
    results = cscv.estimate_overfitting(plot=True)
    assert results['pbo_test'] == 0
    #
    returns = returns_test.__deepcopy__()
    cscv = CSCV(test_dir)
    cscv.add_daily_returns(returns)
    results = cscv.estimate_overfitting(plot=True)
    assert results['pbo_test'] > 0


class Overfitting_Genie:

    def __init__(self, study_dir, pickle_files_paths, cscv_nbins=10,
                 cscv_objective=lambda r: r.mean() / (r.std() + 0.0000001) * (365 ** 0.5),
                 plot_bool=False):
        logger.info(f'Running Overfitting Module')

        self.pickle_files_paths = pickle_files_paths
        self.study_dir = study_dir
        self.cscv_nbins = cscv_nbins
        self.cscv_objective = cscv_objective
        self.plot_bool = plot_bool

    # 0.1349206349206349
    # 0.24206349206349206
    @staticmethod
    @ray.remote
    def get_pfs_returns_for_cscv(pf_index, pickle_path, freq='1d'):
        # print(f"PF #{pf_index + 1}")

        pf_minutes = load_pf_file(pickle_path)
        pf_resmapled = pf_minutes.resample(freq)
        returns = pf_resmapled.get_returns()
        #
        mask = returns.keys()
        #
        # mask = returns.keys()[(returns.fillna(0.0).sum() != 0)]
        # returns = returns[mask]
        if not returns.empty:
            # description = returns.describe()
            # p25 = description.loc["25%"]
            # p50 = description.loc["50%"]
            # p75 = description.loc["75%"]
            # mask = returns.keys()[((p25 != 0) & (p50 != 0) & (p75 != 0))]
            # returns = returns[mask]
            if not returns.empty:
                return returns

    def cscv(self, initial_mask):
        # self.pickle_files_paths = self.pickle_files_paths[:1]
        logger.info(f"\nTotal PFs {len(self.pickle_files_paths)}")

        # for pf_index, pickle_path in enumerate(self.pickle_files_paths):
        #     logger.info(f"\nPF #{pf_index + 1} of  {len(self.pickle_files_paths)}")
        #
        #     pf_minutes = load_pf_file(pickle_path)
        #     pf_daily = pf_minutes.resample('1d')
        #     returns = pf_daily.get_returns(chunked=True)
        #     #
        #     mask = returns.keys()
        #     #
        #     # mask = returns.keys()[(returns.fillna(0.0).sum() != 0)]
        #     # returns = returns[mask]
        #     if not returns.empty:
        #         # description = returns.describe()
        #         # p25 = description.loc["25%"]
        #         # p50 = description.loc["50%"]
        #         # p75 = description.loc["75%"]
        #         # mask = returns.keys()[((p25 != 0) & (p50 != 0) & (p75 != 0))]
        #         # returns = returns[mask]
        #         if not returns.empty:
        #             Returns.append(returns)

        Returns = ray.get([self.get_pfs_returns_for_cscv.remote(pf_index, pf_path, freq='w') for pf_index, pf_path in
                           enumerate(self.pickle_files_paths)])

        Returns = pd.concat(Returns, axis=1)
        if initial_mask:
            assert isinstance(initial_mask, object)
            Returns = Returns[initial_mask]
        # should we only use filtered data

        # Dont use strategies that did not place any trades
        Returns = Returns - 10e-100
        # Returns.fillna(value=Returns.mean(), inplace=True)
        cscv = CSCV(self.study_dir)
        # cscv.add_daily_returns(Returns)

        # n_times=2
        # avg_time = 0
        # for i in range(n_times):
        #     start = perf_counter()
        #     cscv.add_daily_returns(Returns)
        #     time_to_compute = perf_counter() - start
        #     avg_time=(avg_time+time_to_compute)/2
        # print(f'Avg Time for Original = {avg_time}')
        #
        # avg_time = 0
        # for i in range(n_times):
        #     start = perf_counter()
        #     cscv.add_daily_returns_(Returns)
        #     time_to_compute = perf_counter() - start
        #     avg_time = (avg_time + time_to_compute) / 2
        # print(f'Avg Time for NEW = {avg_time}')
        from time import perf_counter

        start = perf_counter()
        cscv.add_daily_returns(Returns)
        logger.info(f'time to finish orig {perf_counter() - start}')

        # start = perf_counter()
        # r1 = cscv.remote_add_daily_returns(Returns)
        # logger.info(f'time to finish new {perf_counter() - start}')
        #
        # print(f'{np.array(r).size = }')
        # print(f'{r1.size = }')
        # # assert r == r1
        # exit()
        cscv_result = cscv.estimate_overfitting(plot=self.plot_bool)
        logger.info(f'PBO: {round(cscv_result["pbo_test"] * 100)} %')
        # print(result["dom_df"].head())
        study_overfitting_output_path = f'{self.study_dir}/cscv_report.csv'
        # if path.exists(study_overfitting_output_path):
        #     split_path = study_overfitting_output_path.rsplit('.', 1)
        #     study_overfitting_output_path = next_path(f'{split_path[0]}_%s.{split_path[1]}')
        logger.info(f'Output File -> {study_overfitting_output_path}')

        return cscv_result


if __name__ == "__main__":
    setup_logging(full_context=1)
    logger.info("Running Test on Overfitting Main")
    test_overfitting()
