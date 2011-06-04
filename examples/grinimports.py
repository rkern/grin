#!/usr/bin/env python
# -*- coding: UTF-8 -*-
""" Transform Python files into normalized import statements for grepping.
"""

import compiler
from compiler.visitor import ASTVisitor, walk
from cStringIO import StringIO
import os
import shlex
import sys

import grin


__version__ = '1.2'

def normalize_From(node):
    """ Return a list of strings of Python 'from' statements, one import on each
    line.
    """
    statements = []
    children = node.getChildren()
    module = '.'*node.level + node.modname
    for name, asname in children[1]:
        line = 'from %s import %s' % (module, name)
        if asname is not None:
            line += ' as %s' % asname
        line += '\n'
        statements.append(line)
    return statements

def normalize_Import(node):
    """ Return a list of strings of Python 'import' statements, one import on
    each line.
    """
    statements = []
    children = node.getChildren()
    for name, asname in children[0]:
        line = 'import %s' % (name)
        if asname is not None:
            line += ' as %s' % asname
        line += '\n'
        statements.append(line)
    return statements

class ImportPuller(ASTVisitor):
    """ Extract import statements from an AST.
    """
    def __init__(self):
        ASTVisitor.__init__(self)
        self.statements = []

    def visitFrom(self, node):
        self.statements.extend(normalize_From(node))

    def visitImport(self, node):
        self.statements.extend(normalize_Import(node))

    def as_string(self):
        """ Concatenate all of the 'import' and 'from' statements.
        """
        return ''.join(self.statements)


def normalize_file(filename, *args):
    """ Import-normalize a file.

    If the file is not parseable, an empty filelike object will be returned.
    """
    try:
        ast = compiler.parseFile(filename)
    except Exception, e:
        return StringIO('')
    ip = ImportPuller()
    walk(ast, ip)
    return StringIO(ip.as_string())

def get_grinimports_arg_parser(parser=None):
    """ Create the command-line parser.
    """
    parser = grin.get_grin_arg_parser(parser)
    parser.set_defaults(include='*.py')
    parser.description = ("Extract, normalize and search import statements "
        "from Python files.")
    parser.epilog = """
For example, if I have a file example.py with a bunch of imports:

    $ cat example.py
    import foo
    import foo.baz as blah
    from foo import bar, baz as bat

    def somefunction():
        "Do something to foo.baz"
        import from_inside.function

We can grep for 'import' in order to get all of the import statements:

    $ grinimports.py import example.py
    example.py:
        1 : import foo
        2 : import foo.baz as blah
        3 : from foo import bar
        4 : from foo import baz as bat
        5 : import from_inside.function

If we just want to find imports of foo.baz, we can do this:

    $ grinimports.py "import foo\.baz|from foo import baz" example.py
    example.py:
        2 : import foo.baz as blah
        4 : from foo import baz as bat

A typical grep (or grin) cannot find all of these in the original files because
the import statements are not normalized.

    $ grin "foo\.baz|from foo import baz" example.py
    example.py:
        2 : import foo.baz as blah
        6 :     "Do something to foo.baz"
"""
    for action in parser._actions:
        if hasattr(action, 'version'):
            action.version = 'grinpython %s' % __version__

    return parser

def grinimports_main(argv=None):
    if argv is None:
        # Look at the GRIN_ARGS environment variable for more arguments.
        env_args = shlex.split(os.getenv('GRIN_ARGS', ''))
        argv = [sys.argv[0]] + env_args + sys.argv[1:]
    parser = get_grinimports_arg_parser()
    args = parser.parse_args(argv[1:])
    if args.context is not None:
        args.before_context = args.context
        args.after_context = args.context
    args.use_color = args.force_color or (not args.no_color and
        sys.stdout.isatty() and
        (os.environ.get('TERM') != 'dumb'))

    regex = grin.get_regex(args)
    g = grin.GrepText(regex, args)
    for filename, kind in grin.get_filenames(args):
        if kind == 'text':
            # Ignore gzipped files.
            report = g.grep_a_file(filename, opener=normalize_file)
            sys.stdout.write(report)

if __name__ == '__main__':
    grinimports_main()
