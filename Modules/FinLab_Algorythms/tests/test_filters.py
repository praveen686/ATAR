"""
Test various filters.
"""

import unittest
import os
import numpy as np
import pandas as pd

from Modules.FinLab_Algorythms.timeseries_algorythms.timeseries_filters import cusum_filter, z_score_filter


class TestCUSUMFilter(unittest.TestCase):
    """
    Tests regarding the CUSUM filter.
    """

    def setUp(self):
        """
        Set the file path for the sample dollar bars data.
        """
        project_path = os.path.dirname(__file__)
        self.path = project_path + '/test_data/dollar_bar_sample.csv'
        self.data = pd.read_csv(self.path, index_col='date_time')
        self.data.index = pd.to_datetime(self.data.index)

    def test_cusum_filter(self):
        """
        Assert that the CUSUM filter works as expected.
        Checks that all the events generated by different threshold values meet the requirements of the filter.
        """

        # Check all events for various threshold levels
        for threshold in [0.005, 0.007, 0.01, 0.015, 0.02, 0.03, 0.04]:
            for timestamp in [True, False]:

                cusum_events = cusum_filter(self.data['close'], threshold=threshold, time_stamps=timestamp)

                for i in range(1, len(cusum_events)):
                    event_1 = self.data.index.get_loc(cusum_events[i - 1])
                    event_2 = self.data.index.get_loc(cusum_events[i])

                    date_range = self.data.iloc[event_1:event_2 + 1]['close']
                    last = np.log(date_range[-1])
                    minimum = np.log(date_range.min())
                    maximum = np.log(date_range.max())

                    # Calculate CUSUM
                    spos = last - minimum
                    sneg = last - maximum
                    cusum = max(np.abs(sneg), spos)

                    self.assertTrue(cusum >= threshold)

    def test_dynamic_cusum_filter(self):
        """
        Test CUSUM filter with dynamic threshold, assert lenght of filtered series
        """
        dynamic_threshold = self.data['close'] * 1e-5
        cusum_events = cusum_filter(self.data['close'], threshold=dynamic_threshold, time_stamps=True)
        self.assertTrue(cusum_events.shape[0] == 9)

    def test_z_score_filter(self):
        """
        Test Z-score filter
        """
        z_score_events = z_score_filter(self.data['close'], 100, 100, 2, time_stamps=True)
        z_score_events_timestamp_false = z_score_filter(self.data['close'], 100, 100, 2, time_stamps=False)

        self.assertTrue(z_score_events.shape[0] == 68)
        self.assertTrue(z_score_events.shape[0] == z_score_events_timestamp_false.shape[0])
        self.assertEqual(self.data.loc[z_score_events[0], 'close'], 2037.25)
        self.assertEqual(self.data.loc[z_score_events[25], 'close'], 2009.5)

    def test_error_raise(self):
        """
        Test ValueError raise of threshold is neither float/int nor pd.Series
        :return:
        """
        with self.assertRaises(ValueError):
            cusum_filter(self.data['close'], threshold='str', time_stamps=True)
