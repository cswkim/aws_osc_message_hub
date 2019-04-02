"""
AWS IoT Message Hub Client
"""
from AWSIoTPythonSDK.exception import AWSIoTExceptions
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

from .message_hub import (
    AbstractMessageHubClient,
    MessageHubConnectionError,
    MessageHubPublishError,
    MessageHubSubscribeError,
)
from .osc import OscMessageHubClient


class AwsIotMessageHubClient(AbstractMessageHubClient):
    def __init__(self, host, port, access_key, secret_key, cert_path,
                 client_id, osc_client=None):
        """
        :param str host:
        :param int port:
        :param str cert_path:                  The path to the aws root ca file
                                               that allows this client access to
                                               the Aws Iot service.
        :param str client_id:                  A string (name) that identifies
                                               this client within the Aws Iot
                                               message broker (this should be
                                               unique per client).
        :param str access_key:                 The AWS access key for the IoT
                                               platform.
        :param str secret_key:                 The AWS secret key for the IoT
                                               platform.
        :param OscMessageHubClient osc_client: An OscMessageHubClient object
                                               that is optional in case it is
                                               needed for a message callback.
        """
        super(AwsIotMessageHubClient, self).__init__(host, port)
        self.cert_path = cert_path
        self.client_id = client_id
        self.osc_client = osc_client
        self._access_key = access_key
        self._secret_key = secret_key

    def connect(self):
        try:
            self._client = AWSIoTMQTTClient(self.client_id, useWebsocket=True)
            self._client.configureEndpoint(self.host, self.port)
            self._client.configureIAMCredentials(self._access_key,
                                                 self._secret_key)
            self._client.configureCredentials(self.cert_path)

            self._client.configureAutoReconnectBackoffTime(1, 32, 20)
            self._client.configureOfflinePublishQueueing(-1)
            self._client.configureDrainingFrequency(2)
            self._client.configureConnectDisconnectTimeout(10)
            self._client.configureMQTTOperationTimeout(5)

            self._client.connect()
        except (OSError, ValueError,
                AWSIoTExceptions.connectTimeoutException) as err:
            raise MessageHubConnectionError(err) from None

    def disconnect(self):
        if not self._client.disconnect():
            raise MessageHubConnectionError("AwsIotPythonSDK disconnect error!")

    def publish(self, channel, message):
        if not self._client.publish(channel, message, 1):
            raise MessageHubSubscribeError("AwsIotPythonSDK publish error!")

    def subscribe(self, channels):
        for channel in channels:
            if not self._client.subscribe(channel, 1, self._message_callback):
                raise MessageHubSubscribeError(
                    "AwsIotPythonSDK subscribe error!")

    def _message_callback(self, client, user_data, message):
        if self.osc_client is not None:
            self.osc_client.publish(message.topic, message.payload)
