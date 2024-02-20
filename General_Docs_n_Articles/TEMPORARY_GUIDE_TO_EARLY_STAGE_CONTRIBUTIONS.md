# Title: Temporary Guide to Contributing to the Project
*~~~~~better guide on each coming soon*~~~~~


Welcome to the Genie-Trader GitHub repository! This repository is currently in its early development stage, and while a lot of code has been written, some modules lack proper documentation. The aim of this project is to optimize the codebase and convert it into microservices while incorporating good CI/CD practices and automating most tasks along the way.

We will provide standard YAML files for more stable and experimental environments in the future, as well as Dockerfiles. Feel free to share your work with us, and we will add it to the repository. We are looking for any and all contributions.

Please make sure to follow the guidelines below when contributing to the project. This will help ensure that your contributions are accepted quickly and efficiently.

However, currently, only the main branch is being updated given the current state of the repo. The repo is currently in a state of flux, and we are working on a more stable version that will exclude Modules_in_Dev, TBD_Contributions_From_Community_in_Dev, need_integration_aka_scattered_work, and any others. 

We welcome contributions from everyone, no matter how small. Thank you for taking the time to visit this repository, and we look forward to working with you!

## Microservices Contributions:
![Screenshot from 2023-03-27 00-12-46.png](static%2FScreenshot%20from%202023-03-27%2000-12-46.png)
e.g. https://aws.amazon.com/serverless/sam/ or https://docs.aws.amazon.com/toolkit-for-jetbrains/latest/userguide/welcome.html

[MICROSERVICES_BEST_PRACTICES.md](MICROSERVICES_BEST_PRACTICES.md)

[CloudFormationPythonExamples](CloudFormation_Test) - for arbitrary resource creation and updates


## Financial Modeling and Backtesting Contributions:
You can install Nautilus Trader, VectorbtPRO, and Autogluon via pip inside the conda environment. However, it is recommended to install RAPIDS via conda. Be sure to install pip dependencies first and then conda dependencies, as conda handles and corrects examples better than pip.

To keep dependencies separated locally, it's recommended to use a conda environment. For instance, Nautilus_Trader tends to break vectorbt's dependencies and vice versa, so keeping them separate is crucial. At the moment, the only actively developed examples are the triple_barrier_meta_labeling_example.py and autogluon_ts_example.py in the Modules_in_Dev folder. One utilizes VectorbtPRO and the standard algorithms for the labeling process without any issues. However, watch out for Dask, Pandas, and NumPy versioning issues. The other utilizes Autogluon and Dask and Pandas.


TODO: to be arranged 
https://raw.githubusercontent.com/Innixma/autogluon-doc-utils/main/docs/cheatsheets/stable/autogluon-cheat-sheet.jpeg
https://automl-mm-bench.s3-accelerate.amazonaws.com/cheatsheet/v0.7.0/AutoGluon_Multimodal_Cheatsheet_v0.7.0.png
https://raw.githubusercontent.com/Innixma/autogluon-doc-utils/main/docs/cheatsheets/stable/timeseries/autogluon-cheat-sheet-ts.jpeg
https://auto.gluon.ai/stable/tutorials/cloud_fit_deploy/index.html




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

coming soon: [CONTRIBUTING.md](CONTRIBUTING.md)

### Genie-Trader Exclusive License Agreement: Overview for Incoming Contributors

This overview summarizes the key points of the Genie-Trader Exclusive License Agreement for contributors to better and
more efficiently understand the license. Please note that this overview does not replace the full license, and you
should read the entire license to ensure that you fully understand its terms and conditions.

1. Purpose: The license aims to control access, usage, and contributions to the Genie-Trader repository by explicitly
   permitted Collaborators, while granting the Licensor (repository owner) complete control over the repository and its
   contents.
2. Collaborators: Individuals or entities who have been explicitly granted permission by the Licensor to contribute to
   the development, maintenance, or distribution of the Software.
3. License Grant: Collaborators are granted a non-exclusive, non-transferable, non-sublicensable, revocable, and limited
   license to access, use, and modify the Software solely for the purpose of making Contributions to the Software.
4. Restrictions: Collaborators must not copy, distribute, sell, or otherwise transfer any portion of the Software or use
   it for commercial purposes without the express written consent of the Licensor. Modifications and derivative works
   are only allowed as explicitly described under the License Grant.
5. Contributions: Collaborators grant the Licensor a perpetual, irrevocable, worldwide, non-exclusive, royalty-free,
   sublicensable, and transferable license to use, reproduce, modify, distribute, prepare derivative works of, display,
   and perform their Contributions in connection with the Software and the Licensor's business.
6. Termination: The Licensor may terminate the Agreement at any time, with or without cause. Upon termination,
   Collaborators must cease all use of the Software and destroy all copies in their possession or control.
7. Warranty and Liability: The Software is provided "as is," and the Licensor disclaims all warranties. The Licensor's
   liability is limited in the event of any damages arising from the use or inability to use the Software.
8. Governing Law and Jurisdiction: The Agreement is governed by the laws of the jurisdiction in which the Licensor
   resides, and any disputes arising out of or in connection with the Agreement are subject to the exclusive
   jurisdiction of the courts of that jurisdiction.

It is important to read and understand the entire [Genie-Trader Exclusive License Agreement](LICENSE.md) before contributing to the
repository. By contributing, you agree to the terms and conditions outlined in the full license.

Please ==> [RISK_AND_PERFORMANCE_DISCLAIMER.md](RISK_AND_PERFORMANCE_DISCLAIMER.md), [LICENSE.md](LICENSE.md), and [CONTRIBUTING.md](CONTRIBUTING.md) <== before using or contributing to the project.
