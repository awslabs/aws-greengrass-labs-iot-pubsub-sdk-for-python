# AWS Greengrass Application Framework

## Simple IoT Core MQTT Update Message

This example provides a single AWS Greengrass V2 component that periodically (every 5 seconds), sends a simulated temperature reading
to this components IPC and MQTT Data Topic. Any other component on the Greengrass core (device) that subscribes to this components data topic 
will receive the message. The message will also be published to the AWS IoT Core via the components MQTT Data topic.

### To Deploy this Greengrass Application:
From the Greengrass core device CLI:
```
# Clone this GIT Repository
git clone https://github.com/aws-samples/aws-greengrass-application-framework.git

# 'cd' into the application deploy_tools directory
cd aws-greengrass-application-framework/examples/01-simple/deploy_tools

# Deploy with AWS Greengrass CLI using the simple AWS Greengrass CLI merge script 
sudo ./gg_merge_components.sh
```

### To Validate this Greengrass Application:

#### Verify the deployment in greengrass.log:
```sudo tail -f /greengrass/v2/logs/greengrass.log```

Once complete, expect to see (can take 30+ seconds):  
```Persist link to last deployment. {link=/greengrass/v2/deployments/previous-success}```

#### Use gg_list_components.sh to check deployed components:
```sudo ./gg_list_components.sh | grep Name```

Once complete, expect to see the default component deployed:  
```Component Name: com.example.my_project.simple_component```

#### Verify the simple_component component logs:
```sudo tail -f /greengrass/v2/logs/com.example.my_project.simple_component.log```

Once complete, expect to see a 5 second update of the IPC and MQTT PubSub Message publish:  

```
[INFO] - Publishing PubSub Message. Topic: com.example.my_project.simple_component/ipc/data - Message: {'message-id': '20210808230431368379', 'reqres': 'update', 'command': 'temp_sensor_01_update', 'response': {'data': {'temp_sensor_id': 'sens_28a', 'units': 'Celsius', 'value': 22.5}, 'status': 200}}

[INFO] - Publishing PubSub Message. Topic: com.example.my_project.simple_component/mqtt/data - Message: {'message-id': '20210808230431368379', 'reqres': 'update', 'command': 'temp_sensor_01_update', 'response': {'data': {'temp_sensor_id': 'sens_28a', 'units': 'Celsius', 'value': 22.5}, 'status': 200}}
```

#### Verify / View Time PubSub Message in AWS IoT Console

At this point you can also view the MQTT PubSub message in the AWS IoT Core console. If unfamiliar with this process, follow the [View MQTT messages with the AWS IoT MQTT client](https://docs.aws.amazon.com/iot/latest/developerguide/view-mqtt-messages.html) to see the message. 

In the AWS IoT Core console, subscribe to the publish_time **Data Topic** on **com.example.my_project.simple_component/mqtt/data** you will see an update similar to below:

![simple_component_iot_console](/images/simple_component_iot_console.png)

