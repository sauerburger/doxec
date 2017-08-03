

Have you ever come across a tutorial or a documentation, which showed some
example code snippets, which turned out to contain bugs, or are not in-sync
with the most recent version of the software? I guess, everyone has, and this
is can be really frustrating. But how can you make sure that this won't happen
for tutorials or example you write? For python documentation inside the code,
doctest is doing its job very well. Tutorials on the other hand are usually
written in markdown, latex or similar languages. How can one ensure that the
code examples actually run?

The answer is __doxec__, a python library and a command line script,
which parses codes examples from a documentation or a tutorial and runs them.
This ensures that the code snippets work as intended.

[![build status](https://srv.sauerburger.com/esel/doxec/badges/master/build.svg)](https://srv.sauerburger.com/esel/doxec/commits/master)


# Installation
You can simply clone the repository and run the setup script to get doxec.

```bash
$ git clone https://srv.sauerburger.com/esel/doxec.git dexec_install
$ cd doxec_install
$ python3 setup.py install
```



# Usage

How to write code snippets in the documentation? You must adhere to a specific
syntax which depends on the markup language. The syntax is not intended to
interfere with the natural syntax of the markup language. The language
specific details are listed below.

When a file is parsed by the `doxec` script, it looks for magic tags and
creates what is called an operation based on the information inferred from the
magic tag. A magic tag consists of three parts: a command, content and optionally
arguments. The command specified how the content block should be executed. The
arguments can fine tune the execution. To give two examples, the 
'write' command creates (or overwrites) the file given as an argument with the
content block, or the 'console' command, executes each line in the content
block starting with `$` in a bash shell.

## Markdown

The syntax in Markdown consists of two parts: the command line and the content
block. The command line looks like a HTML comment.

```
<!-- COMMAND ARGS1 ARGS2 ... -->
```

The first word is treated as the command. Everything afterwards is considered
an argument. Arguments must not contain `>`. The trailing `-->` is not
required to be on the same line, i.e. the HTML comment can span multiple
lines.

Please note, that leading whitespaces before `<!--` are not allowed.

The line immediately after the command line must be the begin of a Markdown
code block. 

```
    ```bash
    $ echo "Hello World!"
    ```
```

The language indication, here `bash`, is ignored. Everything inside the code
block is taken as the content of the operation.

Please note the end of the block, i.e. the line with three backticks, must
consits of only three charaters. This means, trailing spaces, will make the
doxec ignore this operation.

Since `-->` can be on a different line, it is possible to wrap the comment
wround the whole code block, and thus execute an operation, which is not
visible to the user. This can be used to perform operations, which are
explained in a text, but should be executed as a script for testing.

### Example

A full example of a hello world tutorial (hello_world.md) can look like this. 
```markdown
    A mandatory step in learning a new teachnoly in computer science is to
    run 'hello world' example. Your first step in bash should be no exception.
    Open a bash shell and type everything after the `$` sign and hit return.
    The shell should greet you and everybody else in the world as shown in
    this example.
    <!-- console_output -->
    ```bash
    $ echo "Hello World!"
    Hello World!
    ```
```

To verify that this code snipped works as expected run
```bash
$ doxec hello_world.md
running console_output(None) ...
```
The *console_output* command runs the lines starting with `$` in a bash shell
and compares the output list below.

## CLI
The usage of the CLI is rather simple. The script takes any number of files,
which will be executed in order.

```bash
$ doxec file1 file2 file3 ...
```

Since the syntax of the of the magic tags depend on the markup language, you
can chose the parser class using the optional argument `--syntax`. Possible
values are listed in the auto generated help.

```bash
$ doxec --help
```

# Command reference

The following table summarizes the implemented commands.

| Command | Argument(s) | Action |
| ------- | ----------- | ------ |
| `write` | file name | Creates (overwrites) the given file and write the content to it. |
| `append` | file name | Append the content to the given file (or creates). |
| `console` | *none* | Run all lines starting with `$`. All other lines are ignores. This operation fails, if the return code of a command is non-zero. |
| `console_output` | *none* | Run all lines starting with `$`. All following lines without a leading `$`, are compared to the `stdout` of the command. This operation fails, if the outputs differ, of the return value is non-zero. |

# Trivia
In this early version I have not implemented some kind of meta-execution to
run doxec on this README file, so ironically the tutorial for doxec could be
out-of-sync with the actual code.
