# Project specs!

Since the purpose of this project is to enable various implementations, we need to define some sort of protocol that all implementations must follow. To some extent, this entire project would then be 'an implementation' of that protocol. However, not everything in this project is a part of this specification. For example, the frontend that one can visit to see the current state is not specified anywhere.

## Note on naming
there are a few general rules by which things are named both in documentation and code. First of all, everything sent over the websocket connection is a *message*, often abbreviated to *msg*. If this is passed on to derivative functions without any filtering or further changes, it stays the same. If we are taking in raw input and we are not certain that it is correct, we may refer to it as *data*, in the sense that as data is unproccesed information, it becomes a message.

## Structure / architecture
Now this protocol presupposes two main parts: a client and a server. Both the client and the server have a frontend and a backend and both work in completely different ways. The server is the authority, so we will define the manner in which the server works perhaps a little arbitrarily, and we expect every client to follow this. Below is a diagram of the structure and how each part corresponds to other parts.

```mermaid
sequenceDiagram
    autonumber
    box Gray Server
    participant page as Webpage
    participant SF as Game server @ route
    participant SB as Connection interface @ URL
    end
    box Gray Client
    participant CB as Connection interface
    participant CF as Implementation
    end

    critical
        Note over page, CF: Registration protocol
        CF->>CB: URL, username, route
        CB->>+SB: username, route
        Note over SB:Generate UUID
        SB->>+SF: username, UUID
        SF-->>-SB: (optional) initial client state
        SB->>page: New user
        SB->>-CB: recevied registration
    end

    loop
        Note over page, CF: Main communication loop
        SF->>+SB: UUID: state, request
        Note over SB:Find connection associated w/ UUID
        SB->>+CB: state, request
        Note over CB: Find handler associated w/ request
        CB->>+CF: state
        CF->>-CB: response
        CB->>-SB: response
        SB->>-SF: response
        SF->>page: state
        Note over SF: Determine next request
    end
```

Now lets define the format of each message sent internally and over the websocket connection:
- The registration packet (2):
```json
{
    "action": "register",
    "name": username,
    "room": route
}
```
as defined in [verify.py](/app/verify.py):
```py
class RegisterPacket(BaseMessage):
    action: str = "register"
    name: str
    room: str
```
- The registration response (6):
```json
{
	"type": "regResp",
	"msg": Any, // optional
}
```
It is conceivable that you may want to send some sort of initial state to each player and only once. For that reason, the regResp message both exists and has the optional field `'msg'` that can be filled with any message, specified by the game server. Note that any game server may have its own specification on which messages are expected and in which format.

- Main loop requests (8)
These requests are completely dependant on the specification of the game. Here is an example
```json
{
    "type": "turn",
    "state": {
        ...
    }
}
```
- Main loop request responses (11)
Once again dependant on different specifications, but here is another format example. You should be able to quickly see an overview of all accepted responses at the top of all implementations of [game.py](/game/game.py), with a neat pydantic setup.
```json
{
    "choice": move //
}
```

Note that the pair of 8 and 11 can change and do not have a set format. That depends on the game implemented. For example, the server may have a follow op request that is specific and wait for a response that suits that request. Summary: see game server specific documentation for (8) and (11)

## Implementation notes
### game.py
In the webserver, we expect the listener function that is tied to every connected client to be a `Callable[[], Generator[dict, dict, None]]`, that is to say, that it is a python function that contains the `yield` keyword rather than a `return` keyword. In practical implementation that means that we don't have to keep track of the current state of the program, but we can just yield and then continue in whatever place in code it finds itself.

In other words, the game can be treated and can act asif it is almost unrelated to the rest of the code, because it runs through its own code linearly. For example, we are in an infinite loop. At the top we put `msg = yield result`. This means we 'return' a computed `result`, and we read some parameter named `msg`. Depending on what msg contains, we compute this result and go back to the top of the loop, *or* we enter a new loop that yields something like `msg = yield "request clarification"`, with some more logic and a conditional break if "clarification" is provided.

A complete explanation of how generators work is not included here, of course, but this should hopefully provide an insight in how to program implementations of `game.py`.