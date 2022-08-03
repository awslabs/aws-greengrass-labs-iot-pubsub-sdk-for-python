# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0.

'''
Provided as the entry point for the AWS Greengrass V2 PubSub Component SDK. 
'''

__version__ = "0.1.4"
__status__ = "Development"
__copyright__ = "Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved."
__author__ = "Dean Colcott <https://www.linkedin.com/in/deancolcott/>"

import os, sys, json, inspect, logging

from awsgreengrasspubsubsdk.pubsub_ipc import IpcPubSub
from awsgreengrasspubsubsdk.pubsub_mqtt import MqttPubSub
from awsgreengrasspubsubsdk.message_formatter import PubSubMessageFormatter

# Init / Config the logger.
log = logging.getLogger(__name__)
logging.basicConfig(format="[%(name)s.%(funcName)s():%(lineno)d] - [%(levelname)s] - %(message)s", 
                    stream=sys.stdout, 
                    level=logging.INFO)

class AwsGreengrassPubSubSdkClient():
    '''
    This client abstracts the AWS Greengrass IPC and MQTT PubSub functionality, 
    defines a simple PubSub topic schema and routes PubSub messages directly to 
    the given instance of PubSubMessageHandler() in the user’s application logic.
    
    PubSub subscriptions are only initialised and messages processed once the
    activate_ipc_pubsub() and / or activate_mqtt_pubsub() functions are called
    to activate the IPC and MQTT PubSub message channels respectively. 
    
    This defines the base PubSub topic schema with topics for ingress and egress messages. 
        
        The PubSub topic schema is defined as:
        
        * Ingress Topic - (base_topic/THING_NAME/ingress): Subscribes to this topic for incoming messages.  
        
        * Egress Topic - (base_topic/THING_NAME/egress): Default message publish topic.  
        
    ### Parameters
        
        **base_topic**: str   
        
            Based string for the ingress / egress and error topics for this component.
            
        **message_handler**: Class (Instance of: PubSubMessageHandler() )    
        
            An instance of the message_handler.PubSubMessageHandler() class in the AWS Greengrass component code. 
            All messages received on any active PubSub protocols will be forwarded to this class.
            
            
    ### Usage / Constructor
        
       base_topic = 'my_project_name"  
       
       my_message_handler = MyPubSubMessageHandler()  
       
       pubsub_client = AwsGreengrassPubSubSdkClient(base_topic, my_message_handler)
        
    '''

    def __init__(self, base_topic, default_message_handler):
        '''
        Initialises the AWS Greengrass V2 PubSub SDK. 
    
        **Note:** Initialising this client doesn't immediately trigger IPC or MQTT message processing. 
        User must call activate_ipc_pubsub() and / or activate_mqtt_pubsub() 
        to activate the respective PubSub protocols to begin processing messages.
        
        '''
        
        super().__init__()
        
         #######################################################
        # Set Thing Name and Log the start of the process
        self.base_topic = base_topic
        self.formatter = PubSubMessageFormatter()
        self.thing_name = os.getenv('AWS_IOT_THING_NAME')
        log.info('Initialising AWS Greengrass PubSub SDK on Thing: {} with Base Topic: {}.....'.format(self.thing_name, self.base_topic))
        
         # Set the default message handler to catch messages with no matching route.
        log.info('Setting default_message_handler function callback')
        self.default_message_handler = default_message_handler

        # Create objet to hold user defined message handlers.
        # Expected these are Classes with functions that can route messages to by function name.
        self.message_handlers = {}
        # There are the required paramaters for a method in a registered message_handler class to 
        # be considered as a valid message route by this SDK.
        self.handler_required_params = ['protocol', 'topic', 'message_id', 'status', 'route', 'message']

        # Set the initial IPC / MQTT activated modes
        self.is_ipc_active = False
        self.is_mqtt_active = False

        #######################################################
        # Parse SDK config and / or set local topics / parameters to default.
        log.info('Setting SDK Default PubSub Topics...')
        
        # Set Ingress PubSub topic
        self.ingress_topic = '{}/{}/ingress'.format(self.base_topic, self.thing_name)
        log.info('Ingress Topic: {}'.format(self.ingress_topic ))
        
        # Set Egress PubSub topic
        self.egress_topic = '{}/{}/egress'.format(self.base_topic, self.thing_name)
        log.info('Egress topic: {}'.format(self.egress_topic ))

        # Set the subscribe topics for the SDK
        self.ipc_subscribe_topics = [self.ingress_topic ]
        self.mqtt_subscribe_topics = [self.ingress_topic ]
        
        log.info('Setting SDK Default PubSub Topics Complete.')

        log.info('Initialising PubSub message formats....')
        
        # Build and log test message types for user examples and to validate messages has initialised. 
        test_request = self.formatter.get_message(message_id=123456, status_code=200, route='default_message_handler', message={"param01" : "message param01"})
        log.info('Built test Request Message: {}'.format(test_request))

        log.info('Initialising PubSub Message Formats Complete.')
        
        # Completed initialising Greengrass PubSub SDK.
        log.info('Initialising AWS Greengrass V2 PubSub SDK Complete.')

    ##################################################
    ### Register message_handler classes to route messages
    ##################################################

    def register_message_handler(self, message_handler_class):
        '''
        Registers a message handler class to route messages too.
        A message_handler is any user defined class that contains named functions 
        that this SDK will route messages to based on the route value in the message.
        '''

        # Scan the message_handler class for non private functions that are assumed to
        # be valid message handling functions for this SDK based on the route field.

        # Get all callable methods in the provided class
        class_name = type(message_handler_class).__name__
        all_handler_methods = [func for func in dir(message_handler_class) if callable(getattr(message_handler_class, func))]
        
        # For each method, ,check if is non private and has the SDK specified required input paramaters
        # of protocol, topic, message_id, status, route, and message then add all valid to stored message_handlers
        log.info('Registering Message Handler Class: {}'.format(class_name))
        for method_name in all_handler_methods:
            # Exclude private functions if any.
            if not method_name.startswith('_'):
                # Check that this method has the required paramaters to be considered as a value message route.
                method = getattr(message_handler_class, method_name)
                method_params = inspect.signature(method).parameters
                is_valid_method=True

                # Check method has required parameters to be a valid SDK message handler.
                for param in self.handler_required_params:
                    if not param in method_params:
                        is_valid_method=False
                        break

                if is_valid_method:
                    handler_route = '{}.{}'.format(class_name, method_name)
                    self.message_handlers[handler_route] = method
                    log.info('Adding Message Handler Function: {}'.format(method_name))

        log.info('Registering Message Handler Class: {} - Complete'.format(class_name))

    ##################################################
    ### Activate calls for PubSub (IPC / MQTT) Clients
    ##################################################
    
    def activate_ipc_pubsub(self):
        '''
        Activate and initialise the IPC PubSub subscribers and publisher.
        Will start receiving and processing messages in IPC subscribed topics
        immediately on calling this function.
        '''
        
        log.info('Initialising IPC Topic PubSub inter-service messaging.')
        self.ipc_pubsub = IpcPubSub(self._received_message_callback, self.ipc_subscribe_topics)
        
        # Publish a 200 OK message to indicate IPC is activated
        succ_msg = self.formatter.get_message(message={"event" : "IPC Client Activated"})
        self.publish_message('ipc', succ_msg)
        
        # Is IpcPubSub initilises successfully then set the is_ipc_active=True
        self.is_ipc_active = True
    
    def activate_mqtt_pubsub(self):
        '''
        Activate and initialise the MQTT PubSub subscribers and publisher.
        Will start receiving and processing messages in MQTT subscribed topics
        immediately on calling this function.
        '''
        
        log.info('Initialising IPC MQTT IoT Core PubSub messaging.')
        self.mqtt_pubsub = MqttPubSub(self._received_message_callback, self.mqtt_subscribe_topics)
        
        # Publish a 200 OK message to indicate IPC is activated
        succ_msg = self.formatter.get_message(message={"event" : "MQTT Client Activated"})
        self.publish_message('mqtt', succ_msg)
        
        # Is IpcPubSub initilises successfully then set the is_mqtt_active=True
        self.is_mqtt_active = True
    
    ##################################################
    ### PubSub Received Message Callback
    ##################################################

    def _received_message_callback(self, protocol, topic, payload):
        '''
        Callback for all (IPC and MQTT) PubSub Client received messages.
        Provides initial message validation and passing to PubSub topic routers.
        Expects message payload provided is JSON formatted. 
        '''

        try:

            # Debug Log incoming message
            log.debug('Received PubSub Message. Protocol: {} - Topic: {} - Message: {}'.format(protocol, topic, payload))
            
            ########################################################
            #### Message Parsing and SDK Message format parameter validation
            
            # Parse the message to JSON. If not JSON or not valid message format 
            # for this SDK then route to the custom message processor.
            message = self._parse_json_message(payload)
            
            if self._is_sdk_formatted_message(message):
                self._sdk_formatted_message_router(protocol, topic, message)
            else:
                raise Exception('Message received not meeting AWS Greengrass PubSub SDK required format.')

        except Exception as err:
            err_msg = 'Exception raised from _received_message_callback. ERROR MESSAGE: {} - TOPIC: {} - PAYLOAD: {}'.format(err, topic, payload)
            self.publish_error('ipc_mqtt', err_msg)
    
    ##################################################
    ### Message Parse / Validate / Version helpers
    ################################################## 
    
    def _parse_json_message(self, payload):
        '''
            Try to Parse a message as JSON. If parses; return the object, if not return False. 
        '''
        try:
            return json.loads(payload)
            
        except ValueError as e:
            return False

    def _is_sdk_formatted_message(self, message):
        '''
        Tests if a given message is well-formatted as per this SDK message formats
        '''

        sdk_message_values = [ 'sdk_version', 'message_id', 'status', 'route', 'message']
        for sdk_message_value in sdk_message_values:
            if not sdk_message_value in message.keys():
                return False
        
        # If all required message parameters present then return True.
        return True
        
    def _is_same_major_version(self, source_version, target_version):
        '''
            Simple (but easily fooled) method to check two semantic versions
            numbers are of the same major version to detect breaking changes.
            
            TODO: Doesn't validate the version format so check first.
        '''
        source = source_version.split('.')
        target = target_version.split('.')
        return source[0] == target[0]
        
    def _get_sdk_message_values(self, message):
        '''
        Return the given (expected SDK well-formatted) message as a tuple.
        '''
        return (message['sdk_version'], message['message_id'], message['status'], message['route'], message['message'])
            
    ##################################################
    ### Message Routers.
    ##################################################    
    
    # Routes messaged based on SDK prescribed well formatted fields of 
    # route and status.
    def _sdk_formatted_message_router(self, protocol, topic, message):
        '''
            Process PubSub messages that are formatted using this SDK.
        '''

        try:
            log.debug('_sdk_formatted_message_router: Received SDK Formatted PubSub message on topic: {} -  Message: {}'.format(topic, message))
            
            # Decompose the (expected) message parameter values
            message_sdk_version, message_id, status, route, message_payload = self._get_sdk_message_values(message)
            
            # Validate the receiving message was from a supported SDK version.
            sdk_version = self.formatter.sdk_version
            if not self._is_same_major_version(message_sdk_version, sdk_version):
                raise Exception('Received PubSub SDK Message Version: {} but needing major version installed: {}'.format(message_sdk_version, sdk_version))
                    
            # Get a hook to the preferred message_handler or default_message_handler if no route match            
            selected_handler = self.default_message_handler
            if route in self.message_handlers.keys():
                selected_handler = self.message_handlers[route]

            # Route the message to best matching message handler found.
            selected_handler(protocol, topic, message_id, status, route, message_payload)
        
        except Exception as err:
            err_msg = 'Exception raised from _sdk_formatted_message_router. ERROR MESSAGE: {} - PROTOCOL: {} - TOPIC: {} - PAYLOAD: {}'.format(err, protocol, topic, message)
            self.publish_error('ipc_mqtt', err_msg)


    ##################################################
    ### Publish Message / Publish Errors Functions. 
    ##################################################

    def publish_message(self, protocol, message, topic=None):
        '''
        Publishes a JSON message to the respective AWS Greengrass Protocol (IPC or MQTT) Clients.
        
        ### Parameters  

        **protocol**: str   
        
            The protocol client (IPC or MQTT) to publish the message too.
            
            Supported values:   
            
            * ipc: Publish to IPC message bus.
            
            * mqtt: Publish to MQTT message bus.
            
            * ipc_mqtt: Publish to both IPC and MQTT message buses respectively.

        **message**: Object (preferred dict)   
        
            Dict, Array or any object able to be JSON serialised containing data to be published with the response message. 
            Typically expected to be a JSON object created by the AWS Greengrass SDK messageformatter.
            
        **topic**: str (Optional) Default: Component Egress Topic (i.e: base-pubsub-topic/THING_NAME/egress )
            
            The topic to publish this message to on the selected protocol client
            
        '''
        
        # If topic not set, default it to the components egress topic. 
        if topic == None:
            topic = self.egress_topic
        
        # Debug the PubSub publish 
        log.debug('Publishing Message. Topic: {} - Message: {}'.format(topic, message))

        # Publish the message to the AWS Greengrass IPC or MQTT SDKs
        if protocol == 'ipc':
            self.ipc_pubsub.publish_to_topic(topic, message)

        elif protocol == 'mqtt':
            self.mqtt_pubsub.publish_to_mqtt(topic, message)
            
        elif protocol == 'ipc_mqtt':
            self.ipc_pubsub.publish_to_topic(topic, message)
            self.mqtt_pubsub.publish_to_mqtt(topic, message)

        else:
            raise Exception('Publish requested for unknown protocol {}. Supported Values: [ipc || mqtt || ipc_mqtt]',format(protocol))

    def publish_error(self, protocol, err_message):
        '''
        A convenience method that logs and publishes an Error message to IPC and / or MQTT
        This will build a well formatted message with status = 500 and route = 'default_error_handler'

        ### Parameters  

        **protocol**: str   
        
            The protocol client (IPC or MQTT) to publish the message too.
            
            Supported values:   
            
            * ipc: Publish to IPC message bus.
            
            * mqtt: Publish to MQTT message bus.
            
            * ipc_mqtt: Publish to both IPC and MQTT message buses respectively.

        **err_message**: Object (preferred dict)  
        
            Dict, Array or any object able to be JSON serialised containing data to be published with the response message. 
            Is added as message payload in a well-formatted SDK message with status=500 and route='default_error_handler'
        '''
        try:
            log.error(err_message)
            
            # Create a well formed error message and publish to PubSub.
            message = self.formatter.get_error_message(message=err_message)
            self.publish_message(protocol, message)

        except Exception as err:
            # Don't get too clever handling this error as may end up in a recursive loop of error publishing.
            # Catch all exceptions and just log locally.
             log.error('Exception raised publishing error message. ERROR: {} - MESSAGE PAYLOAD: {}'.format(err, err_message))

    ##################################################
    ### Custom topic subscriber
    ##################################################

    def subscribe_to_topic(self, protocol, topic):
        '''
        Subscribes to custom PubSub topics on IPC and / or MQTT clients. 
        If the given protocol client has been activated, then the subscription will take immediate effect
        and the registered message_handler will begin receiving messages from this topic.
        
        If the protocol has not been activated, the subscription request will 
        be stored and will take effect once the protocol is activated. 
        
        ### Parameters
        
        **protocol**: str   
        
            The protocol client (IPC or MQTT) to Subscribe too.
            
            Supported values:   
            
            * ipc: Subscribe to IPC message bus.
            
            * mqtt: Subscribe to MQTT message bus.
            
            * ipc_mqtt: Subscribe to both IPC and MQTT message buses respectively.

        **topic**: str
            The topic to subscribe too.
            
        '''
        
        # Debug the PubSub publish 
        log.debug('Received Subscription request for Topic: {}'.format(topic))

        # Subscribe to requested topic on IPC / MQTT protocols.
        if protocol =='ipc':
            self._subscribe_to_ipc_topic(topic)
        
        elif protocol =='mqtt':
            self._subscribe_to_mqtt_topic(topic)
            
        elif protocol =='ipc_mqtt':
            self._subscribe_to_ipc_topic(topic)
            self._subscribe_to_mqtt_topic(topic)

        else:
            raise Exception('Requested subscribe to topic: {} for unknown protocol {}. Supported Values: [ipc || mqtt || ipc_mqtt]',format(topic, protocol))

    def _subscribe_to_ipc_topic(self, topic):
        '''
        Private helper to subscribe to an IPC client topic. 
        '''
        
        if not topic in self.ipc_subscribe_topics:
            self.ipc_subscribe_topics.append(topic)
            
        if self.is_ipc_active:
             self.ipc_pubsub.subscribe_to_topic(topic)
             
    def _subscribe_to_mqtt_topic(self, topic):
        '''
        Private helper to subscribe to an MQTT client topic. 
        '''
        
        if not topic in self.mqtt_subscribe_topics:
            self.mqtt_subscribe_topics.append(topic)
            
        if self.is_mqtt_active:
             self.mqtt_pubsub.subscribe_to_topic(topic)
