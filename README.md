![RubenTheCuban_Genie-Trader_Algorythm_88b23a91-05f8-4a3f-bbfa-65e9681c87f8_2_20.png](static%2FRubenTheCuban_Genie-Trader_Algorythm_88b23a91-05f8-4a3f-bbfa-65e9681c87f8_2_20.png)

# Advanced Trading Analytics Research Program (ATAR)  

(In Progress - Personal Project and Notes! Not all features are available, these are targets and guides for contributors. To be updated as the project develops based on interests and other client work. Come back later if this is too early of a stage, clear expectations create great partnerships! )


Welcome to the ATAR GitHub repository! Here you'll discover our innovative algorithmic and statistical modeling
platform designed for traders. ATAR is a microservice system that expertly manages intricate processes, creating
a seamless and self-consistent environment.

😂In all seriousness, in its early stages, our platform is focusing on providing modular code that allows experienced developers and
traders to create customized pipelines. As the project evolves, we plan to expand and incorporate scalable cloud-based
solutions and end-to-end integration with various APIs.

We invite and appreciate contributions from everyone, regardless of the scale or scope. Thank you for visiting our
repository, and we're excited to collaborate with you on this groundbreaking project!

## [Quick Start Guide to the codebase for New Contributors](TEMPORARY_GUIDE_TO_EARLY_STAGE_CONTRIBUTIONS.md)

This repository is currently in its early development stage, and while a
lot of code has been written, it is a soup of concepts and the modules that exist lack proper documentation. The aim of this project is to optimize the
codebase for a large event-driven program; through the continuous expansion of loosely coupled components/microservices/modules while incorporating good CI/CD practices and automating most tasks along
the way. Including deployment, maintenance, corrections, and security. The topic is trading but only because it is a complex system to study (check), can help us fund this and other projects (check), my last 3 years of paid development 
hours have consisted of mostly FX, Commodities, and Crypto and thus through this project I am able to expand beyond the simple client requests while reusing the none licenced components (check - this is why is so broken up, I only started from the test scripts
and documentation saved over the years ...  you try looking back at code you wrote while learning a domain 😂) Come back later if this is too early of a stage, clear expectations is what makes for a great partnerships! 

1. Consolidate all scattered code from different branches and repositories.
2. Ensure consistent coding standards and practices across the entire codebase.
3. Design and implement a microservices architecture that enables modularity, flexibility, and scalability.
4. Identify and address potential security vulnerabilities within each service.

[TEMPORARY_GUIDE_TO_EARLY_STAGE_CONTRIBUTIONS.md](TEMPORARY_GUIDE_TO_EARLY_STAGE_CONTRIBUTIONS.md)

[USED_LIBRARIES_EXPLAINED.md](USED_LIBRARIES_EXPLAINED.md) (In Progress)

*note: Links to submodules are currently being displayed in the [USED_LIBRARIES_EXPLAINED.md](USED_LIBRARIES_EXPLAINED.md) and will soon be included in
the pip installation in [all] and [**DEP] format* Some will not be directly used in this codebase and might be part of a submodule that is used e.g. OpenAI, HuggingFace, etc. are used in ContentAdvisor; and may be moved to their respective repos as the codebase is converted into microservices.

## [Control Theory in Algorithmic Trading]()

### Introduction to Control Theory in Trading Systems

Control theory, a fundamental aspect of designing autonomous systems, is increasingly relevant in the development of sophisticated algorithmic trading strategies. In the context of trading, control theory provides a mathematical framework for managing the dynamic nature of financial markets, optimizing trade execution, and mitigating risks. It enhances the ability to adapt to market changes, manage risks, and improve the overall efficiency of trading operations. As the ATAR project evolves, integrating control theory principles can significantly contribute to the development of robust, adaptive, and high-performing trading algorithms.

### Dynamical Systems in Trading

In trading, a dynamical system can be understood as the financial market, influenced by various external inputs. These inputs include:

- **Control Inputs (U):** Intentional actions such as buy or sell orders.
- **Disturbances (D):** Unintentional factors like market news, sudden economic changes, or geopolitical events.

The state of the market (X) is constantly evolving due to these inputs and the internal dynamics of the market.

### Open-Loop Control: Feedforward in Trading

In an open-loop or feedforward control system within trading, strategies are executed based on predictive models without real-time feedback. This approach requires a deep understanding of market dynamics and often involves historical data analysis and predictive modeling. However, its effectiveness is limited in rapidly changing market conditions where real-time adjustments are crucial.

### Closed-Loop Control: Feedback in Trading

Feedback or closed-loop control is vital in trading systems to adapt to real-time market changes. This approach involves:

- **Monitoring Market State:** Continuously tracking market conditions and the performance of the trading strategy.
- **Adjusting Strategies:** Modifying trading actions based on the deviation between the desired outcome (e.g., profit targets) and the actual market performance.

### Control Strategies in Trading

Various control strategies can be applied in algorithmic trading, such as:

- **PID Controllers:** Adjusting trade positions based on proportional, integral, and derivative terms of the market state error.
- **Adaptive Control:** Dynamically adjusting strategies based on changing market conditions.
- **Robust Control:** Ensuring strategy performance under uncertain and volatile market conditions.
- **Predictive Control:** Using predictive models to anticipate market movements and adjust strategies accordingly.

### Planning and State Estimation

- **Planning:** In trading, this involves setting up trading goals, risk management rules, and identifying potential market opportunities.
- **State Estimation:** Utilizing techniques like statistical analysis and machine learning to estimate and predict market states.

### System Analysis and Testing

Before deployment, trading strategies developed using control theory principles must undergo rigorous backtesting, simulation, and analysis. Tools like statistical analysis software, backtesting platforms, and risk assessment models are crucial in this phase.

## [Microservices](MICROSERVICES_BEST_PRACTICES.md)

We are working on transitioning the current codebase into a microservice architecture, thus keeping modularity in mind even
if not directly contributing to the microservices. The microservices maintenance will be the primary focus of the repo
in the future. The current codebase is a bit of a mess and will be cleaned up as the microservices are developed. By no means am I referring to only the current definition of microservices (lambdas/cloud-run/etc...); just old-fashioned modular environments with loosely coupled components and a message bus or CLI will suffice.

![ezgif.com-video-to-gif.gif](static%2Fezgif.com-video-to-gif.gif)

*source: Netflix Microservices https://youtu.be/CZ3wIuvmHeM*

[MICROSERVICES_BEST_PRACTICES.md](MICROSERVICES_BEST_PRACTICES.md) (In Progress)

[Dockerize_and_Deploy_Python.md](..%2FAIOrg%2FPrompts%2FDockerize_and_Deploy_Python.md)

### CodeGens, Clients, and API's Creation

#### [OpenAPI Specification Initiative](https://github.com/OAI/OpenAPI-Specification.git)

[OpenAPI Generator](https://github.com/OpenAPITools/openapi-generator.git) allows the generation of API client libraries (
SDK generation), server stubs, documentation, and configuration automatically given
an [OpenAPI Spec](https://github.com/OAI/OpenAPI-Specification) (both 2.0 and 3.0 are supported). Currently, the
following languages/frameworks are supported:

|                                  | Languages/Frameworks                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
|----------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **API clients**                  | **ActionScript**, **Ada**, **Apex**, **Bash**, **C**, **C#** (.net 2.0, 3.5 or later, .NET Standard 1.3 - 2.1, .NET Core 3.1, .NET 5.0. Libraries: RestSharp, GenericHost, HttpClient), **C++** (Arduino, cpp-restsdk, Qt5, Tizen, Unreal Engine 4), **Clojure**, **Crystal**, **Dart**, **Elixir**, **Elm**, **Eiffel**, **Erlang**, **Go**, **Groovy**, **Haskell** (http-client, Servant), **Java** (Apache HttpClient 4.x, Apache HttpClient 5.x, Jersey1.x, Jersey2.x, OkHttp, Retrofit1.x, Retrofit2.x, Feign, RestTemplate, RESTEasy, Vertx, Google API Client Library for Java, Rest-assured, Spring 5 Web Client, MicroProfile Rest Client, Helidon), **Jetbrains HTTP Client**, **Julia**, **k6**, **Kotlin**, **Lua**, **Nim**, **Node.js/JavaScript** (ES5, ES6, AngularJS with Google Closure Compiler annotations, Flow types, Apollo GraphQL DataStore), **Objective-C**, **OCaml**, **Perl**, **PHP**, **PowerShell**, **Python**, **R**, **Ruby**, **Rust** (hyper, reqwest, rust-server), **Scala** (akka, http4s, scalaz, sttp, swagger-async-httpclient), **Swift** (2.x, 3.x, 4.x, 5.x), **Typescript** (AngularJS, Angular (2.x - 15.x), Aurelia, Axios, Fetch, Inversify, jQuery, Nestjs, Node, redux-query, Rxjs) |
| **Server stubs**                 | **Ada**, **C#** (ASP.NET Core, Azure Functions), **C++** (Pistache, Restbed, Qt5 QHTTPEngine), **Erlang**, **F#** (Giraffe), **Go** (net/http, Gin, Echo), **Haskell** (Servant, Yesod), **Java** (MSF4J, Spring, Undertow, JAX-RS: CDI, CXF, Inflector, Jersey, RestEasy, Play Framework, [PKMST](https://github.com/ProKarma-Inc/pkmst-getting-started-examples), [Vert.x](https://vertx.io/), [Apache Camel](https://camel.apache.org/), [Helidon](https://helidon.io/)), **Julia**, **Kotlin** (Spring Boot, Ktor, Vertx), **PHP** (Laravel, Lumen, [Mezzio (fka Zend Expressive)](https://github.com/mezzio/mezzio), Slim, Silex, [Symfony](https://symfony.com/)), **Python** (FastAPI, Flask), **NodeJS**, **Ruby** (Sinatra, Rails5), **Rust** ([rust-server](https://openapi-generator.tech/docs/generators/rust-server/)), **Scala** (Akka, [Finch](https://github.com/finagle/finch), [Lagom](https://github.com/lagom/lagom), [Play](https://www.playframework.com/), Scalatra)                                                                                                                                                                                                                                               |
| **API documentation generators** | **HTML**, **Confluence Wiki**, **Asciidoc**, **Markdown**, **PlantUML**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| **App_Configuration files**          | [**Apache2**](https://httpd.apache.org/)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| **Others**                       | **GraphQL**, **JMeter**, **Ktorm**, **MySQL Schema**, **Protocol Buffer**, **WSDL**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |


#### AWS Example

Define clear interfaces and APgenI contracts for each service.
Determine the data storage requirements for each service and decide whether to use a shared database or a separate
database per service. 

##### [SAM CLI](https://aws.amazon.com/serverless/sam/)

The AWS Serverless Application Model (SAM) is an open-source framework for building serverless applications. It provides
shorthand syntax to express functions, APIs, databases, and event source mappings. With just a few lines per resource,
you can define the application you want and model it using YAML. During deployment, SAM transforms and expands the SAM
syntax into AWS CloudFormation syntax, enabling you to build serverless applications faster.

SAM CLI provides a Lambda-like execution environment that lets you locally build, test, and debug applications defined by SAM templates or through the AWS Cloud Development Kit (CDK). You can also use the SAM CLI to deploy your applications to AWS, or create secure continuous integration and deployment (CI/CD) pipelines that follow best practices and integrate with AWS' native and third party CI/CD systems.

##### Choose AWS services for deployment and management:

AWS Elastic Container Service (ECS) or Elastic Kubernetes Service (EKS) for container orchestration.
AWS Lambda for serverless, event-driven functions.
API Gateway to manage and expose your APIs securely.
Amazon RDS, DynamoDB, or other AWS database services for data storage.

##### Set up CI/CD pipelines:

AWS CodePipeline, CodeBuild, and CodeDeploy to automate the build, test, and deployment process for each
microservice.

##### Implement monitoring and logging:

Amazon CloudWatch for monitoring and logging.
Set up alarms and notifications to alert you when there are issues with your services.

#### Implement security best practices:

Secure your microservices with proper authentication and authorization using Amazon Cognito or a custom solution.
Use AWS Identity and Access Management (IAM)



## [Data](https://drive.google.com/drive/folders/1ygWAEfmfqn2sWLKxw7ahPg0XzTZXVtVK?usp=share_link)

The data is currently stored in the data folder but will move towards database storage.

The data outside the subdirectories contain example data with 1 minute periods to get you started. However, the
subdirectories contain typically tick data, which is the most accurate data for backtesting; whether it will serve you
during your training process will depend heavily on your target labeled feature and resources available. The data is
stored in the following format:


[CONTRIBUTING.md](CONTRIBUTING.md) (Set Up In Progress)\
[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)\
[Risk and Performance Disclaimer](RISK_AND_PERFORMANCE_DISCLAIMER.md)

## Introduction to the Platform Features (In Progress - Not all features are available, these are targets and guides for contributors)
Welcome to our state-of-the-art trading platform, currently in development, designed to provide a comprehensive and versatile trading environment tailored to the needs of a diverse user base. Our platform focuses on enhancing user experience, streamlining the trading process, and facilitating continuous learning and improvement. In this section, we will provide an overview of the key features under development that will set our platform apart and contribute to its robust capabilities once completed.

Our platform encompasses a wide range of features to address essential aspects of the trading process, such as security, education, and market analysis. These features, while still in early development stages, have been meticulously designed to cater to users with varying needs and preferences, ensuring a seamless and satisfying trading experience for all upon completion.

For a detailed explanation of each feature and its benefits, please refer to the PaaS Proposal or read through the [COMPREHENSIVE_PLATFORM_FEATURES.md](COMPREHENSIVE_PLATFORM_FEATURES.md)  file. This comprehensive guide will help you explore and better understand the full potential of our innovative trading platform as it progresses through development.

| - Trading Features: \
| - - Sophisticated Order Types \
| - - Automated Trading and Order Execution \
| - - Multi-Asset Support and Portfolio Management \
| - - Robust Risk Management Functionality \
|  \
| - Data and Analytics: \
| - - Comprehensive Backtesting Capabilities \
| - - Dynamic Historic and Live Data Transformation and Labeling \
| - - Real-time Market Sentiment Analysis \
| - - Performance Analytics and Reporting \
|  \
| - Machine Learning and AI: \
| - - State-of-the-Art Machine Learning Model Inference and AI Agent Training \
| - - Natural Language Processing and Large Language Models for Enhanced User Assistance \
|  \
| - User Experience and Accessibility: \
| - - User-friendly Interface and Customizable Dashboards \
| - - Mobile and Web Accessibility \
| - - Custom Alerts and Notifications \
|  \
| - Education and Community: \
| - - Interactive Educational Resources and Community Support \
| - - Paper Trading and Simulation Environment \
|  \
| - Integration and Flexibility: \
| - - Flexible Custom Python Strategy Deployment \
| - - Integration with External Tools and Services \
|  \
| - Security and Compliance: \
| - - Advanced Security Measures and Regulatory Compliance




