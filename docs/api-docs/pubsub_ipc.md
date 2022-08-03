<!-- markdownlint-disable -->

<a href="../../awsgreengrasspubsubsdk/pubsub_ipc.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `pubsub_ipc`
Abstracts the AWS Greengrass V2 IPC PubSub SDK that manages subscriptions  and a method to publish to AWS Greengrass IPC topics. This is intended for use in an AWS Greengrass V2 Component SDD to provide PubSub services.  

IPC Topic PubSub is for internal communications between AWS Greengrass Components  within the AWS Greengrass Core (the edge device). For communications between  Greengrass component and the AWS IoT Core platform see the MQTT PubSub class.  

For more detail on AWS Greengrass V2 see the Developer Guide at: https://docs.aws.amazon.com/greengrass/v2/developerguide/what-is-iot-greengrass.html 



---

<a href="../../awsgreengrasspubsubsdk/pubsub_ipc.py#L41"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `IpcPubSub`




<a href="../../awsgreengrasspubsubsdk/pubsub_ipc.py#L43"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(message_callback, ipc_subscribe_topics)
```








---

<a href="../../awsgreengrasspubsubsdk/pubsub_ipc.py#L120"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `publish_to_topic`

```python
publish_to_topic(topic, message_object, timeout=None)
```

Publish a Python object sterilised as a JSON message to the requested local IPC topic. 

---

<a href="../../awsgreengrasspubsubsdk/pubsub_ipc.py#L78"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `set_ipc_default_timeout`

```python
set_ipc_default_timeout(ipc_default_timeout)
```





---

<a href="../../awsgreengrasspubsubsdk/pubsub_ipc.py#L91"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `subscribe_to_topic`

```python
subscribe_to_topic(topic)
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
