
import abc
import re
import subprocess

__version__ = "0.1.1"

class TestException(Exception):
    """
    This exception should be raised, if an operation performed tests and one
    of these tests fails.
    """
    pass
    

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
        with open(self.args, "w") as f:
            for line in self.content:
                print(line, file=f)

class OpAppend(Operation):
    """
    This operation performs a 'append to file' operation.
    """
    command = "append"

    def execute(self):
        with open(self.args, "a") as f:
            for line in self.content:
                print(line, file=f)

class OpConsole(Operation):
    """
    This operation runs all lines starting with $ in the console. The
    operation raises an error, if the return code is not zero.
    """
    command = "console"

    def execute(self):
        job = subprocess.Popen("/bin/bash", stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        script = "\n".join([l[1:] for l in self.content if l.startswith("$")])
        (stdoutdata, stderrdata) = job.communicate(script.encode('utf8'))
        if job.returncode != 0:
            raise TestException("Script failed with %d:" % job.returncode,
                stdoutdata.decode('utf8'), stderrdata.decode('utf8'))
        return stdoutdata
                


class OpConsoleOutput(Operation):
    """
    This operation runs all lines starting with $ in the console and expects
    the output written after that.
    """
    command = "console_output"

    def execute(self):
        commands = []  # items are (command, [output lines])
        for line in self.content:
            if line.startswith("$"):
                commands.append((line[1:], []))
            elif len(commands) == 0:
                # no command yet
                continue
            else:
                commands[-1][1].append(line)

        for command, lines in commands:
            job = subprocess.Popen("/bin/bash", stdin=subprocess.PIPE,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            (stdoutdata, stderrdata) = job.communicate(command.encode('utf8'))
            if job.returncode != 0:
                raise TestException("Script failed with %d:" % job.returncode,
                    stdoutdata.decode('utf8'), stderrdata.decode('utf8'))
            output = stdoutdata.decode('utf8')
            output = re.split(r'\r?\n', output)
            if len(output) > 0 and output[-1] == '':
                del output[-1] 
            if lines != output:
                raise TestException("Output differs", lines, output)
       

# add operations to op_store
Operation.op_store.append(OpConsole)
Operation.op_store.append(OpConsoleOutput)
Operation.op_store.append(OpAppend)
Operation.op_store.append(OpWrite)

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
        while len(lines) > 0:
            cmd = Markdown.parse_command(lines[0])
            del lines[0]
            if cmd is not None:
                code = Markdown.parse_code(lines)
                if code is not None:
                    return cmd[0], cmd[1], code

        return None
                    

    @staticmethod
    def parse_command(line):
        """
        Helper method to parse the command line of the following syntax.

        <!-- COMMAND ARGS -->

        The args part must not contain the greater than '>" character. The
        trailing '-->' is optional.
        None is returned, if the format does not match. If a valid line is
        found, the tuple (command, args) is returned. 

        >>> Markdown.parse_command("<!-- write file.txt -->")
        ('write', 'file.txt')

        >>> Markdown.parse_command("<!-- write file.txt")
        ('write', 'file.txt')

        >>> Markdown.parse_command("-- invalid line -->") is None
        True
        """
        match = re.match(r"<!--\s+([^> \t\n\r\f\v][^>]*)(\s+-->)?\s*$", line)
        if match is None:
            return None

        token = re.split("\s+", match.group(1).strip(), maxsplit=1)
        if len(token) == 2:
            return tuple(token)
        else:
            return token[0], None

    @staticmethod
    def parse_code(lines):
        """
        Expects the beginning of a code block, removes all lines which belong
        to the code block.
        
        Returns the content of this code block as a list of lines, returns
        None if an error.
        occurs.
        >>> lines = []
        >>> lines.append("```bash")
        >>> lines.append("$ whoami")
        >>> lines.append("$ ls")
        >>> lines.append("```")
        >>> lines.append("lalala")
        >>> Markdown.parse_code(lines)
        ['$ whoami', '$ ls']
        >>> lines
        ['lalala']
        """
        if len(lines) == 0:
            return None

        head = lines[0]
        match = re.match(r"```.*$", head)
        if match is None:
            return None

        del lines[0]  # delete start

        buf  = []
        while len(lines) > 0:
            # found end?
            if lines[0] == "```":
                del lines[0]
                return buf
                
            # eat lines and add them to the buffer
            buf.append(lines[0])
            del lines[0]
        
        # there was no end
        return None

parser = {
    "markdown": Markdown
}

class Document:
    """
    The document class represents a single file containing documentation. Upon
    creation, the document is parsed. Code examples and operations are
    identified by their magic tags. The examples and the operations are stored
    inside the document object. When the run() method is called, all the
    operations within the object are executed.
    """

    def __init__(self, document_path, syntax=Markdown):
        """
        Creates a new document object and parses the given document.
        """
        self.operations = []
        with open(document_path) as f:
            self.parse(f.read(), syntax)

    def parse(self, string, syntax):
        """
        Parses the content string and appends all operations defined in the
        string to the internal storage.
        """
        lines = re.split("\r?\n", string)
        while len(lines) > 0:
            op_tuple = syntax.parse(lines)
            if op_tuple is None:
                continue
            op_obj = Operation.factory(*op_tuple)
            if op_obj is None:
                continue
            self.operations.append(op_obj)


    def run(self, monitor=None):
        """
        Runs all operations stored attached to this object. The monitor object
        is called after every iteration. The first argument of monitor is the
        operation object, the second argument is None or the exception that
        occurred.

        The method returns True on success.
        """
        success = True
        for op in self.operations:
            try:
                op.execute()
            except TestException as e:
                success = False
                if callable(monitor):
                    monitor(op, e)
                else:
                    raise e
            else:
                if callable(monitor):
                    monitor(op, None)
        return success
