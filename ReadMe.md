# Temporary Guide to Early Stage Contributions

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

As a rule of thumb the main branch is the most stable and the dev branch is the most experimental. However, currently 
only the main branch is being updated given the current state of the repo.  The repo is currently in a state of flux, 
I am working on a more stable version which will exclude Modules_in_Dev, TBD_Contributions_From_Community_in_Dev, 
need_integration_aka_scattered_work and any other.

## Useful Links

[CONTRIBUTING.md](CONTRIBUTING.md)

[Temporary_Guide_to_Early_Stage_Contributions.md](Temporary_Guide_to_Early_Stage_Contributions.md)

[RISK_AND_PERFORMANCE_DISCLAIMER.md](RISK_AND_PERFORMANCE_DISCLAIMER.md)

[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)

We are working in transitioning the current codebase into a microservice architecture, thus keep modularity in mind even 
if not directly contributing to the microservices.  The microservices maintenance will be the primary focus of the repo 
in the future. The current codebase is a bit of a mess and will be cleaned up as the microservices are developed.

## Genie-Trader Exclusive License Agreement: Overview for Incoming Contributors

This overview summarizes the key points of the Genie-Trader Exclusive License Agreement for incoming contributors to better and more efficiently understand the license. Please note that this overview does not replace the full license, and you should read the entire license to ensure that you fully understand its terms and conditions.

Purpose: The license aims to control access, usage, and contributions to the Genie-Trader repository by explicitly permitted Collaborators, while granting the Licensor (repository owner) complete control over the repository and its contents.

Collaborators: Individuals or entities who have been explicitly granted permission by the Licensor to contribute to the development, maintenance, or distribution of the Software.

License Grant: Collaborators are granted a non-exclusive, non-transferable, non-sublicensable, revocable, and limited license to access, use, and modify the Software solely for the purpose of making Contributions to the Software.

Restrictions: Collaborators must not copy, distribute, sell, or otherwise transfer any portion of the Software or use it for commercial purposes without the express written consent of the Licensor. Modifications and derivative works are only allowed as explicitly described under the License Grant.

Contributions: Collaborators grant the Licensor a perpetual, irrevocable, worldwide, non-exclusive, royalty-free, sublicensable, and transferable license to use, reproduce, modify, distribute, prepare derivative works of, display, and perform their Contributions in connection with the Software and the Licensor's business.

Termination: The Licensor may terminate the Agreement at any time, with or without cause. Upon termination, Collaborators must cease all use of the Software and destroy all copies in their possession or control.

Warranty and Liability: The Software is provided "as is," and the Licensor disclaims all warranties. The Licensor's liability is limited in the event of any damages arising from the use or inability to use the Software.

Governing Law and Jurisdiction: The Agreement is governed by the laws of the jurisdiction in which the Licensor resides, and any disputes arising out of or in connection with the Agreement are subject to the exclusive jurisdiction of the courts of that jurisdiction.

It is important to read and understand the entire Genie-Trader Exclusive License Agreement before contributing to the repository. By contributing, you agree to the terms and conditions outlined in the full license.



