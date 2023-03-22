#!/usr/bin/env python3


import ray

from post_processing_genie_source.Run_Time_Handler.vbtmetricsdictionary import vbtmetricsdictionary
from logger_tt import logger # noqa: F401

#
# def compute_metrics(returns):
#     """
#     Computes a variety of financial asset metrics
#
#     Parameters
#     ----------
#     returns : pd.Series
#         Daily returns of the asset
#
#     Returns
#     -------
#     all_metrics : pd.DataFrame
#         Contains all metrics for the asset
#     """
#
#     total_return = ((returns + 1).prod() - 1) * 100
#     total_trades = len(returns)
#     profit_factor = np.sum(returns[returns > 0]) / np.abs(np.sum(returns[returns < 0]))
#     max_drawdown = (np.maximum.accumulate(returns + 1) - (returns + 1)).max()
#     win_rate = np.sum(returns > 0) / total_trades
#     sharpe_ratio = np.mean(returns) / np.std(returns)
#     omega_ratio = -sharpe_ratio * np.sqrt(total_trades) + np.sum(np.minimum(returns, 0)) / total_trades
#     sortino_ratio = np.mean(returns) / np.std(returns[returns < 0])
#     max_gross_exposure = np.abs(returns).max()
#     best_trade = np.max(returns)
#     worst_trade = np.min(returns)
#     avg_winning_trade = np.mean(returns[returns > 0])
#     avg_losing_trade = np.mean(returns[returns < 0])
#     expectancy = win_rate * avg_winning_trade - (1 - win_rate) * avg_losing_trade
#
#     all_metrics = pd.DataFrame(
#         {'Total Return [%]': total_return, 'Total Trades': total_trades, 'Profit Factor': profit_factor,
#          'Max Drawdown [%]': max_drawdown, 'Win Rate [%]': win_rate, 'Sharpe Ratio': sharpe_ratio,
#          'Omega Ratio': omega_ratio, 'Sortino Ratio': sortino_ratio, 'Max Gross Exposure [%]': max_gross_exposure,
#          'Best Trade [%]': best_trade, 'Worst Trade [%]': worst_trade, 'Avg Winning Trade [%]': avg_winning_trade,
#          'Avg Losing Trade [%]': avg_losing_trade, 'Expectancy': expectancy})
#
#     return all_metrics
#
#
# def test():
#     ...
#
#

#
#
# def load_pf_files(study_dir):
#     pf_pickles_paths = fetch_pf_files_paths(study_dir)
#
#     return [vbt.Portfolio.load(pf_pickle) for pf_pickle in pf_pickles_paths]
#
#
# @ray.remote
# def reconstruct_daily_returns_remote(portfolio):
#     result = portfolio.get_returns()
#     gc.collect()
#     return result
#     # return portfolio.get_daily_returns()
#
#
# def reconstruct_daily_returns(portfolio):
#     result = portfolio.get_returns()
#     gc.collect()
#     return result
#     # return portfolio.get_daily_returns()
#
#
# def user_passed_filter():
#     ...
#     # > Load File (todo could be pickle maybe) < #
#
#     # > Go through flags < #
#     #       Min Trades (Filter)
#     #       Equity Curve Divergance (Filter)
#     #       Classic Max (Filter)
#     #       Classic Min (Filter)
#     #       Symmetric (Filter)
#     #       Classic Ascending or Descending (Reorganization)
#     #       Equity Curve Ordering (Reorganization)
#     #       Top N data points
#
#     # > Create Copy File named using the filters used here, if one already exists create a file with another number < #
#
#
# def apply_pf_function(frequency, pf_daily, pf_weekly, pf_monthly, metric_function, call=False):
#     if frequency == 'd':
#         pf_obj = pf_daily
#     elif frequency == 'w':
#         pf_obj = pf_weekly
#     elif frequency == 'M':
#         pf_obj_ = pf_monthly
#     else:
#         pf_obj = None
#         logger.exception(f'Frequency {frequency} is not accepted, choose d,w, or M')
#         exit()
#     #
#     if call:
#         pf_obj_metric = metric_function
#     else:
#         pf_obj_metric = metric_function
#
#     mask = pf_obj_metric[pf_obj_metric > 0].index
#
#     if len(mask) > 0:
#         pf_daily = pf_daily[mask]
#         pf_weekly = pf_weekly[mask]
#         pf_monthly = pf_monthly[mask]
#     else:
#         pf_daily, pf_weekly, pf_monthly = None, None, None
#     #
#     return pf_daily, pf_weekly, pf_monthly
#
#
# def cscv(returns, n_trials=100):
#     """
#     Calculates the probability of overfitting a backtest using
#     David H. Bailey's CSCV algorithm.
#
#     Parameters
#     ----------
#     returns : pd.Series or np.array
#         Asset financial returns series.
#     n_trials : int, optional
#         Number of simulations to run. The default is 10000.
#
#     Returns
#     -------
#     float
#         Probability of overfitting the backtest.
#
#     """
#
#     # returns = pd.DataFrame(np.random.normal(0, 1, 100) * 0.01 * 0.01 *np.random.randint(100))
#     # returns.columns = ['Returns']
#
#     # Calculate number of periods in the return series
#     # T = len(returns)
#     T, n_strats = len(returns), len(returns.columns)
#
#     # Initialize list to hold results
#     results = []
#
#     n_trials = 1
#     # Loop through each trialzz
#     for i in range(n_trials):
#         print(f'Trial #{i + 1} out of {n_trials}')
#         # Randomly split the return series into two halves
#         split = np.random.randint(np.ceil(T * 0.20), np.floor(T * 0.80))
#         train = returns[:split]
#         test = returns[split:]
#
#         # Calculate Sharpe ratios for training and testing sets
#         train_sharpe = np.sqrt(252) * np.mean(train) / np.std(train)
#         test_sharpe = np.sqrt(252) * np.mean(test) / np.std(test)
#
#         inverse_train = 1 / len(train)
#         inverse_test = 1 / len(test)
#
#         z = (train_sharpe - test_sharpe) / np.sqrt(inverse_train + inverse_test)
#
#         # Append result to list
#         a = z
#         a = sum([1 for x in a if x >= 2]) / n_trials
#         # a = a.mean()
#         # po = a / n_strats
#         po = a
#         results.append(po)
#         # PBO = np.mean([x for x in results if x != 0])
#         PBO = np.mean(results)
#         print(f'{PBO  = }')
#
#     print()
#     print()
#     print(f'{PBO = }')
#
#     from sklearn.model_selection import cross_val_score
#
#     def overfitting_probability(returns, model=None):
#         twenty = np.ceil(T * 0.20)
#         eighty = np.floor(T * 0.80)
#         split = np.random.randint(twenty, eighty)
#         # train = returns[twenty:eighty]
#         # test = returns[twenty:eighty]
#         scores = cross_val_score(model, returns, returns, cv=5)
#         return 1 - scores.mean()
#
#     from sklearn import linear_model
#     lasso_model = linear_model.Lasso()
#     PBO_ = overfitting_probability(returns, lasso_model)
#     print(f'{PBO_ = }')
#     exit()
#
#     # for i, x in enumerate(results):
#     #     if isinstance(x,np.inf) or isinstance(x,-np.inf):
#     #         results[i] = None
#     # results = np.nan_to_num(results, neginf=None, posinf=None)
#
#     # Calculate probability of overfitting from list of z-scores
#     # p_overfit = sum([1 for x in results if x >= 2]) / n_trials
#     # p_overfit = sum([1 for x in results if x >= 2]) / n_trials
#     p_overfit = PBO
#
#     return p_overfit


# if len(mask) > 0:
#     pf_daily = pf_daily[mask]
#     pf_weekly = pf_weekly[mask]
#     pf_monthly = pf_monthly[mask]
# max_winning_streak = (
#             'max_winning_streak',
#             dict(
#                 title='Max Winning Streak',
#                 calc_func=lambda self, group_by:
#                 self.get_trades(group_by=group_by).winning_streak.max()
#             )
#         )
# # pf_monthly_stats = pf_monthly.stats(metrics=max_winning_streak, agg_func=None)
# pf_monthly_stats = pf_monthly.stats(tags=['trades'], agg_func=None)


class Post_Processing_Genie:
    def __init__(self, runtime_parameters):
        self.return_dict = {}
        self.study_dir = runtime_parameters.study_dir
        self.pickle_files_paths = runtime_parameters.pickle_files_paths
        self.requirements = runtime_parameters.requirements
        self.settings = runtime_parameters.settings
        self.metric_call_names = runtime_parameters.metric_call_names

    @staticmethod
    def flatten_dict(df):
        import flatdict
        return flatdict.FlatDict(df, delimiter='.')

    def _get_return_dict_initial_mask_mask(self, flat_key_name):
        ###
        # df = self.return_dict["Filters"]["Default"]
        df = self.return_dict
        df = self.flatten_dict(df)
        df = df[flat_key_name]
        columns = df.columns
        column = "symbol"
        column_index = columns.get_loc(column)
        #
        result = df[df.columns[:column_index + 1]]
        #
        # print(f'{[tuple(i) for i in result.values] = }')
        # exit()
        if not result.empty:
            return [tuple(i) for i in result.values]
        else:
            return None

        ###

    def call_overfitting(self, actions_dict=None):
        """Overfitting Module"""
        if actions_dict is None or actions_dict == 'Default':
            from Overfitting_Genie.overfitting_main import Overfitting_Genie
            overfitting_obj = Overfitting_Genie(self.study_dir, self.pickle_files_paths, cscv_nbins=10,
                                                # cscv_objective=lambda r: r.mean() / (r.std() + 0.0000001) * (
                                                #         365 ** 0.5),
                                                cscv_objective=lambda r: r.mean() / (r.std() + 0.0000001) * (
                                                        252 ** 0.5),
                                                plot_bool=False)

            self.return_dict["Overfitting"] = {
                'Default': overfitting_obj.cscv(initial_mask=None)}
            # 'Default': overfitting_obj.cscv(initial_mask=self._get_return_dict_initial_mask_mask("Filters.Default"))}
        else:
            # Parse actions_dict
            # prepare sequence
            # call actions
            ...
        #

        return self.return_dict["Overfitting"]

    #
    def call_filters(self,
                     actions_dict=None):  # todo actions_dict is meant to accept a dict with details of sequence of calls to filters, needs a parser
        from post_processing_genie_source.Filters_Genie.filters_genie_main import Filters_Genie
        filter_obj = Filters_Genie(self.study_dir, self.pickle_files_paths, self.requirements, self.settings,
                                   self.metric_call_names)

        if actions_dict is None or actions_dict == 'Default':
            self.return_dict["Filters"] = {'Default': filter_obj.quick_filters()}
        else:
            # Parse actions_dict
            # prepare sequence
            # call actions
            ...
        #
        return self.return_dict["Filters"]

    def call_analyser(self, actions_dict=None):
        ...


def call_post_processing_genie(args):  # for overfitting, not for mini_genie
    """"""
    logger.info(f'Post Analysing {args.study_dir}')

    # todo program actions
    #   e.g.
    #         args.actions = dict(
    #             mini_Genie=dict(
    #                 # 1 - Compute Genie Pick Backtests
    #                 actions=None  # Default = 'gp'
    #             ),
    #             Most_Important_Parameters=dict(
    #                 # 2 - Compute what are the most important (agg mean) parameters to optimize (save for step 11)
    #                 actions=['mip-agg']  # Default = 'mip'
    #             ),
    #             Overfitting=dict(
    #                 # 3 - Compute Combinatorially Symmetric Cross Validation
    #                 #   a.  PBO threshold
    #                 #   b. 'Probability Distribution'
    #                 #   c. 'Performance degradation'
    #                 #   d. 'Stochastic dominance' (First and Second)
    #                 #   e. 'Performance optimized vs non-optimized' Filter
    #                 actions=None  # Default = 'cscv'
    #             ),
    #             Neightbors=dict(
    #                 # 4 - Compute 20 closest neightbors per strategy (rolling)
    #                 actions=['dist-20']  # Default = 'd' *distance
    #             ),
    #             Filters=dict(
    #                 # 5 - Delete those strategies with no neighbors
    #                 # 6 - Pass the strategies through filters
    #                 actions=['del-loners', 'qf']  # Default = 'qf * quick-filters
    #             ),
    #             Data_Manager=dict(
    #                 # 7 - Split the data for each strategy in partition (3 months per partition)
    #                 # 8 - Remove first month from partition 1 and last month from partition 2
    #                 actions=['del-f-m', 'del-l-m', 'split-2']  # Default 'nothing'
    #             ),
    #             Filters_1=dict(
    #                 # 9 - Pass the partitions through filters
    #                 # 10 - Delete those strategies that do not have neightboors in the other partition
    #                 actions=['part-qs', 'part-del-loners']  # Default = 'qf * quick-filters
    #             ),
    #             #
    #             # 11 - Repeat steps 1-10 ...
    #             mini_Genie_1=dict(
    #                 actions=['gp-refine']  # Default = 'gp'
    #             ),
    #             # ...
    #             # *Steps 2-10
    #             # ...
    #             mini_Genie_2=dict(
    #                 # 13 - Optimize a subspace using Search Algorythm (e.g. Genetic or TPE Algorythm)
    #                 actions=['gp-sa-gen']  # Default = 'gp'
    #             ),
    #             Data_Manager_1=dict(
    #                 # 13 - Optimize a subspace using Search Algorythm (e.g. Genetic or TPE Algorythm)
    #                 actions=['send-telegram-dasan']  # Default = 'nothing'
    #             ),
    #         )

    VBT_METRICS = [
        'Total Return [%]',
        'Total Trades',
        'Profit Factor',
        'Max Drawdown [%]',
        'Win Rate [%]',
        'Sharpe Ratio',
        'Omega Ratio',
        'Sortino Ratio',
        'Max Gross Exposure [%]',
        'Best Trade [%]',
        'Worst Trade [%]',
        'Avg Winning Trade [%]',
        'Avg Losing Trade [%]',
        'Expectancy',
    ]
    # 'Total Return [%]', 'Total Trades',  'Profit Factor', 'Max Drawdown [%]', 'Win Rate [%]','Sharpe Ratio', 'Omega Ratio','Sortino Ratio','Max Gross Exposure [%]','Avg Winning Trade [%]','Avg Losing Trade [%]','Expectancy',
    args.metric_call_names = [vbtmetricsdictionary[string] for string in VBT_METRICS]

    "''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''"
    post_processing_obj = Post_Processing_Genie(args)

    print(f'{args.actions = }')

    if args.overfitting_bool:
        post_processing_obj.call_overfitting()
    if args.filters_bool:
        post_processing_obj.call_filters()
    #
    if args.analysis_bool:
        post_processing_obj.call_analyser()



if __name__ == "__main__":
    from logger_tt import setup_logging, logger
    from Run_Time_Handler.run_time_handler import run_time_handler

    #
    setup_logging(full_context=1)
    #
    run_time_handler = run_time_handler(run_function=call_post_processing_genie)

    ray.init()
    run_time_handler.call_run_function()
