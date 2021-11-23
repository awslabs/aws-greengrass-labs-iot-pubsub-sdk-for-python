import sys
import json
import pytest
import logging

# Import the src directory
sys.path.append('src')

from src.main import AwsGreengrassV2Component

def test_subscribe_message_types(mocker, monkeypatch, caplog):

    """ Test all Supported PubSub Subscribe Message Types """

    monkeypatch.setenv("AWS_IOT_THING_NAME", "TestDevice")
    ipc_connect = mocker.patch("awsiot.greengrasscoreipc.connect")

    # Read in the GG Component recipe config details
    f = open('src/recipe.json',)
    data = json.load(f)
    ggv2_component_config = data["ComponentConfiguration"]["DefaultConfiguration"]["GGV2ComponentConfig"]

    # Create the GG Component Class
    ggv2_component = AwsGreengrassV2Component(ggv2_component_config)

    #Assert no ERROR logs seen during AwsGreengrassV2Component initilisation
    for record in caplog.records:
        assert record.levelname != "ERROR"


    ######################################################
    # Test IPC / MQTT Publish message types
    #
    # Create the REQUEST message
    request_command = 'request_command'
    reply_topic = ggv2_component.ipc_data_topic
    reply_sdk = 'ipc'
    params = {
        'test_param': 'test parameter'
    }
    request_messsage = ggv2_component.pubsub_messages.get_pubsub_request(request_command, reply_topic, reply_sdk, params)
    assert request_messsage['command'] == request_command
    assert request_messsage['reply-topic'] == reply_topic
    assert request_messsage['reply-sdk'] == reply_sdk
    assert request_messsage['params'] == params

    json_request_messsage = json.dumps(request_messsage)

    # Create the RESPONSE message
    message_id = "123456789"
    response_command = 'response_command'
    status = 200
    data = {
        'test_data': 'test data'
    }
    response_messsage = ggv2_component.pubsub_messages.get_pubsub_response(message_id, response_command, status, data)
    assert response_messsage['message-id'] == message_id
    assert response_messsage['command'] == response_command
    assert response_messsage['response']['status'] == status
    assert response_messsage['response']['data'] == data

    json_response_messsage = json.dumps(response_messsage)

    # Create UPDATE message
    update_command = 'update_command'
    status = 200
    data = {
        'test_data': 'test data'
    }



     ### Test receiving valid message types
    caplog.clear()

    ### IPC TESTS #####
    # Test ipc_service_topic REQUEST Message Received
    ggv2_component.pubsub_message_callback( ggv2_component.ipc_service_topic,  json_request_messsage)

    # Test ipc_service_topic RESPONSE Message Received
    ggv2_component.pubsub_message_callback( ggv2_component.ipc_service_topic,  json_response_messsage)

    # Test ipc_broadcast_topic REQUEST Message Received
    ggv2_component.pubsub_message_callback( ggv2_component.ipc_broadcast_topic,  json_request_messsage)

    # Test ipc_broadcast_topic RESPONSE Message Received
    ggv2_component.pubsub_message_callback( ggv2_component.ipc_broadcast_topic,  json_response_messsage)

    ### MQTT TESTS #####
    # Test mqtt_service_topic REQUEST Message Received
    ggv2_component.pubsub_message_callback( ggv2_component.mqtt_service_topic,  json_request_messsage)

    # Test mqtt_service_topic RESPONSE Message Received
    ggv2_component.pubsub_message_callback( ggv2_component.mqtt_service_topic,  json_response_messsage)

    # Test mqtt_broadcast_topic REQUEST Message Received
    ggv2_component.pubsub_message_callback( ggv2_component_config['mqtt_broadcast_topic'],  json_request_messsage)

    # Test mqtt_broadcast_topic RESPONSE Message Received
    ggv2_component.pubsub_message_callback( ggv2_component_config['mqtt_broadcast_topic'],  json_response_messsage)

    #Assert no ERROR logs seen during AwsGreengrassV2Component initilisation
    for record in caplog.records:
        assert record.levelname != "ERROR"

    ## Force Exception by sending invalid JSON string in message payload
    caplog.clear()
    ggv2_component.pubsub_message_callback( ggv2_component_config['ipc_service_topic'],  "Im not a valid JSON string")
    assert caplog.records[len(caplog.records)-1].levelname == "ERROR"

    ## Force Exception by claiomimg message is from unknown topic
    caplog.clear()
    ggv2_component.pubsub_message_callback( 'unknown-pubsub-topic',  json_response_messsage)
    assert caplog.records[len(caplog.records)-1].levelname == "ERROR"

    ## Force Exception by setting Status to error value
    caplog.clear()
    response_messsage['response']['status'] = 500
    json_response_messsage = json.dumps(response_messsage)
    ggv2_component.pubsub_message_callback( ggv2_component_config['ipc_service_topic'],  json_response_messsage)
    assert caplog.records[len(caplog.records)-1].levelname == "ERROR"
    response_messsage['response']['status'] = 200


    ## Force Exception by sending unknown ReqRes value
    caplog.clear()
    request_messsage['reqres'] = 'UnknownReqResType'
    json_request_messsage = json.dumps(request_messsage)
    ggv2_component.pubsub_message_callback( ggv2_component_config['ipc_service_topic'],  json_request_messsage)
    assert caplog.records[len(caplog.records)-1].levelname == "ERROR"
