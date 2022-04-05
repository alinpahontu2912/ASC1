## Arhitectura Sistemelor de calcul - Tema 1 - Pahontu Stefan Alin

# Program flow:
* the producer keeps on producing items for as long as his product
queue is not full and has to wait after succesfully producing every
item
* the consumer will create carts and take care of them: 
      * he can add/remove products to a cart
      * when no cart operations are left, he will place his order
      * there is a lock and a stdout flush for any problems that might
occur while printing
* the marketplace class is responsible for creating and filling carts
* locks are used for creating new producer ids, cart ids, incrementing
and decrementing the number of products held in a list (all are non 
atomic operations, hence needed protection against race conditions)
* logging is used to keep track of how a function is called and what its
result is 
* unitttests are available for the Marketplace class and its methods, but
in order to be run the import lines from the beginning must be uncommented !
* Useful links:
https://stackoverflow.com/questions/40088496/how-to-use-pythons-rotatingfilehandler
https://www.educba.com/unit-testing-in-python/
* P.S: there is also the .git folder included in the archive :)
