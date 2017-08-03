
import os
import unittest
from tempfile import NamedTemporaryFile

from doxec import Document, OpWrite, OpConsoleOutput


toy_doc = """
# Installation

In order to run the code examples in this repository you need `python3` and
the
python packages `numpy`, `scipy` and `matplotlib`. On ubuntu 16.04 you can
setup
you system by running the following two commands as super-user (prefix
`sudo`).

```bash
apt-get update
apt-get install python3 python3-numpy python3-scipy python3-matplotlib
```

# First Steps
As a first example we can compute the square root of 2. Create a
file named `example.py` with the following content.

<!-- write example.py -->
```python
import math

print("Example 1:")
print("Square root of 2 = %g" % math.sqrt(2))
```

The file can be run with the `python3` interpreter.

<!-- console_output -->
```bash
$ python3 example.py
Example 1:
Square root of 2 = 1.41421
```
"""

class DocumentTestCase(unittest.TestCase):
    """
    This class tests the methods provided by the document class.
    """

    def test_parse(self):
        """
        Test whether the parse() correctly parses all operations in the toy
        file.
        """
        tmp = NamedTemporaryFile(delete=False)
        tmp.write(toy_doc.encode('utf8'))
        tmp.close()

        doc = Document(tmp.name)

        self.assertEqual(len(doc.operations), 2)
        self.assertIsInstance(doc.operations[0], OpWrite)
        self.assertIsInstance(doc.operations[1], OpConsoleOutput)

        os.remove(tmp.name)

    def test_run(self):
        """
        Check that run() does no raise an exception on the toy file.
        """
        tmp = NamedTemporaryFile(delete=False)
        tmp.write(toy_doc.encode('utf8'))
        tmp.close()

        doc = Document(tmp.name)

        doc.run()

        os.remove(tmp.name)

