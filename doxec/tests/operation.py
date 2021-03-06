
import os
import unittest
import random
from tempfile import  NamedTemporaryFile

from doxec import Operation, OpWrite, OpAppend, OpConsole, OpConsoleOutput, \
    TestException

class ToyOperationA(Operation):
    """
    This toy operation is need for the unittests.
    """
    command = "op_a"
    def execute(self):
        pass

class ToyOperationB(Operation):
    """
    This toy operation is need for the unittests.
    """
    command = "op_b"
    def execute(self):
        pass

Operation.op_store.append(ToyOperationA)
Operation.op_store.append(ToyOperationB)

class OperationTestCase(unittest.TestCase):
    """
    Test case for the case class of all operations. The tests focus on the
    factory facility. The Operation factory should know about the two toy
    operations op_a and op_b.
    """

    def test_factory_op_a(self):
        """
        Test the factory when called with "op_a".
        """
        op_obj = Operation.factory("op_a", "args", "content")

        self.assertIsInstance(op_obj, ToyOperationA)
        self.assertEqual(op_obj.args, "args")
        self.assertEqual(op_obj.content, "content")

    def test_factory_op_b(self):
        """
        Test the factory when called with "op_b".
        """
        op_obj = Operation.factory("op_b", "args", "content")

        self.assertIsInstance(op_obj, ToyOperationB)
        self.assertEqual(op_obj.args, "args")
        self.assertEqual(op_obj.content, "content")

    def test_factory_unknown(self):
        """
        Test the factory when called with "op_c".
        """
        op_obj = Operation.factory("op_c", "args", "content")
        self.assertIsNone(op_obj)

    def test_factory_completeness(self):
        """
        Test that the factory knows all common operations.
        """
        op_obj = Operation.factory("write", "args", "content")
        self.assertIsNotNone(op_obj)

        op_obj = Operation.factory("append", "args", "content")
        self.assertIsNotNone(op_obj)

        op_obj = Operation.factory("console", "args", "content")
        self.assertIsNotNone(op_obj)

        op_obj = Operation.factory("console_output", "args", "content")
        self.assertIsNotNone(op_obj)


class OpWriteTestCase(unittest.TestCase):
    """
    Test the functionality of the write-operation. This test case focuses on
    the execute method.
    """

    def test_execute(self):
        """
        Create a write operation for a temporary file and check the file's
        contents after calling execute. 
        """
        tmp_file = NamedTemporaryFile(delete=False)
        tmp_path = tmp_file.name
        tmp_file.close()

        with open(tmp_path, "w") as f:
            print("this should be overwritten", file=f)
        
        write = OpWrite(tmp_path, ["Hello", "  World!"])
        write.execute()

        with open(tmp_path) as f:
            self.assertEqual(f.read(), "Hello\n  World!\n")
        
        os.remove(tmp_path)

    def test_str(self):
        """
        Test string representation.
        """
        op = OpWrite("/path/to/file", ["content", "lines"])
        self.assertEqual(str(op), "write(/path/to/file)")


class OpAppendTestCase(unittest.TestCase):
    """
    Test the functionality of the append-operation. This test case focuses on
    the execute method.
    """

    def test_execute(self):
        """
        Create two append operations for a temporary file and check the file's
        contents after calling execute. 
        """
        tmp_file = NamedTemporaryFile(delete=False)
        tmp_path = tmp_file.name
        tmp_file.close()
        
        append_1 = OpAppend(tmp_path, ["Hello"])
        append_2 = OpAppend(tmp_path, [" World", "!"])

        append_1.execute()
        append_2.execute()


        with open(tmp_path) as f:
            self.assertEqual(f.read(), "Hello\n World\n!\n")
        
        os.remove(tmp_path)

    def test_str(self):
        """
        Test string representation.
        """
        op = OpAppend("/path/to/file", ["content", "lines"])
        self.assertEqual(str(op), "append(/path/to/file)")

class OpConsoleTestCase(unittest.TestCase):
    """
    Test the functionality of the console-operation. This test case focuses on
    the execute method.
    """
    
    def test_execute_pass(self):
        """
        Create a OpConsole operation and check that no exception is raised,
        when the return code is zero.
        """
        tmp_file = NamedTemporaryFile(delete=False)
        tmp_path = tmp_file.name
        tmp_file.close()

        r = random.random()

        console = OpConsole(None, ['$ echo "%s" > %s' % (r, tmp_path)])
        console.execute()

        with open(tmp_path) as f:
            self.assertEqual(float(f.read()), r)

        os.remove(tmp_path)

    def test_execute_fail(self):
        """
        Create a OpConsole operation and check that an exception is raised,
        when the return code is non-zero.
        """
        console = OpConsole(None, ["$ exit 1"])
        self.assertRaises(TestException, console.execute)

    def test_execute_ignore(self):
        """
        Create a OpConsole operation and check that it ignores lines without
        $.
        """
        console = OpConsole(None, ["exit 1"])
        console.execute()

    def test_str(self):
        """
        Test string representation.
        """
        op = OpConsole(None, ["$ command", "ignore"])
        self.assertEqual(str(op), "console")

    def test_log(self):
        """
        Ensure that the console operation calls the log function, when output is
        produced.
        """
        passed_lines = []
        def log_function(lines):
            passed_lines.extend(lines)

        op = OpConsole(None, ["$ echo 'Hey\nYou!'", "$ echo 'Hello You!'"])
        op.execute(log_function)
        
        self.assertEqual(passed_lines,
            ["$ echo 'Hey\nYou!'", "Hey", "You!", "$ echo 'Hello You!'", "Hello You!"])
            

    def test_no_log(self):
        """
        Ensure that the console operation does not crash if the command
        produces output, but no log function is present.
        """
        op = OpConsole(None, ["$ echo 'Hey\nYou!'", "$ echo 'Hello You!'"])
        op.execute()


class OpConsoleOutputTestCase(unittest.TestCase):
    """
    Test the functionality of the console-output-operation. This test case focuses on
    the execute method.
    """
    
    def test_execute_pass(self):
        """
        Creates an OpConsoleOutput operation and checks that no exception is raised,
        when the expected output matches the actual output.
        """
        console = OpConsoleOutput(None,
            ["$ echo 'Hi'", "Hi", "$ echo 'Hello\n  World'", "Hello", "  World"])
        console.execute()

    def test_execute_fail(self):
        """
        Creates an OpConsoleOutput operation and checks that an exception is raised,
        when the expected output does not match the actual output.
        """
        console = OpConsoleOutput(None,
            ["$ echo 'Hi'", "Hi", "$ echo 'Hello\n  World'", "Hello", "Moon"])
        self.assertRaises(TestException, console.execute)

    def test_execute_leading_comments(self):
        """
        Creates an OpConsoleOutput operation and checks whether leading
        non-code lines are ignored.
        """
        console = OpConsoleOutput(None, ["heyho", "$ echo 'Hi'", "Hi"])
        console.execute()

    def test_str(self):
        """
        Test string representation.
        """
        op = OpConsoleOutput(None, ["$ command", "ignore"])
        self.assertEqual(str(op), "console_output")

    def test_log(self):
        """
        Ensure that the console_output operation calls the log function, when output is
        produced.
        """
        passed_lines = []
        def log_function(lines):
            passed_lines.extend(lines)

        block =["$ echo 'Hey\nYou!'", "Hey", "You!", "$ echo 'Hello You!'", "Hello You!"]
        op = OpConsoleOutput(None, block)
        op.execute(log_function)
        
        self.assertEqual(passed_lines, block)

    def test_no_log(self):
        """
        Ensure that the console operation does not crash if the command
        produces output, but no log function is present.
        """
        op = OpConsole(None, ["$ echo 'Hey\nYou!'", "$ echo 'Hello You!'"])
        op.execute()
