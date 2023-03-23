![RubenTheCuban_Genie-Trader_Algorythm_88b23a91-05f8-4a3f-bbfa-65e9681c87f8_50.png](RubenTheCuban_Genie-Trader_Algorythm_88b23a91-05f8-4a3f-bbfa-65e9681c87f8_50.png)

# Temporary Guide to Early Stage Contributions

Welcome to the Genie-Trader GitHub repository! This repository is currently in its early development stage, and while a lot of code has been written, some modules lack proper documentation. The aim of this project is to optimize the codebase and convert it into microservices while incorporating good CI/CD practices and automating most tasks along the way.

To get started, you can install Nautilus Trader, VectorbtPRO, and Autogluon via pip inside the conda environment. However, it is recommended to install RAPIDS via conda. Be sure to install pip dependencies first and then conda dependencies, as conda handles and corrects examples better than pip.

To keep dependencies separated locally, it's recommended to use a conda environment. For instance, Nautilus_Trader tends to break vectorbt's dependencies and vice versa, so keeping them separate is crucial. At the moment, the only actively developed examples are the triple_barrier_meta_labeling_example.py and autogluon_ts_example.py in the Modules_in_Dev folder. One utilizes VectorbtPRO and the standard algorithms for the labeling process without any issues. However, watch out for Dask, Pandas, and NumPy versioning issues. The other utilizes Autogluon and Dask and Pandas.

We will provide standard YAML files for more stable and experimental environments in the future, as well as Dockerfiles. Feel free to share your work with us, and we will add it to the repository. We are looking for any and all contributions.

Please make sure to do a pull before you start working on anything, as we have been making changes to the structure and contents of the repo on a daily basis. While breaking changes to your own work are unlikely at this point, it is still possible, especially with standard algorithms and modules in dev. Ideally, documentation will be automatically merged to the catalog along with changes.

As a rule of thumb, the main branch is the most stable, and the dev branch is the most experimental. However, currently, only the main branch is being updated given the current state of the repo. The repo is currently in a state of flux, and we are working on a more stable version that will exclude Modules_in_Dev, TBD_Contributions_From_Community_in_Dev, need_integration_aka_scattered_work, and any others.

We welcome contributions from everyone, no matter how small. Thank you for taking the time to visit this repository, and we look forward to working with you!

## Useful Links

### Quick Start Guide to the codebase for New Contributors

[TEMPORARY_GUIDE_TO_EARLY_STAGE_CONTRIBUTIONS.md](TEMPORARY_GUIDE_TO_EARLY_STAGE_CONTRIBUTIONS.md)

### Microservices
We are working in transitioning the current codebase into a microservice architecture, thus keep modularity in mind even 
if not directly contributing to the microservices.  The microservices maintenance will be the primary focus of the repo 
in the future. The current codebase is a bit of a mess and will be cleaned up as the microservices are developed.

[MICROSERVICES_BEST_PRACTICES.md](MICROSERVICES_BEST_PRACTICES.md) (In Progress)

### MISCELLANEOUS
[CONTRIBUTING.md](CONTRIBUTING.md) (In Progress)

[RISK_AND_PERFORMANCE_DISCLAIMER.md](RISK_AND_PERFORMANCE_DISCLAIMER.md) 

[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) 

## Data

The data is currently stored in the data folder but will move towards database storage. 

https://drive.google.com/drive/folders/1ygWAEfmfqn2sWLKxw7ahPg0XzTZXVtVK?usp=share_link

The data outside the subdirectories contain example data with 1 minute periods to get you started. However, the subdirectories contain typically tick data, which is the most accurate data for backtesting; whether it will serve you during your training process will depend heavily on your target labeled feature and resources available. The data is stored in the following format:

## Project Focus: Code Integration, Review, and Optimization with Microservices Architecture

### Integration and Review

In the early stages of the project, our primary focus is to integrate and review the existing codebase to create a cutting-edge algorithmic trading platform using a microservices architecture. We will:

1. Consolidate all scattered code from different branches and repositories.
2. Ensure consistent coding standards and practices across the entire codebase.
3. Design and implement a microservices architecture that enables modularity, flexibility, and scalability.
4. Identify and address potential security vulnerabilities within each service.

### Agile Practices and Continuous Integration

We follow Agile practices, including regular sprints and continuous integration and delivery. This approach enables us to:

1. Iterate quickly and adapt to changes in requirements or priorities.
2. Facilitate ongoing collaboration and communication among the development team.
3. Promote a culture of continuous improvement, where the team regularly reflects on their progress and identifies areas for growth.
4. Ensure that each service is always in a releasable state, making it easier to deploy and test new features.

### Optimization with Microservices

Our optimization efforts will focus on:

1. Identifying and eliminating performance bottlenecks within each service.
2. Streamlining data processing and storage to minimize latency and optimize resource utilization.
3. Ensuring that the platform can scale to handle increasing workloads and user demands by adding or removing service instances as needed.
4. Implementing best practices for code optimization and performance tuning in a microservices' context.

### Collaboration and Communication

We encourage active collaboration among team members through:

1. Shared communication channels, such as Slack or Discord. (In Progress)
2. Regular virtual meetings to discuss progress, challenges, and opportunities for improvement.
3. Utilizing a project management tool, like Trello or Jira, for task tracking and prioritization.
4. Creating and maintaining comprehensive documentation to support onboarding and knowledge sharing, including documentation for each microservice.

### Platform Features (In Progress - duh)

#### Advanced Order Types: 

Our platform offers advanced order types, including limit orders, stop orders, and trailing stops. These order types are implemented as independent services to ensure optimal functionality and ease of use.

#### Backtesting Capabilities: 

We understand the importance of evaluating the performance of trading strategies against historical data. To support this, we offer a dedicated backtesting service that enables users to assess their strategies with ease.

#### Historic and Live Data Transformation and Labeling: 

We understand the importance of having high-quality data for effective trading. Our platform offers custom and automatic data pipelines that can be accessed from inside Nautilus Trader, allowing users to transform and label historic and live data to suit their needs.

#### Custom and Premade Model Inference of Machine Learning: 

We are dedicated to staying on the cutting-edge of technology, which is why we offer custom and premade model inference of machine learning. Our platform provides GPU-accelerated modules to enhance performance, giving our users access to the latest and most powerful ML solutions available.

#### Custom Python Strategy Deployment: 

Our platform is designed to offer flexibility to our users. We provide custom Python strategy deployment, allowing users to deploy their trading strategies into Metatrader, Freqtrade, and other popular trading platforms with ease.

#### AI Agent Training: 

Our platform is designed to support the development of sophisticated machine learning models for trading. We provide a separate machine learning service that allows users to train their AI agents and develop powerful models.

#### Risk Management Functionality: 

Managing exposure to market risks is crucial for successful trading. To help users monitor and manage their risk exposure, we offer a dedicated risk management service that provides valuable insights and functionality.
### Genie-Trader Exclusive License Agreement: Overview for Incoming Contributors

This overview summarizes the key points of the Genie-Trader Exclusive License Agreement for contributors to better and more efficiently understand the license. Please note that this overview does not replace the full license, and you should read the entire license to ensure that you fully understand its terms and conditions.

1. Purpose: The license aims to control access, usage, and contributions to the Genie-Trader repository by explicitly permitted Collaborators, while granting the Licensor (repository owner) complete control over the repository and its contents.
2. Collaborators: Individuals or entities who have been explicitly granted permission by the Licensor to contribute to the development, maintenance, or distribution of the Software. 
3. License Grant: Collaborators are granted a non-exclusive, non-transferable, non-sublicensable, revocable, and limited license to access, use, and modify the Software solely for the purpose of making Contributions to the Software. 
4. Restrictions: Collaborators must not copy, distribute, sell, or otherwise transfer any portion of the Software or use it for commercial purposes without the express written consent of the Licensor. Modifications and derivative works are only allowed as explicitly described under the License Grant. 
5. Contributions: Collaborators grant the Licensor a perpetual, irrevocable, worldwide, non-exclusive, royalty-free, sublicensable, and transferable license to use, reproduce, modify, distribute, prepare derivative works of, display, and perform their Contributions in connection with the Software and the Licensor's business. 
6. Termination: The Licensor may terminate the Agreement at any time, with or without cause. Upon termination, Collaborators must cease all use of the Software and destroy all copies in their possession or control.
7. Warranty and Liability: The Software is provided "as is," and the Licensor disclaims all warranties. The Licensor's liability is limited in the event of any damages arising from the use or inability to use the Software. 
8. Governing Law and Jurisdiction: The Agreement is governed by the laws of the jurisdiction in which the Licensor resides, and any disputes arising out of or in connection with the Agreement are subject to the exclusive jurisdiction of the courts of that jurisdiction.

It is important to read and understand the entire Genie-Trader Exclusive License Agreement before contributing to the repository. By contributing, you agree to the terms and conditions outlined in the full license.


