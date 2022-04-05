"""
This module represents the Consumer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""


from threading import Thread
import time
import sys


class Consumer(Thread):
    """
    Class that represents a consumer.
    """

    def __init__(self, carts, marketplace, retry_wait_time, **kwargs):
        """
        Constructor.

        :type carts: List
        :param carts: a list of add and remove cart_operationerations

        :type marketplace: Marketplace
        :param marketplace: a reference to the marketplace

        :type retry_wait_time: Time
        :param retry_wait_time: the number of seconds that a producer must wait
        until the Marketplace becomes available

        :type kwargs:
        :param kwargs: other arguments that are passed to the Thread's __init__()
        """
        Thread.__init__(self, **kwargs)
        self.carts = carts
        self.marketplace = marketplace
        self.retry_wait_time = retry_wait_time
        self.name = kwargs.get('name')

    def add_to_market(self, quantity, cart_id, product):
        """
        :type quantity: int
        :param quantity: number of products

        :type cart_id: int
        :param cart_id: the cart number

        :type product: Product
        :param product: product to be added

        adds the product to the cart with cart_id 'quantity' times

        """
        i = 0
        while i < quantity:
            if not self.marketplace.add_to_cart(cart_id, product):
                time.sleep(self.retry_wait_time)
            else:
                i += 1

    def remove_from_market(self, quantity, cart_id, product):
        """
        :type quantity: int
        :param quantity: number of products

        :type cart_id: int
        :param cart_id: the cart number

        :type product: Product
        :param product: product to be added

        removes the product from the cart with cart_id 'quantity' times

        """
        i = 0
        while i < quantity:
            self.marketplace.remove_from_cart(cart_id, product)
            i += 1

    def run(self):
        for cart in self.carts:
            cart_id = self.marketplace.new_cart()
            for cart_operation in cart:
                if cart_operation['type'] == 'add':
                    self.add_to_market(
                        cart_operation['quantity'], cart_id, cart_operation['product'])
                elif cart_operation['type'] == 'remove':
                    self.remove_from_market(
                        cart_operation['quantity'], cart_id, cart_operation['product'])
            order = self.marketplace.place_order(cart_id)
            for product in order:
                # flush to make sure everything is printed
                sys.stdout.flush()
                print(self.name + " bought " + str(product))
