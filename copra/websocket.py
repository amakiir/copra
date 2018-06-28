# -*- coding: utf-8 -*-
"""Asynchronous websocket client for the Coinbase Pro platform.

"""

import logging

from autobahn.asyncio.websocket import WebSocketClientFactory
from autobahn.asyncio.websocket import WebSocketClientProtocol

logger = logging.getLogger(__name__)

FEED_URL = 'wss://ws-feed.gdax.com'
SANDBOX_FEED_URL = 'wss://ws-feed-public.sandbox.gdax.com'


class Channel:
    """A websocket channel.

    A Channel object encapsulates the Coinbase Pro websocket channel name
    *and* one or more Coinbase Pro product ids.

    To read about Coinbase Pro channels and the data they return, visit:
    https://docs.gdax.com/#channels

    Attributes:
        name (str): The name of the websocket channel.
        product_ids (set of str): Set of product ids for the channel.

    """

    def __init__(self, name, product_ids):
        """Channel __init__ method.

        Args:
            name (str): The name of the websocket channel. Possible values
                are heatbeat, ticker, level2, full, matches, or user

            product_ids (str or list of str): A single product id
                (eg., 'BTC-USD') or list of product ids (eg., ['BTC-USD',
                'ETH-EUR', 'LTC-BTC'])

        Raises:
            ValueError: If name not valid or product ids is empty.
        """
        self.name = name.lower()
        if self.name not in ('heartbeat', 'ticker', 'level2',
                             'full', 'matches', 'user'):
            raise ValueError("invalid name {}".format(name))

        if not product_ids:
            raise ValueError("must include at least one product id")

        if not isinstance(product_ids, list):
            product_ids = [product_ids]
        self.product_ids = set(product_ids)

    def __call__(self):
        return self

    def as_dict(self):
        """Returns the Channel as a dictionary.

        Returns:
            dict: The Channel as a dict with keys name & product_ids.
        """
        return {'name': self.name, 'product_ids': list(self.product_ids)}


class ClientProtocol(WebSocketClientProtocol):
    """Websocket client protocol.

    This is a subclass of autobahn.asyncio.websocket.WebSocketClientProtocol.
    In most cases this should not need to be subclassed or even accessed
    directly.
    """

    def __init__(self, channels):
        """ClientProtocol initialization.

        Args:
            channels (list of Channel objects): The channels to subscribe to.
        """
        super().__init__()


class Client(WebSocketClientFactory):
    """Asyncronous websocket client for Coinbase Pro.

       Attributes:
           feed_url (str): The url of the websocket server.
    """

    def __init__(self, channels, feed_url=FEED_URL):
        """ Client initialization.

        Args:
            channels (Channel or list of Channel): The initial channels to
                subscribe to.
            feed_url (str): The url of the websocket server. The defualt is
                copra.websocket.FEED_URL (wss://ws-feed.gdax.com)
        """
        if not isinstance(channels, list):
            channels = [channels]
        self._initial_channels = channels
        self.feed_url = feed_url

        super().__init__(self.feed_url)

    def add_as_task_to_loop(self, loop):
        """Add the client to the asyncio loop.

        Creates a coroutine for making a connection to the websocket server and
        adds it as a task to the asyncio loop.

        Args:
            loop (asyncio event loop): The event loop that the websocket client
                runs in.
        """
