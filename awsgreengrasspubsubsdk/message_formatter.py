# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0.

'''
 Defines standard message format for PubSub communications. 
 '''
 
__version__ = "0.1.4"
__status__ = "Development"
__copyright__ = "Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved."
__author__ = "Dean Colcott <https://www.linkedin.com/in/deancolcott/>"

from datetime import datetime

class PubSubMessageFormatter():
    '''
    Defines standard message format for PubSub communications between Greengrass 
    components and / or MQTT IoT Core in the AWS Greengrass V2 PubSub SDK.
    
    This enables versioned, efficient and consistent PubSub Message routing and 
    processing between components.
    '''
    
    sdk_version = __version__
    
    def get_message(self, **kwargs):
        '''
        Returns a well formatted PubSub Message as per this PubSub SDK versioned formatting.
        
        ### Parameters  

        **message_id** : str, (Optional) Default=Current Timestamp  
        
            Unique message ID to aid tracking across request / response message patterns. 
            If None or missing, a current timestamp is generated for this value in the format: %Y%m%d%H%M%S%f
            
        **status** : int (Optional) Default=200  
        
            Status code of this message. Any int supported, expected / typical values:  
            
            200: OK COMPLETE, 202: ASYNC REQUEST ACCEPTED, 404: COMMAND NOT RECOGNISED, 500: INTERNAL COMPONENT ERROR.
            
        **route** : str (Optional) Default='default_message_handler'  
        
            Name of the message handler fuction in PubSubMessageHandler() to process this message on the receiving component.
            If None or missing will be set to default_message_handler
            
        **message** : Object (preferred dict), (Optional) default={}  
        
            Dict, Array or any JSON serializable object containing the payload of this message.
            If None or missing, an empty dict is generated for this value.
                
        ### Usage:

        All input parameters are optional and provided as named keyword arguments.
        Defaults are applied for any values not provided or provided as None.
        
        e.g:  

        ```
        get_message(message={"param01" : "message param01"})
        get_message(message_id=123456, route="health_check_response",  message={"status" : "System OK"})
        ```
        
        ### Returns
       
       Example (Dict) returned message object:   
       
        ```
       {
            "sdk_version" : "0.1.4",
            "message_id" : 123456,
            "status" : 200,
            "route" : "health_check_response",
            "message": {
	            "status" : "System OK"
            }
        }
        ```
       
        '''

        # Set message_id or default value
        message_id = datetime.now().strftime("%Y%m%d%H%M%S%f")
        if('message_id' in kwargs and kwargs['message_id']):
            message_id = kwargs['message_id']

        # Set status or default value
        status = 200
        if('status' in kwargs and kwargs['status']):
            status = kwargs['status']

        # Set route or default value
        route = 'default_message_handler'
        if('route' in kwargs and kwargs['route']):
            route = kwargs['route'] 

        # Set message object or default value  
        message = {}
        if('message' in kwargs and kwargs['message']):
            message = kwargs['message'] 
 
        # Return a well formatted PubSub REQUEST
        retval =  {
            'sdk_version' : self.sdk_version,
            'message_id' : message_id,                  # Message Timestamp / ID to track the request flow.
            'status' : status,                          # Message status code.
            'route' : route,                            # Message handler function name that will process message on receiving system. 
            'message': message                          # Optional message payload / data object.
        }
        
        return retval

    def get_error_message(self, **kwargs):
        '''
        Convenience method that returns a well formatted PubSub Error Message 
        with status default to 500 and route to 'default_error_handler'
        
        A status value that isn't a 2xx value will route this message to the 
        default error PubSub topic and default error handler function on the receiving component 
        (Assuming it also implements the AWS Greengrass PubSub Component SDK).
        
        ### Parameters  

        **message_id** : str, (Optional) Default=Current Timestamp  
        
            Unique message ID to aid tracking across request / response message patterns. 
            If None or missing, a current timestamp is generated for this value in the format: %Y%m%d%H%M%S%f
            
        **message** : Object (preferred Dict), (Optional) default={}  
        
            Dict, Array or any JSON serializable object containing the payload of this message.
            If None or missing, an empty Dict is generated for this value.
                
        ### Usage   

        All input parameters are optional and provided as named keyword arguments.
        Defaults are applied for any values not provided or provided as None.
        
        e.g:  
        
        ```
        get_error_message(message={"error" : "PubSub Timeout for process 123XYZ"})
        get_error_message(message_id=123456,  message={"error" : "PubSub Timeout for process 123XYZ"})
        ```
        
       ### Returns
       
       Example (Dict) returned message object:  
       
        ```
       {
            "sdk_version" : "0.1.4",
            "message_id" : 123456,
            "status" : 500,
            "route" : "default_error_handler",
            "message": {
               "error" : "PubSub Timeout for process 123XYZ"
            }
        }
        ```
        
        '''
        
        # Set message_id or default value
        message_id = datetime.now().strftime("%Y%m%d%H%M%S%f")
        if('message_id' in kwargs and kwargs['message_id']):
            message_id = kwargs['message_id']
            
        # Set message object or default value  
        message = {}
        if('message' in kwargs and kwargs['message']):
            message = kwargs['message'] 
        
        return self.get_message(message_id=message_id, status=500, route='default_error_handler', message=message)
