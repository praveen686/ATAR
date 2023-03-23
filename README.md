![RubenTheCuban_Genie-Trader_Algorythm_88b23a91-05f8-4a3f-bbfa-65e9681c87f8.png](RubenTheCuban_Genie-Trader_Algorythm_88b23a91-05f8-4a3f-bbfa-65e9681c87f8.png)


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

[MICROSERVICES_BEST_PRACTICES.md](MICROSERVICES_BEST_PRACTICES.md) (I like the explination of the architecture following a biological viewpoint)


We are working in transitioning the current codebase into a microservice architecture, thus keep modularity in mind even 
if not directly contributing to the microservices.  The microservices maintenance will be the primary focus of the repo 
in the future. The current codebase is a bit of a mess and will be cleaned up as the microservices are developed.

So watch this:

1.
https://youtu.be/otADkIyugzY
and 

2.
Certainly, let's delve deeper into the scientific parallels between microservices architecture and biological systems, while maintaining a rigorous and scientifically grounded approach.

Modular design principles: In both microservices and biological systems, modular design is crucial for maintaining organization and enabling adaptability. In software engineering, modularity refers to the practice of designing software components with well-defined interfaces that can be combined and reused to build complex applications. Similarly, in biology, modularity can be observed at various scales, from molecular networks and cellular pathways to the organization of tissues and organs. This modularity allows biological systems to evolve and adapt to environmental changes, just as modular software components can be updated or replaced without disrupting the entire application.

Emergent properties: Microservices architecture is characterized by the emergence of complex behavior from the interactions of simple, independent components. This concept is also seen in biology, where emergent properties arise from the interactions of individual cells, molecules, or organisms. For example, the complex behavior of ant colonies, flocking birds, or schooling fish emerges from the simple rules and interactions followed by each individual. In both microservices and biological systems, these emergent properties allow the system to exhibit adaptive and robust behavior that cannot be easily predicted from the behavior of individual components alone.

Robustness and adaptability: Microservices architectures are designed to be robust and adaptable, allowing them to cope with changing requirements, unexpected failures, or varying loads. This resilience is achieved through loose coupling, redundancy, and self-healing mechanisms. Similarly, biological systems exhibit robustness and adaptability through a variety of mechanisms, such as redundant gene copies, alternative metabolic pathways, or compensatory organ function. These features enable biological systems to maintain homeostasis and respond to environmental challenges, much like microservices can maintain service availability and performance under diverse conditions.

Self-organization: One of the key features of microservices architecture is its ability to self-organize, with each service independently managing its own state and resources. This decentralized approach allows for greater agility and responsiveness, as well as more efficient use of resources. In biology, self-organization is a fundamental principle observed at multiple scales, from the self-assembly of molecular complexes and cellular structures to the formation of tissues, organs, and entire organisms. This self-organization allows biological systems to adapt and reconfigure themselves in response to changing conditions, much like microservices can dynamically scale or reorganize to meet changing demands.

While the analogy between microservices architecture and biological systems is not a perfect one, these parallels can provide valuable insights into the design principles and strategies that contribute to the success of both types of systems. By studying the underlying mechanisms and principles that govern biological systems, we can gain a deeper understanding of the factors that contribute to the robustness, adaptability, and scalability of microservices architecture, ultimately guiding the development of more effective and resilient software systems.

https://www.youtube.com/watch?v=CZ3wIuvmHeM&t=1554s

    

## Data

The data is currently stored in the data folder but will move towards database storage. 

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
4. Implementing best practices for code optimization and performance tuning in a microservices context.

### Collaboration and Communication

We encourage active collaboration among team members through:

1. Shared communication channels, such as Slack or Discord.
2. Regular virtual meetings to discuss progress, challenges, and opportunities for improvement.
3. Utilizing a project management tool, like Trello or Jira, for task tracking and prioritization.
4. Creating and maintaining comprehensive documentation to support onboarding and knowledge sharing, including documentation for each microservice.

### Platform Features

Our platform aims to provide a comprehensive and user-friendly solution using a microservices architecture, including:

1. Advanced order types, such as limit orders, stop orders, and trailing stops, implemented as independent services.
2. Backtesting capabilities to evaluate the performance of trading strategies against historical data, provided by a dedicated backtesting service.
3. AI agent training to support the development of sophisticated machine learning models for trading, enabled by a separate machine learning service.
4. Risk management functionality to help users monitor and manage their exposure to market risks, managed by a dedicated risk management service.

### Genie-Trader Exclusive License Agreement: Overview for Incoming Contributors

This overview summarizes the key points of the Genie-Trader Exclusive License Agreement for incoming contributors to better and more efficiently understand the license. Please note that this overview does not replace the full license, and you should read the entire license to ensure that you fully understand its terms and conditions.

1. Purpose: The license aims to control access, usage, and contributions to the Genie-Trader repository by explicitly permitted Collaborators, while granting the Licensor (repository owner) complete control over the repository and its contents.
2. Collaborators: Individuals or entities who have been explicitly granted permission by the Licensor to contribute to the development, maintenance, or distribution of the Software. 
3. License Grant: Collaborators are granted a non-exclusive, non-transferable, non-sublicensable, revocable, and limited license to access, use, and modify the Software solely for the purpose of making Contributions to the Software. 
4. Restrictions: Collaborators must not copy, distribute, sell, or otherwise transfer any portion of the Software or use it for commercial purposes without the express written consent of the Licensor. Modifications and derivative works are only allowed as explicitly described under the License Grant. 
5. Contributions: Collaborators grant the Licensor a perpetual, irrevocable, worldwide, non-exclusive, royalty-free, sublicensable, and transferable license to use, reproduce, modify, distribute, prepare derivative works of, display, and perform their Contributions in connection with the Software and the Licensor's business. 
6. Termination: The Licensor may terminate the Agreement at any time, with or without cause. Upon termination, Collaborators must cease all use of the Software and destroy all copies in their possession or control.
7. Warranty and Liability: The Software is provided "as is," and the Licensor disclaims all warranties. The Licensor's liability is limited in the event of any damages arising from the use or inability to use the Software. 
8. Governing Law and Jurisdiction: The Agreement is governed by the laws of the jurisdiction in which the Licensor resides, and any disputes arising out of or in connection with the Agreement are subject to the exclusive jurisdiction of the courts of that jurisdiction.

It is important to read and understand the entire Genie-Trader Exclusive License Agreement before contributing to the repository. By contributing, you agree to the terms and conditions outlined in the full license.


