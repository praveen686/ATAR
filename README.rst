.. figure:: static%2FRubenTheCuban_Genie-Trader_Algorythm_88b23a91-05f8-4a3f-bbfa-65e9681c87f8_2_20.png
   :alt: RubenTheCuban_Genie-Trader_Algorythm_88b23a91-05f8-4a3f-bbfa-65e9681c87f8_2_20.png

   RubenTheCuban_Genie-Trader_Algorythm_88b23a91-05f8-4a3f-bbfa-65e9681c87f8_2_20.png

Genie-Trader
============

Welcome to the Genie Trader GitHub repository! Here you’ll discover our
innovative algorithmic and statistical modeling platform designed for
traders. Genie Trader is a microservice system that expertly manages
intricate processes, creating a seamless and self-consistent
environment.

In its early stages, our platform is currently focused on providing
modular code that allows experienced developers and traders to create
customized pipelines. As the project evolves, we plan to expand and
incorporate scalable cloud-based solutions and end-to-end integration
with various APIs.

We invite and appreciate contributions from everyone, regardless of the
scale or scope. Thank you for visiting our repository, and we’re excited
to collaborate with you on this groundbreaking project!

`Quick Start Guide to the codebase for New Contributors <TEMPORARY_GUIDE_TO_EARLY_STAGE_CONTRIBUTIONS.md>`__
------------------------------------------------------------------------------------------------------------

This repository is currently in its early development stage, and while a
lot of code has been written, some modules lack proper documentation.
The aim of this project is to optimize the codebase and convert it into
microservices while incorporating good CI/CD practices and automating
most tasks along the way.

`TEMPORARY_GUIDE_TO_EARLY_STAGE_CONTRIBUTIONS.md <TEMPORARY_GUIDE_TO_EARLY_STAGE_CONTRIBUTIONS.md>`__

`USED_LIBRARIES_EXPLAINED.md <USED_LIBRARIES_EXPLAINED.md>`__ (In
Progress)

*note: Links to submodules are currently being displayed in
the*\ `USED_LIBRARIES_EXPLAINED.md <USED_LIBRARIES_EXPLAINED.md>`__\ *and
will soon be included in the pip installation in [all] and [**DEP]
format* Some will not be directly used in this codebase and might be
part of a submodule that is used e.g. OpenAI, HuggingFace, etc. are used
in ContentAdvisor; and may be moved to their respective repos as the
codebase is converted into microservices.

`Microservices <MICROSERVICES_BEST_PRACTICES.md>`__
---------------------------------------------------

We are working in transitioning the current codebase into a microservice
architecture, thus keep modularity in mind even if not directly
contributing to the microservices. The microservices maintenance will be
the primary focus of the repo in the future. The current codebase is a
bit of a mess and will be cleaned up as the microservices are developed.

.. figure:: static%2Fezgif.com-video-to-gif.gif
   :alt: ezgif.com-video-to-gif.gif

   ezgif.com-video-to-gif.gif

*source: Netflix Microservices https://youtu.be/CZ3wIuvmHeM*

`MICROSERVICES_BEST_PRACTICES.md <MICROSERVICES_BEST_PRACTICES.md>`__
(In Progress)

`Dockerize_and_Deploy_Python.md <..%2FAIOrg%2FPrompts%2FDockerize_and_Deploy_Python.md>`__

CodeGens, Clients and API’s Creation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`SAM CLI <https://aws.amazon.com/serverless/sam/>`__
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The AWS Serverless Application Model (SAM) is an open-source framework
for building serverless applications. It provides shorthand syntax to
express functions, APIs, databases, and event source mappings. With just
a few lines per resource, you can define the application you want and
model it using YAML. During deployment, SAM transforms and expands the
SAM syntax into AWS CloudFormation syntax, enabling you to build
serverless applications faster.

SAM CLI provides a Lambda-like execution environment that lets you
locally build, test, and debug applications defined by SAM templates or
through the AWS Cloud Development Kit (CDK). You can also use the SAM
CLI to deploy your applications to AWS, or create secure continuous
integration and deployment (CI/CD) pipelines that follow best practices
and integrate with AWS’ native and third party CI/CD systems.

`OpenAPI Specification Initiative <https://github.com/OAI/OpenAPI-Specification.git>`__
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

`OpenAPI
Generator <https://github.com/OpenAPITools/openapi-generator.git>`__
allows generation of API client libraries ( SDK generation), server
stubs, documentation and configuration automatically given an `OpenAPI
Spec <https://github.com/OAI/OpenAPI-Specification>`__ (both 2.0 and 3.0
are supported). Currently, the following languages/frameworks are
supported:

+---+---------------------------------------------------------------------+
|   | Languages/Frameworks                                                |
+===+=====================================================================+
| * | **ActionScript**, **Ada**, **Apex**, **Bash**, **C**, **C#** (.net  |
| * | 2.0, 3.5 or later, .NET Standard 1.3 - 2.1, .NET Core 3.1, .NET     |
| A | 5.0. Libraries: RestSharp, GenericHost, HttpClient), **C++**        |
| P | (Arduino, cpp-restsdk, Qt5, Tizen, Unreal Engine 4), **Clojure**,   |
| I | **Crystal**, **Dart**, **Elixir**, **Elm**, **Eiffel**, **Erlang**, |
| c | **Go**, **Groovy**, **Haskell** (http-client, Servant), **Java**    |
| l | (Apache HttpClient 4.x, Apache HttpClient 5.x, Jersey1.x,           |
| i | Jersey2.x, OkHttp, Retrofit1.x, Retrofit2.x, Feign, RestTemplate,   |
| e | RESTEasy, Vertx, Google API Client Library for Java, Rest-assured,  |
| n | Spring 5 Web Client, MicroProfile Rest Client, Helidon),            |
| t | **Jetbrains HTTP Client**, **Julia**, **k6**, **Kotlin**, **Lua**,  |
| s | **Nim**, **Node.js/JavaScript** (ES5, ES6, AngularJS with Google    |
| * | Closure Compiler annotations, Flow types, Apollo GraphQL            |
| * | DataStore), **Objective-C**, **OCaml**, **Perl**, **PHP**,          |
|   | **PowerShell**, **Python**, **R**, **Ruby**, **Rust** (hyper,       |
|   | reqwest, rust-server), **Scala** (akka, http4s, scalaz, sttp,       |
|   | swagger-async-httpclient), **Swift** (2.x, 3.x, 4.x, 5.x),          |
|   | **Typescript** (AngularJS, Angular (2.x - 15.x), Aurelia, Axios,    |
|   | Fetch, Inversify, jQuery, Nestjs, Node, redux-query, Rxjs)          |
+---+---------------------------------------------------------------------+
| * | **Ada**, **C#** (ASP.NET Core, Azure Functions), **C++** (Pistache, |
| * | Restbed, Qt5 QHTTPEngine), **Erlang**, **F#** (Giraffe), **Go**     |
| S | (net/http, Gin, Echo), **Haskell** (Servant, Yesod), **Java**       |
| e | (MSF4J, Spring, Undertow, JAX-RS: CDI, CXF, Inflector, Jersey,      |
| r | RestEasy, Play Framework,                                           |
| v | `PKMST <                                                            |
| e | https://github.com/ProKarma-Inc/pkmst-getting-started-examples>`__, |
| r | `Vert.x <https://vertx.io/>`__, `Apache                             |
| s | Camel <https://camel.apache.org/>`__,                               |
| t | `Helidon <https://helidon.io/>`__), **Julia**, **Kotlin** (Spring   |
| u | Boot, Ktor, Vertx), **PHP** (Laravel, Lumen, `Mezzio (fka Zend      |
| b | Expressive) <https://github.com/mezzio/mezzio>`__, Slim, Silex,     |
| s | `Symfony <https://symfony.com/>`__), **Python** (FastAPI, Flask),   |
| * | **NodeJS**, **Ruby** (Sinatra, Rails5), **Rust**                    |
| * | (`rust-server                                                       |
|   |  <https://openapi-generator.tech/docs/generators/rust-server/>`__), |
|   | **Scala** (Akka, `Finch <https://github.com/finagle/finch>`__,      |
|   | `Lagom <https://github.com/lagom/lagom>`__,                         |
|   | `Play <https://www.playframework.com/>`__, Scalatra)                |
+---+---------------------------------------------------------------------+
| * | **HTML**, **Confluence Wiki**, **Asciidoc**, **Markdown**,          |
| * | **PlantUML**                                                        |
| A |                                                                     |
| P |                                                                     |
| I |                                                                     |
| d |                                                                     |
| o |                                                                     |
| c |                                                                     |
| u |                                                                     |
| m |                                                                     |
| e |                                                                     |
| n |                                                                     |
| t |                                                                     |
| a |                                                                     |
| t |                                                                     |
| i |                                                                     |
| o |                                                                     |
| n |                                                                     |
| g |                                                                     |
| e |                                                                     |
| n |                                                                     |
| e |                                                                     |
| r |                                                                     |
| a |                                                                     |
| t |                                                                     |
| o |                                                                     |
| r |                                                                     |
| s |                                                                     |
| * |                                                                     |
| * |                                                                     |
+---+---------------------------------------------------------------------+
| * | `Apache2 <https://httpd.apache.org/>`__                             |
| * |                                                                     |
| C |                                                                     |
| o |                                                                     |
| n |                                                                     |
| f |                                                                     |
| i |                                                                     |
| g |                                                                     |
| u |                                                                     |
| r |                                                                     |
| a |                                                                     |
| t |                                                                     |
| i |                                                                     |
| o |                                                                     |
| n |                                                                     |
| f |                                                                     |
| i |                                                                     |
| l |                                                                     |
| e |                                                                     |
| s |                                                                     |
| * |                                                                     |
| * |                                                                     |
+---+---------------------------------------------------------------------+
| * | **GraphQL**, **JMeter**, **Ktorm**, **MySQL Schema**, **Protocol    |
| * | Buffer**, **WSDL**                                                  |
| O |                                                                     |
| t |                                                                     |
| h |                                                                     |
| e |                                                                     |
| r |                                                                     |
| s |                                                                     |
| * |                                                                     |
| * |                                                                     |
+---+---------------------------------------------------------------------+

`Data <https://drive.google.com/drive/folders/1ygWAEfmfqn2sWLKxw7ahPg0XzTZXVtVK?usp=share_link>`__
--------------------------------------------------------------------------------------------------

The data is currently stored in the data folder but will move towards
database storage.

The data outside the subdirectories contain example data with 1 minute
periods to get you started. However, the subdirectories contain
typically tick data, which is the most accurate data for backtesting;
whether it will serve you during your training process will depend
heavily on your target labeled feature and resources available. The data
is stored in the following format:

Project Focus: Code Integration, Review, and Optimization with Microservices Architecture
-----------------------------------------------------------------------------------------

Integration and Review
~~~~~~~~~~~~~~~~~~~~~~

In the early stages of the project, our primary focus is to integrate
and review the existing codebase to create a cutting-edge algorithmic
trading platform using a microservices’ architecture. We will:

1. Consolidate all scattered code from different branches and
   repositories.
2. Ensure consistent coding standards and practices across the entire
   codebase.
3. Design and implement a microservices architecture that enables
   modularity, flexibility, and scalability.
4. Identify and address potential security vulnerabilities within each
   service.

Optimization with Microservices
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Identify the different functionalities and services provided by your
code. Group related functionalities into separate microservices, keeping
in mind the principles of loose coupling and high cohesion.

Design your microservices:
^^^^^^^^^^^^^^^^^^^^^^^^^^

Define clear interfaces and APgenI contracts for each service. Determine
the data storage requirements for each service and decide whether to use
a shared database or a separate database per service.

Choose AWS services for deployment and management:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

AWS Elastic Container Service (ECS) or Elastic Kubernetes Service (EKS)
for container orchestration. AWS Lambda for serverless, event-driven
functions. API Gateway to manage and expose your APIs securely. Amazon
RDS, DynamoDB, or other AWS database services for data storage.

Set up CI/CD pipelines:
^^^^^^^^^^^^^^^^^^^^^^^

AWS CodePipeline, CodeBuild, and CodeDeploy to automate the build, test,
and deployment process for each microservice.

Implement monitoring and logging:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Amazon CloudWatch for monitoring and logging. Set up alarms and
notifications to alert you when there are issues with your services.

Implement security best practices:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Secure your microservices with proper authentication and authorization
using Amazon Cognito or a custom solution. Use AWS Identity and Access
Management (IAM)

Collaboration and Communication
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We encourage active collaboration among team members through:

1. Shared communication channels. (In Progress)
2. Regular virtual meetings to discuss progress, challenges, and
   opportunities for improvement.
3. Utilizing a project management tools for task tracking and
   prioritization.
4. Creating and maintaining comprehensive documentation to support
   onboarding and knowledge sharing, including documentation for each
   microservice.

| `CONTRIBUTING.md <CONTRIBUTING.md>`__ (Set Up In Progress)
| `CODE_OF_CONDUCT.md <CODE_OF_CONDUCT.md>`__
| `Risk and Performance
  Disclaimer <RISK_AND_PERFORMANCE_DISCLAIMER.md>`__

Introduction to the Platform Features
-------------------------------------

Welcome to our state-of-the-art trading platform, currently in
development, designed to provide a comprehensive and versatile trading
environment tailored to the needs of a diverse user base. Our platform
focuses on enhancing user experience, streamlining the trading process,
and facilitating continuous learning and improvement. In this section,
we will provide an overview of the key features under development that
will set our platform apart and contribute to its robust capabilities
once completed.

Our platform encompasses a wide range of features to address essential
aspects of the trading process, such as security, education, and market
analysis. These features, while still in early development stages, have
been meticulously designed to cater to users with varying needs and
preferences, ensuring a seamless and satisfying trading experience for
all upon completion.

For a detailed explanation of each feature and its benefits, please
refer to the PaaS Proposal or read through the
`COMPREHENSIVE_PLATFORM_FEATURES.md <COMPREHENSIVE_PLATFORM_FEATURES.md>`__
file. This comprehensive guide will help you explore and better
understand the full potential of our innovative trading platform as it
progresses through development.

| - Trading Features: \\
| - - Sophisticated Order Types \\
| - - Automated Trading and Order Execution \\
| - - Multi-Asset Support and Portfolio Management \\
| - - Robust Risk Management Functionality \\
|  \\
| - Data and Analytics: \\
| - - Comprehensive Backtesting Capabilities \\
| - - Dynamic Historic and Live Data Transformation and Labeling \\
| - - Real-time Market Sentiment Analysis \\
| - - Performance Analytics and Reporting \\
|  \\
| - Machine Learning and AI: \\
| - - State-of-the-Art Machine Learning Model Inference and AI Agent
  Training \\
| - - Natural Language Processing and Large Language Models for Enhanced
  User Assistance \\
|  \\
| - User Experience and Accessibility: \\
| - - User-friendly Interface and Customizable Dashboards \\
| - - Mobile and Web Accessibility \\
| - - Custom Alerts and Notifications \\
|  \\
| - Education and Community: \\
| - - Interactive Educational Resources and Community Support \\
| - - Paper Trading and Simulation Environment \\
|  \\
| - Integration and Flexibility: \\
| - - Flexible Custom Python Strategy Deployment \\
| - - Integration with External Tools and Services \\
|  \\
| - Security and Compliance: \\
| - - Advanced Security Measures and Regulatory Compliance
