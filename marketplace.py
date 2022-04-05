"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""
from threading import Lock
import time
import unittest
import logging
from logging.handlers import RotatingFileHandler
# Uncomment these lines for the unittesting to work!
# from producer import Producer
# from consumer import Consumer
# from product import Coffee, Tea

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
        with self.prod_lock:
            self.product_no.append(0)
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
        if self.product_no[producer_id] < self.queue_size_per_producer:
            self.available_prod.append((product, producer_id))
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
        with self.cart_lock:
            # look for requested product
            output = list(filter(lambda x: product in x,  self.available_prod))
            # if the product is available, take it from its producer
            if len(output) > 0:
                producer = output[0][1]
                self.consumers[cart_id].append(output[0])
                self.available_prod.remove(output[0])
                self.product_no[producer] -= 1
                logger.info(
                    "Consumer with cart_id: %d couldn't add product: %s", cart_id, str(product))
                return True
            logger.info(
                "Consumer with cart_id: %d could not add prouct: %s", cart_id, product)
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
            "Consumer with cart_id: %d wants to remove prouct: %s", cart_id, product)
        with self.lock_remove:
            # look for wanted product in the cart
            output = list(filter(lambda x: product in x,
                          self.consumers[cart_id]))
            if len(output) > 0:
                # if product was found, remove it from cart and make it available
                producer = output[0][1]
                self.consumers[cart_id].remove(output[0])
                self.available_prod.append(output[0])
                self.product_no[producer] += 1
                logger.info(
                    "Consumer with cart_id: %d removed product: %s", cart_id, product)

    def place_order(self, cart_id):
        """
        Return a list with all the products in the cart.

        :type cart_id: Int
        :param cart_id: id cart
        """
        logger.info(
            "Consumer with cart_id: %d placed order", cart_id)
        # make a list of products from the cart

        logger.info("Consumer with cart_id: %d placed order", cart_id)
        order = [product for product, _ in self.consumers[cart_id]]
        self.consumers.pop(cart_id)
        return order


class TestMarketplace(unittest.TestCase):
    """
    class for unittesting of marketplace class
    """

    def setUp(self):
        '''
        initialising fields for the marketplace test unit
        '''
        self.product1 = Tea(name="TestTea", price=10, type="Green")
        self.product2 = Coffee(name="TestTea", price=10,
                               acidity="Tough", roast_level="High")
        self.carts1 = [
            {
                "ops": [
                    {
                        "type": "add",
                        "product": self.product1,
                        "quantity": 1
                    },
                    {
                        "type": "add",
                        "product": self.product1,
                        "quantity": 3
                    },
                    {
                        "type": "remove",
                        "product": self.product2,
                        "quantity": 1
                    }
                ],
            }
        ]
        self.carts2 = [
            {
                "ops": [
                    {
                        "type": "add",
                        "product": self.product1,
                        "quantity": 1
                    },
                    {
                        "type": "add",
                        "product": self.product2,
                        "quantity": 3
                    },
                    {
                        "type": "remove",
                        "product": self.product2,
                        "quantity": 1
                    }
                ],
            },
            {
                "ops": [
                    {
                        "type": "add",
                        "product": self.product1,
                        "quantity": 5
                    },
                    {
                        "type": "add",
                        "product": self.product2,
                        "quantity": 4
                    },
                    {
                        "type": "remove",
                        "product": self.product1,
                        "quantity": 3
                    }
                ],
            }
        ]
        self.marketplace = Marketplace(2)
        self.first_producer = Producer(products=[self.product1], marketplace=self.marketplace,
                                       republish_wait_time=0.15, kwargs={})
        self.second_producer = Producer(products=[self.product2], marketplace=self.marketplace,
                                        republish_wait_time=0.2, kwargs={})
        self.first_cons = Consumer(
            carts=self.carts1, marketplace=self.marketplace, retry_wait_time=0.1,
            kwargs={'name': "cons1"})
        self.first_cons = Consumer(
            carts=self.carts2, marketplace=self.marketplace, retry_wait_time=0.3,
            kwargs={'name': "cons2"})

    def test_init_marketplace(self):
        '''
        test the initialization of marketplace with specified producer queue size
        '''
        self.assertEqual(2, self.marketplace.queue_size_per_producer)

    def test_register_producer(self):
        '''
        test for checking producer ids
        -> initializes 2 producers and checks their ids
        '''
        self.assertEqual(0, self.first_producer.prod_id)
        self.assertEqual(1, self.second_producer.prod_id)

    def test_publish(self):
        '''
        test for the marketplace publish method
        - check if products are added and if the queue is full they
        should not be added
        '''
        self.marketplace.publish(0, self.product1)
        self.assertEqual(1, len(self.marketplace.available_prod))

        self.marketplace.publish(1, self.product2)
        self.assertEqual(2, len(self.marketplace.available_prod))

        self.marketplace.publish(1, self.product2)
        self.assertFalse(3 == len(self.marketplace.available_prod))

    def test_new_cart(self):
        """
        test for creating new carts
        -> check the resulting cart ids
        """
        self.marketplace.new_cart()
        self.marketplace.new_cart()
        self.assertEqual(self.marketplace.cons_ids, 2)
        self.assertTrue(len(self.marketplace.consumers) == 2)

    def test_add_to_cart(self):
        """
        test for add_to_cart method
        """
        self.assertTrue(self.marketplace.add_to_cart(0, self.product1))
        self.assertTrue(self.marketplace.add_to_cart(1, self.product2))
        self.assertFalse(self.marketplace.add_to_cart(0, self.product2))
        self.assertFalse(self.marketplace.add_to_cart(1, self.product1))

    def test_remove_from_cart(self):
        """
        test for remove_from_Cart method
        -> checks number of products in cart after remove operation
        """
        self.marketplace.remove_from_cart(0, self.product1)
        self.assertEqual(len(self.marketplace.consumers[0]), 0)
        self.marketplace.remove_from_cart(0, self.product1)
        self.assertEqual(len(self.marketplace.consumers[0]), 0)

    def test_place_order(self):
        """
        test for place_order method
        checks if cart has been deleted
        """
        self.marketplace.place_order(1)
        self.assertEqual(self.marketplace.consumers[1], None)

    if __name__ == "main":
        unittest.main()
