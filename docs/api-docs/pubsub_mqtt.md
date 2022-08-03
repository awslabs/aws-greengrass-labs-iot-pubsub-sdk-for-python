<!-- markdownlint-disable -->

<a href="../../awsgreengrasspubsubsdk/pubsub_mqtt.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `pubsub_mqtt`
Abstracts AWS Greengrass V2 MQTT PubSub SDK that manages subscriptions  and a method to publish to AWS Greengrass MQTT topics. This is intended for use in an AWS Greengrass V2 Component SDK to provide MQTT PubSub services.  

IPC MQTT core is for communications between AWS Greengrass Components and  the AWS IoT Core. This can be used to send MQTT messaging to the AWS IoT core  to save data, trigger alarms or alerts or to trigger other AWS services and applications. 

For more detail on AWS Greengrass V2 see the Developer Guide at: https://docs.aws.amazon.com/greengrass/v2/developerguide/what-is-iot-greengrass.html 



---

<a href="../../awsgreengrasspubsubsdk/pubsub_mqtt.py#L40"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `MqttPubSub`




<a href="../../awsgreengrasspubsubsdk/pubsub_mqtt.py#L42"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(message_callback, mqtt_subscribe_topics)
```








---

<a href="../../awsgreengrasspubsubsdk/pubsub_mqtt.py#L120"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `publish_to_mqtt`

```python
publish_to_mqtt(topic, message_object, timeout=None)
```

Publish a Python object serlized as a JSON message to the IoT Core MQTT topic. 

---

<a href="../../awsgreengrasspubsubsdk/pubsub_mqtt.py#L74"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `set_mqtt_default_qos`

```python
set_mqtt_default_qos(mqtt_default_qos)
```





---

<a href="../../awsgreengrasspubsubsdk/pubsub_mqtt.py#L77"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `set_mqtt_default_timeout`

```python
set_mqtt_default_timeout(mqtt_default_timeout)
```





---

<a href="../../awsgreengrasspubsubsdk/pubsub_mqtt.py#L92"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `subscribe_to_topic`

```python
subscribe_to_topic(topic)
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
