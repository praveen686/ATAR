#!/usr/bin/env python3
import argparse
from os import path

from logger_tt import logger

# STUDY_DIRECTORY_DEFAULT = "/home/ruben/PycharmProjects/mini_Genie/Studies/Study_mmt_debug"
# STUDY_DIRECTORY_DEFAULT = "/home/ruben/PycharmProjects/mini_Genie/Studies/Study_mmt_USA30_debug"
# STUDY_DIRECTORY_DEFAULT = "/home/ruben/PycharmProjects/mini_Genie/Studies/Study_mmt_USA30_update_66M"
# STUDY_DIRECTORY_DEFAULT = "/home/ruben/PycharmProjects/mini_Genie/Studies/Study_mmt_USA30_update_test_66M"
# STUDY_DIRECTORY_DEFAULT = "/home/ruben/PycharmProjects/mini_Genie/Studies/Study_mmt_USA100_66M"
# STUDY_DIRECTORY_DEFAULT = "/home/ruben/PycharmProjects/mini_Genie/Studies/Study_mmt_USA30_66M"
# STUDY_DIRECTORY_DEFAULT = "/home/ruben/PycharmProjects/mini_Genie/Studies/Study_mmt_USD30_1.2B_part_2"
# STUDY_DIRECTORY_DEFAULT = "/home/ruben/PycharmProjects/mini_Genie/Studies/Study_mmt_USD100_1.2B"
# STUDY_DIRECTORY_DEFAULT = "/home/ruben/PycharmProjects/mini_Genie/Studies/Study_mmt_TSLA_Expo_Optimization_03042022_07262022"

STUDY_DIRECTORY_DEFAULT = None
OVERFITTING_BOOL_DEFAULT = False
FILTERS_BOOL_DEFAULT = False
ANALYSIS_BOOL_DEFAULT = False
# ACTIONS_PATH_DEFAULT = False
ACTIONS_JSON = None

SETTINGS = dict(
    Leverage=100,  # todo right now used to filter out less and more
    min_strats_per_batch=1,
    N_STEP_INCREASE=1
)
REQUIREMENTS = dict(
    Min_total_trades=1,
    Profit_factor=1.0,
    #
    Expectancy=0.01,
    Daily_drawdown=0.05,
    Total_drawdown=0.1,
    Profit_for_month=0.1,
    Total_Win_Rate=0.03
)


class run_time_handler:
    """


    Args:
         ():
         ():

    Attributes:
         ():
         ():

    Note:

    """

    def __init__(self, run_function,
                 STUDY_DIRECTORY_DEFAULT=STUDY_DIRECTORY_DEFAULT,
                 ACTIONS_JSON=ACTIONS_JSON,
                 OVERFITTING_BOOL_DEFAULT=OVERFITTING_BOOL_DEFAULT,
                 FILTERS_BOOL_DEFAULT=FILTERS_BOOL_DEFAULT,
                 ANALYSIS_BOOL_DEFAULT=ANALYSIS_BOOL_DEFAULT,
                 ):
        """Constructor for run_time_handler"""
        #
        parser = argparse.ArgumentParser(description="Help for mini-Genie Trader")
        general_group = parser.add_argument_group(description="Basic Usage")
        expand_study_group = parser.add_argument_group(description="Expand Study Usage")
        #
        general_group.add_argument("-s", help="Path to Study Folder", dest="study_dir",
                                   action='store',
                                   default=STUDY_DIRECTORY_DEFAULT)
        general_group.add_argument("--actions", help="Path to Study Folder", dest="actions",
                                   action='store',
                                   default=ACTIONS_JSON)
        general_group.add_argument("-o", help="Runs overfitting module", dest="overfitting_bool",
                                   action='store_true',
                                   default=OVERFITTING_BOOL_DEFAULT)
        general_group.add_argument("-f", help="Runs filters module", dest="filters_bool",
                                   action='store_true',
                                   default=FILTERS_BOOL_DEFAULT)
        general_group.add_argument("-a", help="Runs analysis module", dest="analysis_bool",
                                   action='store_true',
                                   default=ANALYSIS_BOOL_DEFAULT)

        self.parser = parser
        self.parser.set_defaults(func=run_function)
        self.args = self.parser.parse_args()
        self.args.requirements = {}
        #
        if self.args.actions:
            # self.args.actions = eval(self.args.actions)
            self.args.study_dir = self.args.actions["study_path"]

            if self.args.filters_bool:
                for key in REQUIREMENTS.keys():
                    self.args.requirements[key] = self.args.actions[key]

        if not self.args.study_dir:
            logger.error(f'No study dir passed')
            exit()
        #
        if not any([vars(self.args)[i] for i in vars(self.args) if i not in ['func', 'study_dir']]):
            if path.exists(self.args.study_dir):
                logger.info(f'Found directory {self.args.study_dir}')
            logger.warning("No action requested, exiting ...")
            parser.print_help()
            exit()
        else:
            self.args.settings = SETTINGS
            self.args.requirements = self.args.requirements or REQUIREMENTS
            #
            from Modules.Utils import fetch_pf_files_paths
            self.args.pickle_files_paths = fetch_pf_files_paths(self.args.study_dir)

            # Order the files by size from highest to lowest
            self.args.pickle_files_paths.sort(key=lambda x: path.getsize(x), reverse=False)
            #

    @staticmethod
    def load_module_from_path(filename, object_name=None):

        module_path = filename.rsplit('.', 1)[0]
        module = module_path.replace("/", ".")

        from importlib import import_module
        mod = import_module(module)

        ###
        # import importlib.util
        # import sys
        # from os import path
        # #
        # logger.info(f"Loading Run_Time_Settings from file {filename}")
        # module_name = path.basename(module_path)
        # #
        # spec = importlib.util.spec_from_file_location(module_name, filename)
        # mod = importlib.util.module_from_spec(spec)
        # sys.modules[module_name] = mod
        # spec.loader.exec_module(mod)
        ###

        if object_name is not None:
            met = getattr(mod, object_name)
            return met
        else:
            return mod

    def call_run_function(self):
        self.args.func(self.args)
