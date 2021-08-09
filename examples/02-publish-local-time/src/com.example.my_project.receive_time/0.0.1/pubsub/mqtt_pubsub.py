'''
mqtt_pubsub.py:

Provides an AWS Greengrass V2 IPC PubSub client that manages subscriptions 
and a method to publish to AWS Greengrass MQTT topics. This is intended
for use in an AWS Greengrass V2 Component to provide PubSub services. 

IPC MQTT core is for communications between AWS Greengrass Components and 
the AWS IoT Core. This can be used to send MQTT messaging to the AWS IoT core 
to save data, trigger alarms or alerts or to trigger other AWS services and applications.

For communications within the AWS Greengrass core between components
see the IPC Topic PubSub class in this framework. 

 For more detail on AWS Greengrass V2 see the Developer Guide at:
https://docs.aws.amazon.com/greengrass/v2/developerguide/what-is-iot-greengrass.html

'''

__author__ = "Dean Colcott <https://www.linkedin.com/in/deancolcott/>"
__copyright__ = "Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved."
__version__ = "0.0.1"
__status__ = "Development"

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

    def __init__(self, message_callback, mqtt_subscribe_topics, mqtt_timeout=5):

        log.info('Initialising AWS Greengrass V2 MQTT IoT Core PubSub Client')

        super().__init__()

        try:

            # PubSub timeout secs. 
            self.mqtt_timeout = mqtt_timeout
            
            # PubSub message callback.
            self.message_callback = message_callback

            # MQTT Subscribe Topics
            self.mqtt_subscribe_topics = mqtt_subscribe_topics

            # Create the mqtt_clients
            self.mqtt_subscribe_client = awsiot.greengrasscoreipc.connect()
            self.mqtt_publish_client = awsiot.greengrasscoreipc.connect()

            # Init MQTT PubSub's
            self.mqtt_qos = QOS.AT_LEAST_ONCE   ## TODO - Parameterise this into config
            self.init_mqtt_subscriber()
            self.init_mqtt_publisher()

        except InterruptedError as iErr:
            log.exception('INTERRUPTED_EXCEPTION: MQTT Iot Core Publisher / Subscriber init was interrupted. ERROR MESSAGE: {}'.format(iErr))

        except Exception as err:
            log.exception('EXCEPTION: Exception occurred initialising AWS Greengrass IPC MQTT Core PubSub. ERROR MESSAGE: {}'.format(err))

    ###############################################
    # IPC MQTT Iot Core PubSub Functions
    def init_mqtt_subscriber(self):
        '''
            Initialise subscription to requested MQTT IoT Core topics.
        '''
        
        handler = MqttPubSub.MqttSubscriber(self.message_callback)

        for subscribe_topic in self.mqtt_subscribe_topics:

            try:
                log.info('MQTT subscribing to topic: {}'.format(subscribe_topic))
                request = SubscribeToIoTCoreRequest()
                request.topic_name = subscribe_topic
                request.qos = self.mqtt_qos
                operation = self.mqtt_subscribe_client.new_subscribe_to_iot_core(handler)
                future = operation.activate(request)
                # call the result to ensure the future has completed before iterating
                future.result(self.mqtt_timeout)
                log.info('Complete MQTT subscribing to topic: {}'.format(subscribe_topic))

            except concurrent.futures.TimeoutError as e:
                log.exception('TIMEOUT_ERROR: Timeout occurred while subscribing to IPC MQTT topic. ERROR MESSAGE: {} - TOPIC {}'.format(e, subscribe_topic))

            except UnauthorizedError as e:
                log.exception('UNATHORIZED_ERROR: Unauthorized error while subscribing to IPC MQTT topic. ERROR MESSAGE: {} - TOPIC: {}'.format(e, subscribe_topic))

            except Exception as e:
                log.exception('EXCEPTION: Exception while subscribing to IPC MQTT topic. ERROR MESSAGE: {} - TOPIC: {}'.format(e, subscribe_topic))

    def init_mqtt_publisher(self):
        '''
            Initialise publisher to requested IoT Core MQTT topics.
        '''

        try:
            log.info('Initialising MQTT Publisher.')
            self.mqtt_request = PublishToIoTCoreRequest()
            self.mqtt_request.qos = self.mqtt_qos

        except Exception as err:
            log.exception('EXCEPTION: Exception Initialising MQTT Publisher. ERROR MESSAGE: {}'.format(err))

    def publish_to_mqtt(self, topic, message):
        '''
            Publish a Python object serialised as a JSON message to the IoT Core MQTT topic.
        '''
        
        try:

            log.debug('MQTT PUBLISH: topic: {} - Message: {}'.format(topic, message))
            self.mqtt_request.topic_name = topic
            json_message = json.dumps(message)
            self.mqtt_request.payload = bytes(json_message, "utf-8")
            operation = self.mqtt_publish_client.new_publish_to_iot_core()
            operation.activate(self.mqtt_request)
            future = operation.get_response()
            future.result(self.mqtt_timeout)

        except KeyError as key_error: # includes requests for fields that don't exixt in the received object
            log.exception('KEY_ERROR: KeyError occurred while publishing to IoT Core on MQTT Topic. ERROR MESSAGE: {} - TOPIC: {} - MESSAGE: {}'.format(key_error,  topic, message))

        except concurrent.futures.TimeoutError as timeout_error:
            log.exception('TIMEOUT_ERROR: Timeout occurred while publishing to IoT Core on MQTT Topic. ERROR MESSAGE: {} - TOPIC: {} - MESSAGE: {}'.format(timeout_error,  topic, message))

        except UnauthorizedError as unauth_error:
            log.exception('UNAUTHORIZED_ERROR: Unauthorized error while publishing to IoT Core on MQTT Topic. ERROR MESSAGE: {} - TOPIC: {} - MESSAGE: {}'.format(unauth_error,  topic, message))

        except Exception as err:
            log.exception('EXCEPTION: Exception while publishing to IoT Core on MQTT Topic. ERROR MESSAGE: {} - TOPIC: {} - MESSAGE: {}'.format(err,  topic, message))
    
    class MqttSubscriber(client.SubscribeToIoTCoreStreamHandler):

        def __init__(self, message_callback):

            log.info('Initialising AWS Greengrass V2 IPC MQTT PubSub Client')

            super().__init__()

            # Create ThreadPoolExecutor to process PubSub received messages.
            self.executor = ThreadPoolExecutor(max_workers=None) 

            self.message_callback = message_callback

        # Topic subscription event handlers 
        def on_stream_event(self, event: IoTCoreMessage) -> None:
            try:
                
                log.debug('MQTT MESSAGE RECEIVED: {}'.format(event))

                topic = event.message.topic_name    
                message = str(event.message.payload, "utf-8")
                
                self.executor.submit(self.message_callback, topic, message)

            except Exception as err:
                log.exception('EXCEPTION: Exception Raised from IoT Core on MQTT Subscriber. ERROR MESSAGE: {} - STREAM EVENT: {}'.format(err, event))

        def on_stream_error(self, error: Exception) -> bool:
            log.exception('ON_STREAM_ERROR: IoT Core MQTT PubSub Subscriber Stream Error. ERROR MESSAGE: {}'.format(error))
            return True  # Return True to close stream, False to keep stream open.

        def on_stream_closed(self) -> None:
            log.exception('ON_STREAM_CLOSED: IoT Core MQTT PubSub Subscriber topic: {} Stream Closed.'.format(self.mqtt_subscribe_topic))
            pass
