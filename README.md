# AWS Greengrass IoT Pub/Sub Framework

![gg-framework-architecture](/images/gg-framework-architecture.png)

The PubSub model supports a range of asynchronous message patterns that overcome limitations of REST micro-service style messaging, especially in large scale distributed systems. However, this flexibility will often create unwanted dependencies and design complexity. The AWS Greengrass IoT PubSub framework provides a consistent application architecture, a defined topic schema, opinionated message routing, processing and format patterns delivered via boiler plate code as an AWS Greengrass component service skeleton.  This assures message routing and processing dependencies are met so developers can focus on application logic improving code quality and release velocity of sophisticated IoT PubSub applications. 

Follow the proceding deployment QuickStart to get up and running wih the AWS IoT Greengrass IoT PuSub Framework. For a more detailed description of the solution, go to the [Application Architecture and Developers Guide.](/docs/architecture-and-developer-guide.md)

## Quickstart: Deploying the AWS Greengrass IoT PubSub Framework Component

### Prerequisites
* An AWS Account with required permissions, see [How to Create a new AWS account](https://aws.amazon.com/premiumsupport/knowledge-center/create-and-activate-aws-account/) if needed.
* A registered [AWS Greengrass V2 core device](https://docs.aws.amazon.com/greengrass/v2/developerguide/setting-up.html).
* Knowledge of [AWS Greengrass Components](https://docs.aws.amazon.com/greengrass/v2/developerguide/create-components.html) and the [AWS Greengrass Developer Guide](https://docs.aws.amazon.com/greengrass/v2/developerguide).
* An active GitHub account (Optionally if forking this project).

### Fork or Clone the Greengrass IoT PubSub Framework:

Fork or Clone this repository as per the functionality that best describes your goals below.

**Method 1: Fork to new Repository:**
Use this method if starting a new project and you intend to capture the changes into your own Git repository now or in the future.

* To fork this project to your own repository, click the Fork button on this page:

![click-fork](/images/click-fork.png)

* Then select the Git account or organisation desired and the project will be forked (copied) onto that location. 

* Finally, substitute in your new repository details and follow the Git clone instructions below to take a local copy of the project to develop.

**Method 2: Clone to Local Copy:**
Use this method if you are testing / developing locally and don't want to capture and version any changes you make into a separate Git repository.
```
# Clone this GIT Repository
git clone https://github.com/awslabs/aws-greengrass-labs-iot-pubsub-framework.git
```
### Publish the AWS Greengrass Skeleton Service Component

In this guide, we will deploy the component service skeleton to AWS IoT Core using the AWS Greengrass Deployment Kit (GDK). The AWS GDK is a simple command line tool to build and publish Greengrass components to the AWS IoT core. It can be downloaded and installed at: (TODO: waiting public reference).

At this point in the workflow before publishing your component, you would normally expect to add your own application logic. However, the AWS GDK automatically manages versioning so we will first deploy this component in its default state and you can build on its functionality as needed. 

* Update the AWS GDK config file. Open the src/greengrass-tools-config.json config file and update the below fields accordingly
```
{
    "component" :{
      "aws-labs-iot-pubsub-framework": {  # << Component name will be set to this value.
        "author": "Amazon",
        "version": "LATEST",
        "build": {
          "build_system" :"zip"
        },
        "publish": {
          "bucket": "[S3_BUCKET_NAME]",    # << A new S3 bucket will be created starting with this name. 
          "region": "[AWS_REGION]"         # << The region your Greengrass core is registered.
        }
      }
    },
    "tools_version": "1.0.0"
  }

```

* To build and publish the AWS IoT PubSub service skeleton:
```
# CD into the locally cloned component service skeleton src directory
cd aws-greengrass-labs-iot-pubsub-framework/src

# Build the component:
greengrass-tools component build -d

# The above will create a greengrass-build and a zip-build directory with all of the files need to publish the component to the AWS Core.

# Publish the component to AWS Core:
greengrass-tools component publish -d

```

The service skeleton component will now be published to the AWS IoT Core. You can verify in the [AWS IoT Console](https://ap-southeast-2.console.aws.amazon.com/iot/) by going to the **Components** section under the **Greengrass** menu as shown below:

![published-component](/images/published-component.png)

**Note:** If you changed the component name as described in greengrass-tools-config.json file, the published component name will be as you applied.

### Deploying the AWS Greengrass Skeleton Service Component to an AWS Core.

The final step is to deploy the component to a registered AWS Greengrass Core:
* In the [AWS IoT Console](https://ap-southeast-2.console.aws.amazon.com/iot/) go to **Greengrass >> Core devices** menu item and click on the Greengrass core to deploy too.

* Select the **Deployments** tab and click on the managed deployment to add this component too.
* Click **Revise**, **Next** then select the **aws-labs-iot-pubsub-framework** (or the renamed) component
* Click next leaving all fields default until the final page then click **Deploy**

Note: You can monitor the deployment on the Greengrass core in the following logs:
* **Greengrass Core Log:** /greengrass/v2/greengrass.log and 
* **Greengrass Component Log:** /greengrass/v2/aws-labs-iot-pubsub-framework.log (or the specified component name.)

### Validating the AWS Greengrass Skeleton Service Component

As an example, the AWS Greengrass Skeleton Service Component publishes a simulated temperature measurement every 5 seconds to the components data topic (aws-greengrass-iot-pubsub-framework/mqtt/data) and will respond to well-formatted **health_check** request with a status object that is configurable from application logic.  

**Verify the Temperature Updates:**
  * In the [AWS IoT Console](https://ap-southeast-2.console.aws.amazon.com/iot/) go to the **Test** menu and subscribe to the **aws-greengrass-iot-pubsub-framework/mqtt/data** topic. You should see periodic well-formatted updates coming from the Greengrass device to the AWS Core as shown below:

![temp-update-message](/images/temp-update-message.png)

**Send a Greengrass component Health Check Request:**
  * In the [AWS IoT Console](https://ap-southeast-2.console.aws.amazon.com/iot/) go to the **Test** menu and subscribe to the **aws-greengrass-iot-pubsub-framework/mqtt/data**. (Can use the same session as above if still open). 

  * In the **Publish** section update the publish topic to **aws-greengrass-iot-pubsub-framework/mqtt/service** 

  * Add the below to the Message window and click **Pubish To Topic**
```
{
  "message-id": "123456789",
  "reqres": "request",
  "reply-sdk" : "mqtt",
  "reply-topic" : "aws-greengrass-iot-pubsub-framework/mqtt/data",
  "command": "health_check"
}
```

You should receive a response similar to the below:
![health-check-message](/images/health-check-message.png)

### Develop the Application Logic. 

At this point in the workflow is where you would start to develop your own application logic. As described in in the previous sections, we use the AWS GDK (Greengrass Deployment Kit) to deploy build and publish this component to AWS Greengrass which automatically manages versioning so it is a valid approach to first deploy this component in its default state and build on its functionality incrementally. 

### Examples

While the component service skeleton describe here provides a good example of a simple single component application, in the [examples](/examples) directory we provide a more sophisticated multi-component example simulating a smart factory application as shown below. 

![smart-factory-example](/images/smart-factory-demo.png)

Once you are familiar with the concepts we encourage you to develop and test multi-component examples like this as it better demonstrates the value of a consistent architecture and messaging formats as provided by the AWS Greengrass IoT PubSub Framework.

### (Optionally) Clean / Delete Unrequired Project Files

This project contains a number of files such as this README and associated images that will be out of context in your project that you may want to remove. Use the below to delete all unnecessary files

```
# CD into the project directory
cd aws-greengrass-labs-iot-pubsub-framework

# Delete README and associated images
rm README
rm -Rf images

# Optionally create a new readme for this project
touch README.md
echo "# My AWS Greengrass IoT PubSub Application Component" > README.md

# Optionally delete the LICENSE file
rm LICENSE

# Optionally delete the Examples and Docs file
rm -Rf examples
rm -Rf docs

```

## Summary

In this guide we have demonstrated how to build, publish and deploy the AWS Greengrass IoT PubSub Framework as a service skeleton and how to interact with it through simple PubSub message updates and requests. At this point we encourage you to read the [Application Architecture and Developers Guide](/docs/architecture-and-developer-guide.md) for this project to better understand how to successfully develop AWS Greengrass components and sophisticated IoT PubSub distributed applications with quality, scale and velocity using the AWS Greengrass IoT PubSub Framework. 

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.
