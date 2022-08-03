 
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0.

'''
my_system_message_handler.py
'''

__version__ = "0.0.1"
__status__ = "Development"
__copyright__ = "Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved."
__author__ = "Dean Colcott <https://www.linkedin.com/in/deancolcott/>"

import logging, random
 
# Config the logger.
log = logging.getLogger(__name__)
 
class MySensorMessageHandler():
    '''
    This is an example class that is developed to handle PubSub messages from the 
    AWS Greengrass PubSub SDK. When this class is registered with the SDK, PubSub
    messages will be routed here when the message 'route' value matches any of the 
    function names in this class. 

    In this example, we provide a response to requests to polls a simulated set of 
    temperature sensors as a means of seperating specific PubSub code functionality.

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
    
    def get_temp_sensor_request(self, protocol, topic, message_id, status, route, message):
        '''
        This is an example of a user defined message handler that would expect to respond
        with a temperature measurement. Once this Class is registered with the SDK as a message_handler, 
        and PubSub messages received (on any subscribed topic)  with route = 'MySensorMessageHandler.get_temp_sensor_request' 
        will be routed here.
        
        In this example, we read in parameters from the requests user defined message attribute,  
        create a well formed 'get_temp_sensor_request' message and publish it 
        to the protocol the request was made on (IPC or MQTT) on the default egress PubSub topic.

        Expected message format:
        message = {
            "sensor_id" : "Sensor1234"
        }

        Here we also publish an error message to notify remote systems of any exception. 
        '''

        try:
            # Log just for Dev / Debug.
            log.info('get_temp_sensor_request received on protocol: {} - topic: {}'.format(protocol, topic))

            # Just as a demoenstration, take the sensor ID from the user defined message.
            # Add default value "default-sensor-1234", otherwise set to vaklue in message parameter.
            sensor_id = "default-sensor-1234"
            if hasattr(message, 'sensor_id'):
                sensor_id = message['sensor_id']

            # Create a response message using the Greengrass PubSub SDK prefered message_formatter.
            # Reflect the request message_id for tracking, status and other fields as defeult.
            response_route = "MySensorMessageHandler.get_temp_sensor_response"
            msg = {
                "sensor_id" : sensor_id,
                "temp_c" : random.randint(30, 50) # Generate random temp value for example.
            }
            response =  self.message_formatter.get_message(message_id=message_id, route=response_route, message=msg)

            # Publish the message on the protocol (IPC or MQTT) that it was received on default egress topic.
            self.publish_message(protocol=protocol, message=response)

        except Exception as err:
            # Publish error to default error route, will log locally as an error as well. 
            err_msg = 'Exception in get_temp_sensor_request: {}'.format(err)
            self.publish_error(protocol, err_msg)
