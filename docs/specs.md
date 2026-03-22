# Project specs!

Since the purpose of this project is to enable various implementations, we need to define some sort of protocol that all implementations must follow. To some extent, this entire project would then be 'an implementation' of that protocol. However, not everything in this project is a part of this specification. For example, the frontend that one can visit to see the current state is not specified anywhere.

## Structure / architecture
Now this protocol presupposes two main parts: a client and a server. Both the client and the server have a frontend and a backend and both work in completely different ways. The server is the authority, so we will define the manner in which the server works as the main 

## test
```mermaid
sequenceDiagram
    box Gray Server
    participant page as Webpage
    participant SF as Game server @ route
    participant SB as Connection interface @ URL
    end
    box Gray Client
    participant CB as Connection interface
    participant CF as Implementation
    end

    critical registration
        CF->>CB: URL, username, route
        CB->>+SB: username, route
        Note over SB:Generate UUID
        SB->>SF: username, UUID
        SB->>page: New user
        SB->>-CB: recevied registration
    end

    loop
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