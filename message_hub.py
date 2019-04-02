"""
Message Hub Interface
"""


class BaseMessageHubError(Exception):
    """The foundation of all message hub exceptions."""


class MessageHubConnectionError(BaseMessageHubError):
    """Raised when a client cannot connect/disconnect to/from a broker."""


class MessageHubPublishError(BaseMessageHubError):
    """Raised when a client cannot publish to a broker."""


class MessageHubStartError(BaseMessageHubError):
    """Raised when a broker cannot start."""


class MessageHubStopError(BaseMessageHubError):
    """Raised when a broker cannot stop."""


class MessageHubSubscribeError(BaseMessageHubError):
    """Raised when a client cannot subscribe to a broker."""


class AbstractMessageHubBroker(object):
    """
    The interface class for all objects that will act as a message broker for
    all observing clients.
    """
    def __init__(self, host, port):
        """
        MessageHubBroker objects are initialized with the host/ip/endpoint and
        the port to listen on.

        :param str host:
        :param int port:
        """
        self._server = None
        self.host = host
        self.port = port

    def start(self):
        """
        Start the broker service.

        Each interfacing object will implement it's own logic in order to
        properly start. The internal `_server` property will be set to the
        returned object upon successful start.

        :raises MessageHubStartError:
        """
        raise NotImplementedError

    def stop(self):
        """
        Stop the broker service.

        :raises MessageHubStopError:
        """
        raise NotImplementedError


class AbstractMessageHubClient(object):
    """
    The interface class for all objects that need to publish or subscribe to a
    broker.
    """
    def __init__(self, host, port):
        """
        MessageHubClient objects are initialized with the host/ip/endpoint and
        the port of the broker.

        :param str host:
        :param int port:
        """
        self._client = None
        self.host = host
        self.port = port

    def connect(self):
        """
        Connect with a broker.

        Each interfacing object will implement it's own logic in order to
        properly connect with the desired broker. The internal `_client`
        property will be set to the returned object upon successful connection.

        :raises MessageHubConnectionError:
        """
        raise NotImplementedError

    def disconnect(self):
        """
        Disconnect with a broker.

        :raises MessageHubConnectionError:
        """
        raise NotImplementedError

    def publish(self, channel, message):
        """
        Publish a message to a particular channel.

        :param str channel:
        :param str message: A JSON string

        :raises MessageHubPublishError:
        """
        raise NotImplementedError

    def subscribe(self, channels):
        """
        Subscribe to a list of channels.

        :param list channels:

        :raises MessageHubSubscribeError:
        """
        raise NotImplementedError
