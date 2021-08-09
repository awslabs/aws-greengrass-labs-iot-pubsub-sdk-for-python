'''
pubsub_messages.py:

Defines standard request / response message formats for PubSub communications between Greengrass 
components and / or MQTT IoT Core in the AWS Greengrass V2 Component Framework.

This supports efficient route, filter and processing of PubSub messages within the application. 

'''

__author__ = "Dean Colcott <https://www.linkedin.com/in/deancolcott/>"
__copyright__ = "Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved."
__version__ = "0.0.1"
__status__ = "Development"

from datetime import datetime

class PubSubMessages():

    def get_pubsub_request(self, command, reply_topic, reply_sdk='ipc', params=None):
        '''
        
        Returns a well formatted PubSub REQUEST Message.
        
        Parameters
        ----------
        message-id: str
            Timestamp or other unique identifier for message tracking across request / response.
        reply-topic : str
            IPC / MQTT Topic that the receiving component will respond with as per the request type.
        reply-sdk : str, default='ipc' valid=['ipc','mqtt']
            The AWS Greengrass SDK that a response is routed to. 
            Valid options are:
                * 'ipc' : route the response via the IPC Component to Component PubSub SDK or 
                * 'mqtt' : route the response via the IoT Core PubSub SDK.
        command : str
            Name of the command, request or action to execute on the receiving component.
        params: any (preferred dict), default=None
                Dict, Array or any object able to be JSON serialised with specific parameters of the requested command to execute. 
        '''
        
        # Return a well formatted PubSub REQUEST
        return {
            'message-id' : datetime.now().strftime("%Y%m%d%H%M%S%f"), # Generated Timestamp / ID to track the request flow.
            'reply-sdk' : reply_sdk,                    # Reply SDK (MQTT Core or IPC topic between Greengrass components.)
            'reply-topic' : reply_topic,                # IPC / MQTT Topic the response should be published to.
            'reqres' : 'request',                       # Indicates is a REQUEST message type to aid application routing.
            'command' : command,                        # Command indicating the data or action that is being requested.
            'params' : params                           # Optional params specific to the request type (Use None instead of removing the field).
        }

    def get_pubsub_response(self, message_id, command, status, data=None):
        '''
        Retuens a well formatted PubSub RESPONSE Message. 

        Parameters
        ----------
        message-id: str
            Timestamp or other unique identifier for message tracking across request / response.
        command : str
            Name of the command, request or action to execute on the receiving component.
        response: dict
            status : int
                200 OK COMPLETE, 202 ASYNC REQUEST ACCEPTED, 404 COMMAND NOT RECOGNISED, 500 INTERNAL COMPONENT ERROR.
            data : any (preferred dict), default=None
                Dict, Array or any object able to be serialised containing data to be published with the response message. 
        '''
        
        # Return a well formatted PubSub RESPONSE
        return {
            'message-id': message_id,                   # Should be reflected from the request to track response.
            'reqres' : 'response',                      # Indicates is a RESPONSE message type to aid application routing.
            'command': command,                         # Command responding too for message routing and application logic.
            'response': {                               # Response Object. Expected to contain response data and mandatory status fields.
                'data': data,                           # Response Data field None or customisable to data request.
                'status': status                        # Response status code: 200, 202, 404, 500
            }
        }

    def get_pubsub_update(self, command, status, data=None):
        '''
        Returns a well formatted PubSub UPDATE Message.
        
        This message type is to identify unsolicited updates meaning it is not 
        in response to a specific REQUEST but instead to some external event or trigger.

        Parameters
        ----------
        command : str
            Name of the command, request or action to execute on the receiving component.
        response: dict
            status : int
                200 OK COMPLETE, 500 INTERNAL COMPONENT ERROR.
            data : any (preferred dict), default=None
                Dict, Array or any object able to be serialised containing data to be published with the response message. 
        '''
        
        # Return well formatted PubSub UPDATE
        return {
            'message-id': datetime.now().strftime("%Y%m%d%H%M%S%f"), # Generated Timestamp / ID to track the request flow.
            'reqres' : 'update',                        # Indicates is a unsolicited UPDATE message type to aid application routing.
            'command': command,                         # Command responding too for message routing and application logic.
            'response': {                               # Response Object. Expected to contain response data and mandatory status fields.
                'data': data,                           # Response Data field None or customisable to data request.
                'status': status                        # Response status code: 200, 202, 404, 500
            }
        }
