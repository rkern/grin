#!/usr/bin/env python

from __future__ import with_statement

import fnmatch
import itertools
import os
import re
import sys

import argparse


#### Constants ####
# Maintain the order of these constants. We use them for sorting.
PRE = -1
MATCH = 0
POST = 1

# Use file(1)'s choices for what's text and what's not.
TEXTCHARS = ''.join(map(chr, [7,8,9,10,12,13,27] + range(0x20, 0x100)))
ALLBYTES = ''.join(map(chr, range(256)))


def is_binary_string(bytes):
    """ Determine if a string is classified as binary rather than text.

    Parameters
    ----------
    bytes : str

    Returns
    -------
    is_binary : bool
    """
    nontext = bytes.translate(ALLBYTES, TEXTCHARS)
    return bool(nontext)
    
def sliding_window(seq, n):
    """ Returns a sliding window (up to width n) over data from the iterable

    Adapted from the itertools documentation.

        s -> (s0,), (s0, s1), ... (s0,s1,...s[n-1]), (s1,s2,...,sn), ...
    """
    it = iter(seq)
    result = ()
    for i, elem in itertools.izip(range(n), it):
        result += (elem,)
        yield result
    for elem in it:
        result = result[1:] + (elem,)
        yield result


class Options(dict):
    """ Simple options.
    """

    def __init__(self, *args, **kwds):
        dict.__init__(self, *args, **kwds)
        self.__dict__ = self


def default_options():
    """ Populate the default options.
    """
    opt = Options(
        before_context = 0,
        after_context = 0,
        show_line_numbers = True,
        show_match = True,
        show_filename = True,
        skip_hidden_dirs=False,
        skip_hidden_files=False,
        skip_dirs=set(),
        skip_exts=set(),
        skip_symlink_dirs=True,
        skip_symlink_files=True,
        binary_bytes=4096,
    )
    return opt


class GrepText(object):
    """ Grep a single file for a regex by iterating over the lines in a file.

    Attributes
    ----------
    regex : compiled regex
    options : Options or similar
    """

    def __init__(self, regex, options=None):
        # The compiled regex.
        self.regex = regex

        # The options object from parsing the configuration and command line.
        if options is None:
            options = default_options()
        self.options = options

    def do_grep(self, fp):
        """ Do a full grep.

        Parameters
        ----------
        fp : filelike object
            An open filelike object or other iterator that yields lines (with
            line endings).
        """
        before = self.options.before_context
        after = self.options.after_context
        # Start keeping track of the "after" context state. When we hit
        # a matched line, we'll reset this counter to the number of "after"
        # context lines we're trying to capture. For each line that follows
        # that doesn't match, we'll decrement the counter. At 0, we'll stop
        # accumulating "after" context lines.
        after_state = 0
        context = []

        # Make a sliding window going over the lines of the file in order to
        # keep track of the "before" context lines.
        window = sliding_window(fp, before + 1)
        for i, lines in enumerate(window):
            # The last line in the window is the line we're actually
            # searching.
            line = lines[-1]
            m = self.regex.search(line)
            if m is None:
                if after_state != 0:
                    # This line is part of the "after" context.
                    context.append((i, POST, line))
                    after_state -= 1
                continue
            else:
                # This line matches.
                # Reset the "after" context counter.
                after_state = after
                for j, before_line in zip(range(i-len(lines)+1, i), lines[:-1]):
                    # XXX: we can probably simply avoid adding duplicate
                    # lines here instead of doing a second pass.
                    context.append((j, PRE, before_line))
                context.append((i, MATCH, line))

        unique_context = self.uniquify_context(context)
        return unique_context

    def uniquify_context(self, context):
        """ Remove duplicate lines from the list of context lines.
        """
        context.sort()
        unique_context = []
        for group in itertools.groupby(context, lambda ikl: ikl[0]):
            for i, kind, line in group[1]:
                if kind == MATCH:
                    # Always use a match.
                    unique_context.append((i, kind, line))
                    break
            else:
                # No match, only PRE and/or POST lines. Use the last one, which
                # should be a POST since we've sorted it that way.
                unique_context.append((i, kind, line))

        return unique_context

    def report(self, context_lines, filename=None):
        """ Return a string showing the results.

        Parameters
        ----------
        context_lines : list of tuples of (int, PRE/MATCH/POST, str)
            The lines of matches and context.
        filename : str, optional
            The name of the file being grepped, if one exists. If not provided,
            the filename may not be printed out.

        Returns
        -------
        text : str
            This will end in a newline character if there is any text. Otherwise, it
            might be an empty string without a newline.
        """
        if len(context_lines) == 0:
            return ''
        lines = []
        if not self.options.show_match:
            # Just show the filename if we match.
            line = '%s\n' % filename
            lines.append(line)
        else:
            if self.options.show_filename and filename is not None:
                line = '%s:\n' % filename
                lines.append(line)
            if self.options.show_line_numbers:
                template = '%(lineno)5s %(sep)s %(line)s'
            else:
                template = '%(line)s'
            for i, kind, line in context_lines:
                ns = dict(
                    lineno = i+1,
                    sep = {PRE: '-', POST: '+', MATCH: ':'}[kind],
                    line = line,
                )
                line = template % ns
                lines.append(line)
                if not line.endswith('\n'):
                    lines.append('\n')

        text = ''.join(lines)
        return text

    def grep_a_file(self, filename):
        """ Grep a single file that actually exists on the file system.

        Parameters
        ----------
        filename : str

        Returns
        -------
        report : str
            The grep results as text.
        """
        f = open(filename, 'rb')
        with f:
            unique_context = self.do_grep(f)
        report = self.report(unique_context, filename)
        return report


class FileRecognizer(object):
    """ Configurable way to determine what kind of file something is.

    Attributes
    ----------
    skip_hidden_dirs : bool
        Whether to skip recursing into hidden directories, i.e. those starting
        with a "." character.
    skip_hidden_files : bool
        Whether to skip hidden files.
    skip_dirs : container of str
        A list of directory names to skip. For example, one might want to skip
        directories named "CVS".
    skip_exts : container of str
        A list of file extensions to skip. For example, some file names like
        ".so" are known to be binary and one may want to always skip them.
    skip_symlink_dirs : bool
        Whether to skip symlinked directories.
    skip_symlink_files : bool
        Whether to skip symlinked files.
    binary_bytes : int
        The number of bytes to check at the beginning and end of a file for
        binary characters.
    """

    def __init__(self, skip_hidden_dirs=False, skip_hidden_files=False,
        skip_dirs=set(), skip_exts=set(), skip_symlink_dirs=True,
        skip_symlink_files=True, binary_bytes=4096):
        self.skip_hidden_dirs = skip_hidden_dirs
        self.skip_hidden_files = skip_hidden_files
        self.skip_dirs = skip_dirs
        self.skip_exts = skip_exts
        self.skip_symlink_dirs = skip_symlink_dirs
        self.skip_symlink_files = skip_symlink_files
        self.binary_bytes = binary_bytes

    def is_binary(self, filename):
        """ Determine if a given file is binary or not.

        Parameters
        ----------
        filename : str

        Returns
        -------
        is_binary : bool
        """
        f = open(filename)
        start = f.read(self.binary_bytes)

        # Now seek back to binary_bytes from the end. If the size of the file is
        # less than binary_bytes, then we have a problem: we can't seek past the
        # beginning of the file from the end with fseek(), so check where we are
        # now. If our current position in the file is less than binary_bytes,
        # then we've already read the entire file and don't need to read from
        # the end. If it is exactly binary_bytes, the file size is at least
        # binary_bytes and we can fseek just fine.
        if f.tell() < self.binary_bytes:
            end = ''
        else:
            f.seek(-self.binary_bytes, 2)
            end = f.read(self.binary_bytes)
        f.close()
        bytes = start + end
        return is_binary_string(bytes)

    def recognize(self, filename):
        """ Determine what kind of thing a filename represents.

        It will also determine what a directory walker should do with the
        file:

            'text' :
                It should should be grepped for the pattern and the matching
                lines displayed. 
            'binary' : 
                The file is binary and should be either ignored or grepped
                without displaying the matching lines depending on the
                configuration.
            'directory' :
                The filename refers to a readable and executable directory that
                should be recursed into if we are configured to do so.
            'link' :
                The filename refers to a symlink that should be skipped.
            'unreadable' :
                The filename cannot be read (and also, in the case of
                directories, is not executable either).
            'skip' :
                The filename, whether a directory or a file, should be skipped
                for any other reason.

        Parameters
        ----------
        filename : str

        Returns
        -------
        kind : str
        """
        if os.path.isdir(filename):
            return self.recognize_directory(filename)
        else:
            return self.recognize_file(filename)
        
    def recognize_directory(self, filename):
        """ Determine what to do with a directory.
        """
        basename = os.path.split(filename)[-1]
        if (self.skip_hidden_dirs and basename.startswith('.') and 
            basename not in ('.', '..')):
            return 'skip'
        if self.skip_symlink_dirs and os.path.islink(filename):
            return 'link'
        if basename in self.skip_dirs:
            return 'skip'
        # Follow any possible symlink to the real file in order to check its
        # permissions.
        filename = os.path.realpath(filename)
        if os.access(filename, os.R_OK|os.X_OK):
            return 'directory'

        return 'unreadable'

    def recognize_file(self, filename):
        """ Determine what to do with a file.
        """
        basename = os.path.split(filename)[-1]
        if self.skip_hidden_files and basename.startswith('.'):
            return 'skip'
        if self.skip_symlink_files and os.path.islink(filename):
            return 'link'
        base, ext = os.path.splitext(filename)
        if ext in self.skip_exts:
            return 'skip'
        # Follow any possible symlink to the real file in order to check its
        # permissions.
        filename = os.path.realpath(filename)
        if os.access(filename, os.R_OK):
            # Just to be sure, catch OSErrors.
            try:
                if self.is_binary(filename):
                    return 'binary'
                else:
                    return 'text'
            except OSError:
                return 'unreadable'

        return 'unreadable'

    def walk(self, startpath):
        """ Walk the tree from a given start path yielding all of the files (not
        directories) and their kinds underneath it depth first.

        Paths which are recognized as 'skip', 'link', or 'unreadable' will
        simply be passed over without comment.

        Parameters
        ----------
        startpath : str

        Yields
        ------
        filename : str
        kind : str
        """
        kind = self.recognize(startpath)
        if kind in ('binary', 'text'):
            yield startpath, kind
            # Not a directory, so there is no need to recurse.
            return
        elif kind == 'directory':
            basenames = os.listdir(startpath)
            for basename in basenames:
                path = os.path.join(startpath, basename)
                for fn, k in self.walk(path):
                    yield fn, k


def get_grin_arg_parser(parser=None):
    """ Create the command-line parser.
    """
    if parser is None:
        parser = argparse.ArgumentParser()

    parser.add_argument('-i', '--ignore-case', action='append_const',
        dest='re_flags', const=re.I, default=[], help="ignore case in the regex")
    parser.add_argument('-A', '--after-context', default=0, type=int,
        help="the number of lines of context to show after the match")
    parser.add_argument('-B', '--before-context', default=0, type=int,
        help="the number of lines of context to show before the match")
    parser.add_argument('-C', '--context', type=int,
        help="the number of lines of context to show on either side of the match")
    parser.add_argument('-n', '--line-number', action='store_true',
        dest='show_line_numbers', default=True, help="show the line numbers")
    parser.add_argument('-N', '--no-line-number', action='store_false',
        dest='show_line_numbers', help="do not show the line numbers")
    parser.add_argument('-H', '--with-filename', action='store_true',
        dest='show_filename', default=True, 
        help="show the filenames of files that match")
    parser.add_argument('--without-filename', action='store_false',
        dest='show_filename', 
        help="do not show the filenames of files that match")
    parser.add_argument('-l', '--files-with-matches', action='store_false',
        dest='show_match',
        help="show only the filenames and not the texts of the matches")
    parser.add_argument('-L', '--files-without-matches', action='store_true',
        dest='show_match', default=False,
        help="show the matches with the filenames")
    parser.add_argument('-s', '--no-skip-hidden-files',
        dest='skip_hidden_files', action='store_false',
        help="do not skip .hidden files")
    parser.add_argument('-S', '--no-skip-hidden-dirs', dest='skip_hidden_dirs',
        action='store_false',
        help="do not skip .hidden directories")
    parser.add_argument('-d', '--skip-dirs',
        default='CVS,RCS,.svn,.hg,.bzr,build,dist',
        help="comma-separated list of directory names to skip [default=%(default)r]")
    parser.add_argument('-D', '--no-skip-dirs', dest='skip_dirs',
        action='store_const', const='',
        help="do not skip any directories")
    parser.add_argument('-e', '--skip-exts',
        default='.pyc,.pyo,.so,.o,.a,.gz,.tgz',
        help="comma-separated list of file extensions to skip [default=%(default)r]")
    parser.add_argument('-E', '--no-skip-exts', dest='skip_exts',
        action='store_const', const='',
        help="do not skip any file extensions")
    parser.add_argument('-f', '--files-from-file', metavar="FILE",
        help="read files to search from a file, one per line; - for stdin")
    parser.add_argument('-0', '--null-separated', action='store_true',
        help="filenames specified in --files-from-file are separated by NULs")

    parser.add_argument('regex', help="the regular expression to search for")
    parser.add_argument('files', nargs='*', help="the files to search")

    return parser

def get_grind_arg_parser(parser=None):
    """ Create the command-line parser for the find-like companion program.
    """
    if parser is None:
        parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--no-skip-hidden-files',
        dest='skip_hidden_files', action='store_false',
        help="do not skip .hidden files")
    parser.add_argument('-S', '--no-skip-hidden-dirs', dest='skip_hidden_dirs',
        action='store_false',
        help="do not skip .hidden directories")
    parser.add_argument('-d', '--skip-dirs',
        default='CVS,RCS,.svn,.hg,.bzr,build,dist',
        help="comma-separated list of directory names to skip [default=%(default)r]")
    parser.add_argument('-D', '--no-skip-dirs', dest='skip_dirs',
        action='store_const', const='',
        help="do not skip any directories")
    parser.add_argument('-e', '--skip-exts',
        default='.pyc,.pyo,.so,.o,.a,.gz,.tgz',
        help="comma-separated list of file extensions to skip [default=%(default)r]")
    parser.add_argument('-E', '--no-skip-exts', dest='skip_exts',
        action='store_const', const='',
        help="do not skip any file extensions")
    parser.add_argument('-0', '--null-separated', action='store_true',
        help="print the filenames separated by NULs")
    parser.add_argument('--dirs', nargs='+', default=["."],
        help="the directories to start from")

    parser.add_argument('glob',
        help="the glob pattern to match")

    return parser

def get_recognizer(args):
    """ Get the file recognizer object from the configured options.
    """
    fr = FileRecognizer(
        skip_hidden_files=args.skip_hidden_files,
        skip_hidden_dirs=args.skip_hidden_dirs,
        skip_dirs=set(args.skip_dirs.split(',')),
        skip_exts=set(args.skip_exts.split(',')),
    )
    return fr

def get_filenames(args):
    """ Generate the filenames to grep.
    """
    files = []
    # If the user has given us a file with filenames, consume them first.
    if args.files_from_file is not None:
        if args.files_from_file == '-':
            files_file = sys.stdin
            should_close = False
        elif os.path.exists(args.files_from_file):
            files_file = open(args.files_from_file)
            should_close = True

        try:
            # Remove ''
            if args.null_separated:
                files.extend([x.strip() for x in files_file.read().split('\0')])
            else:
                files.extend([x.strip() for x in files_file])
        finally:
            if should_close:
                files_file.close()

    # Now add the filenames provided on the command line itself.
    files.extend(args.files)
    if len(files) == 0:
        # Add the current directory at least.
        files = ['.']

    # Make sure we don't have any empty strings lying around.
    while '' in files:
        files.remove('')

    # Go over our list of filenames and see if we can recognize each as
    # something we want to grep.
    fr = get_recognizer(args)
    for fn in files:
        kind = fr.recognize(fn)
        if kind == 'text':
            yield fn
        elif kind == 'directory':
            for filename, k in fr.walk(fn):
                if k == 'text':
                    yield filename
        # XXX: warn about other files?
        # XXX: handle binary?

def get_regex(args):
    """ Get the compiled regex object to search with.
    """
    # Combine all of the flags.
    flags = 0
    for flag in args.re_flags:
        flags |= flag
    return re.compile(args.regex, flags)


def grin_main(argv=None):
    if argv is None:
        argv = sys.argv
    parser = get_grin_arg_parser()
    args = parser.parse_args(argv[1:])
    if args.context is not None:
        args.before_context = args.context
        args.after_context = args.context
    regex = get_regex(args)
    g = GrepText(regex, args)
    for filename in get_filenames(args):
        report = g.grep_a_file(filename)
        sys.stdout.write(report)

def print_line(filename):
    print filename

def print_null(filename):
    # Note that the final filename will have a trailing NUL, just like 
    # "find -print0" does.
    sys.stdout.write(filename)
    sys.stdout.write('\0')

def grind_main(argv=None):
    if argv is None:
        argv = sys.argv
    parser = get_grind_arg_parser()
    args = parser.parse_args(argv[1:])

    # Define the output function.
    if args.null_separated:
        output = print_null
    else:
        output = print_line
        
    fr = get_recognizer(args)
    for dir in args.dirs:
        for filename, k in fr.walk(dir):
            if fnmatch.fnmatch(os.path.basename(filename), args.glob):
                output(filename)

if __name__ == '__main__':
    grin_main()
