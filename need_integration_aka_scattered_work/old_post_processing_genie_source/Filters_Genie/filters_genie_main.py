#!/usr/bin/env python3
# noinspection PyUnresolvedReferences
import gc
from os import path, remove

import numpy as np
import pandas as pd
# from Utilities.utils import load_pf_file, next_path, save_record_to_file
from logger_tt import logger

from Modules.Utils import next_path, save_record_to_file
from vectorbtpro import Portfolio


class Filters_Genie:
    def __init__(self, study_dir, pickle_files_paths, requirements, settings, metric_call_names):

        self.study_dir = study_dir
        self.pickle_files_paths = pickle_files_paths
        self.requirements = requirements
        self.settings = settings
        self.metric_call_names = metric_call_names
        ...

        if not self.pickle_files_paths:
            logger.error(
                f'Paths to pickles found no porfolios for study {self.study_dir}, assure the correct study path was used')
            exit()

    def rescale_requirements(self, req, sett):
        for keynames in req:
            if keynames not in ["Min_total_trades", "Profit_factor", "Total_Win_Rate",
                                "Total_drawdown"  # fixme
                                ]:
                req[keynames] = req[keynames] / sett["Leverage"]

    def filter_unmasked(self, mask, pf_index, pf_daily, pf_weekly, pf_monthly, metric=None):
        if len(mask) < 1:
            logger.warning(f'Portfolio with index {pf_index} filtered completely out by {metric} filter')
            return None, None, None

        pf_daily = pf_daily[mask]
        pf_weekly = pf_weekly[mask]
        pf_monthly = pf_monthly[mask]
        logger.info(f'After {metric} filter -> {pf_monthly.wrapper.shape[1]} strategies')
        return pf_daily, pf_weekly, pf_monthly

    def check_if_continue(self, pf, storage_array, min_strats):
        if pf is None:
            #
            if not len(storage_array) > 1:
                mean_ = np.mean(storage_array)
                if mean_ < min_strats:
                    return storage_array, False
            #
            storage_array.append(0)
            return storage_array, None
        else:
            return storage_array, True

    def quick_filters(self):
        metrics_output_path = f'{self.study_dir}/portfolio_stats.csv'
        if path.exists(metrics_output_path):
            split_path = metrics_output_path.rsplit('.', 1)
            metrics_output_path = next_path(f'{split_path[0]}_%s.{split_path[1]}')

        logger.info(f'Output File -> {metrics_output_path}')

        min_strats_per_batch = self.settings["min_strats_per_batch"]
        N_STEP_INCREASE = self.settings["N_STEP_INCREASE"]
        chunked_type = False

        continue_ = False

        while continue_ is False:
            self.rescale_requirements(self.requirements, self.settings)
            #
            if path.exists(metrics_output_path): remove(metrics_output_path)
            #
            from time import perf_counter
            start = perf_counter()
            pfs_len = len(self.pickle_files_paths)
            successful_strats = []
            for pf_index, pickle_path in enumerate(self.pickle_files_paths):
                gc.collect()
                logger.info(f"\n")
                logger.info(f"PF #{pf_index + 1} of  {pfs_len}")

                # > Load current pc < #
                # pf_minutes = load_pf_file(pickle_path)
                pf_minutes = Portfolio.load(pickle_path)
                # a = [col for col in pf_minutes.wrapper.columns if 'XAUUSD' in col] # select only XAUUSD
                # pf_minutes = pf_minutes[a]  # select only XAUUSD mask

                # > Resample < #
                pf_daily = pf_minutes.resample('1d')
                pf_weekly = pf_minutes.resample('1w')
                pf_monthly = pf_minutes.resample('1M')
                #
                logger.info(f'Starting with {pf_monthly.wrapper.shape[1]} strategies')
                #   #   #   #   #   #   #   #   #   #

                # > Remove those combinations with zero/negative returns< #
                pf_total_returns = pf_monthly.get_total_return(chunked=chunked_type)
                mask = pf_total_returns[pf_total_returns > 0].index

                #
                pf_daily, pf_weekly, pf_monthly = self.filter_unmasked(mask, pf_index, pf_daily, pf_weekly, pf_monthly,
                                                                       metric="Profitable")

                successful_strats, continue_ = self.check_if_continue(pf_monthly, successful_strats,
                                                                      min_strats_per_batch)

                if continue_ is None:
                    continue

                # # > Filter Unwanted Parameter Combinations < #
                # names = mask.names
                # w1_index = names.index("custom_ema_1_windows")
                # w2_index = names.index("custom_ema_2_windows")
                # mask = [col for col in mask if col[w1_index] < col[w2_index]]
                # #
                # w1_index = names.index("custom_take_profit_points")
                # w2_index = names.index("custom_stop_loss_points")
                # mask = [col for col in mask if abs(col[w1_index]) >= abs(col[w2_index])]
                # #
                # pf_daily, pf_weekly, pf_monthly = self.filter_unmasked(mask, pf_index, pf_daily, pf_weekly, pf_monthly,
                #                                                   metric="Parameters")

                # # Todo playing with ai
                #
                # returns = pf_daily.get_returns(chunked=chunked_type)
                # for col in returns.columns:
                #     ob = FinancialAssetMetrics(returns[col])
                #     logger.info(ob.to_dataframe()['Sharpe Ratio'].dropna())
                #     exit()
                # # logger.info(f'{returns = }')
                # # logger.info(f'{compute_metrics(returns) = }')
                # # logger.info(f'{pf_total_returns = }')
                # #
                # exit()

                # > Initial Filters < #
                #   Compute Drawdown
                pf_daily_drawdown = pf_daily.get_drawdown(chunked=chunked_type)
                pf_max_drawdown = pf_daily.get_max_drawdown()
                mask = pf_max_drawdown[
                    ~(-pf_max_drawdown > self.requirements["Total_drawdown"])].index.tolist()
                pf_daily_drawdown = pf_daily_drawdown[mask]
                mask = [col for col in pf_daily_drawdown.columns if
                        ~(pf_daily_drawdown[col] > self.requirements["Daily_drawdown"]).any() and ~(
                                pf_daily_drawdown[col].sum() == 0.0)]
                #
                pf_daily, pf_weekly, pf_monthly = self.filter_unmasked(mask, pf_index, pf_daily, pf_weekly, pf_monthly,
                                                                       metric="Daily_drawdown and Total_drawdown")

                successful_strats, continue_ = self.check_if_continue(pf_monthly, successful_strats,
                                                                      min_strats_per_batch)
                if continue_ is None:
                    continue
                elif continue_ is False:
                    logger.warning("Adjusting Leverage")
                    self.settings["Leverage"] = self.settings["Leverage"] + N_STEP_INCREASE
                    break

                #   Compute Profits
                pf_monthly_returns = pf_monthly.get_returns()
                # pf_monthly_returns = pf_monthly_returns.vbt.sort_index().shift(1, freq ='MS')

                mask = [col for col in pf_monthly_returns.keys()
                        if (pf_monthly_returns[col] >= self.requirements[
                        "Profit_for_month"]).sum() >= np.ceil((pf_monthly_returns.shape[0] - 1) / 2)]
                #
                pf_daily, pf_weekly, pf_monthly = self.filter_unmasked(mask, pf_index, pf_daily, pf_weekly, pf_monthly,
                                                                       metric="Profit_for_month")

                successful_strats, continue_ = self.check_if_continue(pf_monthly, successful_strats,
                                                                      min_strats_per_batch)
                if continue_ is None:
                    continue
                elif continue_ is False:
                    logger.warning("Adjusting Leverage")
                    self.settings["Leverage"] = self.settings["Leverage"] + N_STEP_INCREASE
                    break

                #
                # > Compute All Stats < #

                # > Second Filters < #
                pf_monthly_trades = pf_monthly.get_trades(chunked=chunked_type)
                # pf_total_profit = pf_monthly_trades.pnl.sum()

                #   Min Trades
                pf_total_trades = pf_monthly_trades[mask].count()
                mask = [col for col in pf_total_trades.keys()
                        if (pf_total_trades[col] >= self.requirements["Min_total_trades"])]
                logger.info(f'{pf_total_trades.max() = }')
                #
                pf_daily, pf_weekly, pf_monthly = self.filter_unmasked(mask, pf_index, pf_daily, pf_weekly, pf_monthly,
                                                                       metric="Min_total_trades")

                successful_strats, continue_ = self.check_if_continue(pf_monthly, successful_strats,
                                                                      min_strats_per_batch)
                if continue_ is None:
                    continue
                elif continue_ is False:
                    logger.warning("Adjusting Leverage")
                    self.settings["Leverage"] = self.settings["Leverage"] + N_STEP_INCREASE
                    break

                # #   Expected
                # pf_total_profit = pf_total_profit[mask]
                # pf_total_trades = pf_total_trades[mask]
                # pf_expectancy = pf_total_profit[mask] / pf_total_trades[mask]
                # pf_expected_adj_return = pf_expectancy / self.settings["Init_cash"]
                #
                # mask = [col for col in pf_expected_adj_return.keys()
                #         if (pf_expected_adj_return[col] >= self.requirements["Expectancy"])]
                # #
                # pf_daily, pf_weekly, pf_monthly = self.filter_unmasked(mask, pf_index, pf_daily, pf_weekly, pf_monthly,
                #                                                        metric="Expectancy")
                #
                # successful_strats, continue_ = self.check_if_continue(pf_monthly, successful_strats,
                #                                                       min_strats_per_batch)
                # if continue_ is None:
                #     continue
                # elif continue_ is False:
                #     logger.warning("Adjusting Leverage")
                #     self.settings["Leverage"] = self.settings["Leverage"] + N_STEP_INCREASE
                #     break

                #   Profit Factor
                pf_monthly_profit_factor = pf_monthly_trades[mask].get_profit_factor(chunked=chunked_type)

                mask = [col for col in pf_monthly_profit_factor.keys()
                        if (pf_monthly_profit_factor[col] >= self.requirements["Profit_factor"])]
                #
                pf_daily, pf_weekly, pf_monthly = self.filter_unmasked(mask, pf_index, pf_daily, pf_weekly, pf_monthly,
                                                                       metric="Profit_factor")

                successful_strats, continue_ = self.check_if_continue(pf_monthly, successful_strats,
                                                                      min_strats_per_batch)
                if continue_ is None:
                    continue
                elif continue_ is False:
                    logger.warning("Adjusting Leverage")
                    self.settings["Leverage"] = self.settings["Leverage"] + N_STEP_INCREASE
                    break

                #  Total Win Ratio
                total_win_rate = pf_monthly_trades[mask].get_win_rate(chunked=chunked_type)
                a = [col for col in total_win_rate.keys()
                     if (total_win_rate[col] < self.requirements["Total_Win_Rate"])]
                #
                mask = [col for col in total_win_rate.keys()
                        if (total_win_rate[col] >= self.requirements["Total_Win_Rate"])]
                #
                pf_daily, pf_weekly, pf_monthly = self.filter_unmasked(mask, pf_index, pf_daily, pf_weekly, pf_monthly,
                                                                       metric="Total_Win_Rate")

                successful_strats, continue_ = self.check_if_continue(pf_monthly, successful_strats,
                                                                      min_strats_per_batch)
                if continue_ is None:
                    continue
                elif continue_ is False:
                    logger.warning("Adjusting Leverage")
                    self.settings["Leverage"] = self.settings["Leverage"] + N_STEP_INCREASE
                    break

                # outlier_loss_ratio()
                # outlier_win_ratio()

                # > Compute Stats < #
                if pf_daily.wrapper.shape[1] > 0:
                    logger.info(f'{pf_daily.wrapper.shape[1]} strategies passed in Pf #{pf_index}')

                pf_stats = pf_daily.stats(metrics=self.metric_call_names, agg_func=None)

                # > Create/Append to file < #
                logger.info(f"Saving metrics to {metrics_output_path}\n")
                save_record_to_file(pf_stats, metrics_output_path, write_mode="a")

                successful_strats.append(pf_daily.wrapper.shape[1])

                # pf_max_drawdown = pf_daily[mask].get_max_drawdown()
                # logger.info(pf_max_drawdown)

                gc.collect()

        logger.info(f'Time = {perf_counter() - start}')
        # logger.info(
        #     f'The probability of Backtest Overfitting {np.mean(pbo_list) * 100}%'
        # )
        # > Load File (todo could be pickle maybe) < #

        # > Sort Base on expectancy < #
        if path.exists(metrics_output_path):
            filtered_pf_stats_loaded = pd.read_csv(metrics_output_path)
            #
            # filtered_pf_stats_loaded["Expectancy"] = (filtered_pf_stats_loaded["Expectancy"] / self.settings[
            #     "Init_cash"]) * 100
            #
            # filtered_pf_stats_loaded["Total Profit"] = filtered_pf_stats_loaded["Total Return [%]"] * self.settings["Init_cash"] / 100
            #
            filtered_pf_stats_loaded = filtered_pf_stats_loaded.sort_values("Expectancy", ascending=False)
            save_record_to_file(filtered_pf_stats_loaded, metrics_output_path, write_mode="w")

            # > Sort Base on eq < #
            #   Equity Curve

            return filtered_pf_stats_loaded
