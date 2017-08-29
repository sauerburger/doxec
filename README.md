Have you ever come across a tutorial or a documentation, which showed some
example code snippets, which turned out to contain bugs, or are not in-sync
with the most recent version of the software? I guess, everyone has, and it
can be really frustrating. But how can you make sure that this won't happen
for tutorials or example you write? For python documentation inside the code,
doctest is doing its job very well. Tutorials on the other hand are usually
written in markdown, latex or similar languages. How can you ensure that the
code examples actually run?

The answer is __doxec__, a python library and a command line script,
which parses codes examples from a documentation or a tutorial and runs them.
This ensures that the code snippets work as intended.


# Installation [![build status](https://srv.sauerburger.com/esel/doxec/badges/master/build.svg)](https://srv.sauerburger.com/esel/doxec/commits/master)

You can simply clone the repository and run the setup script to get doxec.


<!-- console -->
```bash
$ git clone https://srv.sauerburger.com/frank/doxec.git doxec_install
$ cd doxec_install && python3 setup.py install
```

# Usage

How to write code snippets in the documentation? You must adhere to a specific
syntax which depends on the markup language used in the documentation. The
syntax is intended to not
interfere with the natural syntax of the markup language. The language
specific details are listed below.

When a file is parsed by the `doxec` script, it looks for magic tags and
creates what is called an operation based on the information inferred from the
magic tag. A magic tag consists of three parts: a command, content and optionally
arguments. The command specifies how the content block should be executed. The
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

Please note, that leading white spaces before `<!--` are not allowed.

The line immediately after the command line must be the beginning of a Markdown
code block. 

<pre>
```bash
$ echo "Hello World!"
```
</pre>

The language indication, here `bash`, is ignored. Everything inside the code
block is taken as the content of the operation.

Please note the end of the block, i.e. the line with three backticks, must
consists of only three characters. This means, trailing spaces, will make the
doxec ignore this operation.

Since `-->` can be on a different line, it is possible to wrap the comment
around the whole code block, and thus execute an operation, which is not
visible to the user. This can be used to perform operations, which are
explained in a text, but should be executed as a script for testing.

Since version 0.3.0, there exists an alternative syntax. The new syntax
accepts `<pre>` and `</pre>` as code block delimiters.

### Example

A full example of a imaginary bash tutorial (hello_world.md) can look like this. 

<!-- write hello_world.md -->
<pre>
A mandatory step in learning a new technology in computer science is to
run a 'hello world' example. Your first step in bash should be no exception.
Open a bash shell and type everything after the `$` sign and hit return.
The shell should greet you and everybody else in the world as shown in
this example.
&lt;!-- console_output --&gt;
```bash
$ echo "Hello World!"
Hello World!
```
</pre>

<!-- console
```
$ recode html..ascii hello_world.md
```
-->

To verify that the code snipped in this tutorial works as expected run
<!-- console_output -->
```bash
$ doxec hello_world.md
Doxec -- Copyright (c) 2017 Frank Sauerburger
/home/esel/rpriv/doxec/hello_world.md:6     console_output ... 
--- $ echo "Hello World!"
--- Hello World!
/home/esel/rpriv/doxec/hello_world.md:6     console_output ... done
--------------------------------------------------------------------------------
Failed:     0
Total:      1
```

The *console_output* command runs the lines starting with `$` in a bash shell
and compares the output list below.

## Command Line Interface
The usage of the command line interface is rather simple. The script takes any number of files,
which will be executed in the given order.

```bash
$ doxec file1 file2 file3 ...
```

Since the syntax of the magic tags depend on the markup language, you
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
| `append` | file name | Append the content to the given file (or creates it). |
| `console` | *none* | Run all lines starting with `$`. All other lines are ignored. This operation fails, if the return value of a command is non-zero. |
| `console_output` | *none* | Run all lines starting with `$`. All following lines without a leading `$`, are compared to the `stdout` of the previous command. This operation fails, if the outputs differ, or the return value is non-zero. |

