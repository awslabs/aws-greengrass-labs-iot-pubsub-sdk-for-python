<!-- markdownlint-disable -->

<a href="../../awsgreengrasspubsubsdk/message_formatter.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `message_formatter`
Defines standard message format for PubSub communications.  



---

<a href="../../awsgreengrasspubsubsdk/message_formatter.py#L15"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `PubSubMessageFormatter`
Defines standard message format for PubSub communications between Greengrass  components and / or MQTT IoT Core in the AWS Greengrass V2 PubSub SDK. 

This enables versioned, efficient and consistent PubSub Message routing and  processing between components. 




---

<a href="../../awsgreengrasspubsubsdk/message_formatter.py#L114"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_error_message`

```python
get_error_message(**kwargs)
```

Convenience method that returns a well formatted PubSub Error Message  with status default to 500 and route to 'default_error_handler' 

A status value that isn't a 2xx value will route this message to the  default error PubSub topic and default error handler function on the receiving component  (Assuming it also implements the AWS Greengrass PubSub Component SDK). 

### Parameters   

**message_id** : str, (Optional) Default=Current Timestamp   

 Unique message ID to aid tracking across request / response message patterns.   If None or missing, a current timestamp is generated for this value in the format: %Y%m%d%H%M%S%f  

**message** : Object (preferred Dict), (Optional) default={}   

 Dict, Array or any JSON serializable object containing the payload of this message.  If None or missing, an empty Dict is generated for this value.  

### Usage    

All input parameters are optional and provided as named keyword arguments. Defaults are applied for any values not provided or provided as None. 

e.g:   

```
 get_error_message(message={"error" : "PubSub Timeout for process 123XYZ"})
 get_error_message(message_id=123456,  message={"error" : "PubSub Timeout for process 123XYZ"})
 ``` 

### Returns 

Example (Dict) returned message object:   

```
{
      "sdk_version" : "0.1.4",
      "message_id" : 123456,
      "status" : 500,
      "route" : "default_error_handler",
      "message": {
         "error" : "PubSub Timeout for process 123XYZ"
      }
 }
 ``` 





---

<a href="../../awsgreengrasspubsubsdk/message_formatter.py#L26"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_message`

```python
get_message(**kwargs)
```

Returns a well formatted PubSub Message as per this PubSub SDK versioned formatting. 

### Parameters   

**message_id** : str, (Optional) Default=Current Timestamp   

 Unique message ID to aid tracking across request / response message patterns.   If None or missing, a current timestamp is generated for this value in the format: %Y%m%d%H%M%S%f  

**status** : int (Optional) Default=200   

 Status code of this message. Any int supported, expected / typical values:    

 200: OK COMPLETE, 202: ASYNC REQUEST ACCEPTED, 404: COMMAND NOT RECOGNISED, 500: INTERNAL COMPONENT ERROR.  

**route** : str (Optional) Default='default_message_handler'   

 Name of the message handler fuction in PubSubMessageHandler() to process this message on the receiving component.  If None or missing will be set to default_message_handler  

**message** : Object (preferred dict), (Optional) default={}   

 Dict, Array or any JSON serializable object containing the payload of this message.  If None or missing, an empty dict is generated for this value.  

### Usage: 

All input parameters are optional and provided as named keyword arguments. Defaults are applied for any values not provided or provided as None. 

e.g:   

```
 get_message(message={"param01" : "message param01"})
 get_message(message_id=123456, route="health_check_response",  message={"status" : "System OK"})
 ``` 

### Returns 

Example (Dict) returned message object:    

```
{
      "sdk_version" : "0.1.4",
      "message_id" : 123456,
      "status" : 200,
      "route" : "health_check_response",
      "message": {
              "status" : "System OK"
      }
 }
 ``` 








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
