from awscrt import mqtt, http
from awsiot import mqtt_connection_builder
from uuid import uuid4

import sys
import threading
import time
import json

# Use MQTT service with AWS IoT to create an MQTT connection
# and connect devices to the cloud.
# Template for the process to register and add a
# new device to the network.

def on_message_received(topic, payload):
    print("Message received from '{}'. Payload: '{}".format(topic, payload))



if __name__ == '__main__':
    # Necessary for an MQTT Connection:
    # topic to subscribe to
    # Endpoint (server address), key, cert, ca filepaths

    endpoint = "a3fn6zbxkxmi7t-ats.iot.us-east-1.amazonaws.com"
    cert_filepath = "/Users/maddielove/certs/device.pem.crt"
    ca_filepath = "/Users/maddielove/certs/AmazonRootCA1.pem"
    key_filepath = "/Users/maddielove/certs/private.pem.key"
    topic = "test/lambda"
    MQTT_connection = mqtt_connection_builder.mtls_from_path(
        endpoint=endpoint,
        port=8883,
        cert_filepath=cert_filepath,
        pri_key_filepath=key_filepath,
        ca_filepath=ca_filepath,
        client_id="test-" + str(uuid4())

    )

    # Create connection, wait until connection established
    connection = MQTT_connection.connect()
    connection.result()
    print("Connected!")


    print("Subscribing to topic '{}'...".format(topic))
    # QOS protocol, will publish messages until the PUBACK signal is sent back

    subscribe_future, packet_id = MQTT_connection.subscribe(
        topic=topic,
        qos=mqtt.QoS.AT_LEAST_ONCE,
        callback=on_message_received)

    subscribe_result = subscribe_future.result()
    print("Subscribed with {}".format(str(subscribe_result['qos'])))


    for i in range(3):
        message = {"number": i, "message": "Sending from Python script to MQTT. Expecting a response from AWS Lambda."}
        print("publishing message")
        print(message)
        #JSON.dumps cleans up message
        message_json = json.dumps(message)
        pub_message = MQTT_connection.publish(
            topic=topic,
            payload=message_json,
            qos=mqtt.QoS.AT_LEAST_ONCE
        )

        time.sleep(1)
