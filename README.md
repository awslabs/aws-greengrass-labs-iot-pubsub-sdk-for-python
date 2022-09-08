# AWS IoT Greengrass PubSub SDK for Python

This document provides information about the AWS IoT Greengrass PubSub SDK for Python.

If you have any issues or feature requests, please file an issue or pull request.

**Note:** This is a library based implementation and replacement for the AWS IoT Greengrass PubSub Framework previoulsy hosted in this repository. 

## Overview

The AWS IoT Greengrass PubSub SDK for Python provides an IoT PubSub application architecture delivered as a Python library to simplify and accelerate development of distributed IoT applications built on AWS IoT Greengrass Components. The SDK abstracts the AWS IoT Greengrass IPC and MQTT PubSub functionality and uses a data driven message format to route PubSub messages to user defined call-backs. This provides a Low/No-Code PubSub messaging service without the common design dependencies of distributed IoT applications. 

![pubsub-sdk-overview](https://github.com/awslabs/aws-greengrass-labs-iot-pubsub-sdk-for-python/blob/main/images/pubsub-sdk-overview.png)

For more details see the AWS IoT Greengrass PubSub SDK:
* [Developer Guide](https://github.com/awslabs/aws-greengrass-labs-iot-pubsub-sdk-for-python/tree/main/docs/developer-guide)
* [API Docs](https://github.com/awslabs/aws-greengrass-labs-iot-pubsub-sdk-for-python/tree/main/docs/api-docs)
* [Samples](https://github.com/awslabs/aws-greengrass-labs-iot-pubsub-sdk-for-python/tree/main/samples)
* [Detailed Deployment Workshop](https://catalog.us-east-1.prod.workshops.aws/workshops/32dc1f13-985f-4f94-9b86-a859806d28f0)

## Getting Started

The easiest way to get started is to build and deploy the AWS IoT Greengrass PubSub SDK component template described in the [Samples](https://github.com/awslabs/aws-greengrass-labs-iot-pubsub-sdk-for-python/tree/main/samples) directory.

For new users just starting out with AWS IoT Greengrass or those that want to see a more detailed example of using the SDK to deploy multiple components that we recommend running through the workshop [Build a Distributed IoT Application with the AWS IoT Greengrass PubSub SDK](https://catalog.us-east-1.prod.workshops.aws/workshops/32dc1f13-985f-4f94-9b86-a859806d28f0/en-US) where you build a Smart Factory IoT application using the AWS IoT Greengrass PubSub SDK. 

## Installation

### Minimum Requirements
*   Python 3.6+

### Install via an AWS IoT Greengrass Custom Component Recipe

To configure the AWS IoT Greengrass PubSub SDK to deploy with an AWS IoT Greengrass Component, update the recipe Lifecycle / Install event as per below:
```
"Lifecycle": {
  "Install" : {
    "Timeout" : 300,
    "Script" : "python3 -m pip install awsgreengrasspubsubsdk"
  },
  .....
```

 A full example of this is given in the [Greengrass component recipe example](https://github.com/awslabs/aws-greengrass-labs-iot-pubsub-sdk-for-python/blob/main/samples/gg-pubsub-sdk-component-template/src/recipe.json)

### Installing Manually
The AWS IoT Greengrass PubSub SDK provides functionality within an AWS IoT Greengrass component. It only has context within that framework and so for production solutions, its preferred to deploy the SDK with the component as described in the previous example. Manual installation examples given below are intended for development machines. 

**Note**: If installing manually, do so as the user that will own the Greengrass component process (i.e: gcc_user by default).

#### Install from PyPI
```
python3 -m pip install awsgreengrasspubsubsdk
```

#### Install from source
```
git clone https://github.com/awslabs/aws-greengrass-labs-iot-pubsub-sdk-for-python.git
python3 -m pip install ./aws-greengrass-pubsub-sdk-for-python
```

## Usage and Code Examples

Once the AWS IoT Greengrass PubSub SDK is deployed with an AWS IoT Greengrass Component, you can route messages to your application logic via user defined Message Handlers that you register with the SDK 

A production ready AWS IoT Greengrass component template and more detailed examples are provided in the [Samples](https://github.com/awslabs/aws-greengrass-labs-iot-pubsub-sdk-for-python/tree/main/samples) directory.

The SDK defines the following required message format (with more details provided in the [Developer Guide](https://github.com/awslabs/aws-greengrass-labs-iot-pubsub-sdk-for-python/tree/main/docs/developer-guide)
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
The SDK will route received PubSub messages to a user defined message handler class and method as provided in the message **route** value. The message route value is a **Class.Method** namespace representation of the desired message route target.  

Using this approach, the AWS IoT Greengrass PubSub SDK routes PubSub messages to your application logic in easily defined message callbacks.

### Initialising the SDK and Message Handler Classes
1.  Add a method that will be the route of last resort for received PubSub messages and the expected message parameters.
```
def default_message_handler(self, protocol, topic, message_id, status, route, message):
   
   # Process messages without a registered handler router target
   log.error('Received message to unknown route / message handler: {} - message: {}'.format(route, message)))
```

2. Initialise the AWS IoT Greengrass PubSub SDK Client
```
# Import the AWS IoT Greengrass PubSub SDK
from awsgreengrasspubsubsdk.pubsub_client import AwsGreengrassPubSubSdkClient

# Declare the PubSub Base topic, this is used to build the default Ingress and Egress PubSub topics.
pubsub_base_topic = 'com.my_greengrass.application'

# Initilise the AwsGreengrassPubSubSdkClient with the pubsub_base_topic and default_message_handler
pubsub_client = AwsGreengrassPubSubSdkClient(pubsub_base_topic, default_message_handler )

```

3. Create one or more user defined message handler class/es with named functions to route PubSub messages with the expected parameters. This method allows easy separation of message processing functionality within your application.
```
class MyPubSubMessageHandler():

    def pubsub_message_route_target(self, protocol, topic, message_id, status, route, message):
        
        # Process messages with route = 'MyPubSubMessageHandler.pubsub_message_route_target'
        log.info('MyPubSubMessageHandler.pubsub_message_route_target received message: {}'.format(message))
```

4. Register the message handler class/es with the PubSub SDK Client with the [register_message_handler](https://github.com/awslabs/aws-greengrass-labs-iot-pubsub-sdk-for-python/tree/main/docs/api-docs/pubsub_client.md#method-register_message_handler) call.
```
my_pubsub_message_handler = MyPubSubMessageHandler()
pubsub_client.register_message_handler(my_pubsub_message_handler)
```

5. Activate the IPC and / or MQTT Protocols in the SDK:
```
# Activate IPC Protocol
pubsub_client.activate_ipc_pubsub()

# Acticate MQTT Protocol
pubsub_client.activate_mqtt_pubsub()
```

6. Complete!  
On completion of the above and once successfully deployed, your AWS IoT Greengrass component will listen on the default Ingress topic **(base-pubsub-topic/THING_NAME/ingress)** and any other user defined topics. The SDK will begin routing PubSub messages to your registered Message Handler classes as per the message **route** value. As describe above, any message received on the SDK subscribed topic with value **route = MyPubSubMessageHandler.pubsub_message_route_target** will be automatically forwarded to the method provided in the example. 

**Note:** If the route value does not match any route target methods, the message will be forwarded to the default_message_handler class.

### Subscribing to Custom Topics
The SDK provides a programmatic means of subscribing to user defined topics. You can subscribe to any topic that is permitted by the access policy provided in the component recipe. 
```
my_topic = 'my/interesting/topic'

# Subscribe to topic on IPC
pubsub_client.subscribe_to_topic('ipc', topic)

# Subscribe to topic on MQTT
pubsub_client.subscribe_to_topic('mqtt', topic)

# Subscribe to topic on IPC and MQTT
pubsub_client.subscribe_to_topic('ipc_mqtt', topic)

```

If the protocol (IPC or MQTT) is activated, the SDK will subscribe to the topic and begin routig messages immediatly. If not, the subscription request will be stored and actioned when the selected protocol is activated.

### Publishing Message to PubSub
The SDK provides a message formatter class to ensure consistent messages. See the [message_formatter](https://github.com/awslabs/aws-greengrass-labs-iot-pubsub-sdk-for-python/tree/main/docs/api-docs/message_formatter.md) API Docs for more detail.

```
# Initialise the PubSubMessageFormatter
from awsgreengrasspubsubsdk.message_formatter import PubSubMessageFormatter
message_formatter = PubSubMessageFormatter()

# Use the message formatter to create a well-formatted PubSub SDK response message
receive_route = 'MyPubSubMessageHandler.pubsub_message_response'
my_message = {
    "my-message-param01": "param01",
    "my-message-param02": "param02"
}
# Defaults will be applied for parameteres not provided here. See API Docs.
sdk_format_msg = message_formatter.get_message(route=receive_route, message=my_message)

## Publish the message to IPC and MQTT. 
pubsub_client.publish_message('ipc_mqtt', sdk_format_msg)
```

### Installation Issues

1. The AWS IoT Greengrass PubSub SDK (`awsgreengrasspubsubsdk`) installs [awsiotsdk](https://github.com/aws/aws-iot-device-sdk-python-v2) as a dependancy with the following listed [Installation issues](https://github.com/aws/aws-iot-device-sdk-python-v2#installation).

2. If running the AWS IoT Greengrass component with root privileges, you will need to install in a python virtual environment by replacing the component recipe install policy with the below:
```
"Install" : {
          "Timeout" : 300,
          "Script" : "python3 -m venv pubsubsdk; . pubsubsdk/bin/activate; pip3 install --upgrade pip; python3 -m pip install awsgreengrasspubsubsdk"
        }
```

## Samples

A complete production ready AWS IoT Greengrass component template is provided in the [Samples](https://github.com/awslabs/aws-greengrass-labs-iot-pubsub-sdk-for-python/tree/main/samples) directory.

## Getting Help

The best way to interact with our team is through GitHub. You can [open an issue](https://github.com/awslabs/aws-greengrass-labs-iot-pubsub-sdk-for-python/issues) for guidance, bug reports, or feature requests. 

Please make sure to check out our resources before opening an issue:
* [Developer Guide](https://github.com/awslabs/aws-greengrass-labs-iot-pubsub-sdk-for-python/tree/main/docs/developer-guide)
* [API Docs](https://github.com/awslabs/aws-greengrass-labs-iot-pubsub-sdk-for-python/tree/main/docs/api-docs)
* [AWS IoT Greengrass PubSub SDK Deployment Workshop](https://catalog.us-east-1.prod.workshops.aws/workshops/32dc1f13-985f-4f94-9b86-a859806d28f0)
* [AWS IoT Greengrass V2 Developer Guide](https://docs.aws.amazon.com/greengrass/v2/developerguide/what-is-iot-greengrass.html) 
* [AWS IoT Core Documentation](https://docs.aws.amazon.com/iot/)
* [AWS Dev Blog](https://aws.amazon.com/blogs/?awsf.blog-master-iot=category-internet-of-things%23amazon-freertos%7Ccategory-internet-of-things%23aws-greengrass%7Ccategory-internet-of-things%23aws-iot-analytics%7Ccategory-internet-of-things%23aws-iot-button%7Ccategory-internet-of-things%23aws-iot-device-defender%7Ccategory-internet-of-things%23aws-iot-device-management%7Ccategory-internet-of-things%23aws-iot-platform)

## Giving Feedback and Contributions

We need your help in making this SDK great. Please participate in the community and contribute to this effort by submitting issues, participating in discussion forums and submitting pull requests through the following channels.

*   [Contributions Guidelines](https://github.com/awslabs/aws-greengrass-labs-iot-pubsub-sdk-for-python/blob/main/CONTRIBUTING.md)
*   Submit [Issues, Feature Requests or Bugs](https://github.com/awslabs/aws-greengrass-labs-iot-pubsub-sdk-for-python/issues)

## AWS IoT Core Resources

*   [AWS IoT Core Documentation](https://docs.aws.amazon.com/iot/)
*   [AWS IoT Developer Guide](https://docs.aws.amazon.com/iot/latest/developerguide/what-is-aws-iot.html) ([source](https://github.com/awsdocs/aws-iot-docs))
*   [AWS Dev Blog](https://aws.amazon.com/blogs/?awsf.blog-master-iot=category-internet-of-things%23amazon-freertos%7Ccategory-internet-of-things%23aws-greengrass%7Ccategory-internet-of-things%23aws-iot-analytics%7Ccategory-internet-of-things%23aws-iot-button%7Ccategory-internet-of-things%23aws-iot-device-defender%7Ccategory-internet-of-things%23aws-iot-device-management%7Ccategory-internet-of-things%23aws-iot-platform)


## Security

See [CONTRIBUTING](https://github.com/awslabs/aws-greengrass-labs-iot-pubsub-sdk-for-python/blob/main/CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.
