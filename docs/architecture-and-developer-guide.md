# AWS Greengrass IoT Pub Sub Framework

## Application Architecture and Developer Guide.

- [AWS Greengrass IoT Pub Sub Framework](#aws-greengrass-iot-pub-sub-framework)
  * [Application Architecture and Developer Guide.](#application-architecture-and-developer-guide)
    + [AWS Greengrass V2 Overview](#aws-greengrass-v2-overview)
    + [AWS Greengrass Component Patterns](#aws-greengrass-component-patterns)
    + [AWS Greengrass PubSub Message Bus (IPC / MQTT)](#aws-greengrass-pubsub-message-bus--ipc---mqtt-)
    + [Anatomy of the AWS Greengrass IoT PubSub Framework](#anatomy-of-the-aws-greengrass-iot-pubsub-framework)
    + [PubSub Topic Schema](#pubsub-topic-schema)
    + [PubSub Message Patterns](#pubsub-message-patterns)
    + [1 to 1 On Demand Synchronous Request](#1-to-1-on-demand-synchronous-request)
    + [Fan-Out On Demand Synchronous Request](#fan-out-on-demand-synchronous-request)
    + [1 to 1 On Demand Asynchronous Request](#1-to-1-on-demand-asynchronous-request)
    + [Fan-Out On Demand Asynchronous Request](#fan-out-on-demand-asynchronous-request)
    + [Unsolicited Updates](#unsolicited-updates)
    + [PubSub Access Policy](#pubsub-access-policy)
    + [PubSub Subscription Policy:](#pubsub-subscription-policy-)
    + [PubSub Publish Policy](#pubsub-publish-policy)
    + [PubSub Message Format](#pubsub-message-format)
    + [Message Formatting:](#message-formatting-)
  * [Features and Functionality](#features-and-functionality)
    + [Application Properties Dependency Injection](#application-properties-dependency-injection)
    + [PubSub Topic Schema](#pubsub-topic-schema-1)
    + [Property Dependency Injection](#property-dependency-injection)
    + [PubSub Access Policy](#pubsub-access-policy-1)
    + [PubSub Convenience Classes](#pubsub-convenience-classes)
    + [Message Publishing](#message-publishing)
    + [PubSub Message Concurrency](#pubsub-message-concurrency)
    + [PubSub Message Routing](#pubsub-message-routing)
    + [PubSub Message Formats](#pubsub-message-formats)
    + [Request Message](#request-message)
    + [Response Message](#response-message)
    + [Update Message](#update-message)
    + [Main Module](#main-module)
    + [Application Workflows](#application-workflows)
  * [Applying the Framework Architecture (Made Easy)](#applying-the-framework-architecture--made-easy-)

Event-driven applications are all but synonymous with the Publish / Subscribe (PubSub) model where loosely coupled services communicate via event triggered messages. Events can be described by a number of real-time triggers but are often associated with Internet of Things (IoT) devices and so event-driven PubSub applications find a natural affinity with distributed IoT solutions.   

The PubSub model supports a range of asynchronous 1-to-1 and 1-to-Many message patterns that overcome numerous well-known (and long suffered) limitations of REST APIs and offer the developer considerable flexibility. Accordingly, event-driven applications are seen to offer flexibility in design and are well suited to highly scalable, real-time distributed IoT systems.  

However, this flexibility puts a lot of design decisions in the hand of the developer and can create dependencies across distributed systems. The following diagram highlights just how much the PubSub model leaves to unstructured fields for the developer to consider compared to the more defined control fields of REST APIs.

![rest-vs-pubsub](/images/rest-vs-pubsub.png)

The result is PubSub applications provide greater flexibility but require more design effort. The AWS Greengrass IoT PubSub Framework addresses this with consistent design patterns and boiler plate code so developers can focus on application logic when building distributed IoT applications with AWS Greengrass V2 custom components.

The following sections describe in detail the design patterns, architecture and a developer guide for those working with the AWS IoT PubSub Framework. 

### AWS Greengrass V2 Overview
Before we get started, it’s worth while providing a brief overview of AWS Greengrass V2 itself and a description of the individual features. For more detail, see the [AWS Greengrass V2 Developer Guide](https://docs.aws.amazon.com/greengrass/v2/developerguide/what-is-iot-greengrass.html).

![gg-overview](/images/gg-overview.png)

1.  **AWS IoT Core:** The AWS cloud hosted IoT services that provides a scalable device gateway for message processing and an interface to the variety of AWS data and analytics, messaging and notification, logging and storage services that integrate to the AWS IoT Core.

3.  **AWS Greengrass Core:** The edge device running the AWS Greengrass V2 runtime agent that provides the physical resources and interfaces to the real world. Acts as both a gateway and IoT edge device.

5.  **AWS Greengrass V2 Runtime:** The AWS Greengrass agent that runs on remote cores and enables OTA deployment of component groups as well as inter-component communications, messaging to AWS IoT Core platform and remote device management, logging and status updates.

7.  **AWS Greengrass V2 Deployment**: Groups of services (known in AWS Greengrass V2 as components) and metadata that defines which remote AWS IoT Greengrass Core (Edge devices) to deploy components, the code itself and a set of security policies and configurations to apply. Data driven configuration for each component within the deployment is provided by a JSON configuration file that is provided as an AWS Greengrass V2 recipe.

9.  **AWS Greengrass V2 Component:** Is a code module (and dependencies) in any native language supported by the AWS Greengrass core that is deployed and managed Over the Air (OTA) by the AWS IoT Greengrass platform. This can be considered as a service or the most granular level of separation of application functionality in the AWS Greengrass V2 framework.

11. **AWS Greengrass V2 Recipe:** Provides metadata and configuration parameters for an AWS IoT Greengrass V2 Component.

13. **IPC Topic / MQTT PubSub Message Bus:** The AWS Greengrass IPC Topic and MQTT PubSub message bus that enables topic-based messaging between AWS Greengrass V2 Components and the AWS IoT Core respectively.

### AWS Greengrass Component Patterns

It helps with design consistency to classify each function of a distributed system into categories. For example, event-driven application architectures typically classify functions as event producers or event consumers. Extending this thought process, AWS Greengrass V2 components will generally fall into one of the following categories:

* **Application Control:** Application control such as bootstrap and initialisation services that configure or trigger other components and functionality.
* **Data Source:** Services that source data, optionally filter, transform or process and then post to the message bus. Data typically originates from sensors, the IoT Core, data base and data caches (key/value pair data) and in some case other components.
* **Data Sink:** Includes functions that accept or request data from another component for monitoring (listening to a temperature or pressure sensor) or to process and store.
* **Actuators:** Provide a PubSub interface to physical controllers and actuators.
* **Computational:** Preforms computationally heavy processes within the application such as statistical analysis and machine learning processes.
* **Interface and Messaging:** Manages messaging to and from external interfaces and systems. 

The AWS Greengrass IoT PubSub Fremework makes use of these classifications in describing message workflows and formats.

### AWS Greengrass PubSub Message Bus (IPC / MQTT) 
The AWS Greengrass V2 [InterProcess Communication (IPC)](https://docs.aws.amazon.com/greengrass/v2/developerguide/interprocess-communication.html) system has separate SDKs for PubSub messaging between components local to the Greengrass device that we refer to here as **IPC Topic** or just **IPC** messaging and PubSub messages over the Internet to the AWS IoT Core using the [MQTT protocol](https://mqtt.org/) that we refer to here as **IPC MQTT** or just **MQTT** messaging.  

In this framework, the topic schema and publish / subscribe rules are replicated and applied equally to both methods but it is important to understand the distinction when developing AWS Greengrass custom components.

### Anatomy of the AWS Greengrass IoT PubSub Framework

The AWS Greengrass IoT PubSub Framework provides a consistent PubSub topic schema, message workflows, formats and common coding patterns. The application architecture is practically applied through a template AWS Greengrass component skeleton found in the [src](/src) directory which comes with AWS Greengrass Deployment (GDK) config.

The AWS Greengrass IoT PubSub Framework component skeleton

```text
aws-greengrass-labs-iot-pubsub-framework
└── src                                          <--- Greengrass component artifacts source directory
    ├──  pubsub                                  <-- PubSub SDK Wrappers
    │    ├── ipc_pubsub.py                       <-- IPC Topic PubSub Wrapper
    │    ├── mqtt_pubsub.py                      <-- MQTT Topic PubSub Wrapper
    │    └── pubsub_messages.py                  <-- PubSub Message Format definition
    └── greengrass-tools-config.json             <-- AWS GDK build / publish config
    └── main.py                                  <-- Message processing and main application logic
    └── recipe.json                              <--- AWS Greengrass component recipe
```

* [**greengrass-tools-config.json:**](/src/greengrass-tools-config.json) AWS Greengrass Deployment Kit (GDK) configuration file. 

* [**main.py:**](/src/main.py) Main method of the AWS Greengrass Application Template. Provides a PubSub message callback and per topic message routers and processors to simplify and standardised message processing. 

* [**recipe.json:**](/src/recipe.json) A Template [AWS Greengrass Component Recipe](https://docs.aws.amazon.com/greengrass/v2/developerguide/component-recipe-reference.html) with pre-defined config that manages the PubSub topic schema, access policy and other parametrised fields.

* [**ipc_pubsub.py:**](/src/pubsub/ipc_pubsub.py) A convenience wrapper around the AWS Greengrass [InterProcess communication (IPC)](https://docs.aws.amazon.com/greengrass/v2/developerguide/interprocess-communication.html) library. This initialises the SDK to publish and subscribe to the prescribed topic schema for communication between AWS Greengrass components.

* [**mqtt_pubsub.py:**](/src/pubsub/mqtt_pubsub.py) As for IPC PubSub, however; the MQTT SDK is responsible for publishing and subscribing to messages using the MQTT protocol between the Greengrass component and the AWS IoT Core platform. 

* [**pubsub_messages.py:**](/src/pubsub/pubsub_messages.py) Provides a consistent PubSub message format with defined request / response, message routing and tracing fields.

### PubSub Topic Schema
One of the first decisions to make when developing a PubSub application is the IPC/MQTT topics that will be used for communications between individual components and the central hub / gateway (The AWS IoT Core in this case). A well-defined PubSub topic schema avoids recursive messages and inter-service dependencies. This framework prescribes a PubSub Topic Schema and PubSub Message Patterns with a small set of pre-defined topics that perform specific functions as described below.

Prescribed PubSub Topics:

* **Service Topic:** Messages to the service (Greengrass component) itself such as status and data request messages.
* **Data Topic:** Publishing data such as sensor data that other components can subscribe to.
* **Broadcast Topic:** A system wide broadcast typically to manage components or systems errors.  

If applied consistently across all Greengrass components in the application stack; this forms a common set of communications channels to simplify application design.

### PubSub Message Patterns

This framework defines message workflows for short and long-lived processes as well as 1-to-1, Fan-In (many-to-1) and Fan-Out (1-to-many) patterns. Messages requesting data or triggering short lived actions simulate a synchronous request, whereas requesting longer lived processes require an asynchronous workflow. 

In reality; all messages in the PubSub model are asynchronous, but it is beneficial for developers to have the language to describe requests that are expected to be blocking or non-blocking in the application logic. The same is true for describing the topics that will be used for specific request types. 

By using a series of consistent design patterns for messaging, we can approximate the functionality of the more defined REST API without losing the flexibility of asynchronous and Fan-In / Fan-Out communications across distributed systems. 

In general, the message patterns we consider possess a combination of the following characteristics:
* **On-Demand or Unsolicited:** Describes a Request/Response message pattern compared to a periodic or externally triggered update.
* **Synchronous / Asynchronous:** Indicates if a request, task or process is long-lived and if the requesting component should expect long wait times or an immediate response or error message. This is useful when deciding on blocking or non-blocking workflows in the application logic.
* **Unicast / Broadcast Pattern:** 
    * 1-to-1: Direct message from one component to another
    * Fan-Out: 1-to-Many messages
    * Fan-In: Mant-to-1 messages. 

The following sections describe the common message patterns used by this framework. 

### 1 to 1 On Demand Synchronous Request
The simplest of the message patterns, this is to request data or trigger a short-lived action or process between AWS Greengrass components in a way that simulates a synchronous request. By specifying a message is synchronous, the receiving component is expected to provide an immediate response or error message if the request fails.

![message-1-to-1-sync](/images/message-1-to-1-sync.png)

The Message workflow is as follows:
* **REQUEST**: Made to the data-source component **Service Topic**
* **RESPONSE 200 OK**: 200 OK or error on the data-source component **Data Topic**.

As example of this message type is requesting a value from a connected temperature sensor to a component that actions an environmental control system. 

### Fan-Out On Demand Synchronous Request
Fan-Out On Demand Synchronous Request follows the same pattern as the 1-to-1 equivalent but the request is made by a control component and many interested components are listening on the data-source component **Data Topic** to process the response. The controller may also listen for the response. 

![message-fanout-sync](/images/message-fanout-sync.png)

 The message workflow is as per the 1-to-1 Synchronous Request.

Using the same example of requesting a reading from a connected temperature sensor, this message type can be used if other interested components responsible for logging and an alarm/alert threshold component also need to receive the data for their individual functions. 

### 1 to 1 On Demand Asynchronous Request
Asynchronous messages follow the same topics for request and response as the synchronous equivalent, but the workflow differs to include an immediate response to acknowledge the request was received and an asynchronous response to return the requested data or to confirm that the long-lived action or process has competed. 

![message-1-to-1-async](/images/message-1-to-1-async.png)

The Message workflow for Asynchronous or long-lived processes is as follows:
* **REQUEST**: Send to the data-source **Service Topic**
* **RESPONSE 202 ACK**: is returned immediately with 202 Acknowledge or an error on the data-source components **Data Topic**. A data payload may be included with details such as the expected duration of the long-lived request.
* **RESPONSE 200 COMPLETE**: is returned with 200 OK / Complete or an error on the data-source components **Data Topic** once the long-lived process is complete and may contain the data payload of the request.

As example of this message type is requesting a stepper motor move a number of steps (actuator component type) that is expected to take an extended period to compete. 

### Fan-Out On Demand Asynchronous Request
As per the 1-to-1 On Demand Asynchronous Request but the request is made by a control component and many interested components are listening on the data-source component **Data Topic** to receive the response. The controller may also listen for the response. 

![message-fanout-async](/images/message-fanout-async.png)

The message workflow is as per the 1-to-1 On-Demand Asynchronous Request.

### Unsolicited Updates
Unsolicited updates are messages that are not triggered in response to a request from another component. They may be periodic / timed or in response to some external trigger such as an out of threshold sensor reading. Unsolicited Updates can be 1-to-1, Fan-In or Fan-Out.  

![message-unsolicited](/images/message-unsolicited.png)

### PubSub Access Policy

AWS Greengrass provides a PubSub topic-based access policy to protect components from intentionally or unintentionally publishing or subscribing to unauthorised PubSub topics. This prevents unauthorised components listening in or injecting spurious or malicious messages into the AWS Greengrass application message bus.
 
### PubSub Subscription Policy:
This framework applies the following PubSub topic **SUBSCRIBE** rules to all Greengrass components:
1.  Each component must subscribe to its own **Service Topic** and is the only one that listens on this topic making it a means to send 1-to-1 messages, to request status updates and data requests.
2.  No component may subscribe to the **Service Topic** of another component.
3.  Each component must subscribe to the **Broadcast Topic**. This is a system wide control mechanism that may be for critical shutdown or update of all component or to request a restart.
4.  Each component subscribes to the **Data Topic** of any other component that have interesting messages. For example, a temperature monitoring and control component would subscribe to the **Data Topic** of the Temperature Sensor component to listen for temperature values.
5.  Developers can add custom topic with self-determined access policies as needed.

### PubSub Publish Policy
This framework applies the following PubSub topic **PUBLISH** rules to all Greengrass components:
1.  A component is not permitted to publish to its own **Service Topic**. The component itself is the only resource that should be listening and so may cause a recursive update.
2.  All components are permitted to publish to their own **Data Topic**. However, a component doesn't control (or know, or care) what components listen to their **Data Topic**. This is consistent with event-driven application architecture.
3.  No component may publish to another components **Data Topic**. This is implied to be data from the that component only.
4.  All components are permitted to publish to the **Broadcast Topic**. There is no hierarchy on the broadcast topic (unless applied in application logic), all broadcast messages are considered equal. Care should be taken on responding to broadcast messages that may result in a recursive update.
5.  A component may publish to another components **Service Topic**. This may be to request data, status updates or send 1-to-1 messages.
 
![pubsub-access-policy](/images/pubsub-access-policy.png)

### PubSub Message Format
As with the PubSub Topic schema, a policy is needed for message payload type and size that all AWS Greengrass V2 Components adhere to so consistent behaviour is seen across the distributed application.

In this framework the PubSub message processing is performed by the convenience classes within **ipc_pubsub.py** and **mqtt_pubsup.py** for IPC topic and MQTT IoT Core messaging respectively.

### Message Formatting:
Both the IPC Topic and MQTT IoT Core PubSub convenience classes expect all messages to be serialised as valid JSON and are parsed into python objects on reception. If invalid JSON, binary, plain text or other formatted message payloads are received the given service will throw an error with a default behaviour of logging and gracefully discarding the message. You can of course as the developer extend this behaviour to update a central component or perform some other action. If a service needs to post binary data it should parse to Base64 and send in the JSON payload remembering that MQTT messages are limited to 8KBs in size. 

## Application Properties Dependency Injection

In AWS Greengrass V2, the [Component Recipe](https://docs.aws.amazon.com/greengrass/v2/developerguide/component-recipe-reference.html) defines various parameters and lifecycle events for the Greengrass component. The component recipe is JSON formatted and can pass in configuration and metadata to the service. This includes the components functional name, version, description, PubSub access policy and provides a **DefaultConfiguration** tag for JSON fields that can be passed to the Greengrass component application logic. 

The AWS Greengrass IoT PubSub Framework defines a DefaultConfiguration field called **GGV2ComponentConfig** in which all configuration values are passed to the components application logic. Apart from enforcing consistent design patterns, this config driven approach allows updates of common PubSub application properties and topic schema without the need for application or code updates. 

i.e:
```
"RecipeFormatVersion": "2020-01-25",
"ComponentName": "aws-greengrass-iot-pubsub-framework",
"ComponentVersion": "0.0.1",
"ComponentDescription": "AWS Greengrass V2 IoT PubSub Framework recipe skeleton with prescribed IPC and MQTT Topics.",
"ComponentPublisher": "Dean Colcott: <https://www.linkedin.com/in/deancolcott/>",
"ComponentConfiguration": {
  "DefaultConfiguration": {
    "GGV2ComponentConfig": {
    [Parameterised application configuration......]
```

### PubSub Topic Schema
As previously described, the AWS Greengrass IoT PubSub framework defines three common topics to address most common PubSub message patterns:

* **Service Topic:** Messages to the service itself such as status and 1-to-1 data or action request messages.
* **Data Topic:** Publishing data such as sensor data that other components can subscribe to.
* **Broadcast Topic:** A system wide broadcast typically to manage components or systems errors.

These are defined in the template component recipe as below
```
"DefaultConfiguration": {
  "GGV2ComponentConfig": {
    "mqtt_pubsub_timeout" : 5,
    "mqtt_service_topic" : "aws-greengrass-iot-pubsub-framework/mqtt/service",
    "mqtt_data_topic" : "aws-greengrass-iot-pubsub-framework/mqtt/data",
    "mqtt_broadcast_topic" : "com.example.my_project/mqtt/broadcast",
    "mqtt_subscribe_topics" : ["aws-greengrass-iot-pubsub-framework/mqtt/service", "com.example.my_project/mqtt/broadcast"],
    "ipc_pubsub_timeout" : 5,
    "ipc_service_topic": "aws-greengrass-iot-pubsub-framework/ipc/service",
    "ipc_data_topic" : "aws-greengrass-iot-pubsub-framework/ipc/data",
    "ipc_broadcast_topic" : "aws-greengrass-iot-pubsub-framework/ipc/broadcast",
    "ipc_subscribe_topics" : ["aws-greengrass-iot-pubsub-framework/ipc/service", "com.example.my_project/ipc/broadcast"]
  }
```
The Main module reads in and parameterises the individual topics and passes them to the IPC and MQTT PubSub modules which automatically initialises the required publishers and topic subscriptions. Parametrising the PubSub topic schema enforces consistency across components and solves the challenge of updating the applications topic schema without the need for code changes. If applied equally across all Greengrass components in a distributed IoT application; this forms a common set of communications channels to simplify development and greatly reduces dependencies and design decisions needed to get started.

You can of course, extend this or any part of the GGV2ComponentConfig object to add your own config parameters.

### PubSub Access Policy

The Greengrass component recipe defines the components PubSub access policy. The recipe template has been configured to follow the PubSub Access Policy recommended in this framework. The PubSub access policy configured in the recipe template is automatically applied to the component as its deployed to the Greengrass core device/s.

e.g:
```
"accessControl": {
  "aws.greengrass.ipc.pubsub": {
    "com.example.simple_component:publish:1": {
      "policyDescription": "Allows access to publish to the component IPC data topic and application IPC broadcast topic (and / or others as required).",
      "operations": [
        "aws.greengrass#PublishToTopic"
      ],
      "resources": [
        "com.example.simple_component/ipc/data",
        "com.example/ipc/broadcast"
      ]
    },
    "com.example.simple_component:subscribe:1": {
      "policyDescription": "Allows access to subscribe to the component IPC service topic and application IPC broadcast topic (and / or others as required).",
      "operations": [
        "aws.greengrass#SubscribeToTopic"
      ],
      "resources": [
        "com.example.simple_component/ipc/service",
        "com.example/ipc/broadcast"
      ]
    }
  },

```

### Property Dependency Injection
The parameterised fields of the framework’s recipe template described for topic schema and access policies are passed to the component application logic in the **Lifecycle >> Run** field where we set main.py to call on start-up and pass the GGV2ComponentConfig object as configuration to the application.

```
"Lifecycle": {
  "Run": {
    "Script": "python3 -u {artifacts:path}/main.py '{configuration:/GGV2ComponentConfig}'",
    "RequiresPrivilege": "false"
  }

```
**Note:** You can configure the component to run with root privileges by setting the **RequiresPrivilege** field to **True**

And finally, in main.py of the application template, we accept the GGV2ComponentConfig as sys.argv[1], parse it to a Python Object and provide it to the AwsGreengrassV2Component class.

```
if __name__ == "__main__":

  try:
      ggv2_component_config = json.loads(sys.argv[1])
      ggv2_component = AwsGreengrassV2Component(ggv2_component_config)

      ........
```

## PubSub Convenience Classes
The application template provides wrappers for the [AWS Greengrass V2 IPC and MQTT PubSub SDKs](https://docs.aws.amazon.com/greengrass/v2/developerguide/interprocess-communication.html) which subscribe to the required topics and initialises publish capabilities as needed. This is the ipc_pubsub.py and mqtt_pubsub.py modules in the application template. 

While source access is provided for the PubSub wrappers, they have been developed to be largely self-sufficient and expected to provide their required functionality of simplified access to the IPC/MQTT SDKs without any user interaction. 

The PubSub convenience classes are initialised from the components main method and are passed:
1.  The required publish and subscribe topics and a timeout value from the component recipe template and
2.  A message callback for any received messages.

i.e (main.py):
```
log.info('Initialising IPC Topic PubSub inter-service messaging.')
self.ipc_pubsub = IpcPubSub(self.pubsub_message_callback, self.ipc_subscribe_topics, self.ipc_pubsub_timeout)

log.info('Initialising IPC MQTT IoT Core PubSub messaging.')
self.mqtt_pubsub = MqttPubSub(self.pubsub_message_callback, self.mqtt_subscribe_topics, self.mqtt_pubsub_timeout)
```
All received PubSub messages are passed from the PubSub wrappers to the **pubsub_message_callback** function in main.py of the application template. This is the primary method by which the user should not generally need to make any changes to the PubSub wrappers, they work in the background and pass received messages back to Main where the user’s application logic is applied. 

![pubsub-classes](/images/pubsub-classes.png)

## Message Publishing

The PubSub Wrapper classes also provide a **publish_to_topic** function and the main method parameterises the SDK (IPC or MQTT) to allow simple selection of the SDK to publish a message.

i.e (main.py):
```
    ##################################################
    ### PubSub Message Publisher
    ##################################################

    def publish_message(self, sdk, topic, message)

```

### PubSub Message Concurrency
The PubSub wrappers are not threaded and so any **RECEIVED** message will block the message bus for the duration it is being processed. The developer is responsible for considering the need for concurrency when processing received messages. 

Alternatively, the PubSub wrappers use Python concurrent.futures and a ThreadPoolExecutor to **PUBLISH** messages providing concurrency up to the number of threads supported by the core device. The reason for this is to break a protentional thread lock / timeout if a received PubSub message triggers a new message to be published.

### PubSub Message Routing
Distributed PubSub applications can quickly become difficult to manage if the topic schema is not well defined and an efficient and repeatable message handling system in place. As the number of topics receiving messages increases, so does the complexity of the application logic. The AWS Greengrass IoT PubSub Framework solves this with a system that approximates that of a REST based API with a single message callback that validates and normalises incoming messages and then a series of message routers and processors. This simplifies message handling and scales to meet the needs of very simple to very sophisticated applications. 

![pubsub-sub-routing](/images/pubsub-sub-routing.png)

The component framework has predefined message routers and processors for the recommended Service, Data and Broadcast topics. To extend to handle additional topics, just copy the patterns used for these.

i.e main.py:
```
    
    ##################################################
    ### PubSub Topic Message Callback
    ##################################################

    def pubsub_message_callback(self, topic, payload):
        ……
    
    ##################################################
    ### PubSub Topic Message Routers.
    ################################################## 

    # AWS Greengrass Application SDK prescribed topic routers.  
    def ipc_service_topic_router(self, message_id, reqres, command, message):
      ……

    def mqtt_service_topic_router(self, message_id, reqres, command, message):
      ……

    def application_broadcast_topic_router(self, message_id, reqres, command, message):
      ……

    ##################################################
    ### PubSub Message Processors.
    ##################################################    

    def ipc_service_topic_request(self, message_id, reqres, command, message):
      ……

    def ipc_service_topic_response(self, message_id, reqres, command, message):
      ……

    def mqtt_service_topic_request(self, message_id, reqres, command, message):
      ……

    def mqtt_service_topic_response(self, message_id, reqres, command, message):
      ……
```

### PubSub Message Formats

In general, the PubSub model provides greater flexibility than a REST interface which has more defined control fields. The trade-off is that developers need to design and agree on individual message tracking, return path, message routing and type fields for each application.

Defining message formats for payload, control and routing fields influences many design decisions and ultimately forms a major part of interface contracts. This process can grind even a simple application to a halt with dependencies between components, systems and teams. The AWS Greengrass IoT PubSub Framework solves this problem by providing a defined message format for REQUEST, RESPONSE and UPDATE message types that have been developed in support of the frameworks prescribed means of PubSub message routing and processing. 

The message formats are defined in the **pubsub_messages.py** module that offer simple parametrised functions that returns well formatted messages in JSON serializable form.  Applying these formats equally across all components of the distributed IoT application avoids the never-ending interface contract negotiations and updates. 

e.g (pubsub_messages.py):
```
class PubSubMessages():

    def get_pubsub_request(self, command, reply_topic, reply_sdk='ipc', params=None):
      # Return a well formatted PubSub REQUEST
      ....

    def get_pubsub_response(self, message_id, command, status, data=None):
      # Return a well formatted PubSub RESONSE
      ....

    def get_pubsub_update(self, command, status, data=None):
      # Return a well formatted PubSub UPDATE
      ....
```

### Request Message
Example REQUEST message asking for the value of a connected temperature sensor on a receiving component. 
```

request = {
  "message-id" : "20210805191652125786",                # Generated Timestamp / ID to track the request flow.
  "reply-sdk" : "ipc",                                  # Reply SDK (MQTT Core or IPC topic between Greengrass components.)
  "reply-topic" : "com.example.rx_component/ipc/data",  # IPC / MQTT Topic the response should be published to.
  "reqres" : "request",                                 # Indicates is a REQUEST message type to aid application routing.
  "command" : "temp_sensor_request",                    # Command indicating the data or action that is being requested.
  "params" : {                                          # Optional params specific to the request type
      "units" : "celsius",
      "temp_sensor_id" : "sens_28a"
  }
}
```
Notice in the REQUEST message the **reply-sdk** ('ipc' or 'mqtt') and **reply-topic** fields. These allow the requesting message to nominate where any response message should be published to. This removes another dependency on the requesting component to interact with upstream systems if they update or change the local topic schema. 

The below demonstrates how to build and publish the example well-formatted REQUEST PubSub message using the AWS Greengrass IoT PubSub Framework.
```

#### Create a well formatted REQUEST message #####

# Specify the requested command and param fields to send in the REQUEST.
command = 'temp_sensor_request'
params = {
  "units" : "celsius",
  "temp_sensor_id" : "sens_28a"
}

# Specify the reply Topic and SDK (ipc or mqtt) any associated RESPONSE should be returned on.
# e.g (is most common to request a return on the receiving components Data Topic):
reply_sdk = 'ipc'
reply_topic = 'com.example.rx_component/ipc/data'

# Create the well-formatted REQUEST message object
request_message = self.pubsub_messages.get_pubsub_request(command, reply_topic, reply_api, params)

#### Publish the REQUEST Message #####
# is most common to publish a REQUEST on the receiving components Service Topic.

publish_sdk='ipc'
publish_topic = 'com.example.my_project.rx_component/ipc/service'
self.publish_message(publish_sdk, publish_topic, request_message)

```

### Response Message
Example RESPONSE message to the request asking for the value of a connected temperature sensor. 
```
response = {
  "message-id" : "20210805191652125786",                # Value is reflected from the request to track response.
  "reqres" : "request",                                 # Indicates is a REQUEST message type to aid application routing.
  "command" : "temp_sensor_request",                    # Value is reflected from the request to assist routing
  "response": {                                         # Response with optional response data and mandatory status fields.
      "data": {                                         # Response Data field None or customisable to data request.
        "temp_sensor_id" : "sens_28a",
        "units" : "celsius"
        "temp" : 22.5
      },
      "status": 200                                     # Response status code: 200, 202, 404, 500
  }
}
```

In the RESPONSE message, the message_id and command field are reflected from the requesting message. This allows message tracking across request/response flows for any listening component.

The below demonstrates how to build and publish the example well-formatted RESPONSE PubSub message using the AWS Greengrass IoT PubSub Framework.
```

#### Create a well formatted RESPONSE message #####

# Get the REQUESTing message message_id and command field to reflect in the RESPONSE for message tracking.
message_id = request_message['message-id']
command = request_message['command']

# Get the REQUESTing message reply_sdk and reply_topic to return the RESPONSE on.
reply_sdk = request_message['reply-sdk']
reply_topic = request_message['reply-sdk']

# Build the response data and status objects
# e.g:
status = 200
data = {
  "temp_sensor_id" : "sens_28a",
  "units" : "celsius"
  "temp" : 22.5
}

# Create the well-formatted RESPONSE message object
response_message = self.pubsub_messages.get_pubsub_response(message_id, command, status, data)

#### Publish the RESPONSE Message #####
self.publish_message(reply_sdk, reply_topic, response_message)

```

### Update Message
Example UPDATE that periodically publishes local time from the component
```
{
  "message-id": "20210805193646037205",                 # Generated Timestamp / ID to track the request flow.
  "reqres": "update",                                   # Indicates is a UPDATE message type to aid application routing.
  "command": "date_time_update",
  "response": {                                         # Response with optional response data and mandatory status fields
    "data": {                                           # Response Data field None or customisable to data request.
      "device": "iot-time-device01",
      "local-time": "19:36:46"
    },
    "status": 200                                         # Response status code: 200, 500
  }
}
```

As the developer, you are free to extend on these message formats as long as the key tracking and routing fields are not removed.

## Main Module

The final piece of the AWS Greengrass IoT PubSub framework is the main module. This is called on component boot-up (as nominated by the template component recipe). The Main module provides the PubSub message callback and message processing and routing functions. In a larger production application, you may choose to separate message routers and processors completely or for groups of related functions to an external module. 

### Main Application Workflows
The Main module offers two application workflows. The first, is the main process loop that is called after initialisation is complete. This is the **service_loop** function and is where the component process is held up with a slow loop and where any application logic for the component should be managed from.

e.g main.py:
```
    def service_loop(self):
        '''
        Put service specific application logic in the loop here. This also holds the 
        component process up so keeps the loop with a small sleep delay even if the 
        component is event driven based on IPC / MQTT PubSub messaging.
        '''
```
The second workflow is message / event driven where application logic is applied purely in response to PubSub message events in the message processors. It’s possible (and common) that application logic is in both the service_loop and event / message driven workflows.

At this point you have both an Event Driven and application process loop to develop against with well-defined message patterns and workflows. Try the examples to learn more, otherwise Happy Hacking! 


