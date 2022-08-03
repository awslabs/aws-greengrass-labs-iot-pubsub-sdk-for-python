# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0.
 
'''
Abstracts the AWS Greengrass V2 IPC PubSub SDK that manages subscriptions 
and a method to publish to AWS Greengrass IPC topics. This is intended
for use in an AWS Greengrass V2 Component SDD to provide PubSub services. 

IPC Topic PubSub is for internal communications between AWS Greengrass Components 
within the AWS Greengrass Core (the edge device). For communications between 
Greengrass component and the AWS IoT Core platform see the MQTT PubSub class. 

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
    PublishToTopicRequest,
    SubscribeToTopicRequest,
    SubscriptionResponseMessage,
    PublishMessage,
    BinaryMessage,
    UnauthorizedError
)

# Init the logger.
log = logging.getLogger(__name__)

class IpcPubSub():

    def __init__(self, message_callback, ipc_subscribe_topics):

            
        super().__init__()
        
        log.info('Initialising / Activating AWS Greengrass V2 IPC PubSub Client....')

        # PubSub timeout default secs. 
        self.ipc_default_timeout = 10

        # PubSub message callback.
        self.message_callback = message_callback

        # IPC Subscribe Topics.
        self.ipc_subscribe_topics = ipc_subscribe_topics

        # List of active topics subscribed too.
        self.ipc_subscribed_topics = []

        # Create the ipc_clients.
        self.ipc_subscribe_client = awsiot.greengrasscoreipc.connect()
        self.ipc_publish_client = awsiot.greengrasscoreipc.connect()

        # Create ThreadPoolExecutor to process PubSub messages.
        # Changed in version 3.8: Default max_workers changed to min(32, os.cpu_count() + 4).
        self.executor = ThreadPoolExecutor(max_workers=None)

        # Init IPC PubSub's.
        self._init_topic_subscriber()
        self._init_topic_publisher()
        
        log.info('Initialising / Activating AWS Greengrass V2 IPC PubSub Client Complete')

    ###############################################
    # Setters
    def set_ipc_default_timeout(self, ipc_default_timeout):
        self.ipc_default_timeout = ipc_default_timeout

    ###############################################
    # IPC Topic PubSub Functions
    def _init_topic_subscriber(self):
        '''
            Initialise subscription to requested IPC local topics.
        '''

        for subscribe_topic in self.ipc_subscribe_topics:
            self.subscribe_to_topic(subscribe_topic)

    def subscribe_to_topic(self, topic):

        log.info('IPC SDK Subscribing to Topic: {}:'.format(topic))
        
        if (topic in self.ipc_subscribed_topics):
            log.info('Returning with no action. Already subscribed to IPC topic: {}'.format(topic))
            return
        
        request = SubscribeToTopicRequest()
        request.topic = topic
        handler = IpcPubSub._IpcSubscribeHandler(self.message_callback, topic, self.executor)
        operation = self.ipc_subscribe_client.new_subscribe_to_topic(handler)
        future = operation.activate(request)
        # call the result to ensure the future has completed.
        future.result(self.ipc_default_timeout)

        self.ipc_subscribed_topics.append(topic)
        log.info('IPC SDK Subscribing to Topic: {} Complete'.format(topic))

    def _init_topic_publisher(self):
        '''
            Initialise publisher to requested IPC local topics.
        '''

        log.info('Initialising IPC Topic Publisher.')
        self.pub_request = PublishToTopicRequest()
        self.publish_message = PublishMessage()
        self.publish_message.binary_message = BinaryMessage()

    def publish_to_topic(self, topic, message_object, timeout=None):
        '''
            Publish a Python object sterilised as a JSON message to the requested local IPC topic.
        '''
        
        try:
            log.debug('IPC Publish - Topic: {} - Message: {}'.format(topic, message_object))
            
            self.pub_request.topic = topic
            json_message = json.dumps(message_object)
            self.publish_message.binary_message.message = bytes(json_message, "utf-8")
            self.pub_request.publish_message = self.publish_message
            operation = self.ipc_publish_client.new_publish_to_topic()
            operation.activate(self.pub_request)
            future = operation.get_response()
            future.result(timeout if timeout else self.ipc_default_timeout)

        except KeyError as key_error:
            raise Exception('KeyError occurred publishing to IPC topic. ERROR: {} - TOPIC {} - MESSAGE: {}'.format(key_error, topic, message_object))

        except concurrent.futures.TimeoutError as timeout_error:
            raise Exception('Timeout occurred publishing to IPC topic. ERROR: {} - TOPIC {} - MESSAGE: {}'.format(timeout_error, topic, message_object))

        except UnauthorizedError as unauth_error:
            raise Exception('Unauthorized error publishing to IPC topic. ERROR {} - TOPIC {} - MESSAGE: {}'.format(unauth_error, topic, message_object))

        except Exception as err:
            raise Exception('Exception publishing to IPC topic. ERROR: {} - TOPIC {} - MESSAGE: {}'.format(err,  topic, message_object))

    class _IpcSubscribeHandler(client.SubscribeToTopicStreamHandler):

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

                log.debug('IPC EVENT RECEIVED: {}'.format(event))

                message = str(event.binary_message.message, "utf-8")
                
                self.executor.submit(self.message_callback, "ipc", self.ipc_subscribe_topic, message)

            except Exception as err:
                log.error('EXCEPTION: Exception Raised from IPC Topic Subscriber. ERROR: {} - STREAM EVENT: {}'.format(err, event))

        def on_stream_error(self, error: Exception) -> bool:
            log.error('ON_STREAM_ERROR: IPC PubSub Subscriber Stream Error. ERROR: {}'.format(error))
            return False  # Return True to close stream, False to keep stream open.

        def on_stream_closed(self) -> None:
            log.error('ON_STREAM_CLOSED: IPC PubSub Subscriber topic: {} Stream Closed.'.format(self.ipc_subscribe_topic))
