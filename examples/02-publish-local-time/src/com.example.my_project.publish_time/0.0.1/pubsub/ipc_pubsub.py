'''
ipc_pubsub.py:

Provides an AWS Greengrass V2 IPC PubSub client that manages subscriptions 
and a method to publish to AWS Greengrass IPC topics. This is intended
for use in an AWS Greengrass V2 Component to provide PubSub services. 

IPC Topic PubSub is for internal communications between AWS Greengrass Components 
within the AWS Greengrass Core (the edge device). For communications between 
Greengrass component and the AWS IoT Core platform see the MQTT PubSub class in this 
series. 

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
    PublishToTopicRequest,
    SubscribeToTopicRequest,
    SubscriptionResponseMessage,
    IoTCoreMessage,
    PublishMessage,
    BinaryMessage,
    UnauthorizedError,
    QOS
)

# Init the logger.
log = logging.getLogger(__name__)

class IpcPubSub():

    def __init__(self, message_callback, ipc_subscribe_topics, ipc_timeout=5):

        log.info('Initialising AWS Greengrass V2 IPC Topic PubSub Client')

        super().__init__()

        try:

            # PubSub timeout secs. 
            self.ipc_timeout = ipc_timeout
            
            # PubSub message callback.
            self.message_callback = message_callback

            # IPC Subscribe Topics
            self.ipc_subscribe_topics = ipc_subscribe_topics

            # Create the ipc_clients
            self.ipc_subscribe_client = awsiot.greengrasscoreipc.connect()
            self.ipc_publish_client = awsiot.greengrasscoreipc.connect()

            # Init IPC PubSub's
            self.init_topic_subscriber()
            self.init_topic_publisher()

        except InterruptedError as iErr:
            log.error('INTERRUPTED_EXCEPTION: IPC Topic Publisher / Subscriber init was interrupted. ERROR MESSAGE: {}'.format(iErr))

        except Exception as err:
            log.error('EXCEPTION: Exception occurred initialising AWS Greengrass IPC Topic PubSub. ERROR MESSAGE: {}'.format(err))

    ###############################################
    # IPC Topic PubSub Functions
    def init_topic_subscriber(self):
        '''
            Initialise subscription to requested IPC local topics.
        '''

        # Create ThreadPoolExecutor to process PubSub messages.
        # Changed in version 3.8: Default value of max_workers is changed to min(32, os.cpu_count() + 4)
        executor = ThreadPoolExecutor(max_workers=None)

        for subscribe_topic in self.ipc_subscribe_topics:

            try:
                log.info('IPC subscribing to topic: {}'.format(subscribe_topic))
                request = SubscribeToTopicRequest()
                request.topic = subscribe_topic
                handler = IpcPubSub.TopicSubscriber(self.message_callback, subscribe_topic, executor)
                operation = self.ipc_subscribe_client.new_subscribe_to_topic(handler)
                future = operation.activate(request)
                future.result(self.ipc_timeout)

            except concurrent.futures.TimeoutError as e:
                log.error('TIMEOUT_ERROR: Timeout occurred while subscribing to IPC topic. ERROR MESSAGE: {} -  TOPIC {}'.format(e, subscribe_topic))

            except UnauthorizedError as e:
                log.error('UNATHORIZED_ERROR: Unauthorized error while subscribing to IPC topic. ERROR MESSAGE: {} -  TOPIC {}'.format(e, subscribe_topic))

            except Exception as e:
                log.error('EXCEPTION: Exception while subscribing to IPC topic. ERROR MESSAGE: {} -  TOPIC {}'.format(e, subscribe_topic))

    def init_topic_publisher(self):
        '''
            Initialise publisher to requested IPC local topics.
        '''

        try:
            log.info('Initialising IPC Topic Publisher.')
            self.pub_request = PublishToTopicRequest()
            self.publish_message = PublishMessage()
            self.publish_message.binary_message = BinaryMessage()

        except Exception as err:
            log.error('EXCEPTION: Exception Initialising IPC Topic Publisher. ERROR MESSAGE: {}'.format(err))

    def publish_to_topic(self, topic, message):
        '''
            Publish a Python object sterilised as a JSON message to the requested local IPC topic.
        '''
        
        try:
            log.debug('IPC PUBLISH: topic: {} - Message: {}'.format(topic, message))
            self.pub_request.topic = topic
            json_message = json.dumps(message)
            self.publish_message.binary_message.message = bytes(json_message, "utf-8")
            self.pub_request.publish_message = self.publish_message
            operation = self.ipc_publish_client.new_publish_to_topic()
            operation.activate(self.pub_request)
            future = operation.get_response()
            future.result(self.ipc_timeout)

        except KeyError as key_error: # includes requests for fields that don't exixt in the received object
            log.error('KEY_ERROR: KeyError occurred while publishing to IPC topic. ERROR MESSAGE: {} - TOPIC: {} - MESSAGE: {}'.format(key_error,  topic, message))

        except concurrent.futures.TimeoutError as timeout_error:
            log.error('TIMEOUT_ERROR: Timeout occurred while publishing to IPC topic. ERROR MESSAGE: {} - TOPIC: {} - MESSAGE: {}'.format(timeout_error,  topic, message))

        except UnauthorizedError as unauth_error:
            log.error('UNAUTHORIZED_ERROR: Unauthorized error while publishing to IPC topic. ERROR MESSAGE: {} - TOPIC: {} - MESSAGE: {}'.format(unauth_error,  topic, message))

        except Exception as err:
            log.error('EXCEPTION: Exception while publishing to IPC topic. ERROR MESSAGE: {} - TOPIC: {} - MESSAGE: {}'.format(err,  topic, message))

    class TopicSubscriber(client.SubscribeToTopicStreamHandler):

        def __init__(self, message_callback, ipc_subscribe_topic, executor):

            log.info('Initialising AWS Greengrass V2 IPC Topic Subscriber: {}'.format(ipc_subscribe_topic))

            super().__init__()

            self.message_callback = message_callback

            #IPC Topic
            self.ipc_subscribe_topic = ipc_subscribe_topic

            # PubSub message process ThreadExecutor
            self.executor = executor

        # Topic subscription event handlers 
        def on_stream_event(self, event: SubscriptionResponseMessage) -> None:
            try:

                log.debug('IPC MESSAGE RECEIVED: {}'.format(event))

                message = str(event.binary_message.message, "utf-8")
                
                self.executor.submit(self.message_callback, self.ipc_subscribe_topic, message)

            except Exception as err:
                log.error('EXCEPTION: Exception Raised from IPC Topic Subscriber. ERROR MESSAGE: {} - STREAM EVENT: {}'.format(err, event))

        def on_stream_error(self, error: Exception) -> bool:
            log.error('ON_STREAM_ERROR: IPC PubSub Subscriber Stream Error. ERROR MESSAGE: {}'.format(error))
            return False  # Return True to close stream, False to keep stream open.

        def on_stream_closed(self) -> None:
            log.error('ON_STREAM_CLOSED: IPC PubSub Subscriber topic: {} Stream Closed.'.format(self.ipc_subscribe_topic))
