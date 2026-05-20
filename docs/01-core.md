`# Core design concepts
In this document, we will discuss the core design principles and concepts to place the rest of the codebase in context. This includes mostly the philosophy behind the design and which components exists, which (hopefully) makes every implementatino detail obvious.

## Global overview
### What is this project?
This is a webserver that has one single purpose. It aims to host real-time programming competitions, and in particular for unsolved (or virtually unsolved) problems. Although programming competitions are quite established, they tend to focus on problems where a solution either works or does not. From time to time, speed matters, but that can often be bypassed by just choosing a faster language for the same implementation. Aside from that, some problems can just be bruteforced or don't require any 'good' code. That is to say, in my experience, the only factor considered is the speed of writing your solution, which is in my opinion the least interesting factor in a programming competition.

At the same time, many problems that we encounter these days do not have a single definitive solution. There are multiple strategies, where one may be better than the other depending on the context. For example, a game like chess. Another example could be automated stock trading, and even something lile poker. For all of these problems, there are various different solutions, all with their own 'personality' (agressive, passive, defensive, etc).

To this end, we can write a system where programmed solutions to such problems can 

This project aims to present players with these kinds of problems and to match them up against one another, so that programming competitions have direct competition, and a bit more skill involved.

### What does this mean for a implementation?
From the section above, we can determine a small list of requirements:
- An interface for some sort of client that can connect to out server to make choices in a problem
    - A way to store and access all of our connected clients
    - A way to handle incoming messages and outgoing responses
- A set of rooms or sub-servers a client can connect to that has its own encapsulated problem
    - Some way to quickly implement new problems without rewriting anything other than the problem itself
    - A way to create or destroy these rooms (i.e. a room manager)
- An admin web-interface
    - To interact with the room manager and see an overview of the room managers's state
    - To show the state of current problems or rooms
    - Some way to properly secure the admin interface

### How can we implement that?
To actually implement this abstract idea, we can use the following:
- FastAPI + pydantic for managing everything web related (websockets, websites)
- A few asynchronous actors that continously wait for items to be pushed into queues to handle them. This can be done for receiving messages and for sending messages, and for managing the game rooms.
- Builtin python libraries for hashing and for generating tokens.