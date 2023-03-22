

Use conda environment to keep dependencies separated locally, e.g. while not utilizing the AWS microservices. Nautilus_Trader
tends to break vectorbt's dependencies and vice versa.  So, I have to keep them separate.  I have a conda environment
for utilizing Nautilus_Trader, vectorbtpro, RAPIDS,and autogluon although the latter is more flexible if not utilzing 
GPU version to pytorch. For example, at the moment the only actively examples being developed are the triple_barrier_meta_labeling_example.py and 
autogluon_ts_example.py in Modules_in_Dev, one utilizes vectorbtpro and the standard_algorithms for the labeling process 
without any issues (although watch out for dask, pandas and numpy versioning issues).  The other utilizes autogluon and 
dask and pandas.

BE SURE TO DO A PULL BEFORE YOU START WORKING ON ANYTHING.  I HAVE BEEN MAKING CHANGES TO THE STRUCTURE AND CONTENTS OF 
THE REPO ON A DAILY BASIS! ALTHOUGH BREAKING CHANGES TO YOUR OWN WORK IS UNLIKELY AT THIS POINT, IT IS STILL POSSIBLE, 
SPECIALLY STANDARD ALGORITHMS AND MODULES IN DEV. IDEALLY DOCUMENTATION WILL BE AUTOMATICALLY MERGED TO THE CATALOG 
ALONG WITH CHANGES

[CONTRIBUTING.md](CONTRIBUTING.md)

[Temporary_Guide_to_Early_Stage_Contributions.md](Temporary_Guide_to_Early_Stage_Contributions.md)

[RISK_AND_PERFORMANCE_DISCLAIMER.md](RISK_AND_PERFORMANCE_DISCLAIMER.md)

[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)


Not Much here yet.  Just a plac

[...]

Check mini_Genie and mini_Genie_ML Repos for more info example in the meantime or ask me questions directly.

