#!/usr/bin/env python
# -*- coding: UTF-8 -*-
""" Transform Python code by omitting strings, comments, and/or code.
"""

from cStringIO import StringIO
import os
import shlex
import string
import sys
import tokenize

import grin


__version__ = '1.2'


class Transformer(object):
    """ Transform Python files to remove certain features.
    """
    def __init__(self, python_code, comments, strings):
        # Keep code.
        self.python_code = python_code
        # Keep comments.
        self.comments = comments
        # Keep strings.
        self.strings = strings

        table = [' '] * 256
        for s in string.whitespace:
            table[ord(s)] = s
        # A table for the translate() function that replaces all non-whitespace
        # characters with spaces.
        self.space_table = ''.join(table)

    def keep_token(self, kind):
        """ Return True if we should keep the token in the output.
        """
        if kind in (tokenize.NL, tokenize.NEWLINE):
            return True
        elif kind == tokenize.COMMENT:
            return self.comments
        elif kind == tokenize.STRING:
            return self.strings
        else:
            return self.python_code

    def replace_with_spaces(self, s):
        """ Replace all non-newline characters in a string with spaces.
        """
        return s.translate(self.space_table)

    def __call__(self, filename, mode='rb'):
        """ Open a file and convert it to a filelike object with transformed
        contents.
        """
        g = StringIO()
        f = open(filename, mode)
        try:
            gen = tokenize.generate_tokens(f.readline)
            old_end = (1, 0)
            for kind, token, start, end, line in gen:
                if old_end[0] == start[0]:
                    dx = start[1] - old_end[1]
                else:
                    dx = start[1]
                # Put in any omitted whitespace.
                g.write(' ' * dx)
                old_end = end
                if not self.keep_token(kind):
                    token = self.replace_with_spaces(token)
                g.write(token)
        finally:
            f.close()
        # Seek back to the beginning of the file.
        g.seek(0, 0)
        return g

def get_grinpython_arg_parser(parser=None):
    """ Create the command-line parser.
    """
    parser = grin.get_grin_arg_parser(parser)
    parser.set_defaults(include='*.py')
    parser.description = ("Search Python code with strings, comments, and/or "
        "code removed.")
    for action in parser._actions:
        if hasattr(action, 'version'):
            action.version = 'grinpython %s' % __version__

    group = parser.add_argument_group('Code Transformation')
    group.add_argument('-p', '--python-code', action='store_true',
        help="Keep non-string, non-comment Python code.")
    group.add_argument('-c', '--comments', action='store_true',
        help="Keep Python comments.")
    group.add_argument('-t', '--strings', action='store_true',
        help="Keep Python strings, especially docstrings.")
    return parser

def grinpython_main(argv=None):
    if argv is None:
        # Look at the GRIN_ARGS environment variable for more arguments.
        env_args = shlex.split(os.getenv('GRIN_ARGS', ''))
        argv = [sys.argv[0]] + env_args + sys.argv[1:]
    parser = get_grinpython_arg_parser()
    args = parser.parse_args(argv[1:])
    if args.context is not None:
        args.before_context = args.context
        args.after_context = args.context
    args.use_color = args.force_color or (not args.no_color and
        sys.stdout.isatty() and
        (os.environ.get('TERM') != 'dumb'))

    xform = Transformer(args.python_code, args.comments, args.strings)

    regex = grin.get_regex(args)
    g = grin.GrepText(regex, args)
    for filename, kind in grin.get_filenames(args):
        if kind == 'text':
            # Ignore gzipped files.
            report = g.grep_a_file(filename, opener=xform)
            sys.stdout.write(report)

if __name__ == '__main__':
    grinpython_main()

