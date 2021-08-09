# AWS Greengrass Application Framework
## AWS Greengrass V2 Anatomy
The below propvides a brief overview of AWS Greengrass V2 itself and a description of the individual features. For more detail, see the [AWS Greengrass V2 Developer Guide](https://docs.aws.amazon.com/greengrass/v2/developerguide/what-is-iot-greengrass.html).

![gg-overview](/images/gg-overview.png)

1.	**AWS IoT Core:** The AWS cloud hosted IoT services that provides a scalable device gateway for message processing and an interface to the variety of AWS data and analytics, messaging and notification, logging and storage services that integrate to the AWS IoT Core.

3.	**AWS Greengrass Core:** The edge device running the AWS Greengrass V2 runtime agent that provides the physical resources and interfaces to the real world. Acts as both a gateway and IoT edge device.

5.	**AWS Greengrass V2 Runtime:** The AWS Greengrass agent that runs on remote cores and enables OTA deployment of component groups as well as inter-component communications, messaging to AWS IoT Core platform and remote device management, logging and status updates.

7.	**AWS Greengrass V2 Deployment**: Groups of services (known in AWS Greengrass V2 as components) and metadata that defines which remote AWS IoT Greengrass Core (Edge devices) to deploy components, the code itself and a set of security policies and configurations to apply. Data driven configuration for each component within the deployment is provided by a JSON configuration file that is provided as an AWS Greengrass V2 recipe.

9.	**AWS Greengrass V2 Component:** Is a code module (and dependencies) in any native language supported by the AWS Greengrass core that is deployed and managed Over the Air (OTA) by the AWS IoT Greengrass platform. This can be considered as a service or the most granular level of separation of application functionality in the AWS Greengrass V2 framework.

11.	**AWS Greengrass V2 Recipe:** Provides metadata and configuration parameters for an AWS IoT Greengrass V2 Component.

13.	**IPC Topic / MQTT PubSub Message Bus:** The AWS Greengrass IPC Topic and MQTT PubSub message bus that enables topic-based messaging between AWS Greengrass V2 Components and the AWS IoT Core respectively.

