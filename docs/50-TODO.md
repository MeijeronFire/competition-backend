# TODO

This is a non-comprehensive list of TODO's for this codebase. For a complete list, search for TODO.

Furthermore, curernt projects, i.e. test coverage and documentation coverage is included here.

## Refactoring changes
1. The frontend looks pretty good, but is rather cumbersome to program. We should change the current system to simply "patch" the state and look for differences, rather than redrawing needlessly and often. In general, writing the JS is so painfull that even for this small project, it might be worth looking into other options, like frontend frameworks.

2. Rewrite the admin dashboard to use SSE's together with mostly POST and PUT requests rather than arduous websockets. We use far less functionality than provided, and they make documentation and code handling far harder. Once changes are started, design decisions will be explained further. The broad idea is to create a few streams the client can "subscribe to", and based on that send requests for further info or changes.

3. When loading webpages, most of the space is not filled with a placeholder or a default value. That should be an easy fix, as all information is known at the time the user sends a request. Therefore, the template should be filled with some info that the JS can override (although it should look identical) later, i.e. unresponsive but good looking initial info.

## Documentation
The list below is what _is_ covered, not what still must be done.

### Markdown coverage
Current documentation coverage:
1. Meta documentation
2. Architecture documentation
3. Prerequisite knowledge

4. Conventions (not done)

### Docstring and comment coverage
1. Routes/
2. lifecycle
3. Models/
3. Utils
4. Init

## Testing
We have 0% testing coverage currently.