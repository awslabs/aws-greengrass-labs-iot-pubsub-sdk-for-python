import sys
import json
import pytest
import logging
import awsiot.greengrasscoreipc.model as model

# Import the src directory
sys.path.append('src')

from src.pubsub.ipc_pubsub import IpcPubSub

def test_init_ipc_pubsub(mocker, monkeypatch, caplog):

    """ Positove and negatove unit tests for IPC PubSub wrapper """

    caplog.set_level(logging.INFO)

    monkeypatch.setenv("AWS_IOT_THING_NAME", "TestDevice")
    ipc_connect = mocker.patch("awsiot.greengrasscoreipc.connect")
    thread_executor = mocker.patch("concurrent.futures.ThreadPoolExecutor" )

    # Read in the GG Component recipe config details
    f = open('src/recipe.json',)
    data = json.load(f)
    ggv2_component_config = data["ComponentConfiguration"]["DefaultConfiguration"]["GGV2ComponentConfig"]

    ######################################################
    # Test manual creation and negative test / exception of IPC PubSub wrapper
    #
    caplog.clear()
    ipc_pubsub_timeout = ggv2_component_config['ipc_pubsub_timeout']
    ipc_subscribe_topics = ggv2_component_config['ipc_subscribe_topics']
    ipc_pubsub = IpcPubSub(None, ipc_subscribe_topics, ipc_pubsub_timeout)

    # Add unauthorised topic to subscribe list
    ipc_subscribe_topics.append('unauthorised.topic')
    ipc_pubsub_timeout = -10
    ipc_pubsub = IpcPubSub(None, ipc_subscribe_topics, ipc_pubsub_timeout)

    for record in caplog.records:
        assert record.levelname != "ERROR"


    event = model.IoTCoreMessage(
        message=model.MQTTMessage(
            topic_name=None, payload=json.dumps({"test": "test"}).encode()
        )
    )


    topic_subscriber = ipc_pubsub.TopicSubscriber(None, ipc_subscribe_topics, thread_executor)

    topic_subscriber.on_stream_event(event)
    topic_subscriber.on_stream_error(Exception('Test Exception'))
    topic_subscriber.on_stream_closed()
