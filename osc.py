"""
OSC Message Hub Broker/Client
"""
import json
import socket

from pythonosc import (
    dispatcher,
    osc_server,
    udp_client,
)

from .message_hub import (
    AbstractMessageHubBroker,
    AbstractMessageHubClient,
    MessageHubConnectionError,
    MessageHubPublishError,
    MessageHubStartError,
)


class OscMessageHubBroker(AbstractMessageHubBroker):
    def __init__(self, host, port, channels, aws_client=None):
        """
        :param str host:
        :param int port:
        :param list channels:
        :param AwsIotMessageHubClient aws_client: An AwsIotMessageHubClient
                                                  object that is optional in
                                                  case it is needed for a
                                                  message callback.
        """
        super(OscMessageHubBroker, self).__init__(host, port)
        self.channels = channels
        self.aws_client = aws_client

    def start(self):
        try:
            osc_dispatcher = dispatcher.Dispatcher()

            for channel in self.channels:
                osc_dispatcher.map(channel, self._message_callback, None)

            self._server = osc_server.ThreadingOSCUDPServer(
                (self.host, self.port),
                 osc_dispatcher)

            self._server.serve_forever()
        except OSError as err:
            raise MessageHubStartError(err) from None

    def _message_callback(self, channel, args, message):
        if self.aws_client is not None:
            formatted_message = json.loads(message)
            self.aws_client.publish(channel, formatted_message)


class OscMessageHubClient(AbstractMessageHubClient):
    def __init__(self, host, port):
        super(OscMessageHubClient, self).__init__(host, port)

    def connect(self):
        try:
            self._client = udp_client.SimpleUDPClient(self.host, self.port)
            self._client._sock.setsockopt(socket.SOL_SOCKET,
                                          socket.SO_BROADCAST, 1)
        except OSError as err:
            raise MessageHubConnectionError(err) from None

    def publish(self, channel, message):
        try:
            self._client.send_message(channel, message)
        except OSError as err:
            raise MessageHubPublishError(err) from None
