<!-- markdownlint-disable -->

<a href="../../awsgreengrasspubsubsdk/pubsub_client.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `pubsub_client`
Provided as the entry point for the AWS Greengrass V2 PubSub Component SDK.  



---

<a href="../../awsgreengrasspubsubsdk/pubsub_client.py#L25"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `AwsGreengrassPubSubSdkClient`
This client abstracts the AWS Greengrass IPC and MQTT PubSub functionality,  defines a simple PubSub topic schema and routes PubSub messages directly to  the given instance of PubSubMessageHandler() in the user’s application logic. 

PubSub subscriptions are only initialised and messages processed once the activate_ipc_pubsub() and / or activate_mqtt_pubsub() functions are called to activate the IPC and MQTT PubSub message channels respectively.  

This defines the base PubSub topic schema with topics for ingress and egress messages.   

 The PubSub topic schema is defined as:  

 * Ingress Topic - (base_topic/THING_NAME/ingress): Subscribes to this topic for incoming messages.    

 * Egress Topic - (base_topic/THING_NAME/egress): Default message publish topic.    

### Parameters  

 **base_topic**: str     

 Based string for the ingress / egress and error topics for this component.  

 **message_handler**: Class (Instance of: PubSubMessageHandler() )      

 An instance of the message_handler.PubSubMessageHandler() class in the AWS Greengrass component code.   All messages received on any active PubSub protocols will be forwarded to this class.  

 

### Usage / Constructor  

 base_topic = 'my_project_name"    

 my_message_handler = MyPubSubMessageHandler()    

 pubsub_client = AwsGreengrassPubSubSdkClient(base_topic, my_message_handler)  



<a href="../../awsgreengrasspubsubsdk/pubsub_client.py#L65"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(base_topic, default_message_handler)
```

Initialises the AWS Greengrass V2 PubSub SDK.  

**Note:** Initialising this client doesn't immediately trigger IPC or MQTT message processing.  User must call activate_ipc_pubsub() and / or activate_mqtt_pubsub()  to activate the respective PubSub protocols to begin processing messages. 




---

<a href="../../awsgreengrasspubsubsdk/pubsub_client.py#L174"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `activate_ipc_pubsub`

```python
activate_ipc_pubsub()
```

Activate and initialise the IPC PubSub subscribers and publisher. Will start receiving and processing messages in IPC subscribed topics immediately on calling this function. 

---

<a href="../../awsgreengrasspubsubsdk/pubsub_client.py#L191"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `activate_mqtt_pubsub`

```python
activate_mqtt_pubsub()
```

Activate and initialise the MQTT PubSub subscribers and publisher. Will start receiving and processing messages in MQTT subscribed topics immediately on calling this function. 

---

<a href="../../awsgreengrasspubsubsdk/pubsub_client.py#L373"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `publish_error`

```python
publish_error(protocol, err_message)
```

A convenience method that logs and publishes an Error message to IPC and / or MQTT This will build a well formatted message with status = 500 and route = 'default_error_handler' 

### Parameters   

**protocol**: str    

 The protocol client (IPC or MQTT) to publish the message too.  

 Supported values:     

 * ipc: Publish to IPC message bus.  

 * mqtt: Publish to MQTT message bus.  

 * ipc_mqtt: Publish to both IPC and MQTT message buses respectively. 

**err_message**: Object (preferred dict)   

 Dict, Array or any object able to be JSON serialised containing data to be published with the response message.   Is added as message payload in a well-formatted SDK message with status=500 and route='default_error_handler' 

---

<a href="../../awsgreengrasspubsubsdk/pubsub_client.py#L323"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `publish_message`

```python
publish_message(protocol, message, topic=None)
```

Publishes a JSON message to the respective AWS Greengrass Protocol (IPC or MQTT) Clients. 

### Parameters   

**protocol**: str    

 The protocol client (IPC or MQTT) to publish the message too.  

 Supported values:     

 * ipc: Publish to IPC message bus.  

 * mqtt: Publish to MQTT message bus.  

 * ipc_mqtt: Publish to both IPC and MQTT message buses respectively. 

**message**: Object (preferred dict)    

 Dict, Array or any object able to be JSON serialised containing data to be published with the response message.   Typically expected to be a JSON object created by the AWS Greengrass SDK messageformatter.  

**topic**: str (Optional) Default: Component Egress Topic (i.e: base-pubsub-topic/THING_NAME/egress )  

 The topic to publish this message to on the selected protocol client  



---

<a href="../../awsgreengrasspubsubsdk/pubsub_client.py#L132"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `register_message_handler`

```python
register_message_handler(message_handler_class)
```

Registers a message handler class to route messages too. A message_handler is any user defined class that contains named functions  that this SDK will route messages to based on the route value in the message. 

---

<a href="../../awsgreengrasspubsubsdk/pubsub_client.py#L413"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `subscribe_to_topic`

```python
subscribe_to_topic(protocol, topic)
```

Subscribes to custom PubSub topics on IPC and / or MQTT clients.  If the given protocol client has been activated, then the subscription will take immediate effect and the registered message_handler will begin receiving messages from this topic. 

If the protocol has not been activated, the subscription request will  be stored and will take effect once the protocol is activated.  

### Parameters 

**protocol**: str    

 The protocol client (IPC or MQTT) to Subscribe too.  

 Supported values:     

 * ipc: Subscribe to IPC message bus.  

 * mqtt: Subscribe to MQTT message bus.  

 * ipc_mqtt: Subscribe to both IPC and MQTT message buses respectively. 

**topic**: str  The topic to subscribe too.  






---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
