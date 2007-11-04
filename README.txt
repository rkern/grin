I wrote grin to help me search directories full of source code. The venerable
GNU grep_ and find_ are great tools, but they fall just a little short for my
normal use cases.

The main problem I had with GNU grep_ is that I had no way to exclude certain
directories that I knew had nothing of interest for me, like .svn/, CVS/ and
build/. The results from those directories obscured the results I was actually
interested in. There are tools like ack_, which skip these directories, but ack_
also only grepped files with extensions that it knew about. Furthermore, it had
not implemented the context lines feature, which I had grown accustomed to.

One can construct a GNU find_ command that will exclude .svn/ and the rest, but
the only way I am aware of runs grep_ on each file independently. The startup
cost of invoking many separate grep_ processes is relatively large. Also, I have
not found a way to get grep_ to print out the name of the file it is searching
when it is only given one filename.

Thus, I wrote grin to get the features I wanted:

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

I have also exposed the directory recursion logic as the command-line tool
"grind" in homage to find_. It will recurse through directories matching a glob
pattern to file names and printing out the matches. It shares the directory and
file extension skipping settings that grin uses.

I've decided to punt on configuration for the moment. I wanted to use
ConfigObj_, but I found that importing it added a fair bit of startup time that
I found unacceptable for this use. Instead, to configure grin, I recommend
writing your own script that uses grin.py as a library. You can make a modified
copy of grin.main() which configures the defaults to your liking.

To do:

  * The test for binariness can be made more efficient, I believe.
  * Test coverage needs to be improved.
  * Needs testing on Windows.


.. _grep : http://www.gnu.org/software/grep/
.. _ack : http://search.cpan.org/~petdance/ack-1.69_01/ack
.. _find : http://www.gnu.org/software/findutils/
.. _ConfigObj : http://www.voidspace.org.uk/python/configobj.html
