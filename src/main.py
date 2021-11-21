'''
main.py:

Provided as the entry script for an AWS Greengrass V2 custom component. Reads in config
from the AWS Greengrass V2 component recipe as shown in https://github.com/awslabs/aws-greengrass-labs-iot-pubsub-framework

Provides clients for IPC / MQTT PubSub messaging prescribed Topic schemas for:
1) Service Topic: Messages to / from this service itself such as status request and ACKs of data messages.
2) Data Topic: Publishing data such as sensor data that other components can subscribe and listen for.
3) Broadcast Topic: A system wide broadcast typically to manage components or systems errors. 

For more detail on AWS Greengrass V2 see the Developer Guide at:
https://docs.aws.amazon.com/greengrass/v2/developerguide/what-is-iot-greengrass.html
'''

__author__ = "Dean Colcott <https://www.linkedin.com/in/deancolcott/>"
__copyright__ = "Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved."
__version__ = "0.0.1"
__status__ = "Development"

import sys
import json
import time
import random   # Note: only needed for processor temp example, can remove otherise. 
import logging
from pubsub.pubsub_messages import PubSubMessages
from pubsub.ipc_pubsub import IpcPubSub
from pubsub.mqtt_pubsub import MqttPubSub

# Config the logger.
log = logging.getLogger(__name__)
logging.basicConfig(format="[%(name)s.%(funcName)s():%(lineno)d] - [%(levelname)s] - %(message)s", 
                    stream=sys.stdout, 
                    level=logging.INFO)

class AwsGreengrassV2Component():

    def __init__(self, ggv2_component_config):
        '''
            Initialises the AWS Greengrass V2 custom component including the IPC and MQTT PubSub Client
            Greengrass Config expected to be passed from AWS Greengrass V2 deployment recipe.
        '''
        
        try:
            #######################################################
            # Log the start of the process
            log.info('Initialising AWS Greengrass V2 Component')

            super().__init__()

            #######################################################
            # Parse config passed to service from AWS Greengrass recipe
            log.info('Parsing AWS Greengrass V2 Config.')
            log.info('AWS Greengrass V2 Config: {}'.format(ggv2_component_config))

            # This variable is returned in response to a component health_check request.
            # Update it through the component logic with any valid object to describe 
            # the current component status.
            self.health_status = {
                "health-status-code" : 200,
                "health-status: ":  "healthy",
                "last_status_message" : "initilised component"
            }

            # Common variables for all components in this framework / architecture
            self.mqtt_pubsub_timeout = ggv2_component_config['mqtt_pubsub_timeout']
            self.ipc_pubsub_timeout = ggv2_component_config['ipc_pubsub_timeout']

            # MQTT Service, Data and Broadcast Topics
            self.mqtt_service_topic = ggv2_component_config['mqtt_service_topic']
            self.mqtt_data_topic = ggv2_component_config['mqtt_data_topic']
            self.mqtt_broadcast_topic = ggv2_component_config['mqtt_broadcast_topic']
            self.mqtt_subscribe_topics = ggv2_component_config['mqtt_subscribe_topics']

            # IPC Service, Data and Broadcast Topics
            self.ipc_service_topic = ggv2_component_config['ipc_service_topic']
            self.ipc_data_topic = ggv2_component_config['ipc_data_topic']
            self.ipc_broadcast_topic = ggv2_component_config['ipc_broadcast_topic']
            self.ipc_subscribe_topics = ggv2_component_config['ipc_subscribe_topics']

            # Completed processing recipe driven config for the Greengrass application.
            log.info('Parsing AWS Greengrass V2 Config Complete.')

            #######################################################
            # Init local Topic and MQTT IoT Core PubSub message service.

            log.info('Initialising IPC Topic PubSub message type / formats.')
            self.pubsub_messages = PubSubMessages()
            
            log.info('Initialising IPC Topic PubSub inter-service messaging.')
            self.ipc_pubsub = IpcPubSub(self.pubsub_message_callback, self.ipc_subscribe_topics, self.ipc_pubsub_timeout)

            log.info('Initialising IPC MQTT IoT Core PubSub messaging.')
            self.mqtt_pubsub = MqttPubSub(self.pubsub_message_callback, self.mqtt_subscribe_topics, self.mqtt_pubsub_timeout)

            log.info('Initialising AWS Greengrass V2 Component Complete.')

        except ValueError as val_error: # pragma: no cover 
            log.error('VAL_ERROR: JSON Parsing Error / Unexpected component recipe config message format. ERROR MESSAGE: {} - GG CONFIG: {}'.format(val_error, ggv2_component_config))

        except KeyError as key_error: # pragma: no cover 
            log.error('KEY_ERROR: Component recipe config missing required fields. ERROR MESSAGE: {} - GG CONFIG: {}'.format(key_error, ggv2_component_config))

        except Exception as err: # pragma: no cover 
            log.error('EXCEPTION: Exception raised initialising AwsGreengrassV2Component. ERROR MESSAGE: {} - GG CONFIG: {}'.format(err, ggv2_component_config))
    
    ##################################################
    ### PubSub Topic Message Callback
    ##################################################

    def pubsub_message_callback(self, topic, payload):
        '''
            Single Callback for all (IPC and MQTT) PubSub messages. 
            Provides initial message validation and passing to PubSub topic routers.
            
            Expects message payload provided is JSON that can be Serialized and 
            Deserialized to a programmatic language specific object.
        '''

        try:

            # Log incomming message
            log.info('Received PubSub Message. Topic: {} - Message: {}'.format(topic, payload))

            # Note: Expects all ingress messages to be in JSON format
            message = json.loads(payload)

            ########################################################
            #### Common Message Parameter Validation ####
            # Parse AWS Greengrass Component SDK (mandatory) fields for initial validation.
            message_id = message['message-id']
            reqres = message['reqres']
            command = message['command']

            ########################################################
            #### ReqRes Parameter Validation ####
            # Validate RESPONSE message status code (exists and value) before processing message further.
            if reqres == 'response' or reqres == 'update':
                status =  message['response']['status']
                if status < 200 or status > 299:
                    raise Exception('PubSub RESPONSE received with status: {}'.format(status))

            # Validate REQUEST message required parameters exist before message further.
            elif reqres == 'request':
                reply_topic = message['reply-topic']
                reply_sdk = message['reply-sdk']

            # Raise exception if not recognised ReqRes message type
            else:
                raise Exception('Message PubSub received with unknown ReqRes type: {}'.format(reqres))

            ########################################################
            #### Message Routing ####
            ## Route the AWS Greengrass Component SDK prescribed IPC / MQTT PubSub topics.

            # Route IPC service topic message.
            if topic == self.ipc_service_topic:
                self.ipc_service_topic_router(message_id, reqres, command, message)

            # Route MQTT service topic message
            elif topic == self.mqtt_service_topic:
                self.mqtt_service_topic_router(message_id, reqres, command, message)

            # Route IPC and MQTT broadcast topics to single router
            elif topic == self.ipc_broadcast_topic or topic == self.mqtt_broadcast_topic:
                self.application_broadcast_topic_router(message_id, reqres, command, message)

            ## Route custom topics that this component subscribes too.
            # As needed for specific component / application

            else:
                raise Exception('PubSub message received on unknown / unhandled topic.')

        except ValueError as val_error: # includes JSON parsing errors
            log.error('VAL_ERROR: JSON Parsing Error / Unexpected PubSub message format received. ERROR MESSAGE: {} - TOPIC: {} - PAYLOAD: {}'.format(val_error,  topic, payload))

        except KeyError as key_error: # pragma: no cover  # includes requests for fields that don't exist in the received object
            log.error('KEY_ERROR: Received PubSub message missing required fields. ERROR MESSAGE: {} - TOPIC: {} - PAYLOAD: {}'.format(key_error,  topic, payload))

        except Exception as err:
            log.error('EXCEPTION: Exception raised from PubSub message received. ERROR MESSAGE: {} - TOPIC: {} - PAYLOAD: {}'.format(err, topic, payload))
    
    ##################################################
    ### PubSub Topic Message Routers.
    ################################################## 

    # AWS Greengrass Application SDK prescribed topic routers.  
    def ipc_service_topic_router(self, message_id, reqres, command, message):
        '''
            Route IPC PubSub messages to this components IPC Service topic.
            
            Here you can route messages to this or an external module based on the 
            increasingly specific detail provided in the request/response 
            and command message fields as prescribed in this AWS Greengrass SDK
            (see pubsub_message.py).

            In this example we just route to a message processor based on request/response type. 
        '''

        if reqres == 'request':
            self.ipc_service_topic_request(message_id, command, message)

        elif reqres == 'response':
            self.ipc_service_topic_response(message_id, command, message)

    def mqtt_service_topic_router(self, message_id, reqres, command, message):
        '''
            Route MQTT IoT Core PubSub messages to this components MQTT IoT Core Service topic.
            
            Here you can route messages to this or an external module based on the 
            increasingly specific detail provided in the request/response 
            and command message fields as prescribed in this AWS Greengrass SDK
            (see pubsub_message.py).

            In this example we just route to a message processor based on request/response type. 
        '''

        if reqres == 'request':
            self.mqtt_service_topic_request(message_id, command, message)

        elif reqres == 'response':
            self.mqtt_service_topic_response(message_id, command, message)
    
    def application_broadcast_topic_router(self, message_id, reqres, command, message):
        '''
            Route PubSub messages to this components Application Broadcast topic.
            
            Here you can route messages to this or an external module based on the 
            increasingly specific detail provided in the request/response 
            and command message fields as prescribed in this AWS Greengrass SDK
            (see pubsub_message.py).

            In this example we just route to a message processor based on request/response type. 
        '''

        if reqres == 'request':
            self.application_broadcast_topic_request(message_id, command, message)

        elif reqres == 'response':
            self.application_broadcast_topic_response(message_id, command, message)

    # AWS Greengrass application custom topic subscription routers. 
    # As needed for specific component / application
    
    ##################################################
    ### PubSub Message Processors.
    ##################################################    

    # Exmple AWS Greengrass V2 Aplication SDK message processors
    def ipc_service_topic_request(self, message_id, command, message):
        '''
            Process PubSub REQUEST type messages to the IPC service topic.

            In this example we log the message and process if is a health_check request command.
        '''
        log.info('Received PubSub REQUEST on IPC Service topic. Message: {}'.format(message))

        if (command == "health_check"):
            self.health_request_processor(message_id, command, message)

    def ipc_service_topic_response(self, message_id, command, message):
        '''
            Process PubSub RESPOSNE type messages to the IPC service topic.

            In this example we just log the message.
        '''
        log.info('Received PubSub RESPONSE on IPC Service topic. Message: {}'.format(message))

    def mqtt_service_topic_request(self, message_id, command, message):
        '''
            Process PubSub REQUEST type messages to the MQTT service topic.

            In this example we log the message and process if is a health_check request command.
        '''
        log.info('Received PubSub REQUEST on MQTT Service topic. Message: {}'.format(message))

        if (command == "health_check"):
            self.health_request_processor(message_id, command, message)

    def mqtt_service_topic_response(self, message_id, command, message):
        '''
            Process PubSub RESPOSNE type messages to the IoT Core MQTT service topic.

            In this example we just log the message.
        '''
        log.info('Received PubSub RESPONSE on IoT Core MQTT Service topic. Message: {}'.format(message))

    def application_broadcast_topic_request(self, message_id, command, message):
        '''
            Process PubSub REQUEST type messages to the application broadcast topic.

            In this example we just log the message.
        '''
        log.info('Received PubSub REQUEST on the Application Broadcast topic. Message: {}'.format(message))

    def application_broadcast_topic_response(self, message_id, command, message):
        '''
            Process PubSub RESPONSE type messages to the application broadcast topic.

            In this example we just log the message.
        '''
        log.info('Received PubSub RESPONSE on the Application Broadcast topic. Message: {}'.format(message))

    # AWS Greengrass application custom topic message processors. 
    # As needed for specific component / application
    # Simple component health check example provided. 

    def health_request_processor(self, message_id, command, message):

        # Create the RESPONSE message format.
        status = 200                    # The response message status, not health status. 
        data = self.health_status       # Return any data needed in health_status object
        response_message = self.pubsub_messages.get_pubsub_response(message_id, command, status, data)

        # Get the requests reply SDK ('ipc' || 'mqtt' and reply topic from the request message) 
        # is possible that a request received on IPC is responsed to via MQTT.
        reply_sdk = message['reply-sdk']; 
        reply_topic = message['reply-topic']
        
        # Publish the message to requested SDK and topic
        self.publish_message(reply_sdk, reply_topic, response_message)

    ##################################################
    ### PubSub Message Publisher
    ##################################################

    def publish_message(self, sdk, topic, message):
        '''
            Single callback for all PubSub (IPC / MQTT) message publisher.
        '''

        try:
            
            # Log the publish 
            log.info('Publishing PubSub Message. Topic: {} - Message: {}'.format(topic, message))

            # Publish the message to the AWS Greengrass IPC or MQTT sdks
            if sdk == 'ipc':
                self.ipc_pubsub.publish_to_topic(topic, message)

            elif sdk == 'mqtt':
                self.mqtt_pubsub.publish_to_mqtt(topic, message)

            else:
                raise Exception('Publish for unknown publish_sdk: {} sent to topic: {}'.format(sdk, topic))
        
        except Exception as err:
            log.error('EXCEPTION: Error Publishing ERROR: {} - PUBLISH_SDK: {} - TOPIC: {} - MESSAGE: {}'.format(err, sdk, topic, message))

    ##################################################
    # Main service / process application logic
    ##################################################
    
    def service_loop(self): # pragma: no cover
        '''
        Put service specific application logic in the loop here. This also holds the 
        component process up so keep the loop with a small sleep delay even if the 
        component is event driven based on IPC / MQTT PubSub messaging.
        '''

        # If this component is completely event driven based on PubSub messages or other triggers 
        # just do a slow loop here  to hold the process up (or do so some other way).
        # Otherwise add application logic here as needed.
        #
        # In this example we call the publish_processor_temp method every 5 secs. 

        while True:
            try:

                self.publish_processor_temp()

                # Keep a slow loop delay to hold the component process up.
                time.sleep(5)

            except Exception as err:
                log.error('EXCEPTION: Exception occurred in service loop - ERROR MESSAGE: {}'.format(err))



    def publish_processor_temp(self):
        '''
        In this example we publish an unsolicited update message to this components 
        data topic to the MQTT API so can be viewed in the AWS IoT Core.

        The example is sending a random value between 40 and 50 to represent reading 
        and publishing edge devices processor temperature. 
        '''
        
        try:
            ### Create an example data update command and params fields
            command = 'processor_temp_update'
            status = 200
            params = {
                "units" : "Celsius",
                "value" : random.randint(40,50)
            }

            # Create the UPDATE message well-formatted object
            update_message = self.pubsub_messages.get_pubsub_update(command, status, params)
            
            # Publish the message to this components MQTT Data Topic
            # Once deployed, this message will be viewable in the AWS IoT Core
            self.publish_message('mqtt', self.mqtt_data_topic, update_message)

        except Exception as err:
                log.error('EXCEPTION: Exception in publish_processor_temp - ERROR MESSAGE: {}'.format(err))

if __name__ == "__main__": # pragma: no cover

    try:
        # Accepts the Greengrass V2 config from deployment recipe into sys.argv[1] as shown in:
        # https://github.com/awslabs/aws-greengrass-labs-iot-pubsub-framework
        ggv2_component_config = json.loads(sys.argv[1])
        ggv2_component = AwsGreengrassV2Component(ggv2_component_config)

        # The main process loop, add application logic in this function.
        ggv2_component.service_loop()

    except Exception as err:
        log.error('EXCEPTION: Exception occurred initialising component. ERROR MESSAGE: {}'.format(err))
