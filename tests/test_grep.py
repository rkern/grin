# Doctests are a bit easier to write for these tests.

r'''
Set up

    >>> import grin
    >>> from cStringIO import StringIO
    >>> import re
    >>> 
    >>> all_foo = """\
    ... foo
    ... foo
    ... foo
    ... foo
    ... foo
    ... """
    >>> first_foo = """\
    ... foo
    ... bar
    ... bar
    ... bar
    ... bar
    ... """
    >>> last_foo = """\
    ... bar
    ... bar
    ... bar
    ... bar
    ... foo
    ... """
    >>> second_foo = """\
    ... bar
    ... foo
    ... bar
    ... bar
    ... bar
    ... """
    >>> second_last_foo = """\
    ... bar
    ... bar
    ... bar
    ... foo
    ... bar
    ... """
    >>> middle_foo = """\
    ... bar
    ... bar
    ... foo
    ... bar
    ... bar
    ... """
    >>> small_gap = """\
    ... bar
    ... bar
    ... foo
    ... bar
    ... foo
    ... bar
    ... bar
    ... """
    >>> no_eol = "foo"
    >>> middle_of_line = """\
    ... bar
    ... bar
    ... barfoobar
    ... bar
    ... bar
    ... """

Test the basic defaults, no context.

    >>> gt_default = grin.GrepText(re.compile('foo'))
    >>> gt_default.do_grep(StringIO(all_foo))
    [(0, 0, 'foo\n', [(0, 3)]), (1, 0, 'foo\n', [(0, 3)]), (2, 0, 'foo\n', [(0, 3)]), (3, 0, 'foo\n', [(0, 3)]), (4, 0, 'foo\n', [(0, 3)])]
    >>> gt_default.do_grep(StringIO(first_foo))
    [(0, 0, 'foo\n', [(0, 3)])]
    >>> gt_default.do_grep(StringIO(last_foo))
    [(4, 0, 'foo\n', [(0, 3)])]
    >>> gt_default.do_grep(StringIO(second_foo))
    [(1, 0, 'foo\n', [(0, 3)])]
    >>> gt_default.do_grep(StringIO(second_last_foo))
    [(3, 0, 'foo\n', [(0, 3)])]
    >>> gt_default.do_grep(StringIO(middle_foo))
    [(2, 0, 'foo\n', [(0, 3)])]
    >>> gt_default.do_grep(StringIO(small_gap))
    [(2, 0, 'foo\n', [(0, 3)]), (4, 0, 'foo\n', [(0, 3)])]
    >>> gt_default.do_grep(StringIO(no_eol))
    [(0, 0, 'foo', [(0, 3)])]
    >>> gt_default.do_grep(StringIO(middle_of_line))
    [(2, 0, 'barfoobar\n', [(3, 6)])]

Symmetric 1-line context.

    >>> gt_context_1 = grin.GrepText(re.compile('foo'), options=grin.Options(before_context=1, after_context=1))
    >>> gt_context_1.do_grep(StringIO(all_foo))
    [(0, 0, 'foo\n', [(0, 3)]), (1, 0, 'foo\n', [(0, 3)]), (2, 0, 'foo\n', [(0, 3)]), (3, 0, 'foo\n', [(0, 3)]), (4, 0, 'foo\n', [(0, 3)])]
    >>> gt_context_1.do_grep(StringIO(first_foo))
    [(0, 0, 'foo\n', [(0, 3)]), (1, 1, 'bar\n', None)]
    >>> gt_context_1.do_grep(StringIO(last_foo))
    [(3, -1, 'bar\n', None), (4, 0, 'foo\n', [(0, 3)])]
    >>> gt_context_1.do_grep(StringIO(second_foo))
    [(0, -1, 'bar\n', None), (1, 0, 'foo\n', [(0, 3)]), (2, 1, 'bar\n', None)]
    >>> gt_context_1.do_grep(StringIO(second_last_foo))
    [(2, -1, 'bar\n', None), (3, 0, 'foo\n', [(0, 3)]), (4, 1, 'bar\n', None)]
    >>> gt_context_1.do_grep(StringIO(middle_foo))
    [(1, -1, 'bar\n', None), (2, 0, 'foo\n', [(0, 3)]), (3, 1, 'bar\n', None)]
    >>> gt_context_1.do_grep(StringIO(small_gap))
    [(1, -1, 'bar\n', None), (2, 0, 'foo\n', [(0, 3)]), (3, 1, 'bar\n', None), (4, 0, 'foo\n', [(0, 3)]), (5, 1, 'bar\n', None)]
    >>> gt_context_1.do_grep(StringIO(no_eol))
    [(0, 0, 'foo', [(0, 3)])]
    >>> gt_context_1.do_grep(StringIO(middle_of_line))
    [(1, -1, 'bar\n', None), (2, 0, 'barfoobar\n', [(3, 6)]), (3, 1, 'bar\n', None)]

Symmetric 2-line context.

    >>> gt_context_2 = grin.GrepText(re.compile('foo'), options=grin.Options(before_context=2, after_context=2))
    >>> gt_context_2.do_grep(StringIO(all_foo))
    [(0, 0, 'foo\n', [(0, 3)]), (1, 0, 'foo\n', [(0, 3)]), (2, 0, 'foo\n', [(0, 3)]), (3, 0, 'foo\n', [(0, 3)]), (4, 0, 'foo\n', [(0, 3)])]
    >>> gt_context_2.do_grep(StringIO(first_foo))
    [(0, 0, 'foo\n', [(0, 3)]), (1, 1, 'bar\n', None), (2, 1, 'bar\n', None)]
    >>> gt_context_2.do_grep(StringIO(last_foo))
    [(2, -1, 'bar\n', None), (3, -1, 'bar\n', None), (4, 0, 'foo\n', [(0, 3)])]
    >>> gt_context_2.do_grep(StringIO(second_foo))
    [(0, -1, 'bar\n', None), (1, 0, 'foo\n', [(0, 3)]), (2, 1, 'bar\n', None), (3, 1, 'bar\n', None)]
    >>> gt_context_2.do_grep(StringIO(second_last_foo))
    [(1, -1, 'bar\n', None), (2, -1, 'bar\n', None), (3, 0, 'foo\n', [(0, 3)]), (4, 1, 'bar\n', None)]
    >>> gt_context_2.do_grep(StringIO(middle_foo))
    [(0, -1, 'bar\n', None), (1, -1, 'bar\n', None), (2, 0, 'foo\n', [(0, 3)]), (3, 1, 'bar\n', None), (4, 1, 'bar\n', None)]
    >>> gt_context_2.do_grep(StringIO(small_gap))
    [(0, -1, 'bar\n', None), (1, -1, 'bar\n', None), (2, 0, 'foo\n', [(0, 3)]), (3, 1, 'bar\n', None), (4, 0, 'foo\n', [(0, 3)]), (5, 1, 'bar\n', None), (6, 1, 'bar\n', None)]
    >>> gt_context_2.do_grep(StringIO(no_eol))
    [(0, 0, 'foo', [(0, 3)])]
    >>> gt_context_2.do_grep(StringIO(middle_of_line))
    [(0, -1, 'bar\n', None), (1, -1, 'bar\n', None), (2, 0, 'barfoobar\n', [(3, 6)]), (3, 1, 'bar\n', None), (4, 1, 'bar\n', None)]

1 line of before-context, no lines after.

    >>> gt_before_context_1 = grin.GrepText(re.compile('foo'), options=grin.Options(before_context=1, after_context=0))
    >>> gt_before_context_1.do_grep(StringIO(all_foo))
    [(0, 0, 'foo\n', [(0, 3)]), (1, 0, 'foo\n', [(0, 3)]), (2, 0, 'foo\n', [(0, 3)]), (3, 0, 'foo\n', [(0, 3)]), (4, 0, 'foo\n', [(0, 3)])]
    >>> gt_before_context_1.do_grep(StringIO(first_foo))
    [(0, 0, 'foo\n', [(0, 3)])]
    >>> gt_before_context_1.do_grep(StringIO(last_foo))
    [(3, -1, 'bar\n', None), (4, 0, 'foo\n', [(0, 3)])]
    >>> gt_before_context_1.do_grep(StringIO(second_foo))
    [(0, -1, 'bar\n', None), (1, 0, 'foo\n', [(0, 3)])]
    >>> gt_before_context_1.do_grep(StringIO(second_last_foo))
    [(2, -1, 'bar\n', None), (3, 0, 'foo\n', [(0, 3)])]
    >>> gt_before_context_1.do_grep(StringIO(middle_foo))
    [(1, -1, 'bar\n', None), (2, 0, 'foo\n', [(0, 3)])]
    >>> gt_before_context_1.do_grep(StringIO(small_gap))
    [(1, -1, 'bar\n', None), (2, 0, 'foo\n', [(0, 3)]), (3, -1, 'bar\n', None), (4, 0, 'foo\n', [(0, 3)])]
    >>> gt_before_context_1.do_grep(StringIO(no_eol))
    [(0, 0, 'foo', [(0, 3)])]
    >>> gt_before_context_1.do_grep(StringIO(middle_of_line))
    [(1, -1, 'bar\n', None), (2, 0, 'barfoobar\n', [(3, 6)])]

1 line of after-context, no lines before.

    >>> gt_after_context_1 = grin.GrepText(re.compile('foo'), options=grin.Options(before_context=0, after_context=1))
    >>> gt_after_context_1.do_grep(StringIO(all_foo))
    [(0, 0, 'foo\n', [(0, 3)]), (1, 0, 'foo\n', [(0, 3)]), (2, 0, 'foo\n', [(0, 3)]), (3, 0, 'foo\n', [(0, 3)]), (4, 0, 'foo\n', [(0, 3)])]
    >>> gt_after_context_1.do_grep(StringIO(first_foo))
    [(0, 0, 'foo\n', [(0, 3)]), (1, 1, 'bar\n', None)]
    >>> gt_after_context_1.do_grep(StringIO(last_foo))
    [(4, 0, 'foo\n', [(0, 3)])]
    >>> gt_after_context_1.do_grep(StringIO(second_foo))
    [(1, 0, 'foo\n', [(0, 3)]), (2, 1, 'bar\n', None)]
    >>> gt_after_context_1.do_grep(StringIO(second_last_foo))
    [(3, 0, 'foo\n', [(0, 3)]), (4, 1, 'bar\n', None)]
    >>> gt_after_context_1.do_grep(StringIO(middle_foo))
    [(2, 0, 'foo\n', [(0, 3)]), (3, 1, 'bar\n', None)]
    >>> gt_after_context_1.do_grep(StringIO(small_gap))
    [(2, 0, 'foo\n', [(0, 3)]), (3, 1, 'bar\n', None), (4, 0, 'foo\n', [(0, 3)]), (5, 1, 'bar\n', None)]
    >>> gt_after_context_1.do_grep(StringIO(no_eol))
    [(0, 0, 'foo', [(0, 3)])]
    >>> gt_after_context_1.do_grep(StringIO(middle_of_line))
    [(2, 0, 'barfoobar\n', [(3, 6)]), (3, 1, 'bar\n', None)]

'''


