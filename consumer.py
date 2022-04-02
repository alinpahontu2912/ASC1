"""
This module represents the Consumer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""


from threading import Thread
import time


class Consumer(Thread):
    """
    Class that represents a consumer.
    """

    def __init__(self, carts, marketplace, retry_wait_time, **kwargs):
        """
        Constructor.

        :type carts: List
        :param carts: a list of add and remove operations

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
        self.name = kwargs['name']

    def run(self):
        for cart in self.carts:
            cart_id = self.marketplace.new_cart()
            for op in cart:
                if op['type'] == 'add':
                    i = 0
                    while i < op['quantity']:
                        tmp = self.marketplace.add_to_cart(
                            cart_id, op['product'])
                        if not tmp:
                            time.sleep(self.retry_wait_time)
                        else:
                            i += 1
                elif op['type'] == 'remove':
                    i = 0
                    while i < op['quantity']:
                        self.marketplace.remove_from_cart(
                            cart_id, op['product'])
                        i += 1
            order = self.marketplace.place_order(cart_id)
            for product in order:
                print(self.name + " bought " + str(product))
