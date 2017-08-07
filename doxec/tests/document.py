
import os
import unittest
from unittest.mock import MagicMock
from tempfile import NamedTemporaryFile

from doxec import Document, OpWrite, OpConsoleOutput, Markdown, Monitor


toy_doc = """# Installation

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

# This is line 19
<!-- write example.py -->
```python
import math

print("Example 1:")
print("Square root of 2 = %g" % math.sqrt(2))
```

The file can be run with the `python3` interpreter.
# This is line 29
<!-- console_output -->
```bash
$ python3 example.py
Example 1:
Square root of 2 = 1.41421
```
"""

toy_doc2 = """
Hello this is an other toy document.
<!-- console_output -->
```bash
$ echo 123
1234
```
"""

toy_doc3 = """
Hello this is an other toy document.
<!-- console_output -->
```bash
$ echo 123
123
```
"""

class DocumentTestCase(unittest.TestCase):
    """
    This class tests the methods provided by the document class.
    """

    def test_parse(self):
        """
        Test whether the init correctly parses all operations with correct
        line numbers in the toy file. 
        """
        tmp = NamedTemporaryFile(delete=False)
        tmp.write(toy_doc.encode('utf8'))
        tmp.close()

        doc = Document(tmp.name, Markdown)

        self.assertEqual(len(doc.operations), 2)

        line, op = doc.operations[0]
        self.assertIsInstance(op, OpWrite)
        self.assertEqual(line, 20)

        line, op = doc.operations[1]
        self.assertIsInstance(op, OpConsoleOutput)
        self.assertEqual(line, 30)

        os.remove(tmp.name)

    def test_run(self):
        """
        Check that run() does no raise an exception on the toy file.
        """
        tmp = NamedTemporaryFile(delete=False)
        tmp.write(toy_doc.encode('utf8'))
        tmp.close()

        doc = Document(tmp.name, Markdown)

        fail, total = doc.run()
        self.assertEqual(fail, 0)
        self.assertEqual(total, 2)

        os.remove(tmp.name)


    def test_run_monitor_with_error(self):
        """
        Check that run() calls the monitor.
        """
        tmp = NamedTemporaryFile(delete=False)
        tmp.write(toy_doc2.encode('utf8'))
        tmp.close()

        monitor = Monitor(tmp.name)
        monitor.before_execute = MagicMock()
        monitor.log = MagicMock()
        monitor.after_execute = MagicMock()

        doc = Document(tmp.name, Markdown)

        fail, total = doc.run(monitor=monitor)
        self.assertEqual(fail, 1)
        self.assertEqual(total, 1)

        os.remove(tmp.name)


        self.assertEqual(monitor.before_execute.call_count, 1)
        self.assertEqual(monitor.before_execute.call_args[0][0], 3)
        self.assertIsInstance(monitor.before_execute.call_args[0][1],
            OpConsoleOutput)

        # first call with $ echo 123
        self.assertEqual(monitor.log.call_count, 2) 
        self.assertEqual(monitor.log.call_args[0][0], ["123"])

        self.assertEqual(monitor.after_execute.call_count, 1)
        self.assertIsInstance(monitor.after_execute.call_args[0][0], Exception)



    def test_run_monitor_wo_error(self):
        """
        Check that run() calls the monitor.
        """
        tmp = NamedTemporaryFile(delete=False)
        tmp.write(toy_doc3.encode('utf8'))
        tmp.close()

        monitor = Monitor(tmp.name)
        monitor.before_execute = MagicMock()
        monitor.log = MagicMock()
        monitor.after_execute = MagicMock()

        doc = Document(tmp.name, Markdown)

        fail, total = doc.run(monitor=monitor)
        self.assertEqual(fail, 0)
        self.assertEqual(total, 1)

        os.remove(tmp.name)

        self.assertEqual(monitor.before_execute.call_count, 1)
        self.assertEqual(monitor.before_execute.call_args[0][0], 3)
        self.assertIsInstance(monitor.before_execute.call_args[0][1],
            OpConsoleOutput)

        # first call with $ echo 123
        self.assertEqual(monitor.log.call_count, 2) 
        self.assertEqual(monitor.log.call_args[0][0], ["123"])

        self.assertEqual(monitor.after_execute.call_count, 1)
        self.assertEqual(monitor.after_execute.call_args[0], ())

