 
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0.

'''
my_system_message_handler.py
'''

__version__ = "0.0.1"
__status__ = "Development"
__copyright__ = "Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved."
__author__ = "Dean Colcott <https://www.linkedin.com/in/deancolcott/>"

import logging, platform
 
# Config the logger.
log = logging.getLogger(__name__)
 
class MySystemMessageHandler():
    '''
    This is an example class that is developed to handle PubSub messages from the 
    AWS Greengrass PubSub SDK. When this class is registered with the SDK, PubSub
    messages will be routed here when the message 'route' value matches any of the 
    function names in this class. 

    In this example, we provide a response to example System related functions
    that would provide information form the AWS Greengrass core device. 

    i.e:
    1) Register this class with the AWS Greengrass PubSub SDK
    2) Any received messages with 'route' = 'my_message_handler' will route to a function here called def my_message_handler()

    ```
    Message handling functions much be in the below format:
    def my_message_handler(self, protocol, topic, message_id, status, route, message):
        # Process message
    ```

    The SDK will decompose the received message fields and route to valid functions here accordingly.    
  
    '''

    def __init__(self, publish_message, publish_error, message_formatter):
        '''
        A common patten when receiving a PubSub message is to create and publish a response
        so we in this example we pass a reference to the PubSub SDK publish_message, publis_error callbacks 
        and message_formatter object.

        '''
        self.publish_message = publish_message
        self.publish_error = publish_error
        self.message_formatter = message_formatter

    ########################################################
    ## Example User Defined Message handlers  ##############
    ########################################################
    
    def get_health_check_request(self, protocol, topic, message_id, status, route, message):
        '''
        This is an example of a user defined message handler that would expect to respond
        with a system health status. Once this Class is registered with the SDK as a message_handler, 
        and PubSub messages received (on any subscribed topic)  with route = 'MySystemMessageHandler.health_check_request' 
        will be routed here.
        
        In this example, we create a well formed 'health_check_response' message and publish it 
        to the protocol the request was made on (IPC or MQTT) on the default egress PubSub topic.

        Here we also publish an error message to notify remote systems of any exception. 
        '''

        try:
            # Log just for Dev / Debug.
            log.info('get_health_check_request received on protocol: {} - topic: {}'.format(protocol, topic))

            # Create a response message using the Greengrass PubSub SDK prefered message_formatter.
            # Reflect the request message_id for tracking, status and other fields as defeult.
            response_route = "MySystemMessageHandler.get_health_check_response"
            msg = {"status" : "System OK"}
            response =  self.message_formatter.get_message(message_id=message_id, route=response_route, message=msg)

            # Publish the message on the protocol (IPC or MQTT) that it was received on default egress topic.
            self.publish_message(protocol=protocol, message=response)

        except Exception as err:
            # Publish error to default error route, will log locally as an error as well. 
            err_msg = 'Exception in get_health_check_request: {}'.format(err)
            self.publish_error(protocol, err_msg)
    
    def get_system_details_request(self, protocol, topic, message_id, status, route, message):
        '''
        Here we use the Python Platform Library to return platform (arch and OS / Distro) 
        details.
        
        In this example, we create a well formed 'get_system_response' message and publish it 
        to the protocol the request was made on (IPC or MQTT) on the default egress PubSub topic.
        '''

        try:
            # Log just for Dev / Debug.
            log.info('get_system_request received on protocol: {} - topic: {}'.format(protocol, topic))

            # Create a response message using the Greengrass PubSub SDK prefered message_formatter.
            # Reflect the request message_id for tracking, status and other fields as defeult. 
            response_route = "get_system_response"
            msg = {
                "system" : platform.system(),
                "release" : platform.release(),
                "version" : platform.version(),
                "platform" : platform.platform()
            }
            response =  self.message_formatter.get_message(message_id=message_id, route=response_route, message=msg)

            # Publish the message on the protocol (IPC or MQTT) that it was received on default egress topic.
            self.publish_message(protocol=protocol, message=response)

        except Exception as err:
            # Publish error to default error route, will log locally as an error as well. 
            err_msg = 'Exception in get_system_request: {}'.format(err)
            self.publish_error(protocol, err_msg)
