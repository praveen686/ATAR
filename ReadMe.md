
Use conda environment to keep dependencies separated locally, e.g. while not utilizing the AWS microservices. Nautilus_Trader
tends to break vectorbt's dependencies and vice versa.  So, I have to keep them separate.  I have a conda environment
for utilizing Nautilus_Trader, vectorbtpro, RAPIDS,and autogluon although the latter is more flexible if not utilzing 
GPU version to pytorch. For example, at the moment the only actively examples being developed are the triple_barrier_meta_labeling_example.py and 
autogluon_ts_example.py in Modules_in_Dev, one utilzes vectorbtpro and the standard_algorithms for the labeling process 
without any issues (although watchout for dask, pandas and numpy versioning issues).  The other utilizes autogluon and 
dask and pandas.


Not Much here yet.  Just a plac

[...]

Check mini_Genie and mini_Genie_ML Repos for more info example in the meantime 