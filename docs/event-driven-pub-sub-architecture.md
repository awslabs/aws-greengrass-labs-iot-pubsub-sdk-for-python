# AWS Greengrass Application Framework
## Event Driven IoT PubSub Application Architecture with AWS Greengrass V2

- [Event Driven IoT PubSub Application Architecture with AWS Greengrass V2](#event-driven-iot-pubsub-application-architecture-with-aws-greengrass-v2)
- [AWS Greengrass V2 Overview](#aws-greengrass-v2-overview)
- [AWS Greengrass Component Patterns](#aws-greengrass-component-patterns)
- [AWS Greengrass PubSub Message Bus (IPC / MQTT)](#aws-greengrass-pubsub-message-bus--ipc---mqtt-)
- [PubSub Topic Schema](#pubsub-topic-schema)
- [PubSub Message Patterns](#pubsub-message-patterns)
  * [1 to 1 On Demand Synchronous Request](#1-to-1-on-demand-synchronous-request)
  * [Fan-Out On Demand Synchronous Request](#fan-out-on-demand-synchronous-request)
  * [1 to 1 On Demand Asynchronous Request](#1-to-1-on-demand-asynchronous-request)
  * [Fan-Out On Demand Asynchronous Request](#fan-out-on-demand-asynchronous-request)
  * [Unsolicited Updates](#unsolicited-updates)
- [PubSub Access Policy](#pubsub-access-policy)
  * [PubSub Subscription Policy:](#pubsub-subscription-policy-)
  * [PubSub Publish Policy](#pubsub-publish-policy)
- [Applying the Framework Architecture (Made Easy)](#applying-the-framework-architecture--made-easy-)

## Event Driven PubSub Applications

Event-driven applications are all but synonymous with the Publish / Subscribe (PubSub) model where loosely coupled services communicate via event triggered messages. Events can be described by a number of real-time triggers but are often associated with Internet of Things (IoT) devices and so event-driven PubSub applications find a natural affinity with distributed IoT solutions.   

The PubSub model supports a range of asynchronous 1-to-1 and 1-to-Many message patterns that overcome numerous well-known (and long suffered) limitations of REST APIs and offer the developer considerable flexibility. Accordingly, event-driven applications are seen to offer flexibility in design and are well suited to highly scalable, real-time distributed IoT systems.  

However, this flexibility puts a lot of design decisions in the hand of the developer and can create dependencies across distributed systems. The following diagram highlights just how much the PubSub model leaves to unstructured fields for the developer to consider compared to the more defined control fields of REST APIs.

![rest-vs-pubsub](/images/rest-vs-pubsub.png)

The result is PubSub applications provide greater flexibility but require more design effort. The AWS Greengrass Application Framework addresses this with consistent design patterns and boiler plate code so developers can focus on application logic when building distributed IoT applications with AWS Greengrass V2 custom components.

## AWS Greengrass Component Patterns

It helps with design consistency to classify each function of a distributed system into categories. For example, event-driven application architectures typically classify functions as event producers or event consumers. Extending this thought process, AWS Greengrass V2 components will generally fall into one of the following categories:

* **Application Control:** Application control such as bootstrap and initialisation services that configure or trigger other components and functionality.
* **Data Source:** Services that source data, optionally filter, transform or process and then post to the message bus. Data typically originates from sensors, the IoT Core, data base and data caches (key/value pair data) and in some case other components.
* **Data Sink:** Includes functions that accept or request data from another component for monitoring (listening to a temperature or pressure sensor) or to process and store.
* **Actuators:** Provide a PubSub interface to physical controllers and actuators.
* **Computational:** Preforms computationally heavy processes within the application such as statistical analysis and machine learning processes.
* **Interface and Messaging:** Manages messaging to and from external interfaces and systems. 

The AWS Greengrass Application Framework makes use of these classifications in describing message workflows and formats.

## AWS Greengrass PubSub Message Bus (IPC / MQTT) 
The AWS Greengrass V2 [InterProcess Communication (IPC)](https://docs.aws.amazon.com/greengrass/v2/developerguide/interprocess-communication.html) system has separate APIs for PubSub messaging between components within the Greengrass core that we refer to here as IPC Topic or just IPC messaging and PubSub messages over the Internet to the AWS IoT Core using the [MQTT protocol](https://mqtt.org/) that we refer to here as IPC MQTT or just MQTT messaging.  

In this framework, the topic schema and publish / subscribe rules are replicated and applied equally to both methods.

## PubSub Topic Schema

A well-defined PubSub topic schema avoids recursive messages and increases speed and quality of component development. This framework prescribes the following MQTT / IPC topic schema. These should be considered as base functionality and can be extended to include your own specific topics as required.

Prescribed PubSub Topics:

* **Service Topic:** Messages to the service itself such as status and data request messages.
* **Data Topic:** Publishing data such as sensor data that other components can subscribe to.
* **Broadcast Topic:** A system wide broadcast typically to manage components or systems errors.  

If applied consistently across all Greengrass components in the application stack; this forms a common set of communications channels to simplify application design.

## PubSub Message Patterns

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

## PubSub Access Policy

AWS Greengrass provides a PubSub topic-based access policy to protect components from intentionally or unintentionally publishing or subscribing to unauthorised PubSub topics. This prevents unauthorised components listening in or injecting spurious or malicious messages into the AWS Greengrass application message bus.
 
### PubSub Subscription Policy:
This framework applies the following PubSub topic **SUBSCRIBE** rules to all Greengrass components:
1.	Each component must subscribe to its own **Service Topic** and is the only one that listens on this topic making it a means to send 1-to-1 messages, to request status updates and data requests.
2.	No component may subscribe to the **Service Topic** of another component.
3.	Each component must subscribe to the **Broadcast Topic**. This is a system wide control mechanism that may be for critical shutdown or update of all component or to request a restart.
4.	Each component subscribes to the **Data Topic** of any other component that have interesting messages. For example, a temperature monitoring and control component would subscribe to the **Data Topic** of the Temperature Sensor component to listen for temperature values.
5.	Developers can add custom topic with self-determined access policies as needed.

### PubSub Publish Policy
The AWS Greengrass application framework applies the following PubSub topic **PUBLISH** rules to all Greengrass components:
1.	A component is not permitted to publish to its own **Service Topic**. The component itself is the only resource that should be listening and so may cause a recursive update.
2.	All components are permitted to publish to their own **Data Topic**. However, a component doesn't control (or know, or care) what components listen to their **Data Topic**. This is consistent with event-driven application architecture.
3.	No component may publish to another components **Data Topic**. This is implied to be data from the that component only.
4.	All components are permitted to publish to the **Broadcast Topic**. There is no hierarchy on the broadcast topic (unless applied in application logic), all broadcast messages are considered equal. Care should be taken on responding to broadcast messages that may result in a recursive update.
5.	A component may publish to another components **Service Topic**. This may be to request data, status updates or send 1-to-1 messages.
 
![pubsub-access-policy](/images/pubsub-access-policy.png)

## PubSub Message Format
As with the PubSub Topic schema, a policy is needed for message payload type and size that all AWS Greengrass V2 Components adhere to so consistent behaviour is seen across the application stack.

In this AWS Greengrass V2 deveapplicationlopment framework the PubSub message processing is performed by the convenience classes within **ipc_pubsub.py** and **mqtt_pubsup.py** for IPC topic and MQTT IoT Core messaging respectively.

### Message Formatting:
Both the IPC Topic and MQTT IoT Core PubSub convenience classes expect all messages to be serialised as valid JSON and are parsed into python objects on reception. If invalid JSON, binary, plain text or other formatted message payloads are received the given service will throw an error with a default behaviour of logging and gracefully discarding the message. You can of course as the developer extend this behaviour to update a central component or perform some other action. 

If a service needs to post binary data it should parse to Base64 and send in the JSON payload. 

## Applying the Framework Architecture (Made Easy)

We have covered a lot of prescribed rules and schema here that are needed to keep the IoT application architecture consistent and functional. The good news is you don't need to build the capability here yourself (what’s the point of a development framework in that case!).

This framework provides two development skeletons:

* ***AWS Greengrass V2 Recipe Template:** that has all of the config driven data to define and apply the PubSub message topic schema we discussed and the publish / subscribe rules that meet the above criteria and
* **AWS Greengrass V2 Component Template:** With convenience classes to manage publish and subscribe functions (with call-backs for message processing) and application logic to process messages differentiated by topics that meet the described topic schema.

All you need to do to meet the AWS Greengrass Application Framework architecture described is base your AWS Greengrass V2 components and deployment recipes on the templates provided. The rest is taken care of already. Go to the deployment guide for more detail. 
