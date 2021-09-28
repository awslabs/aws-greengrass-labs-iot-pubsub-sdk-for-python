import sys
import json
import pytest

# Import the boilerplate example
sys.path.append('examples/00-greengrass-application-template/src/com.example.my_project.my_component/0.0.1/')

from main import AwsGreengrassV2Component
from pubsub.pubsub_messages import PubSubMessages
from pubsub.ipc_pubsub import IpcPubSub
from pubsub.mqtt_pubsub import MqttPubSub

def test_publish_message_types(mocker, monkeypatch):
    """ Test all PubSub Message Types """

    monkeypatch.setenv("AWS_IOT_THING_NAME", "TestDevice")
    ipc_connect = mocker.patch("awsiot.greengrasscoreipc.connect")

    # Read in the GG Component recipe config details
    f = open('examples/00-greengrass-application-template/recipes/com.example.my_project.my_component.json',)
    data = json.load(f)
    ggv2_component_config = data["ComponentConfiguration"]["DefaultConfiguration"]["GGV2ComponentConfig"]

    # Create the GG Component Class
    ggv2_component = AwsGreengrassV2Component(ggv2_component_config)

    # Configure Mocker functions
    mock_publish_message = mocker.patch("main.AwsGreengrassV2Component.publish_message")
    mock_ipc_publish_init = mocker.patch("pubsub.ipc_pubsub.IpcPubSub.init_topic_publisher")
    mock_publish_to_topic = mocker.patch("pubsub.ipc_pubsub.IpcPubSub.publish_to_topic")
    mock_mqtt_publish_init = mocker.patch("pubsub.mqtt_pubsub.MqttPubSub.init_mqtt_publisher")
    mock_publish_to_mqtt = mocker.patch("pubsub.mqtt_pubsub.MqttPubSub.publish_to_mqtt")
    
    ######################################################
    # Test Init Publisher
    ggv2_component.ipc_pubsub.init_topic_publisher()
    mock_ipc_publish_init.assert_called_once()

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

    # Create the RESPONSE message
    message_id = "123456789"
    response_command = 'response_command'
    status = 200
    data = {
        'test_data': 'test data'
    }
    response_messsage = ggv2_component.pubsub_messages.get_pubsub_response(message_id, response_command, status, data)


    # Test IPC REQUEST Message
    ggv2_component.publish_message('ipc',  ggv2_component.ipc_service_topic,  request_messsage)
    mock_publish_message.assert_called_with('ipc', ggv2_component.ipc_service_topic, request_messsage)

    ggv2_component.ipc_pubsub.publish_to_topic(ggv2_component.ipc_service_topic,  request_messsage)
    mock_publish_to_topic.assert_called_with(ggv2_component.ipc_service_topic, request_messsage)

    # Test IPC RESPONSE Message
    ggv2_component.publish_message('ipc',  ggv2_component.ipc_service_topic,  response_messsage)
    mock_publish_message.assert_called_with('ipc', ggv2_component.ipc_service_topic, response_messsage)

    ggv2_component.ipc_pubsub.publish_to_topic(ggv2_component.ipc_service_topic,  response_messsage)
    mock_publish_to_topic.assert_called_with(ggv2_component.ipc_service_topic, response_messsage)


    # Test MQTT REQUEST Message
    reply_topic = ggv2_component.mqtt_data_topic
    ggv2_component.publish_message('mqtt',  ggv2_component.mqtt_service_topic,  request_messsage)
    mock_publish_message.assert_called_with('mqtt', ggv2_component.mqtt_service_topic, request_messsage)

    ggv2_component.mqtt_pubsub.publish_to_mqtt(ggv2_component.mqtt_service_topic,  request_messsage)
    mock_publish_to_mqtt.assert_called_with(ggv2_component.mqtt_service_topic, request_messsage)


    # Test MQTT RESPONSE Message
    ggv2_component.publish_message('mqtt',  ggv2_component.mqtt_service_topic,  response_messsage)
    mock_publish_message.assert_called_with('mqtt', ggv2_component.mqtt_service_topic, response_messsage)

    ggv2_component.mqtt_pubsub.publish_to_mqtt(ggv2_component.mqtt_service_topic,  response_messsage)
    mock_publish_to_mqtt.assert_called_with(ggv2_component.mqtt_service_topic, response_messsage)
