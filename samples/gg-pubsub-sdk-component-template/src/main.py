# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0.

'''
main.py:

AWS Greengrass component demo for the AWS Greengrass PubSub SDK.

Simple Time publish and IPC / MQTT message logger
'''

__version__ = "0.0.1"
__status__ = "Development"
__copyright__ = "Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved."
__author__ = "Dean Colcott <https://www.linkedin.com/in/deancolcott/>"

import sys
import json
import time
import logging
from datetime import datetime

# AWS Greengrass PubSub Componnht SDK Imports.
from awsgreengrasspubsubsdk.message_formatter import PubSubMessageFormatter
from awsgreengrasspubsubsdk.pubsub_client import AwsGreengrassPubSubSdkClient

# Example user defined message handling classes
from pubsub_message_handlers.my_system_message_handler import MySystemMessageHandler
from pubsub_message_handlers.my_sensor_message_handler import MySensorMessageHandler

# Config the logger.
log = logging.getLogger(__name__)
logging.basicConfig(format="[%(name)s.%(funcName)s():%(lineno)d] - [%(levelname)s] - %(message)s", 
                    stream=sys.stdout, 
                    level=logging.DEBUG)

class MyAwsGreengrassV2Component():

    def __init__(self, ggv2_component_config):
        '''
            Initialises the AWS Greengrass V2 custom component including IPC and MQTT PubSub SDK Client.
        '''
        
        log.info('Initialising AwsGreengrassV2 PubSub SDK Component Example.....')
        
        pubsub_base_topic = ggv2_component_config['base-pubsub-topic']
        log.info('PubSub Base Topic: {}'.format(pubsub_base_topic))
        
        ipc_subscribe_topics = ggv2_component_config['ipc-subscribe-topics']
        log.info('IPC Custom Subscribe Topics: {}'.format(ipc_subscribe_topics))
        
        mqtt_subscribe_topics = ggv2_component_config['mqtt-subscribe-topics']
        log.info('MQTT Custom Subscribe Topics: {}'.format(mqtt_subscribe_topics))
        
        # Initilise the PubSub Message Formatter and PubSub Client SDK. 
        self.message_formatter = PubSubMessageFormatter()
        self.pubsub_client = AwsGreengrassPubSubSdkClient(pubsub_base_topic, self.default_message_handler )

        # Take handles to SDK publish message and error just for easier access.
        self.publish_message = self.pubsub_client.publish_message
        self.publish_error = self.pubsub_client.publish_error

        ##################################################################################
        # Initilise and register example user defined message handler classes for message routing.
        ##################################################################################
        # Message handler for System type requests
        log.info('Initialising and registering MySystemMessageHandler Class')
        self.my_system_message_handler = MySystemMessageHandler(self.publish_message, self.publish_error, self.message_formatter)
        self.pubsub_client.register_message_handler(self.my_system_message_handler)
        log.info('Initialising and registering MySystemMessageHandlerClass - Complete')

         # Message handler for connected sensor type requests
        log.info('Initialising and registering MySensorMessageHandler Class')
        self.my_sensor_message_handler = MySensorMessageHandler(self.publish_message, self.publish_error, self.message_formatter)
        self.pubsub_client.register_message_handler(self.my_sensor_message_handler)
        log.info('Initialising and registering MySensorMessageHandler Class - Complete')

        # Activate the MQTT and IPC PubSub Channels, can active one, either or both.
        log.info('Activating AWS Greengrass PubSub SDK IPC and MQTT Protocols')
        self.pubsub_client.activate_ipc_pubsub()
        self.pubsub_client.activate_mqtt_pubsub()
        log.info('Activating AWS Greengrass PubSub SDK IPC and MQTT Protocols - Complete')
        
        # Subscribe to any user defined IPC topics
        log.info('Subscribing to user defined IPC Protocols')
        for topic in ipc_subscribe_topics:
            self.pubsub_client.subscribe_to_topic('ipc', topic)
        log.info('Subscribing to user defined IPC Protocols - Complete')

        # Subscribe to any user defined MQTT topics
        log.info('Subscribing to user defined MQTT Protocols')
        for topic in mqtt_subscribe_topics:
            self.pubsub_client.subscribe_to_topic('mqtt', topic)
        log.info('Subscribing to user defined MQTT Protocols - Complete')
        
        log.info('Initilising AwsGreengrassV2 PubSub SDK Component Example Complete.')

    ##################################################
    # Main service / process application logic
    ##################################################
    def service_loop(self):
        '''
        Holds the process up while handling event-driven PubSub triggers.
        Put synchronous application logic here or have the component completely event driven.
        
        This example periodically publishes the local time to IPC and MQTT in a well formatted message.
        '''
        
        while True:
            try:
                # Build and publish a well formatted message displaying local time to IPC and MQTT
                receive_route = "local_time_update"
                my_message = { "local-time" : datetime.now().strftime("%d-%b-%Y %H:%M:%S")  }
                sdk_format_msg = self.message_formatter.get_message(route=receive_route, message=my_message)
                log.info('Publishing message: {}'.format(sdk_format_msg))
                self.publish_message('ipc_mqtt', sdk_format_msg)
            
            except Exception as err:
                # Publish error to IPC and MQTT on default error topic. 
                protocol = 'ipc_mqtt'
                err_msg = 'Exception in main process loop: {}'.format(err)
                self.publish_error(protocol, err_msg)
                
            finally:
                time.sleep(10)

    def default_message_handler(self, protocol, topic, message_id, status, route, message):
        '''
            This default message handler function is a route of last resort to handle 
            PubSub messages received by the SDK with a route value that does not 
            match any functions in the registered message_handler classes.

            In this example, we generate and publish an error message to both IPC and MQTT.
            You could instead handle this locally or just sliently discard messages here depending 
            on the application.
        '''

        # Publish error to IPC and MQTT on default error topic, will log locally as an error as well. 
        err_msg = 'Received message to unknown route / message handler: {} - message: {}'.format(route, message)
        self.publish_error(protocol, err_msg)

if __name__ == "__main__":

    try:

        # Parse config from component recipe into sys.argv[1] 
        ggv2_component_config = sys.argv[1]
        ggv2_component_config = json.loads(ggv2_component_config)
        
        log.info('GG PubSub SDK Config: {}'.format(ggv2_component_config))

        # Create the component class with the parsed Greengrass recipe config.
        ggv2_component = MyAwsGreengrassV2Component(ggv2_component_config)
        
        # Start the main process loop to hold up the process.
        ggv2_component.service_loop()

    except Exception as err:
        log.error('Exception occurred initialising component. ERROR MESSAGE: {}'.format(err))
