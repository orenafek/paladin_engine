PaLaDiN's architecture is built around a powerful pythonic engine that leverages the abstract syntax tree (AST) of the
code to provide a comprehensive debugging solution. The engine performs an initial analysis of the program's AST to
identify the code fragments that require monitoring, including assignments, function calls, function definitions, loops,
and built-in collections manipulation methods. Using this information, PaLaDiN creates a "PaLaDiNized Code," which is an
instrumented version of the original code with stubs added before and after the selected code fragments, and sometimes
replacing entire code fragments with equivalent structures that maintain the program's functionality and flow.

PaLaDiN then runs the newly created code, with each stub logging the event that has occurred during the run and
assigning it a unique time stamp. This log of events is used to reconstruct the program's state at any point in time,
with a representation of each variable and object throughout the flow of the run. PaLaDiN provides an interactive web
server, where the user can run queries using PaLaDiN's comprehensive queries DSL to debug the code after it has ended.
This architecture enables PaLaDiN to provide a unique and comprehensive approach to debugging, which is both
user-friendly and effective.