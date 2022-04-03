"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import Lock
import time
import logging
from logging.handlers import RotatingFileHandler
logging.basicConfig(
    handlers=[RotatingFileHandler(
        'marketplace.log', maxBytes=10000, backupCount=10, mode='a')],
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(message)s")
logging.Formatter.converter = time.gmtime
logger = logging.getLogger()


class Marketplace:
    """
    Class that represents the Marketplace. It's the central part of the implementation.
    The producers and consumers use its methods concurrently.
    """

    def __init__(self, queue_size_per_producer):
        """
        Constructor

        :type queue_size_per_producer: Int
        :param queue_size_per_producer: the maximum size of a queue associated with each producer
        """
        logger.info(
            "Inititalizing marketplace with %d queue size", queue_size_per_producer)
        self.queue_size_per_producer = queue_size_per_producer
        self.prod_ids = 0
        self.cons_ids = 0
        self.available_prod = []
        self.consumers = {}
        self.product_no = []
        self.prod_lock = Lock()
        self.cons_lock = Lock()
        self.cart_lock = Lock()
        self.lock_remove = Lock()
        self.lock = Lock()
        logger.info(
            "Inititialized marketplace with %d queue size", queue_size_per_producer)

    def register_producer(self):
        """
        Returns an id for the producer that calls this.
        """
        logger.info("Registering new producer")
        # only one producer ccan be created at a time
        self.product_no.append(0)
        with self.prod_lock:
            new_id = self.prod_ids
            self.prod_ids += 1
            logger.info("Registered producer with id: %d", new_id)
            return new_id

    def publish(self, producer_id, product):
        """
        Adds the product provided by the producer to the marketplace

        :type producer_id: String
        :param producer_id: producer id

        :type product: Product
        :param product: the Product that will be published in the Marketplace

        :returns True or False. If the caller receives False, it should wait and then try again.
        """

        logger.info(
            "Producer with id: %d wants to publish product: %s", producer_id, str(product))
        # only publish if producer product queue is not full
        if self.product_no[producer_id] < self.queue_size_per_producer:
            self.available_prod.append((product, producer_id))
            # use mutex here to ensure atomicity
            with self.lock:
                self.product_no[producer_id] += 1
            logger.info(
                "Producer with id: %d published product: %s", producer_id, str(product))
            return True
        logger.info(
            "Producer with id: %d couldn't publish product: %s", producer_id, str(product))
        return False

    def new_cart(self):
        """
        Creates a new cart for the consumer

        :returns an int representing the cart_id
        """
        logger.info("Registering new cart")
        # only one new cart can be created at a time
        with self.cons_lock:
            self.consumers[self.cons_ids] = []
            self.cons_ids += 1
            new_id = self.cons_ids - 1
            logger.info("Registered cart with id: %d", new_id)
            return new_id

    def add_to_cart(self, cart_id, product):
        """
        Adds a product to the given cart. The method returns

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to add to cart

        :returns True or False. If the caller receives False, it should wait and then try again
        """
        logger.info(
            "Consumer with cart_id: %d wants to add product: %s", cart_id, str(product))

        # look for requested product
        output = list(filter(lambda x: product in x,  self.available_prod))
        if len(output) > 0:
            # if the product is available, take it from its producer
            producer = output[0][1]
            self.consumers[cart_id].append(output[0])
            with self.cart_lock:
                self.available_prod.remove(output[0])
                self.product_no[producer] -= 1
            logger.info(
                "Consumer with cart_id: %d added prouct: %s", cart_id, str(product))
            return True
        logger.info(
            "Consumer with cart_id: %d couldn't add product: %s", cart_id, str(product))
        return False

    def remove_from_cart(self, cart_id, product):
        """
        Removes a product from cart.

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to remove from cart
        """
        logger.info(
            "Consumer with cart_id: %d wants to remove product: %s", cart_id, str(product))

        # look for wanted product in the cart
        output = list(filter(lambda x: product in x,
                             self.consumers[cart_id]))
        if len(output) > 0:
            # if product was found, remove it from cart and make it available
            producer = output[0][1]
            self.available_prod.append(output[0])
            with self.lock_remove:
                self.product_no[producer] += 1
                self.consumers[cart_id].remove(output[0])
            logger.info(
                "Consumer with cart_id: %d removed product: %s", cart_id, str(product))

    def place_order(self, cart_id):
        """
        Return a list with all the products in the cart.

        :type cart_id: Int
        :param cart_id: id cart
        """
        logger.info(
            "Consumer with cart_id: %d placed order", cart_id)
        # make a list of products from the cart
        order = [product for product, _ in self.consumers[cart_id]]
        self.consumers.pop(cart_id)
        return order
