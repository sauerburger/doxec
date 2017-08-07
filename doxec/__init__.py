
import abc
import re
import os
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

    def __init__(self, args, content, line=None):
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
    def execute(self, log=None):
        """
        Performs the operation represented by this object. The optional
        function is called, when the operation produces output. A list of
        lines is passed to the log function. The log function might be called
        multiple times.

        An exception is thrown, when the method encounters problems, or a test
        fails.
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

    def execute(self, log=None):
        with open(self.args, "w") as f:
            for line in self.content:
                print(line, file=f)

    def __str__(self):
        return "%s(%s)" % (self.command, self.args)

class OpAppend(Operation):
    """
    This operation performs a 'append to file' operation.
    """
    command = "append"

    def execute(self, log=None):
        with open(self.args, "a") as f:
            for line in self.content:
                print(line, file=f)

    def __str__(self):
        return "%s(%s)" % (self.command, self.args)

class OpConsole(Operation):
    """
    This operation runs all lines starting with $ in the console. All other
    lines are ignored. The operation raises an error, if the return code is
    not zero.
    """
    command = "console"

    def execute(self, log=None):
        if log is None:
            log = lambda x: None

        script = [l[1:].lstrip() for l in self.content if l.startswith("$")]
        for command in script:
            log(["$ %s" % command])
            job = subprocess.Popen("/bin/bash", stdin=subprocess.PIPE,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            (stdoutdata, stderrdata) = job.communicate(command.encode('utf8'))
            output = stdoutdata.decode('utf8')
            output = re.split(r'\r?\n', output)
            if len(output) > 0 and output[-1] == '':
                del output[-1] 
            log(output)
            if job.returncode != 0:
                raise TestException("Script failed with return code %d:" % job.returncode,
                    stdoutdata.decode('utf8'), stderrdata.decode('utf8'))
                
    def __str__(self):
        return "%s" % self.command


class OpConsoleOutput(Operation):
    """
    This operation runs all lines starting with $ in the console and expects
    the output written after that.
    """
    command = "console_output"

    def execute(self, log=None):
        if log is None:
            log = lambda x: None

        commands = []  # items are (command, [output lines])
        for line in self.content:
            if line.startswith("$"):
                commands.append((line[1:].lstrip(), []))
            elif len(commands) == 0:
                # no command yet
                continue
            else:
                commands[-1][1].append(line)

        for command, lines in commands:
            log(["$ %s" % command])
            job = subprocess.Popen("/bin/bash", stdin=subprocess.PIPE,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            (stdoutdata, stderrdata) = job.communicate(command.encode('utf8'))
            if job.returncode != 0:
                raise TestException("Script failed with return code %d:" % job.returncode,
                    stdoutdata.decode('utf8'), stderrdata.decode('utf8'))
            output = stdoutdata.decode('utf8')
            output = re.split(r'\r?\n', output)
            if len(output) > 0 and output[-1] == '':
                del output[-1] 
            log(output)
            if lines != output:
                first_offending = None
                for l, o in zip(lines, output):
                    if l != o:
                        first_offending = "First mismatch: %s != %s " % (repr(l), repr(o))
                        break
                raise TestException("Output differs", first_offending,
                "Expected: %s" % repr(lines), "Actual: %s" % repr(output))
       
    def __str__(self):
        return "%s" % self.command

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

        The return value is a tuple of (command, argument, content, length).
        None is returned, if no valid magic tag could be found. The content
        item is a list of code lines. The length is the number of lines, which
        belong to this operation.
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
            start_line_count = len(lines)
            cmd = Markdown.parse_command(lines[0])
            del lines[0]
            if cmd is not None:
                code = Markdown.parse_code(lines)
                if code is not None:
                    end_line_count = len(lines)
                    length = start_line_count - end_line_count
                    return cmd[0], cmd[1], code, length

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

    def __init__(self, document_path, syntax):
        """
        Creates a new document object and parses the given document.
        Parses the given file and appends all operations defined in the
        string to the internal storage. The syntax class is used to parse the
        file.
        """
        self.operations = []  # each item is a tuple of (line, operation)
        with open(document_path) as f:
            lines = re.split("\r?\n", f.read())
            line_count = len(lines)
            while len(lines) > 0:
                op_tuple = syntax.parse(lines)
                if op_tuple is None:
                    continue
                command, args, content, length = op_tuple
                op_obj = Operation.factory(command, args, content)
                if op_obj is None:
                    continue
                line_number = line_count - len(lines) + 1 - length
                self.operations.append((line_number, op_obj))


    def run(self, monitor=None):
        """
        Runs all operations stored attached to this object. The monitor object
        is might be called before, during and after the execution of each
        operation.

        The method returns a tuple with the number of failed operations and
        the total number of operations.
        """
        fail_count = 0
        total_operations = 0

        # set defaults
        before_method = lambda l, o: None
        log_method = lambda ls: None
        after_method = lambda e=None: None

        # overwrite defaults if monitor is given
        if monitor is not None and isinstance(monitor, Monitor):
            before_method = monitor.before_execute
            log_method = monitor.log
            after_method = monitor.after_execute

        for line, op in self.operations:
            before_method(line, op)
            total_operations += 1
            try:
                 op.execute(log=log_method)
            except TestException as e:
                after_method(e)
                fail_count += 1
            else:
                after_method()

        return (fail_count, total_operations)


class Monitor(metaclass=abc.ABCMeta):
    """
    This class is the default monitor which displays the results of
    Document.run in a user friendly way. The monitor object also keeps track
    of a fail and total counter.
    """

    def __init__(self, path, short=False):
        """
        Initializes the monitor. A new monitor should be used for each file.
        The short argument, defines whether the standard output of operations
        should be displayed.
        """

        self.full_path = os.path.abspath(path)
        self.short = short

        self.first_line = False

        self.fail_count = 0
        self.total_count = 0

    def before_execute(self, line, operation):
        """
        This method is should before the operations execute method is called.
        This method set the internal values and caches the lines and the
        operation.
        """
        print("\033[2K\033[0G\033[33m%s:%-5d %s ... \033[39;49m" % (self.full_path, line, operation), end="")
        self.pending_line_break = True
        self.line = line
        self.operation = operation

    def after_execute(self, error=None):
        """
        This method should be called after the operations execute method is
        called The optional parameter error is an exception, if one occurred
        during execution. This method uses the cached values for line and
        operation provided to before_execute.
        """
        self.total_count += 1
        if error is None:
            print("\033[2K\033[0G\033[32m%s:%-5d %s ... done\033[39;49m" % (self.full_path, self.line, self.operation))
        else:
            self.fail_count += 1
            if self.pending_line_break:
                print()
                self.pending_line_break = False

            if error.args is not None:
                args = error.args
            else:
                args = [str(error)]
            for error_line in args:
                print("\033[31m%s" % str(error_line))
            print("\033[31m%s:%-5d %s ... failed\033[39;49m" % (self.full_path, self.line, self.operation))

    def log(self, lines):
        """
        This method should be called during the execution of a method. This
        method can be called multiple times, or not at all. The given lines
        should be printed to the terminal. This method might uses the cached
        values for line and operation provided to before_execute.
        """
        if self.short:
            return

        if self.pending_line_break:
            print()
            self.pending_line_break = False

        for line in lines:
            print("--- %s" % line)
                
