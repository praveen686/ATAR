![RubenTheCuban_Genie-Trader_Algorythm_88b23a91-05f8-4a3f-bbfa-65e9681c87f8_2_20.png](static%2FRubenTheCuban_Genie-Trader_Algorythm_88b23a91-05f8-4a3f-bbfa-65e9681c87f8_2_20.png)

# Genie-Trader

Welcome to the Genie-Trader GitHub repository! The home to the ever evolving algorithmic microservice system that makes
Genie tick. Scalable (local&cloud) end-to-end endpoints for all of our API's, and more.

We encourage contributions from everyone, no matter how small. Thank you for taking the time to visit this repository,
and we look forward to working with you!

## Quick Start Guide to the codebase for New Contributors

This repository is currently in its early development stage, and while a
lot of code has been written, some modules lack proper documentation. The aim of this project is to optimize the
codebase and convert it into microservices while incorporating good CI/CD practices and automating most tasks along
the way. 

[TEMPORARY_GUIDE_TO_EARLY_STAGE_CONTRIBUTIONS.md](TEMPORARY_GUIDE_TO_EARLY_STAGE_CONTRIBUTIONS.md)

[DEPENDENCIES_EXPLAINED.md](DEPENDENCIES_EXPLAINED.md) (In Progress)

*note: Links to submodules are currently being displayed in the DEPENDENCIES_EXPLAINED.md and will soon be included in the pip installation in [all] and [**DEP] format*

## Microservices

We are working in transitioning the current codebase into a microservice architecture, thus keep modularity in mind even
if not directly contributing to the microservices. The microservices maintenance will be the primary focus of the repo
in the future. The current codebase is a bit of a mess and will be cleaned up as the microservices are developed.

![ezgif.com-video-to-gif.gif](static%2Fezgif.com-video-to-gif.gif)

*source: Netflix Microservices https://youtu.be/CZ3wIuvmHeM*

[MICROSERVICES_BEST_PRACTICES.md](MICROSERVICES_BEST_PRACTICES.md) (In Progress)

## CodeGens, Clients and API's

OpenAPI Generator allows generation of API client libraries (SDK generation), server stubs, documentation and
configuration automatically given an OpenAPI Spec (both 2.0 and 3.0 are supported). Currently, the following
languages/frameworks are supported:

Languages/Frameworks

### API clients

ActionScript, Ada, Apex, Bash, C, C# (.net 2.0, 3.5 or later, .NET Standard 1.3 - 2.1, .NET Core 3.1, .NET 5.0.
Libraries: RestSharp, GenericHost, HttpClient), C++ (Arduino, cpp-restsdk, Qt5, Tizen, Unreal Engine 4), Clojure,
Crystal, Dart, Elixir, Elm, Eiffel, Erlang, Go, Groovy, Haskell (http-client, Servant), Java (Apache HttpClient 4.x,
Apache HttpClient 5.x, Jersey1.x, Jersey2.x, OkHttp, Retrofit1.x, Retrofit2.x, Feign, RestTemplate, RESTEasy, Vertx,
Google API Client Library for Java, Rest-assured, Spring 5 Web Client, MicroProfile Rest Client, Helidon), Jetbrains
HTTP Client, Julia, k6, Kotlin, Lua, Nim, Node.js/JavaScript (ES5, ES6, AngularJS with Google Closure Compiler
annotations, Flow types, Apollo GraphQL DataStore), Objective-C, OCaml, Perl, PHP, PowerShell, Python, R, Ruby, Rust (
hyper, reqwest, rust-server), Scala (akka, http4s, scalaz, sttp, swagger-async-httpclient), Swift (2.x, 3.x, 4.x, 5.x),
Typescript (AngularJS, Angular (2.x - 15.x), Aurelia, Axios, Fetch, Inversify, jQuery, Nestjs, Node, redux-query, Rxjs)

### Server stubs

Ada, C# (ASP.NET Core, Azure Functions), C++ (Pistache, Restbed, Qt5 QHTTPEngine), Erlang, F# (Giraffe), Go (net/http,
Gin, Echo), Haskell (Servant, Yesod), Java (MSF4J, Spring, Undertow, JAX-RS: CDI, CXF, Inflector, Jersey, RestEasy, Play
Framework, PKMST, Vert.x, Apache Camel, Helidon), Julia, Kotlin (Spring Boot, Ktor, Vertx), PHP (Laravel, Lumen,
Mezzio (fka Zend Expressive), Slim, Silex, Symfony), Python (FastAPI, Flask), NodeJS, Ruby (Sinatra, Rails5), Rust (
rust-server), Scala (Akka, Finch, Lagom, Play, Scalatra)

### API documentation generators

HTML, Confluence Wiki, Asciidoc, Markdown, PlantUML

### Configuration files

Apache2

### Others

GraphQL, JMeter, Ktorm, MySQL Schema, Protocol Buffer, WSDL

https://github.com/OpenAPITools/openapi-generator.git

## Data

The data is currently stored in the data folder but will move towards database storage.

https://drive.google.com/drive/folders/1ygWAEfmfqn2sWLKxw7ahPg0XzTZXVtVK?usp=share_link

The data outside the subdirectories contain example data with 1 minute periods to get you started. However, the
subdirectories contain typically tick data, which is the most accurate data for backtesting; whether it will serve you
during your training process will depend heavily on your target labeled feature and resources available. The data is
stored in the following format:

## MISCELLANEOUS

[CONTRIBUTING.md](CONTRIBUTING.md) (In Progress)

[RISK_AND_PERFORMANCE_DISCLAIMER.md](RISK_AND_PERFORMANCE_DISCLAIMER.md)

[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)


## Project Focus: Code Integration, Review, and Optimization with Microservices Architecture

### Integration and Review

In the early stages of the project, our primary focus is to integrate and review the existing codebase to create a
cutting-edge algorithmic trading platform using a microservices architecture. We will:

1. Consolidate all scattered code from different branches and repositories.
2. Ensure consistent coding standards and practices across the entire codebase.
3. Design and implement a microservices architecture that enables modularity, flexibility, and scalability.
4. Identify and address potential security vulnerabilities within each service.

### Optimization with Microservices

Identify the different functionalities and services provided by your code.
Group related functionalities into separate microservices, keeping in mind the principles of loose coupling and high
cohesion.

#### Design your microservices:

Define clear interfaces and APgenI contracts for each service.
Determine the data storage requirements for each service and decide whether to use a shared database or a separate
database per service.

#### Choose AWS services for deployment and management:

AWS Elastic Container Service (ECS) or Elastic Kubernetes Service (EKS) for container orchestration.
AWS Lambda for serverless, event-driven functions.
API Gateway to manage and expose your APIs securely.
Amazon RDS, DynamoDB, or other AWS database services for data storage.

#### Set up CI/CD pipelines:

AWS CodePipeline, CodeBuild, and CodeDeploy to automate the build, test, and deployment process for each
microservice.

#### Implement monitoring and logging:

Amazon CloudWatch for monitoring and logging.
Set up alarms and notifications to alert you when there are issues with your services.

#### Implement security best practices:

Secure your microservices with proper authentication and authorization using Amazon Cognito or a custom solution.
Use AWS Identity and Access Management (IAM)

### Collaboration and Communication

We encourage active collaboration among team members through:

1. Shared communication channels, such as Slack or Discord. (In Progress)
2. Regular virtual meetings to discuss progress, challenges, and opportunities for improvement.
3. Utilizing a project management tool, like Trello or Jira, for task tracking and prioritization.
4. Creating and maintaining comprehensive documentation to support onboarding and knowledge sharing, including
   documentation for each microservice.

### Platform Features (In Progress - duh)

#### Advanced Order Types:

Our platform offers advanced order types, including limit orders, stop orders, and trailing stops. These order types are
implemented as independent services to ensure optimal functionality and ease of use.

#### Backtesting Capabilities:

We understand the importance of evaluating the performance of trading strategies against historical data. To support
this, we offer a dedicated backtesting service that enables users to assess their strategies with ease.

#### Historic and Live Data Transformation and Labeling:

We understand the importance of having high-quality data for effective trading. Our platform offers custom and automatic
data pipelines that can be accessed from inside Nautilus Trader, allowing users to transform and label historic and live
data to suit their needs.

#### Custom and Premade Model Inference of Machine Learning:

We are dedicated to staying on the cutting-edge of technology, which is why we offer custom and premade model inference
of machine learning. Our platform provides GPU-accelerated modules to enhance performance, giving our users access to
the latest and most powerful ML solutions available.

#### Custom Python Strategy Deployment:

Our platform is designed to offer flexibility to our users. We provide custom Python strategy deployment, allowing users
to deploy their trading strategies into Metatrader, Freqtrade, and other popular trading platforms with ease.

#### AI Agent Training:

Our platform is designed to support the development of sophisticated machine learning models for trading. We provide a
separate machine learning service that allows users to train their AI agents and develop powerful models.

#### Risk Management Functionality:

Managing exposure to market risks is crucial for successful trading. To help users monitor and manage their risk
exposure, we offer a dedicated risk management service that provides valuable insights and functionality.

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

It is important to read and understand the entire Genie-Trader Exclusive License Agreement before contributing to the
repository. By contributing, you agree to the terms and conditions outlined in the full license.


