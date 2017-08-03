
import unittest

from doxec import Operation

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



