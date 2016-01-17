====
grin
====

I wrote grin to help me search directories full of source code. The venerable
GNU grep_ and find_ are great tools, but they fall just a little short for my
normal use cases.

The main problem I had with GNU grep_ is that I had no way to exclude certain
directories that I knew had nothing of interest for me, like .svn/, CVS/ and
build/. The results from those directories obscured the results I was actually
interested in. There are tools like ack_, which skip these directories, but ack_
also only grepped files with extensions that it knew about. Furthermore, it had
not implemented the context lines feature, which I had grown accustomed to.
Recent development has added these features, but I had already released grin by
the time I found out.

One can construct a GNU find_ command that will exclude .svn/ and the rest, but
the only reliable way I am aware of runs grep_ on each file independently. The
startup cost of invoking many separate grep_ processes is relatively large.

Also, I was bored. It seems to be catching. Perl has ack_, Ruby has rak_, and
now Python has grin.

I wrote grin to get exactly the features I wanted:

  * Recurse directories by default.
  * Do not go into directories with specified names.
  * Do not search files with specified extensions.
  * Be able to show context lines before and after matched lines.
  * Python regex syntax (one can quibble as to whether this is a feature or my
    laziness for using the regex library provided with my implementation
    language, but as a Python programmer, this is the syntax I am most familiar
    with).
  * Unless suppressed via a command line option, display the filename regardless
    of the number of files.
  * Accept a file (or stdin) with a list of newline-separated filenames. This
    allows one to use find_ to feed grin a list of filenames which might have
    embedded spaces quite easily.
  * Grep through gzipped text files.
  * Be useful as a library to build custom tools quickly.

I have also exposed the directory recursion logic as the command-line tool
"grind" in homage to find_. It will recurse through directories matching a glob
pattern to file names and printing out the matches. It shares the directory and
file extension skipping settings that grin uses.

For configuration, you can specify the environment variables GRIN_ARGS and
GRIND_ARGS. These should just contain command-line options of their respective
programs. These will be prepended to the command-line arguments actually given.
Options given later will override options given earlier, so all options
explicitly in the command-line will override those in the environment variable.
For example, if I want to default to two lines of context and no skipped
directories, I would have this line in my bashrc::

    export GRIN_ARGS="-C 2 --no-skip-dirs"

.. _grep : http://www.gnu.org/software/grep/
.. _ack : http://search.cpan.org/~petdance/ack/ack
.. _rak: http://rak.rubyforge.org/
.. _find : http://www.gnu.org/software/findutils/


Installation
------------

Install using pip_::

  $ pip install grin

Running the unittests requires the nose_ framework::

  $ pip install nose
  ...
  $ nosetests 
  .........................
  ----------------------------------------------------------------------
  Ran 25 tests in 0.192s

  OK
  $ python setup.py test   # The other way to run the tests.
  running test
  ... etc.

The development sources are hosted on Github:

  https://github.com/rkern/grin

There is one little tweak to the installation that you may want to consider. By
default, setuptools installs scripts indirectly; the scripts installed to
$prefix/bin or Python2x\Scripts use setuptools' pkg_resources module to load
the exact version of grin egg that installed the script, then runs the script's
main() function. This is not usually a bad feature, but it can add substantial
startup overhead for a small command-line utility like grin. If you want the
response of grin to be snappier, I recommend installing custom scripts that just
import the grin module and run the appropriate main() function. See the files
examples/grin and examples/grind for examples.

.. _pip : https://pip.pypa.io/en/stable/
.. _nose : https://nose.readthedocs.org/en/latest/


Using grin
----------

To recursively search the current directory for a regex::

  $ grin some_regex

To search an explicit set of files::

  $ grin some_regex file1.txt path/to/file2.txt

To recursively search an explicit set of directories::

  $ grin some_regex dir1/ dir2/

To search data piped to stdin::

  $ cat somefile | grin some_regex -

To make the regex case-insensitive::

  $ grin -i some_regex

To output 2 lines of context before, after, or both before and after the
matches::

  $ grin -B 2 some_regex
  $ grin -A 2 some_regex
  $ grin -C 2 some_regex

To only search Python .py files::

  $ grin -I "*.py" some_regex

To suppress the line numbers which are printed by default::

  $ grin -N some_regex

To just show the names of the files that contain matches rather than the matches
themselves::

  $ grin -l some_regex

To suppress the use of color highlighting::

  # Note that grin does its best to only use color when it detects that it is
  # outputting to a real terminal. If the output is being piped to a file or
  # a pager, then no color will be used.
  $ grin --no-color some_regex

To force the use of color highlighting when piping the output to something that
is capable of understanding ANSI color escapes::

  $ grin --force-color some_regex | less -R

To avoid recursing into directories named either CVS or RCS::

  $ grin -d CVS,RCS some_regex

By default grin skips a large number of files. To suppress all of this behavior
and search everything::

  $ grin -sbSDE some_regex

To search for files newer than some_file.txt::

  # If no subdirectory or file in the list contains whitespace:
  $ grin some_regex `find . -newer some_file.txt`

  # If a subdirectory or file in the list may contain whitespace:
  $ find . -newer some_file.txt | grin -f - some_regex


Using grind
-----------

To find files matching the glob "foo*.py" in this directory or any subdirectory
using same the default rules as grin::

  $ grind "foo*.py"

To suppress all of the default rules and not skip any files or directories while
searching::

  $ grind -sbSDE "foo*.py"

To find all files that are not skipped by the default rules::

  $ grind

To start the search in a particular set of directories instead of the current
one (not the -- separator)::

  $ grind --dirs thisdir that/dir -- "foo*.py"


Using grin as a Library
-----------------------

One of the goals I had when writing grin was to be able to use it as a library
to write custom tools. You can see one example that I quickly hacked up in 
examples/grinimports.py . It reuses almost all of grin's infrastructure, except
that it preprocesses Python files to extract and normalize just the import
statements. This lets you conveniently and robustly search for import
statements. Look at "grinimports.py --help" for more information.

examples/grinpython.py allows you to search through Python files and specify whether you want to search through actual Python code, comments or string literals in any combination. For example::

    $ grinpython.py -i --strings grep grin.py
    grin.py:
      188 :     """ Grep a single file for a regex by iterating over the lines in a file.
      292 :         """ Do a full grep.
    ...

    $ grinpython.py -i --comments grep grin.py
    grin.py:
      979 :     # something we want to grep.

    $ grinpython.py -i --python-code grep grin.py
    grin.py:
      187 : class GrepText(object):
      291 :     def do_grep(self, fp):
    ...

Similarly, it should be straightforward to write small tools like this which
extract and search text metadata from binary files.


To Do
-----

* Figure out the story for grepping UTF-8, UTF-16 and UTF-32 Unicode text files.

* Python 3


Bugs and Such
-------------

Please make a new issue at the Github issue tracker.

  https://github.com/rkern/grin
