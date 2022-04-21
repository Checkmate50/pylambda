# Tools for Pylambda

## pylambda_to_python.py

Given a `.pylambda` file, writes the file as raw Python for interpretation to stdout.  The intention of this is for testing to make sure that both the pylambda compiler works and to check that the pylambda program works.  The output of this can be put into a file or read directly by python with `python tools\pylambda_to_python.py > python -` (assuming you're in root)
