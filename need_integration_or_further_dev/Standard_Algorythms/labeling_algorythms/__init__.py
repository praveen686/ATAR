"""
Labeling techniques used in financial machine learning.
"""

from need_integration_or_further_dev.Standard_Algorythms.labeling_algorythms.labeling import (add_vertical_barrier, apply_pt_sl_on_t1, barrier_touched, drop_labels,
                                                  get_bins, get_events)
from need_integration_or_further_dev.Standard_Algorythms.labeling_algorythms.trend_scanning import trend_scanning_labels
from need_integration_or_further_dev.Standard_Algorythms.labeling_algorythms.tail_sets import TailSetLabels
from need_integration_or_further_dev.Standard_Algorythms.labeling_algorythms.fixed_time_horizon import fixed_time_horizon
from need_integration_or_further_dev.Standard_Algorythms.labeling_algorythms.matrix_flags import MatrixFlagLabels
from need_integration_or_further_dev.Standard_Algorythms.labeling_algorythms.excess_over_median import excess_over_median
from need_integration_or_further_dev.Standard_Algorythms.labeling_algorythms.raw_return import raw_return
from need_integration_or_further_dev.Standard_Algorythms.labeling_algorythms.return_vs_benchmark import return_over_benchmark
from need_integration_or_further_dev.Standard_Algorythms.labeling_algorythms.excess_over_mean import excess_over_mean
