Current state of the project:

The system of sending and receiving works but it not flexible in the slightest. We require some some sort of system to dynamically create games and to forward messages to the respective game agents. We want to pass virtually nothing to every function and class and infer the desired action with as little context as possible.

To this end we are going to:
1. enable the dynamic creation of 'game agents'. Aside from an interface for a client (Client) and a class for keeping track of which clients there are and their respective methods (ConnectionMgr), we are going to need a way to keep track of which games there are (roomManager). Here we bind clients to rooms (read: a small asynchronous agent), startup rooms and we create and destroy queues.