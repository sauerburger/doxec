
import abc

class Operation(metaclass=abc.ABCMeta):
    """
    This class represents a single task defined in a documentation, such as
    'create a file' or 'run a command'. Each operation is implemented by a sub
    class.
    """
    op_store = []

    def __init__(self, args, content):
        """
        Creates an operation. The args argument is the token after the
        operation key word, content is the markdown block after the operation
        line.
        """
        self.args = args
        self.content = content

    @classmethod
    def create(cls, command, args, content):
        """
        Checks whether this class is responsible for handling the command
        'command'. If so, this class returns an object of type Operation. If
        the command is unknown, None is returned.
        """
        if command == cls.command:
            return cls(args, content)
   
    @abc.abstractmethod
    def execute(self):
        """
        Performs the operation represented by this object.
        """
        pass


    @staticmethod
    def factory(command, args, content):
        """
        Similar to create, but it will look over Operation.op_store and call
        create on each item.
        """
        for op_cls in Operation.op_store:
            op = op_cls.create(command, args, content)
            if op is not None:
                return op

class OpWrite(Operation):
    """
    This operation performs a 'write to file' operation.
    """
    command = "write"

    def execute(self):
        pass

# add write operation to op_store
Operation.op_store.append(OpWrite)

class OpConsoleOutput(Operation):
    """
    This operation runs all lines starting with $ in the console and expects
    the output written after that.
    """
    command = "console_output"

    def executed(self):
        pass

# add write operation to op_store
Operation.op_store.append(OpConsoleOutput)

class DoxecSyntax(metaclass=abc.ABCMeta):
    """
    This class defines the rules and implements the syntax of the magic
    commands, to be used in the documentation. Depending on the language (e.g.
    Markdown or latex) a different subclass of the syntax rules has to be
    used.
    """

    @staticmethod
    @abc.abstractmethod
    def parse(lines):
        """
        Reads everything from the given list of lines until a valid magic tag
        is found. The method the extracts the command name, its argument and
        the command content. These parts are also removed from the line list.
        The method modifies the list in place.

        The return value is a triplet of (command, argument, content). None is
        returned, if no valid magic tag could be found. The content item is a
        list of code lines.
        """
        pass

class Markdown(DoxecSyntax):
    """
    This class implements the syntax rules for a markdown document. A valid
    magic tag consists of a command line immediately followed by a markdown
    code block.
    
    <!-- COMMAND ARGS -->
    ```python
    CONTENT
    ```

    Instead of python, any language indication can be used, this property is
    stripped from the content. Please note, there must not be a new line
    between the command line and the content block.
    """

    @staticmethod
    def parse(lines):
        """
        See DoxecSyntax.
        """
        pass

    @staticmethod
    def parse_command(line):
        """
        Helper method to parse the command line of the following syntax.

        <!-- COMMAND ARGS -->

        None is returned, if the format does not match. If a valid line is
        found, the tuple (command, args) is returned. 

        >>> Markdown.parse_command("<!-- write file.txt -->")
        ('write', 'file.txt')

        >>> Markdown.parse_command("<!-- invalid line ")
        None
        """
        pass

    @staticmethod
    def parse_code(lines):
        """
        Expects the beginning of a code block, removes all lines which belong
        to the code block.
        
        Returns the content of this code block as a list of lines, returns
        None if an error.
        occurs.
        >>> lines = []
        >>> lines += "```bash"
        >>> lines += "$ whoami"
        >>> lines += "$ ls"
        >>> lines += "```"
        >>> Markdown.parse_code(lines)
        ["$ whoami", "$ ls"]
        """
        pass


class Document:
    """
    The document class represents a single file containing documentation. Upon
    creation, the document is parsed. Code examples and operations are
    identified by their magic tags. The examples and the operations are stored
    inside the document object. When the run() method is called, all the
    operations within the object are executed.
    """

    def __init__(self, document_path):
        """
        Creates a new document object and parses the given document.
        """
        self.operations = []
        pass

    def parse(self, string):
        """
        Parses the content string and appends all operations defined in the
        string to the internal storage.
        """
        pass
