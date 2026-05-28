# Documentation
First of all we describe what the goals of the project are. From that we get a list of requirements (admin dashboard, real time communication with users). Based on that we describe how all of the requirements could be implemented (which library, which pattern, etc). That in turn yields a small list of concrete parts of our code. Then we describe how all of these parts would be connected and what that would require.

If all of this is done, every class in my code has a reason to exist, a responsibility and a 'contract'. The only step left is to say where exactly that lives in the code and how it is implemented, but that should be trivial if the code is well writen.

Then we only describe naming conventions, how to build the code and maybe some testing or development considerations, and we should be done.

## Rules for writing documentation
Always following some sort of precedent, for example in [httproutes.py](/app/routes/httpsroutes.py), we describe the GET routes that respond with a webpage as "Route for \[description\] page". This is the same for other similar functions.

## Responsibilities of different levels of doucmentation
We describe all functions and classes with docstrings. There is a slight seperation between comments, docstring documentation responsibility and generic markdown documentation responsibility. Comments should somewhat convey the workings of a function. Docstrings should be used to convey the meaning and purpose of a function on a slightly higher level, and markdown documentation should worry about issues such as how classes correspond to one another, the architecture behind the code, broader ideas, TODO lists, etc. In other words, responsibility for anything on a higher level than what a function is and what it does, should be written in markdown files.