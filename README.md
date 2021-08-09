# AWS Greengrass V2 Application Framework
## Developing Event Driven IoT PubSub applications using AWS Greengrass V2.

![gg-framework-architecture](/images/gg-framework-architecture.png)

- [Developer Guide](#developer-guide)
  * [Prerequisites](#prerequisites)
  * [Anatomy of the AWS Greengrass Application Framework](#anatomy-of-the-aws-greengrass-application-framework)
  * [AWS Greengrass Example Applications](#aws-greengrass-example-applications)
  * [IDE to Greengrass Core Device](#ide-to-greengrass-core-device)
  * [Develop a Custom Greengrass V2 Application](#develop-a-custom-greengrass-v2-application)
    + [Step 1: Copy the Template Greengrass Application:](#step-1--copy-the-template-greengrass-application-)
    + [Step 2: Create Custom Publish Time Component](#step-2--create-custom-publish-time-component)
    + [Step 3: Deploy the Publish Local Time Component:](#step-3--deploy-the-publish-local-time-component-)
    + [Deployment Example Summary](#deployment-example-summary)
  * [Features and Functionality](#features-and-functionality)
  * [Application Properties Dependency Injection](#application-properties-dependency-injection)
    + [PubSub Topic Schema](#pubsub-topic-schema)
    + [Property Dependency Injection](#property-dependency-injection)
    + [PubSub Access Policy](#pubsub-access-policy)
  * [PubSub Convenience Classes](#pubsub-convenience-classes)
    + [Message Publishing](#message-publishing)
    + [PubSub Message Concurrency](#pubsub-message-concurrency)
    + [PubSub Message Routing](#pubsub-message-routing)
  * [PubSub Message Formats](#pubsub-message-formats)
    + [Request Message](#request-message)
    + [Response Message](#response-message)
    + [Update Message](#update-message)
  * [Main Module](#main-module)
    + [Application Workflows](#application-workflows)

# Developer Guide

The AWS Greengrass Application Framework provides a consistent application architecture and template code to improve code quality and velocity while reducing the initial learning curve for those wishing to develop event driven IoT applications using [AWS Greengrass V2](https://docs.aws.amazon.com/greengrass/v2/developerguide/what-is-iot-greengrass.html) and in particular, [AWS Greengrass V2 Custom Components](https://docs.aws.amazon.com/greengrass/v2/developerguide/create-components.html).

This document provides a functional Developer Guide for the AWS Greengrass Application Framework, an application architecture is presented in the [AWS Greengrass Application Framework Architecture Guide](docs/event-driven-pub-sub-architecture.md) 

## Prerequisites
* An AWS Account with required permissions, see [How to Create a new AWS account](https://aws.amazon.com/premiumsupport/knowledge-center/create-and-activate-aws-account/) if needed.
* An [AWS Greengrass V2 core device](https://docs.aws.amazon.com/greengrass/v2/developerguide/setting-up.html) with the [Greengrass CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-welcome.html) installed.
* Knowledge of [AWS Greengrass Components](https://docs.aws.amazon.com/greengrass/v2/developerguide/create-components.html) and the [AWS Greengrass Developer Guide](https://docs.aws.amazon.com/greengrass/v2/developerguide).

## Anatomy of the AWS Greengrass Application Framework 

The AWS Greengrass Application Framework provides a consistent PubSub topic schema, message workflows, formats and common coding patterns. The application architecture is practically applied through a template AWS Greengrass application found in the [00-greengrass-application-template](examples/00-greengrass-application-template) directory.

The AWS Greengrass application template includes:

```text
00-greengrass-application-template
├── deploy_tools
│   └── gg_list_components.sh                        <--- Script to list installed Greengrass components
│   └── gg_merge_components.sh                       <--- Script to install applications Greengrass components
│   └── gg_remove_components.sh                      <--- Script to remove applications Greengrass components
├── recipes
│   └── com.example.my_project.my_component.json     <--- Template Component Recipe
└── src                                              <--- Greengrass component artifacts source directory
    └── 0.0.1                                        <-- Greengrass semantic versioning directory
        ├──  pubsub                                  <-- PubSub SDK Wrappers
        │    ├── ipc_pubsub.py                       <-- IPC Topic PubSub Wrapper
        │    ├── mqtt_pubsub.py                      <-- MQTT Topic PubSub Wrapper
        │    └── pubsub_messages.py                  <-- PubSub Message Format definition
        └── main.py                                  <-- Message processing and application logic

```

* [**com.example.my_project.my_component.json:**](examples/00-greengrass-application-template/recipes/com.example.my_project.my_component.json) A Template [AWS Greengrass Component Recipe](https://docs.aws.amazon.com/greengrass/v2/developerguide/component-recipe-reference.html) with pre-defined config that manages the PubSub topic schema, access policy and other parametrised fields.

* [**deploy_tools:**](examples/00-greengrass-application-template/src/com.example.my_project.my_component/deploy_tools) Simple bash scripts to use the [AWS Greengrass CLI](https://docs.aws.amazon.com/greengrass/v2/developerguide/gg-cli.html) to list, deploy and remove components for the contained Greengrass application. This toolset is for deploying locally on a Greengrass core device during development opposed to deploying through the AWS console as for production releases.
* [**main.py:**](examples/00-greengrass-application-template/src/com.example.my_project.my_component/0.0.1/main.py) Main method of the AWS Greengrass Application Template. Provides a PubSub message callback and per topic message routers and processors to simplify and standardised message processing. 

* [**ipc_pubsub.py:**](examples/00-greengrass-application-template/src/com.example.my_project.my_component/0.0.1/pubsub/ipc_pubsub.py) A convenience wrapper around the AWS Greengrass [InterProcess communication (IPC)](https://docs.aws.amazon.com/greengrass/v2/developerguide/interprocess-communication.html) library. This initialises the SDK to publish and subscribe to the prescribed topic schema for communication between AWS Greengrass components.

* [**mqtt_pubsub.py:**](examples/00-greengrass-application-template/src/com.example.my_project.my_component/0.0.1/pubsub/mqtt_pubsub.py) As for IPC PubSub, however; the MQTT SDK is responsible for publishing and subscribing to messages using the MQTT protocol between the Greengrass component and the AWS IoT Core platform. 

* [**pubsub_messages.py:**](examples/00-greengrass-application-template/src/com.example.my_project.my_component/0.0.1/pubsub/pubsub_messages.py) Provides a consistent PubSub message format with defined request / response, message routing and tracing fields.

## AWS Greengrass Example Applications
The AWS Greengrass Application Framework provides a number of example applications from single component solutions to a more advanced Smart Factory example. Each example has a detailed deployment guide and a set of simple deploy scripts that uses the [AWS Greengrass CLI](https://docs.aws.amazon.com/greengrass/v2/developerguide/gg-cli.html) to deploy the component locally from the Greengrass core device. 

If at this stage your goal is just to deploy and test a functional Greengrass application, we recommend trying these [examples](examples) to get started. 

## IDE to Greengrass Core Device
When developing locally on an AWS Greengrass core device, it’s convenient to have an Integrated Development Environment (IDE) you can work in. The recommended way of developing on a Greengrass core device is to use the remote SSH facilities of common IDEs such as Visual Studio Code to connect to your Greengrass core device from your development machine. See [Remote Developing using SSH](https://code.visualstudio.com/docs/remote/ssh) to see how to configure this using Visual Studio. 

## Develop a Custom Greengrass V2 Application

If your goal is to create your own custom AWS Greengrass application this is the section for you!

An AWS Greengrass application consists of one or more [Greengrass Components](https://docs.aws.amazon.com/greengrass/v2/developerguide/manage-components.html), each of which contain a **component recipe** that defines metadata, configuration and lifecycle events and the **component artifacts** which include source code, binaries, other dependencies and static resources. See the [Greengrass Application Anatomy](docs/greengrass-application-anatomy.md) for a more detailed description.

 The AWS Greengrass Application Framework provides a template application in the [00-greengrass-application-template](examples/00-greengrass-application-template) directory. This contains a Greengrass component called: **com.example.my_project.my_component**.  
 
 In the below example, we will first copy the Greengrass Application Template as a base. From there, we will develop custom application logic to build a component that publishes the Greengrass core device local time on the IPC (component to component) and MQTT (component to AWS IoT Core) SDKs over the components **Data Topic** that other interested components or the AWS IoT core can subscribe to. 

### Step 1: Copy the Template Greengrass Application:
```
# Clone this GIT Repository
git clone https://github.com/aws-samples/aws-greengrass-application-framework.git

# Copy the Greengrass application template to a new directory for the publish_time application
APP_NAME=greengrass_publish_time
cp -rf aws-greengrass-application-framework/examples/00-greengrass-application-template $APP_NAME

# 'cd' into the application deploy_tools directory
cd $APP_NAME/deploy_tools

```

### Step 2: Create Custom Publish Time Component
In this step, we replicate the component template to a new component that will publish the local time to the components **Data Topic** every 1 second.   

**Note:** Below assumes active path is **$APP_NAME/deploy_tools** from previous step. 
```
# Copy the template recipe to a new component called: com.example.my_project.publish_time
cp ../recipes/com.example.my_project.my_component.json ../recipes/com.example.my_project.publish_time.json 

# Copy the template source code for the corresponding component: com.example.my_project.publish_time
cp -rf ../src/com.example.my_project.my_component ../src/com.example.my_project.publish_time
```

#### Update the publish_time component recipe:
Open the component recipe **recipes/com.example.my_project.publish_time.json** in an IDE and use Find and Replace function to replace the default name **my_component** with the new component name **publish_time**.   

In a production component, you would also update the **com.example.my_project** prefix. 

**Note:** Make sure to save and then can close the publish_time component recipe.

#### Update the merge and remove component deploy scripts:
In the **deploy_tools** directory, open **gg_merge_components.sh** and **gg_remove_components.sh** and again, Find and Replace the default **my_component** with the new component name **publish_time**  

**Note:** Make sure to save and then can close the merge and remove deploy scripts.

#### Update publish_time component to publish the local time every second:

In src/com.example.my_project.publish_time/0.0.1/main.py:
```

# 1) Add datetime import at top of module (with other import statements)
from datetime import datetime

# 2) Replace the default service_loop() function with the below:
    def service_loop(self):
        '''
        Example service_loop function that publishes the local time from the AWS Greengrass core device 
        every 1 second to the components Data Topic.
        '''

        while True:
            try:
                # Example: perform a periodic action (Remove / comment out as needed)
                self.publish_local_time()

                # Loop for 1 sec and publish time update
                time.sleep(1)

            except Exception as err:
                log.error('EXCEPTION: Exception occurred in service loop - ERROR MESSAGE: {}'.format(err))

# 3) Add the following function publish_local_time function directly below the service_loop() function

    def publish_local_time(self):
        '''
        Publish the Greengrass core device local time to the components IPC and MQTT Data topic
        as an unsolicited UPADTE message.
        '''
        
        try:
            ### Create an example data update command and params fields
            command = 'date_time_update'
            status = 200
            now = datetime.now()
            params = {
                    "device" : "iot-time-device01",
                    "local-date" : now.strftime("%d-%b-%Y"),
                    "local-time" : now.strftime("%H:%M:%S")
            }

            # Create the local time UPDATE message format
            update_message = self.pubsub_messages.get_pubsub_update(command, status, params)
            
            # Publish the message to this applications IPC DATA Topic
            # This will be available to other components that subscribe to this components data topic
            self.publish_message('ipc', self.ipc_data_topic, update_message)

            # Publish the message to this applications MQTT Data Topic
            # This will be available in the AWS IoT Core for viewing / processing
            self.publish_message('mqtt', self.mqtt_data_topic, update_message)

        except Exception as err:
                log.error('EXCEPTION: Exception in publish_local_time - ERROR MESSAGE: {}'.format(err))

```
**Note:** Make sure to save and then can close **main.py**.

* **In the above:**
1. We imported the datetime library
2. Updated the main service_loop process to call the publish_local_time() function every 1 second
3. In publish_local_time() function:
  * Created a well-formatted UPDATE message (message that is generated without a specific request)
  * Published the messages to the IPC SDK (component to component) message bus on the IPC Data Topic,
  * Published the messages to the MQTT SDK (component to component) message bus on the MQTT Data Topic.

### Step 3: Deploy the Publish Local Time Component:
```
# Deploy with AWS Greengrass CLI using the simple AWS Greengrass CLI merge script 
sudo ./gg_merge_components.sh

```

#### Verify the deployment in greengrass.log:
```sudo tail -f /greengrass/v2/logs/greengrass.log```

Once complete, expect to see (can take 30+ seconds):  
```Persist link to last deployment. {link=/greengrass/v2/deployments/previous-success}```

#### Use gg_list_components.sh to check deployed components:
```sudo ./gg_list_components.sh | grep Name```

Once complete, expect to see the default component deployed:  
```Component Name: com.example.my_project.publish_time```

#### Verify the specific example component/s logs:
```sudo tail -f /greengrass/v2/logs/com.example.my_project.publish_time.log```

Once complete, expect to see a 1 second update of the IPC and MQTT PubSub Message publish:  

```
[INFO] - Publishing PubSub Message. Topic: com.example.my_project.publish_time/ipc/data - Message: {'message-id': '20210808204933370697', 'reqres': 'update', 'command': 'date_time_update', 'response': {'data': {'device': 'iot-time-device01', 'local-date': '08-Aug-2021', 'local-time': '20:49:33'}, 'status': 200}}

[INFO] - Publishing PubSub Message. Topic: com.example.my_project.publish_time/mqtt/data - Message: {'message-id': '20210808204933370697', 'reqres': 'update', 'command': 'date_time_update', 'response': {'data': {'device': 'iot-time-device01', 'local-date': '08-Aug-2021', 'local-time': '20:49:33'}, 'status': 200}}
```

#### Verify / View Time PubSub Message in AWS IoT Console

At this point you can also view the MQTT PubSub message in the AWS IoT Core console. If unfamiliar with this process, follow the [View MQTT messages with the AWS IoT MQTT client](https://docs.aws.amazon.com/iot/latest/developerguide/view-mqtt-messages.html) to see the message. 

In the AWS IoT Core console, subscribe to the publish_time **Data Topic** on **com.example.my_project.publish_time/mqtt/data** you will see a update similar to below:

![pubsub-classes](/images/publish_time_console.png)

### Deployment Example Summary
In the above example, we deployed a simple single component application that published a well-formatted UPDATE message containing the Greengrass core device local time once per second. This exercise is a base for the [02-publish-local-time](examples/02-publish-local-time) example that extends this to include a second Greengrass component that listens and logs the time PubSub message from the IPC PubSub SDK. Compare your code to the publish_time component in that example if needed.

In summary, to create an AWS Greengrass application using this framework:
1) Copy [00-greengrass-application-template](examples/00-greengrass-application-template) to a new application directory,
2) Copy and rename the component and recipe templates once for each new AWS Greengrass component the application will deploy,
3) Update the deploy_tools merge and remove scripts to include the new components (Only needed for development purposes),
4) Update each component recipe to the components name and add / update to the components topic schema, subscribe topics and the IPC/MQTT access policies,
5) Update the application logic as needed in main.py and / or create new modules called from main,
6) Test locally with the deploy_tools scripts. 

Once development is complete, launch via the AWS IoT Greengrass console. 

For more detailed deployments with request/response PubSub patterns, see the [examples](examples) directory.
 
## Features and Functionality
The following sections detail the features and functionality of the AWS Greengrass Application Framework. 

## Application Properties Dependency Injection

In AWS Greengrass V2, the [Component Recipe](https://docs.aws.amazon.com/greengrass/v2/developerguide/component-recipe-reference.html) defines various parameters and lifecycle events for the Greengrass component. The component recipe is JSON formatted and can pass in configuration and metadata to the service. This includes the components functional name, version, description, PubSub access policy and provides a **DefaultConfiguration** tag for JSON fields that can be passed to the Greengrass component application logic.

The AWS Greengrass Application Framework defines a DefaultConfiguration field called **GGV2ComponentConfig** in which all configuration values are passed to the components application logic.

i.e:
```
"RecipeFormatVersion": "2020-01-25",
"ComponentName": "com.example.my_project.my_component",
"ComponentVersion": "0.0.1",
"ComponentDescription": "AWS Greengrass V2 Application Framework recipe skeleton with prescribed IPC and MQTT Topics.",
"ComponentPublisher": "Dean Colcott: <https://www.linkedin.com/in/deancolcott/>",
"ComponentConfiguration": {
  "DefaultConfiguration": {
    "GGV2ComponentConfig": {
    [Parameterised application configuration......]
```

### PubSub Topic Schema
One of the first decisions to make when developing a PubSub application is the IPC/MQTT topics that will be used for communications between individual components and the central hub / gateway (The AWS IoT Core in this case). This framework prescribes a [PubSub Topic Schema](docs/event-driven-pub-sub-architecture.md#aws-greengrass-pubsub-message-bus-ipc--mqtt) and [PubSub Message Patterns](docs/event-driven-pub-sub-architecture.md#pubsub-message-patterns) with a small set of pre-defined topics that perform specific functions.

These are:
* **Service Topic:** Messages to the service itself such as status and 1-to-1 data or action request messages.
* **Data Topic:** Publishing data such as sensor data that other components can subscribe to.
* **Broadcast Topic:** A system wide broadcast typically to manage components or systems errors.

These topics are config driven in that they are defined in the template component recipe: 
```
"DefaultConfiguration": {
  "GGV2ComponentConfig": {
    "mqtt_pubsub_timeout" : 5,
    "mqtt_service_topic" : "com.example.my_project.my_component/mqtt/service",
    "mqtt_data_topic" : "com.example.my_project.my_component/mqtt/data",
    "mqtt_broadcast_topic" : "com.example.my_project/mqtt/broadcast",
    "mqtt_subscribe_topics" : ["com.example.my_project.my_component/mqtt/service", "com.example.my_project/mqtt/broadcast"],
    "ipc_pubsub_timeout" : 5,
    "ipc_service_topic": "com.example.my_project.my_component/ipc/service",
    "ipc_data_topic" : "com.example.my_project.my_component/ipc/data",
    "ipc_broadcast_topic" : "com.example.my_project/ipc/broadcast",
    "ipc_subscribe_topics" : ["com.example.my_project.my_component/ipc/service", "com.example.my_project/ipc/broadcast"]
  }
```
The Main module reads in and parameterises the individual topics and passes them to the IPC and MQTT PubSub modules which automatically initialises the required publishers and topic subscriptions. Parametrising the PubSub topic schema enforces consistency across components and solves the challenge of updating the applications topic schema without the need for code changes. If applied equally across all Greengrass components in a distributed IoT application; this forms a common set of communications channels to simplify development and greatly reduces dependencies and design decisions needed to get started.

You can of course, extend this or any part of the GGV2ComponentConfig object to add your own config parameters.

### Property Dependency Injection
The parameterised fields of the framework’s recipe template are passed to the component application logic in the **Lifecycle >> Run** field where we set main.py to call on start-up and pass the GGV2ComponentConfig object as configuration to the application.

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

### PubSub Access Policy

The Greengrass component recipe defines the components PubSub access policy. The recipe template has been configured to follow the [PubSub Access Policy](docs/event-driven-pub-sub-architecture.md#pubsub-access-policy) recommended in this framework. The PubSub access policy configured in the recipe template is automatically applied to the component as its deployed to the Greengrass core device/s.

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

### Message Publishing

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
Distributed PubSub applications can quickly become difficult to manage if the topic schema is not well defined and an efficient and repeatable message handling system in place. As the number of topics receiving messages increases, so does the complexity of the application logic. The AWS Greengrass Application Framework solves this with a system that approximates that of a REST based API with a single message callback that validates and normalises incoming messages and then a series of message routers and processors. This simplifies message handling and scales to meet the needs of very simple to very sophisticated applications. 

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

## PubSub Message Formats

In general, the PubSub model provides greater flexibility than a REST interface which has more defined control fields. The trade-off is that developers need to design and agree on individual message tracking, return path, message routing and type fields for each application. This is described in more detail in [Event Driven PubSub Applications](docs/event-driven-pub-sub-architecture.md#event-driven-pubsub-applications).

Defining message formats for payload, control and routing fields influences many design decisions and ultimately forms a major part of interface contracts. This process can grind even a simple application to a halt with dependencies between components, systems and teams. The AWS Greengrass Application Framework solves this problem by providing a defined message format for REQUEST, RESPONSE and UPDATE message types that have been developed in support of the frameworks prescribed means of PubSub message routing and processing. 

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

The below demonstrates how to build and publish the example well-formatted REQUEST PubSub message using the AWS Greengrass Application Framework.
```
# Example from main.py. 

#### Create a well formatted REQUEST message #####
# Specify the requested command and param fields to send in the REQUEST.
# e.g:
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
# e.g (is most common to publish a REQUEST on the receiving components Service Topic):

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

The below demonstrates how to build and publish the example well-formatted RESPONSE PubSub message using the AWS Greengrass Application Framework.
```
# Example from main.py. 

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

The final piece of the AWS Greengrass Application framework is the main module. This is called on component boot-up (as nominated by the template component recipe). The Main module provides the PubSub message callback and message processing and routing functions. In a larger production  application, you may choose to separate message routers and processors completely or for groups of related functions to an external module. 

### Application Workflows
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


## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.
