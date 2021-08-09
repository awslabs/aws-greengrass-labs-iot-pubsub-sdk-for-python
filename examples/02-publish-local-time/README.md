# AWS Greengrass Application Framework

## Publish Local Time Greengrass Application Example

In this example, two Greengrass components are deployed in a single AWS Greengrass application. 

These are:
1) **publish_time:** Publishes the local time as an unsolicited UPADTE to the components IPC and MQTT **Data Topic**
2) **receive_time:** Reads in the time publish message and logs to console.

Even though the receive_time component is very simple, it displays the techniques needed for a component to subscribe and process messages from another components Data topic and not one of the default topics pre-configured by the AWS Greengrass Application Framework. 

For example, to subscribe and make available the topic "com.example.my_project.publish_time/ipc/data":
1. Add a variable to reference the topic from application logic in the component recipe:
    ```"ipc_publish_time_data_topic" : "com.example.my_project.publish_time/ipc/data"```
2. Add the topic to the component recipe 'Subscribe Topics' array:
    ```"ipc_subscribe_topics" : ["com.example.my_project.receive_time/ipc/service", "com.example.my_project.publish_time/ipc/data", "com.example.my_project/ipc/broadcast"]```
3. Add the topic to the IPC (in this case) subscribe access policy in the component recipe:
    ```
              "com.example.my_project.receive_time:subscribe:1": {
            "policyDescription": "Allows access to subscribe to the component IPC service topic and application IPC broadcast topic (and / or others as required).",
            "operations": [
              "aws.greengrass#SubscribeToTopic"
            ],
            "resources": [
              "com.example.my_project.receive_time/ipc/service",
              "com.example.my_project.publish_time/ipc/data",
              "com.example.my_project/ipc/broadcast"
            ]
          }
    ```
4. Create local reference to the topic in main.py __init__:
    ```
        # Get the Publish Time component Data topic var name.
        self.ipc_publish_time_data_topic = ggv2_component_config['ipc_publish_time_data_topic']
    ```
5. Route messages to the topic in main.py pubsub_message_callback()
    ```
        # Route IPC messages from publish_time Data Topic
        elif topic == self.ipc_publish_time_data_topic:
            self.ipc_publish_time_topic_router(message_id, reqres, command, message)
    ```
6. Create a message router for the topic with reqres routing for expected messages:
    ```
        def ipc_publish_time_topic_router(self, message_id, reqres, command, message):
            '''
                Route IPC PubSub messages from the publish_time components Data Topic.
            '''

            if reqres == 'update':
                self.ipc_publish_time_data_topic_update(message_id, reqres, command, message)
    ```
7. Create a message processor for the tipoc expected reqres types:
    ```
        def ipc_publish_time_data_topic_update(self, message_id, reqres, command, message):
        '''
            Process PubSub UPDATE type messages from the publish_time component Data Topic
        '''
        log.info('Received PubSub UPDTAE on publish_time component Data topic. Message: {}'.format(message))
    ```

### To Deploy this Greengrass Application:
From the Greengrass core device CLI:
```
# Clone this GIT Repository
git clone https://github.com/aws-samples/aws-greengrass-application-framework.git

# 'cd' into the application deploy_tools directory
cd aws-greengrass-application-framework/examples/02-publish-local-time/deploy_tools

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
```
Component Name: com.example.my_project.publish_time
Component Name: com.example.my_project.receive_time
```

#### Verify the specific example component/s logs:

```sudo tail -f /greengrass/v2/logs/com.example.my_project.publish_time.log```

Once complete, expect to see a 5 second update of the IPC and MQTT PubSub Message publish:  

```
INFO] - Publishing PubSub Message. Topic: com.example.my_project.publish_time/ipc/data - Message: {'message-id': '20210808232525806987', 'reqres': 'update', 'command': 'date_time_update', 'response': {'data': {'device': 'iot-time-device01', 'local-date': '08-Aug-2021', 'local-time': '23:25:25'}, 'status': 200}}

INFO] - Publishing PubSub Message. Topic: com.example.my_project.publish_time/mqtt/data - Message: {'message-id': '20210808232525806987', 'reqres': 'update', 'command': 'date_time_update', 'response': {'data': {'device': 'iot-time-device01', 'local-date': '08-Aug-2021', 'local-time': '23:25:25'}, 'status': 200}}
```

#### Verify / View Time PubSub Message in AWS IoT Console

At this point you can also view the MQTT PubSub message in the AWS IoT Core console. If unfamiliar with this process, follow the [View MQTT messages with the AWS IoT MQTT client](https://docs.aws.amazon.com/iot/latest/developerguide/view-mqtt-messages.html) to see the message. 

In the AWS IoT Core console, subscribe to the publish_time **Data Topic** on **com.example.my_project.simple_component/mqtt/data** you will see an update similar to below:

![simple_component_iot_coonsole](/images/simple_component_iot_console.png)
