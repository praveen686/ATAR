Nautilus Trader, VectorbtPRO, and Autogluon can all be installed via pip inside the conda environment however RAPIDS is
recommended to be installed via conda. Install pip dependencies first, then conda dependencies since conda handles and 
corrects examples better than pip.

Use conda environment to keep dependencies separated locally, e.g. while not utilizing the AWS microservices. Nautilus_Trader
tends to break vectorbt's dependencies and vice versa.  So, I have to keep them separate.  I have a conda environment
for utilizing Nautilus_Trader, vectorbtpro, RAPIDS,and autogluon although the latter is more flexible if not utilzing 
GPU version to pytorch. For example, at the moment the only actively examples being developed are the triple_barrier_meta_labeling_example.py and 
autogluon_ts_example.py in Modules_in_Dev, one utilizes vectorbtpro and the standard_algorithms for the labeling process 
without any issues (although watch out for dask, pandas and numpy versioning issues).  The other utilizes autogluon and 
dask and pandas.

Standard yml files will be provided for more stable and experimental environments in the future as well as a 
dockerfiles. Feel free to share your work with me and I will add it to the repo. No work is small enough to be
considered insignificant.  I am looking for any and all contributions.

BE SURE TO DO A PULL BEFORE YOU START WORKING ON ANYTHING.  I HAVE BEEN MAKING CHANGES TO THE STRUCTURE AND CONTENTS OF 
THE REPO ON A DAILY BASIS! ALTHOUGH BREAKING CHANGES TO YOUR OWN WORK IS UNLIKELY AT THIS POINT, IT IS STILL POSSIBLE, 
SPECIALLY STANDARD ALGORITHMS AND MODULES IN DEV. IDEALLY DOCUMENTATION WILL BE AUTOMATICALLY MERGED TO THE CATALOG 
ALONG WITH CHANGES.

As a rule of thumb the main branch is the most stable and the dev branch is the most experimental. However currently 
only the main branch is being updated given the current state of the repo.  I am working on a more stable version which
will exclude Modules_in_Dev, TBD_Contributions_From_Community_in_Dev, need_integration_aka_scattered_work and any other.




[CONTRIBUTING.md](CONTRIBUTING.md)

[Temporary_Guide_to_Early_Stage_Contributions.md](Temporary_Guide_to_Early_Stage_Contributions.md)

[RISK_AND_PERFORMANCE_DISCLAIMER.md](RISK_AND_PERFORMANCE_DISCLAIMER.md)

[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)

We are working in transitioning the current codebase into a microservice architecture, thus keep modularity in mind even 
if not directly contributing to the microservices.  The microservices maintenance will be the primary focus of the repo 
in the future. The current codebase is a bit of a mess and will be cleaned up as the microservices are developed.

Not Much here yet.  Just a plac

[...]

Check mini_Genie and mini_Genie_ML Repos for more info example in the meantime or ask me questions directly.

