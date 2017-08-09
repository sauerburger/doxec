
import unittest
from doxec import Markdown

class MarkdownSyntaxTestCase(unittest.TestCase):
    """
    Class to test the syntax parser implementation for markdown.
    """

    def test_parse_command_valid(self):
        """
        Run parse_command on a standard input and check the return value.
        """
        retval = Markdown.parse_command("<!-- WRITE hello_world.c -->")
        self.assertEqual(retval, ("WRITE", "hello_world.c"))

    def test_parse_command_valid_no_end(self):
        """
        Run parse_command on an input without the comment end `-->` and check
        the return value.
        """
        retval = Markdown.parse_command("<!-- WRITE hello_world.c")
        self.assertEqual(retval, ("WRITE", "hello_world.c"))

    def test_parse_command_whitespace(self):
        """
        Run parse_command on a valid input with whitespace added/removed in various
        places check the return value. Additional whitespace should be
        ignored, except at the beginning of the line. Missing whitespace
        should be invalid.
        """
        expectation = ("WRITE", "hello_world.c")

        # valid whitespace
        retval = Markdown.parse_command("<!-- WRITE hello_world.c -->")
        self.assertEqual(retval, expectation)

        retval = Markdown.parse_command("<!--   WRITE hello_world.c -->")
        self.assertEqual(retval, expectation)

        retval = Markdown.parse_command("<!--\tWRITE hello_world.c -->")
        self.assertEqual(retval, expectation)

        retval = Markdown.parse_command("<!-- WRITE   hello_world.c -->")
        self.assertEqual(retval, expectation)

        retval = Markdown.parse_command("<!-- WRITE hello_world.c     -->")
        self.assertEqual(retval, expectation)

        retval = Markdown.parse_command("<!-- WRITE hello_world.c -->  ")
        self.assertEqual(retval, expectation)

        retval = Markdown.parse_command("<!-- WRITE hello_world.c\r-->")
        self.assertEqual(retval, expectation)

        retval = Markdown.parse_command("<!--  WRITE  hello_world.c  -->  ")
        self.assertEqual(retval, expectation)

        # special case: space within argument, also valid
        retval = Markdown.parse_command("<!--  WRITE  hello  world c  -->  ")
        self.assertEqual(retval, ("WRITE", "hello  world c"))

        # special case: no argument, but valid
        retval = Markdown.parse_command("<!-- WRITEhello_world.c -->")
        self.assertEqual(retval, ("WRITEhello_world.c", None))

        # invalid whitespace
        retval = Markdown.parse_command("<!-- WRITE hello_world.c-->")
        self.assertIsNone(retval)

        retval = Markdown.parse_command("<!--WRITE hello_world.c -->")
        self.assertIsNone(retval)

        retval = Markdown.parse_command(" <!-- WRITE hello_world.c -->")
        self.assertIsNone(retval)

        retval = Markdown.parse_command("<! -- WRITE hello_world.c -->")
        self.assertIsNone(retval)

        # this is still invalid, since the args part must not contain '>'
        retval = Markdown.parse_command("<!-- WRITE hello_world.c - ->")
        self.assertIsNone(retval)

    def test_parse_command_invalid(self):
        """
        Run parse_command on an input with missing characters, i.e. invalid
        input, and expect that the return valid is None.
        """
        retval = Markdown.parse_command("<-- WRITE hello_world.c -->")
        self.assertIsNone(retval)

        retval = Markdown.parse_command("!-- WRITE hello_world.c -->")
        self.assertIsNone(retval)

        retval = Markdown.parse_command("WRITE hello_world.c")
        self.assertIsNone(retval)

        retval = Markdown.parse_command("<!-- -->")
        self.assertIsNone(retval)

        retval = Markdown.parse_command("<!--   -->")
        self.assertIsNone(retval)

    def test_parse_command_trailing_chars(self):
        """
        Run parse_command on an input with trailing characters. This should be
        illegal.
        """
        retval = Markdown.parse_command("<!-- WRITE hello_world.c --> oops")
        self.assertIsNone(retval)

    def test_parse_code_valid(self):
        """
        Run parse_command on a standard input and check that the return valid
        contains the specified block of code. The example should remove all
        lines from the input.
        """
        block = []
        block.append("```bash")
        block.append("whoami")
        block.append("ls ~")
        block.append("```")
        retval = Markdown.parse_code(block)
        self.assertEqual(len(retval), 2)
        self.assertEqual(retval[0], "whoami")
        self.assertEqual(retval[1], "ls ~")

        self.assertEqual(block, [])

    def test_parse_code_valid_python(self):
        """
        Run parse_command on an input with a different language indication and
        check that the return valid contains the specified block of code.
        """
        block = []
        block.append("```python")
        block.append("print(3)")
        block.append("```")
        retval = Markdown.parse_code(block)
        self.assertEqual(retval, ["print(3)"])

    def test_parse_code_valid_unnamed(self):
        """
        Run parse_command on an input without language indication and
        check that the return valid contains the specified block of code.
        """
        block = []
        block.append("```")
        block.append("void main() {};")
        block.append("```")
        retval = Markdown.parse_code(block)
        self.assertEqual(retval, ["void main() {};"])

    def test_parse_code_empty(self):
        """
        Run parse_command on an empty code block. The return value should be
        an empty list.
        """
        block = []
        block.append("```root")
        block.append("```")
        retval = Markdown.parse_code(block)
        self.assertEqual(retval, [])

    def test_parse_code_trailing_lines(self):
        """
        Run parse_command on input with trailing lines. Check that the
        trailing list is not in the output and all other lines have been
        removed from the input.
        """
        block = []
        block.append("```shell")
        block.append("touch /tmp")
        block.append("touch /home")
        block.append("```")
        block.append("This should not cause a crash.") 
        
        retval = Markdown.parse_code(block)
        self.assertEqual(retval, ["touch /tmp", "touch /home"])

        self.assertEqual(block, ["This should not cause a crash."])

    def test_parse_code_leading_lines(self):
        """
        Run parse_command on input with leading lines and check that parsing
        failed.
        """
        block = []
        block.append("This is a leading line.")
        block.append("```shell")
        block.append("touch /tmp")
        block.append("touch /home")
        block.append("```")
        
        retval = Markdown.parse_code(block)
        self.assertIsNone(retval)
        self.assertEqual(block, [])

    def test_parse_code_missing_start(self):
        """
        Run parse_command on input without the block start and check that
        parsing failed.
        """
        block = []
        block.append("touch /tmp")
        block.append("touch /home")
        block.append("```")
        
        retval = Markdown.parse_code(block)
        self.assertIsNone(retval)
        self.assertEqual(block, ['touch /tmp', 'touch /home', '```'])

    def test_parse_code_missing_end(self):
        """
        Run parse_command on input without the block end and check that
        parsing failed.
        """
        block = []
        block.append("```shell")
        block.append("touch /tmp")
        block.append("touch /home")
        
        retval = Markdown.parse_code(block)
        self.assertIsNone(retval)
        self.assertEqual(block, [])


    def test_parse_code_leading_lines(self):
        """
        Run parse_command on input with leading lines and check that parsing
        failed. The parse method should not remove any lines in this case.
        """
        block = []
        block.append("This is a leading line.")
        block.append("```shell")
        block.append("touch /tmp")
        block.append("touch /home")
        block.append("```")

        
        retval = Markdown.parse_code(block)
        self.assertIsNone(retval)

        self.assertEqual(len(block), 5)

    def test_parse_valid(self):
        """
        Check that a simple example runs and returns args, command and
        content.
        """
        doc = []
        doc.append("<!-- APPEND /dev/null -->")
        doc.append("```shell")
        doc.append("touch /tmp")
        doc.append("touch /home")
        doc.append("```")

        retval = Markdown.parse(doc)
        self.assertEqual(len(retval), 4)
        command, args, content, length = retval
        self.assertEqual(command, "APPEND")
        self.assertEqual(args, "/dev/null")
        self.assertEqual(content, ["touch /tmp", "touch /home"])
        self.assertEqual(length, 5)

    def test_parse_valid_additional_lines(self):
        """
        Check that an example with unrelated lines runs and returns args,
        command and content. The inital list of lines should be modified and
        is expected to contain only the tailing lines.
        """
        doc = []
        doc.append("Yeeharr, this is an example.")
        doc.append("<!-- APPEND /dev/null -->")
        doc.append("```shell")
        doc.append("touch /tmp")
        doc.append("touch /home")
        doc.append("```")
        doc.append("This caused a seg fault?")

        retval = Markdown.parse(doc)
        self.assertEqual(len(retval), 4)
        command, args, content, length = retval
        self.assertEqual(command, "APPEND")
        self.assertEqual(args, "/dev/null")
        self.assertEqual(content, ["touch /tmp", "touch /home"])
        self.assertEqual(length, 5)
        self.assertEqual(doc, ["This caused a seg fault?"])


    def test_parse_invalid_middle_line(self):
        """
        Check that an example with a separation line between command and code
        fails. The violating line should stay in the original document.
        """
        doc = []
        doc.append("<!-- APPEND /dev/null -->")
        doc.append("This caused a seg fault?")

        retval = Markdown.parse(doc)
        self.assertIsNone(retval)
        self.assertEqual(doc, [])  # lines are eaten in the second round

    def test_parse_empty_input(self):
        """
        Check that an empty example fails.
        """
        retval = Markdown.parse([])
        self.assertIsNone(retval)

    def test_parse_no_tag(self):
        """
        Check that an example without any tags fails. This sould consume all
        lines.
        """
        doc = []
        doc.append("Yeeharr, this is an example.")
        doc.append("```shell")
        doc.append("touch /tmp")
        doc.append("touch /home")
        doc.append("```")
        doc.append("This caused a seg fault?")

        retval = Markdown.parse([])
        self.assertIsNone(retval)
