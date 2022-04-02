"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""
from threading import Lock


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
        self.queue_size_per_producer = queue_size_per_producer
        self.prod_ids = 0
        self.cons_ids = 0
        self.available_prod = []
        self.product_to_producer = {}
        self.consumers = {}
        self.product_no = []
        self.prodLock = Lock()
        self.consLock = Lock()
        self.cartLock = Lock()

    def register_producer(self):
        """
        Returns an id for the producer that calls this.
        """
        self.prodLock.acquire()
        self.available_prod.append([])
        self.product_no.append(0)
        self.prod_ids += 1
        self.prodLock.release()
        return self.prod_ids - 1

    def publish(self, producer_id, product):
        """
        Adds the product provided by the producer to the marketplace

        :type producer_id: String
        :param producer_id: producer id

        :type product: Product
        :param product: the Product that will be published in the Marketplace

        :returns True or False. If the caller receives False, it should wait and then try again.
        """
        if self.product_no[producer_id] < self.queue_size_per_producer:
            if product in self.product_to_producer:
                self.product_to_producer[product].append(producer_id)
            else:
                self.product_to_producer[product] = []
                self.product_to_producer[product].append(producer_id)
            self.product_no[producer_id] += 1
            self.available_prod[producer_id].append(product)
            return True
        return False

    def new_cart(self):
        """
        Creates a new cart for the consumer

        :returns an int representing the cart_id
        """
        self.consLock.acquire()
        self.consumers[self.cons_ids] = []
        self.cons_ids += 1
        self.consLock.release()
        return self.cons_ids - 1

    def add_to_cart(self, cart_id, product):
        """
        Adds a product to the given cart. The method returns

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to add to cart

        :returns True or False. If the caller receives False, it should wait and then try again
        """
        if product in self.product_to_producer:
            prodList = self.product_to_producer[product]
            for producer in prodList:
                if product in self.available_prod[producer]:
                    self.consumers[cart_id].append(product)
                    self.available_prod[producer].remove(product)
                    self.product_no[producer] -= 1
                    return True
        return False

    def remove_from_cart(self, cart_id, product):
        """
        Removes a product from cart.

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to remove from cart
        """
        if product in self.consumers[cart_id]:
            producer = self.product_to_producer[product][0]
            self.consumers[cart_id].remove(product)
            self.available_prod[producer].append(product)
            self.product_no[producer] += 1

    def place_order(self, cart_id):
        """
        Return a list with all the products in the cart.

        :type cart_id: Int
        :param cart_id: id cart
        """
        order = []
        for product in self.consumers[cart_id]:
            order.append(product)
        self.consumers.pop(cart_id, None)
        return order
