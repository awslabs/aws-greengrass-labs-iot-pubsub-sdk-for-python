import sys
import json
import pytest
import logging

# Import the boilerplate example
sys.path.append('examples/00-greengrass-application-template/src/com.example.my_project.my_component/0.0.1/')

from main import AwsGreengrassV2Component
from pubsub.pubsub_messages import PubSubMessages
from pubsub.ipc_pubsub import IpcPubSub
from pubsub.mqtt_pubsub import MqttPubSub



def test_publish_message_types(mocker, monkeypatch, caplog):
    

    """ Test all Supported PubSub Publish Message Types """
    

    monkeypatch.setenv("AWS_IOT_THING_NAME", "TestDevice")
    ipc_connect = mocker.patch("awsiot.greengrasscoreipc.connect")

    # Read in the GG Component recipe config details
    f = open('examples/00-greengrass-application-template/recipes/com.example.my_project.my_component.json',)
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


    # Create UPDATE message
    update_command = 'update_command'
    status = 200
    data = {
        'test_data': 'test data'
    }
    update_messsage = ggv2_component.pubsub_messages.get_pubsub_update(update_command, status, data)
    assert update_messsage['command'] == update_command
    assert update_messsage['response']['status'] == status
    assert update_messsage['response']['data'] == data


    ### Test sending valid message types
    caplog.clear()

    # Test IPC REQUEST Message
    ggv2_component.publish_message('ipc',  ggv2_component.ipc_service_topic,  request_messsage)

    # Test IPC RESPONSE Message
    ggv2_component.publish_message('ipc',  ggv2_component.ipc_service_topic,  response_messsage)

    # Test MQTT REQUEST Message
    reply_topic = ggv2_component.mqtt_data_topic
    ggv2_component.publish_message('mqtt',  ggv2_component.mqtt_service_topic,  request_messsage)

    # Test MQTT RESPONSE Message
    ggv2_component.publish_message('mqtt',  ggv2_component.mqtt_service_topic,  response_messsage)

    # validate no ERRORs in sending well formatted messages
    for record in caplog.records:
        assert record.levelname != "ERROR"

    # Validate ERROR is logged sending Unknown API Type Message
    caplog.clear()
    ggv2_component.publish_message('unknown',  ggv2_component.mqtt_service_topic,  response_messsage)
    assert caplog.records[len(caplog.records)-1].levelname == "ERROR"
