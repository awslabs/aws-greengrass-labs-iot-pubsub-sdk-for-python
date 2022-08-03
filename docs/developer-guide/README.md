# Developer Guide

The AWS Greengrass V2 PubSub Component SDK for Python provides an IoT PubSub application architecture delivered as a Python library to simplify and accelerate development of distributed IoT applications built on AWS Greengrass V2 Components.  

The SDK abstracts the AWS Greengrass IPC and MQTT PubSub functionality and uses a prescribed message format to enable data driven PubSub message routing to user defined application call-backs. This provides a Low/No-Code PubSub messaging service without the common design dependencies of distributed IoT applications.   

When the AWS Greengrass SDK is deployed system wide, it creates a unified message service across distributed IoT components that could span a single Greengrass device or applications, users and consumers from across the globe.

![pubsub-sdk-overview](/images/pubsub-sdk-overview.png)

## AWS Greengrass IoT PubSub Application Architecture
This SDK provides a codified implementation of the principals described in the [AWS Greengrass IoT PubSub Framework](https://github.com/awslabs/aws-greengrass-labs-iot-pubsub-framework).

## Getting Started

The easiest way to get started is to deploy the AWS Greengrass PubSub SDK component template described in the [Samples](/samples) directory, then develop your custom application logic and update as required.

## Functional Overview

The SDK defines a prescribed message format that includes a **route** field to enable data driven message routing to users’ application logic. This allows for a simplified PubSub topic schema that supports functional interface updates without code changes. Accordingly, the SDK operates all default messaging over a single **Ingress** and **Egress** PubSub topic pair per Greengrass core device which further reduces dependencies between distributed IoT applications and teams.

 Message routing is based on the **route** field in the SDKs prescribed message format as shown below:
 ```
{
  "sdk_version": "0.1.4",
  "message_id": "20220403170948930231",
  "status": 200,
  "route": "MyPubSubMessageHandler.pubsub_message_route_target",
  "message": {
    "my-message-param01": "param01",
    "my-message-param02": "param02"
  }
}
```

You simply register user defined message handler classes (which are Plain Old Python Objects) with the SDK. The message **route** field is in Class.Method namespace convention. If the SDK receives a PubSub message with a route value matching the Class.Method value of a registered message handler class, it will automatically route the message to that method for processing.

In this way, you can easily import a complete PubSub message service into your AWS Greengrass custom component and have PubSub messages delivered to your application logic directly.  

As the Class.Method namespace is preserved in message routing; you can register multiple message handler classes. This provides an easy way to separate PubSub message processing into functional code blocks (finally!).
 
### Example

To include a new **health_check** call in your distributed AWS Greengrass IoT Application. 

* Initialise the AWS Greengrass PubSub Component SDK as shown in the proceeding sections.
* In your application, define a message handler class called **SystemMessageHandler** with a method **health_check** to act as a message route target for the SDK.

```
class SystemMessageHandler():

    def health_check(self, protocol, topic, message_id, status, route, message):
        
        # Process messages with route = 'SystemMessageHandler.health_check'
        log.info('SystemMessageHandler.health_check received message: {}'.format(message))
```

Notice that the **health_check** method contains the parameters protocol, topic, message_id, status, route and message. The SDK will only register methods as message route targets that have these exact parameters. The SDK will also ignore any private methods (starting with '_'). And so, you are quite free to add helper and other functional methods as needed in the message handler classes you register with the SDK and not have them interfere with expected message routing functionality.

* Register the message handler class with the SDK client: 

```
system_message_handler = SystemMessageHandler()
pubsub_client.register_message_handler(system_message_handler)
```

* Activate IPC and / or MQTT:
```
# Activate IPC Protocol
pubsub_client.activate_ipc_pubsub()

# Acticate MQTT Protocol
pubsub_client.activate_mqtt_pubsub()
```

* Once the protocol is activated, the SDK will immediately start routing received messages from all subscribed PubSub topics to the registered message handler classes. 

* Advertise to any upstream systems and teams that your application now supports the health_check route! 

Once the message handler is created, it becomes simple to add additional calls to your interface. Just add new methods to the registered message handler classes. 

![message-processing-health-check-example](/images/message-processing-health-check.png)

1. Consuming application publishes a well formatted message to the devices **Ingress Topic** with the **route** field set to **SystemMessageHandler.health_check**,
1. Message is validated and IPC and MQTT protocols are combined into single message routing pipeline,
1. SDK routes the message to the method **def health_check(...)** in the SDK registered **SystemMessageHandler** class, 
1. We assume the **health_check** method logic publishes a response message to the SDK programmatically,
1. SDK publishes the message to the selected protocols (IPC and / or MQTT) and topic (Egress topic by default). 

This health_check example is shown in the SDK component template module [my_system_message_handler.py](/samples/gg-pubsub-sdk-component-template/src/pubsub_message_handlers/my_system_message_handler.py)

## PubSub Topic Schema

One of the key dependencies when developing a distributed IoT application is the PubSub topic schema and topic to function mapping. This is an ongoing dependency that can cause API breaking changes for even minor functional updates.

The SDK removes this dependency by defining a simple but extensible PubSub topic schema. The data driven message routing described breaks the dependency on topics being used to address interface functionality and so, the SDK base topic schema consists of just two topics, the **ingress** and **egress** topics. 

The topics paths are constructed from the **pubsub-base-topic** provided when initialising the SDK and are as such:
* **Ingress Topic:** [pubsub-base-topic]/[AWS_IOT_THING_NAME]/ingress
* **Egress Topic:**[pubsub-base-topic]/[AWS_IOT_THING_NAME]/egress

The SDK component will automatically subscribe to and process messages received on the Ingress topic and will by default publish messages to the components Egress topic. 

### Custom Topics
While greatly simplified, this one in / one out topic schema doesn't support some of the key benefits of PubSub architectures over synchronous message services such as one to many and many to one message patterns. To overcome this, the SDK also supports programmatically subscribing and publishing to user defined topics. 

The SDK provides a [subscribe_to_topic()](/docs/api-docs/pubsub_client.md#method-subscribe_to_topic) function that allows you to programmatically subscribe to any topic that the components recipe access policy will allow. 

Similarly, the [publish_message](/docs/api-docs/pubsub_client.md#method-publish_message) function will default to the components Egress topic if none provided but any custom topic can be given here as long as its allowed by the components recipe access policy.

You can also define custom topics the component should subscribe to via config in the component’s recipe file. 

## SDK PubSub Message Format

An example of an AWS Greengrass PubSub SDK well-formatted message is as below:
```
{
  "sdk_version": "1.0.0",
  "message_id": "123456789",
  "status": "200",
  "route": "MyPubSubMessageHandler.message_route_target_method",
  "message": {
    "my-message-param01": "param01",
    "my-message-param02": "param02"
  }
}
```

1. **sdk_version**: Semantic version of the SDK message format for compatibility.
2. **message_id**: Timestamp or unique ID to track messages across request / response patterns. 
3. **status**: Status code of this message.
4. **route**: Message routing to matching named callback functions in user defined message handler classes.
5. **message**: User defined data payload in an SDK well formatted message. 

### Initialising the SDK Client
1.  Define a method that will be the route of last resort for received PubSub messages and the expected message parameters.
```
def default_message_handler(self, protocol, topic, message_id, status, route, message):
   
   # Process messages without a registered handler router target
   log.error('Received message to unknown route / message handler: {} - message: {}'.format(route, message)))
```

Any PubSub messages received that don't have a matching route target in any of the registered message handler classes will be router here.


2. Initialise the AWS Greengrass PubSub SDK Client
```
# Import the AWS Greengrass PubSub SDK
from awsgreengrasspubsubsdk.pubsub_client import AwsGreengrassPubSubSdkClient

# Declare the PubSub Base topic, this is used to build the default Ingress and Egress PubSub topics.
pubsub_base_topic = 'com.my_greengrass.application'

# Initilise the AwsGreengrassPubSubSdkClient with the pubsub_base_topic and default_message_handler
pubsub_client = AwsGreengrassPubSubSdkClient(pubsub_base_topic, default_message_handler )

```

## User Defined Message Handler Class

Message Handler classes are user defined Plain Old Python Objects (POPOs) that contain methods the SDK will consider as valid route targets for received PubSub messages. To define a Message Handler class, just create a regular Python class with methods that meet the criteria to be considered as valid message route targets. 

```
Class MyMessageHandler():

def my_custom_messsage_handler(self, protocol, topic, message_id, status, route, message):
      # Process message request
```

The SDK deconstructs the message fields and provides these to the message handlers in a parameterised format. To be considered as valid message route targets, methods in the registered message handler classes must accepts the following parameters:

Where:
* **protocol:** **ipc** or **mqtt** to describe the protocol the message was received on.
* **topic:** The PubSub topic that the message was received on.
* **message_id:** The message_id that was sent in the PubSub message.
* **status:** The status code that was received in the PubSub message.
* **route:** The route value that was received in the PubSub message.
* **message:** The user defined payload field that was received in the PubSub message.

Methods that are private or don't have these named parameters will be ignored by the SDK and not considered as potential route targets. This allows you to add helpers and private methods in the message handler classes you register without impacting expected message routing functionality. 

### Registering a Message Handler
To register a message handler class with the SDK, call the SDK client register_message_handler() method.
```
my_pubsub_message_handler = MyPubSubMessageHandler()
pubsub_client.register_message_handler(my_pubsub_message_handler)
```

### Activate IPC and / or MQTT Protocols in the SDK
```
# Activate IPC Protocol
pubsub_client.activate_ipc_pubsub()

# Acticate MQTT Protocol
pubsub_client.activate_mqtt_pubsub()
```

## Creating Well Formatted Messages
The SDK provides a message_formatter that returns well-formatted messages from a list of parameterised values. These are described in the API Docs [message_formatter](/docs/api-docs/message_formatter.md).

In particular the [get_message](/docs/api-docs/message_formatter.md#method-get_message) and [get_error_message](/docs/api-docs/message_formatter.md#method-get_error_message) calls as shown below:
```
from awsgreengrasspubsubsdk.message_formatter import PubSubMessageFormatter
formatter = PubSubMessageFormatter()

# Create a well formatted message with default values and local time in message payload.
my_message = { "local-time" : datetime.now().strftime("%d-%b-%Y %H:%M:%S")  }
sdk_format_msg = self.formatter.get_message(message=my_message)
```
