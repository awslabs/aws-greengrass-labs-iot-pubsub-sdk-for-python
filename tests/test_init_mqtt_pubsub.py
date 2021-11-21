import sys
import json
import pytest
import logging
import awsiot.greengrasscoreipc.model as model

# Import the boilerplate example
sys.path.append('examples/00-greengrass-application-template/src/com.example.my_project.my_component/0.0.1/')

from pubsub.mqtt_pubsub import MqttPubSub

def test_init_mqtt_pubsub(mocker, monkeypatch, caplog):

    """ Positove and negatove unit tests for IPC PubSub wrapper """

    caplog.set_level(logging.INFO)

    monkeypatch.setenv("AWS_IOT_THING_NAME", "TestDevice")
    ipc_connect = mocker.patch("awsiot.greengrasscoreipc.connect")
    thread_executor = mocker.patch("concurrent.futures.ThreadPoolExecutor" )

    # Read in the GG Component recipe config details
    f = open('examples/00-greengrass-application-template/recipes/com.example.my_project.my_component.json',)
    data = json.load(f)
    ggv2_component_config = data["ComponentConfiguration"]["DefaultConfiguration"]["GGV2ComponentConfig"]

    ######################################################
    # Test manual creation and negative test / exception of MQTT PubSub wrapper
    #
    caplog.clear()
    mqtt_pubsub_timeout = ggv2_component_config['mqtt_pubsub_timeout']
    mqtt_subscribe_topics = ggv2_component_config['mqtt_subscribe_topics']
    mqtt_pubsub = MqttPubSub(None, mqtt_subscribe_topics, mqtt_pubsub_timeout)

    # Add unauthorised topic to subscribe list
    mqtt_subscribe_topics.append('unauthorised.topic')
    mqtt_pubsub_timeout = -10
    mqtt_pubsub = MqttPubSub(None, mqtt_subscribe_topics, mqtt_pubsub_timeout)

    for record in caplog.records:
        assert record.levelname != "ERROR"


    event = model.IoTCoreMessage(
        message=model.MQTTMessage(
            topic_name=None, payload=json.dumps({"test": "test"}).encode()
        )
    )

    mqtt_subscriber = mqtt_pubsub.MqttSubscriber(None)

    mqtt_subscriber.on_stream_event(event)
    mqtt_subscriber.on_stream_error(Exception('Test Exception'))
    mqtt_subscriber.on_stream_closed()
