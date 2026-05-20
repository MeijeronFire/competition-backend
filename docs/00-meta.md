# Meta documentation
First of all we describe what the goals of the project are. From that we get a list of requirements (admin dashboard, real time communication with users). Based on that we describe how all of the requirements could be implemented (which library, which pattern, etc). That in turn yields a small list of concrete parts of our code. Then we describe how all of these parts would be connected and what that would require.

If all of this is done, every class in my code has a reason to exist, a responsibility and a 'contract'. The only step left is to say where exactly that lives in the code and how it is implemented, but that should be trivial if the code is well writen.

Then we only describe naming conventions, how to build the code and maybe some testing or development considerations, and we should be done.