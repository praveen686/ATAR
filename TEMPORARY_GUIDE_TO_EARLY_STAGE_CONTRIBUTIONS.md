# Title: Temporary Guide to Contributing to the Project

Welcome to the Genie-Trader GitHub repository! This repository is currently in its early development stage, and while a lot of code has been written, some modules lack proper documentation. The aim of this project is to optimize the codebase and convert it into microservices while incorporating good CI/CD practices and automating most tasks along the way.

To get started, you can install Nautilus Trader, VectorbtPRO, and Autogluon via pip inside the conda environment. However, it is recommended to install RAPIDS via conda. Be sure to install pip dependencies first and then conda dependencies, as conda handles and corrects examples better than pip.

To keep dependencies separated locally, it's recommended to use a conda environment. For instance, Nautilus_Trader tends to break vectorbt's dependencies and vice versa, so keeping them separate is crucial. At the moment, the only actively developed examples are the triple_barrier_meta_labeling_example.py and autogluon_ts_example.py in the Modules_in_Dev folder. One utilizes VectorbtPRO and the standard algorithms for the labeling process without any issues. However, watch out for Dask, Pandas, and NumPy versioning issues. The other utilizes Autogluon and Dask and Pandas.

We will provide standard YAML files for more stable and experimental environments in the future, as well as Dockerfiles. Feel free to share your work with us, and we will add it to the repository. We are looking for any and all contributions.

Please make sure to do a pull before you start working on anything, as we have been making changes to the structure and contents of the repo on a daily basis. While breaking changes to your own work are unlikely at this point, it is still possible, especially with standard algorithms and modules in dev. Ideally, documentation will be automatically merged to the catalog along with changes.

As a rule of thumb, the main branch is the most stable, and the dev branch is the most experimental. However, currently, only the main branch is being updated given the current state of the repo. The repo is currently in a state of flux, and we are working on a more stable version that will exclude Modules_in_Dev, TBD_Contributions_From_Community_in_Dev, need_integration_aka_scattered_work, and any others.

We welcome contributions from everyone, no matter how small. Thank you for taking the time to visit this repository, and we look forward to working with you!

# SUMMARY - Contributing 
We appreciate your interest in contributing to our project! Please read through the following guidelines before you begin to ensure a smooth and efficient collaboration process.

Step 1: Fork the Repository
To get started, fork the repository to create your own copy, where you can make changes without affecting the original project. This will allow you to submit your changes as a pull request later on.

Step 2: Create a New Branch
After forking the repository, create a new branch in your fork to work on your changes. This will help keep your work organized and make it easier to merge your changes with the original project later.

Step 3: Make Your Changes
Feel free to work on any independent sections of the codebase or create new files as needed. Please ensure that your changes are in line with the project's objectives and maintain a high standard of quality. Keep in mind the importance of using common sense when making changes to the codebase.

Step 4: Document Your Work
Properly document your work by adding clear and concise comments to your code, as well as any necessary documentation for new features or modifications. This will help others understand your changes and ensure that they can be easily integrated into the main project.

Step 5: Submit a Pull Request
Once you have completed your work, submit a pull request to the original repository. Be sure to provide a detailed description of your changes, including any issues you encountered and how you resolved them. Please be precise in your description, especially when suggesting changes to files that you do not own.

Step 6: Addressing Issues
Feel free to add issues to the repository as needed. When submitting an issue, please provide a clear and concise description of the problem or recommended changes. If the issue pertains to a file that you do not own, be particularly precise in your description to help the file's owner understand the issue and implement the necessary changes.

Contributing.md (In Progress)
Please note that we are currently working on a detailed contributing.md file that will provide more in-depth instructions for contributors. In the meantime, we ask that you follow the guidelines outlined above to ensure a smooth collaboration process.

Thank you for your interest in contributing to our project! We look forward to working with you and building something great together.


