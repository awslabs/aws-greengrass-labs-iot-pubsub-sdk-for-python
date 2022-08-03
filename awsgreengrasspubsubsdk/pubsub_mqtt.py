# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0.

'''
Abstracts AWS Greengrass V2 MQTT PubSub SDK that manages subscriptions 
and a method to publish to AWS Greengrass MQTT topics. This is intended
for use in an AWS Greengrass V2 Component SDK to provide MQTT PubSub services. 

IPC MQTT core is for communications between AWS Greengrass Components and 
the AWS IoT Core. This can be used to send MQTT messaging to the AWS IoT core 
to save data, trigger alarms or alerts or to trigger other AWS services and applications.

 For more detail on AWS Greengrass V2 see the Developer Guide at:
https://docs.aws.amazon.com/greengrass/v2/developerguide/what-is-iot-greengrass.html

'''

__version__ = "0.1.4"
__status__ = "Development"
__copyright__ = "Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved."
__author__ = "Dean Colcott <https://www.linkedin.com/in/deancolcott/>"

import json
import logging
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
import awsiot.greengrasscoreipc
import awsiot.greengrasscoreipc.client as client
from awsiot.greengrasscoreipc.model import (
    PublishToIoTCoreRequest,
    SubscribeToIoTCoreRequest,
    IoTCoreMessage,
    UnauthorizedError,
    QOS
)

# Init the logger.
log = logging.getLogger(__name__)

class MqttPubSub():

    def __init__(self, message_callback, mqtt_subscribe_topics):
        
            
        super().__init__()

        log.info('Initialising / Activating AWS Greengrass V2 MQTT PubSub Client....')
        
        # PubSub default MQTT Timeout and QoS
        self.mqtt_default_timeout = 10
        self.mqtt_default_qos = QOS.AT_LEAST_ONCE 
        
        # PubSub message callback.
        self.message_callback = message_callback

        # MQTT Subscribe Topics
        self.mqtt_subscribe_topics = mqtt_subscribe_topics

        # List of active topics subscribed too.
        self.mqtt_subscribed_topics = []

        # Create the mqtt_clients
        self.mqtt_subscribe_client = awsiot.greengrasscoreipc.connect()
        self.mqtt_publish_client = awsiot.greengrasscoreipc.connect()
        
        # Init MQTT PubSub's
        self._init_mqtt_subscriber()
        self._init_mqtt_publisher()

        log.info('Initialising / Activating AWS Greengrass V2 MQTT PubSub Client Complete')

    ###############################################
    # Setters
    def set_mqtt_default_qos(self, mqtt_default_qos):
        self.mqtt_default_qos = mqtt_default_qos
    
    def set_mqtt_default_timeout(self, mqtt_default_timeout):
        self.mqtt_default_timeout = mqtt_default_timeout
    
    ###############################################
    # IPC MQTT Iot Core PubSub Functions
    def _init_mqtt_subscriber(self):
        '''
        Initialise subscription to requested MQTT IoT Core topics.
        '''
        
        self.handler = MqttPubSub.__MqttSubscribeHandler(self.message_callback)

        for subscribe_topic in self.mqtt_subscribe_topics:
            self.subscribe_to_topic(subscribe_topic)
    
    def subscribe_to_topic(self, topic):

        log.info('MQTT Subscribing to Topic: {}:'.format(topic))
        
        if (topic in self.mqtt_subscribed_topics):
            log.info('Returning with no action. Already subscribed to MQTT topic: {}'.format(topic))
            return
        
        request = SubscribeToIoTCoreRequest()
        request.topic_name = topic
        request.qos = self.mqtt_default_qos
        operation = self.mqtt_subscribe_client.new_subscribe_to_iot_core(self.handler)
        future = operation.activate(request)
        # call the result to block until the future has completed.
        future.result(self.mqtt_default_timeout)

        self.mqtt_subscribed_topics.append(topic)
        log.info('Complete MQTT subscribing to topic: {}'.format(topic))

    def _init_mqtt_publisher(self):
        '''
        Initialise publisher to requested IoT Core MQTT topics.
        '''

        log.info('Initialising MQTT Publisher.')
        self.mqtt_request = PublishToIoTCoreRequest()
        self.mqtt_request.qos = self.mqtt_default_qos

    def publish_to_mqtt(self, topic, message_object, timeout=None):
        '''
        Publish a Python object serlized as a JSON message to the IoT Core MQTT topic.
        '''
        
        try:

            log.debug('MQTT PUBLISH: topic: {} - Message: {}'.format(topic, message_object))
            self.mqtt_request.topic_name = topic
            json_message = json.dumps(message_object)
            self.mqtt_request.payload = bytes(json_message, "utf-8")
            operation = self.mqtt_publish_client.new_publish_to_iot_core()
            operation.activate(self.mqtt_request)
            future = operation.get_response()
            future.result(timeout if timeout!=None else self.mqtt_default_timeout)

        except KeyError as key_error:
            raise Exception('KeyError occurred publishing to IoT Core on MQTT Topic. ERROR: {} - TOPIC: {} - MESSAGE: {}'.format(key_error,  topic, message_object))

        except concurrent.futures.TimeoutError as timeout_error:
            raise Exception('Timeout occurred publishing to IoT Core on MQTT Topic. ERROR: {} - TOPIC: {} - MESSAGE: {}'.format(timeout_error,  topic, message_object))

        except UnauthorizedError as unauth_error:
            raise Exception('Unauthorized error publishing to IoT Core on MQTT Topic. ERROR: {} - TOPIC: {} - MESSAGE: {}'.format(unauth_error,  topic, message_object))

        except Exception as err:
            raise Exception('Exception publishing to IoT Core on MQTT Topic. ERROR: {} - TOPIC: {} - MESSAGE: {}'.format(err, topic, message_object))
    
    class __MqttSubscribeHandler(client.SubscribeToIoTCoreStreamHandler):

        def __init__(self, message_callback):

            log.info('Initialising AWS Greengrass V2 IPC MQTT Subscribe Client')

            super().__init__()

            # Create ThreadPoolExecutor to process PubSub reveived messages.
            self.executor = ThreadPoolExecutor(max_workers=None) 

            self.message_callback = message_callback

        # Topic subscription event handlers 
        def on_stream_event(self, event: IoTCoreMessage) -> None:
            try:
                
                log.debug('MQTT EVENT RECEIVED: {}'.format(event))

                topic = event.message.topic_name    
                message = str(event.message.payload, "utf-8")
                self.executor.submit(self.message_callback, "mqtt", topic, message)

            except Exception as err:
                log.error('EXCEPTION: Exception Raised from IoT Core on MQTT Subscriber. ERROR MESSAGE: {} - STREAM EVENT: {}'.format(err, event))

        def on_stream_error(self, error: Exception) -> bool:
            log.error('ON_STREAM_ERROR: IoT Core MQTT PubSub Subscriber Stream Error. ERROR MESSAGE: {}'.format(error))
            return True  # Return True to close stream, False to keep stream open.

        def on_stream_closed(self) -> None:
            log.error('ON_STREAM_CLOSED: IoT Core MQTT PubSub Subscriber Closed.')
            pass
