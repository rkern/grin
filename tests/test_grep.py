# Doctests are a bit easier to write for these tests.

from __future__ import unicode_literals

from io import BytesIO
import re

import grin


all_foo = b"""\
foo
foo
foo
foo
foo
"""
first_foo = b"""\
foo
bar
bar
bar
bar
"""
last_foo = b"""\
bar
bar
bar
bar
foo
"""
second_foo = b"""\
bar
foo
bar
bar
bar
"""
second_last_foo = b"""\
bar
bar
bar
foo
bar
"""
middle_foo = b"""\
bar
bar
foo
bar
bar
"""
small_gap = b"""\
bar
bar
foo
bar
foo
bar
bar
"""
no_eol = b"foo"
middle_of_line = b"""\
bar
bar
barfoobar
bar
bar
"""


def test_basic_defaults_with_no_context():

    gt_default = grin.GrepText(re.compile(b"foo"))
    assert gt_default.do_grep(BytesIO(all_foo)) == [
        (0, 0, b"foo\n", [(0, 3)]),
        (1, 0, b"foo\n", [(0, 3)]),
        (2, 0, b"foo\n", [(0, 3)]),
        (3, 0, b"foo\n", [(0, 3)]),
        (4, 0, b"foo\n", [(0, 3)]),
    ]
    assert gt_default.do_grep(BytesIO(first_foo)) == [(0, 0, b"foo\n", [(0, 3)])]
    assert gt_default.do_grep(BytesIO(last_foo)) == [(4, 0, b"foo\n", [(0, 3)])]
    assert gt_default.do_grep(BytesIO(second_foo)) == [(1, 0, b"foo\n", [(0, 3)])]
    assert gt_default.do_grep(BytesIO(second_last_foo)) == [(3, 0, b"foo\n", [(0, 3)])]
    assert gt_default.do_grep(BytesIO(middle_foo)) == [(2, 0, b"foo\n", [(0, 3)])]
    assert gt_default.do_grep(BytesIO(small_gap)) == [
        (2, 0, b"foo\n", [(0, 3)]),
        (4, 0, b"foo\n", [(0, 3)]),
    ]
    assert gt_default.do_grep(BytesIO(no_eol)) == [(0, 0, b"foo", [(0, 3)])]
    assert gt_default.do_grep(BytesIO(middle_of_line)) == [
        (2, 0, b"barfoobar\n", [(3, 6)])
    ]


def test_symetric_1_line_context():

    gt_context_1 = grin.GrepText(
        re.compile(b"foo"), options=grin.Options(before_context=1, after_context=1)
    )
    assert gt_context_1.do_grep(BytesIO(all_foo)) == [
        (0, 0, b"foo\n", [(0, 3)]),
        (1, 0, b"foo\n", [(0, 3)]),
        (2, 0, b"foo\n", [(0, 3)]),
        (3, 0, b"foo\n", [(0, 3)]),
        (4, 0, b"foo\n", [(0, 3)]),
    ]
    assert gt_context_1.do_grep(BytesIO(first_foo)) == [
        (0, 0, b"foo\n", [(0, 3)]),
        (1, 1, b"bar\n", None),
    ]
    assert gt_context_1.do_grep(BytesIO(last_foo)) == [
        (3, -1, b"bar\n", None),
        (4, 0, b"foo\n", [(0, 3)]),
    ]
    assert gt_context_1.do_grep(BytesIO(second_foo)) == [
        (0, -1, b"bar\n", None),
        (1, 0, b"foo\n", [(0, 3)]),
        (2, 1, b"bar\n", None),
    ]
    assert gt_context_1.do_grep(BytesIO(second_last_foo)) == [
        (2, -1, b"bar\n", None),
        (3, 0, b"foo\n", [(0, 3)]),
        (4, 1, b"bar\n", None),
    ]
    assert gt_context_1.do_grep(BytesIO(middle_foo)) == [
        (1, -1, b"bar\n", None),
        (2, 0, b"foo\n", [(0, 3)]),
        (3, 1, b"bar\n", None),
    ]
    assert gt_context_1.do_grep(BytesIO(small_gap)) == [
        (1, -1, b"bar\n", None),
        (2, 0, b"foo\n", [(0, 3)]),
        (3, 1, b"bar\n", None),
        (4, 0, b"foo\n", [(0, 3)]),
        (5, 1, b"bar\n", None),
    ]
    assert gt_context_1.do_grep(BytesIO(no_eol)) == [(0, 0, b"foo", [(0, 3)])]
    assert gt_context_1.do_grep(BytesIO(middle_of_line)) == [
        (1, -1, b"bar\n", None),
        (2, 0, b"barfoobar\n", [(3, 6)]),
        (3, 1, b"bar\n", None),
    ]


def test_symmetric_2_line_context():

    gt_context_2 = grin.GrepText(
        re.compile(b"foo"), options=grin.Options(before_context=2, after_context=2)
    )
    assert gt_context_2.do_grep(BytesIO(all_foo)) == [
        (0, 0, b"foo\n", [(0, 3)]),
        (1, 0, b"foo\n", [(0, 3)]),
        (2, 0, b"foo\n", [(0, 3)]),
        (3, 0, b"foo\n", [(0, 3)]),
        (4, 0, b"foo\n", [(0, 3)]),
    ]
    assert gt_context_2.do_grep(BytesIO(first_foo)) == [
        (0, 0, b"foo\n", [(0, 3)]),
        (1, 1, b"bar\n", None),
        (2, 1, b"bar\n", None),
    ]
    assert gt_context_2.do_grep(BytesIO(last_foo)) == [
        (2, -1, b"bar\n", None),
        (3, -1, b"bar\n", None),
        (4, 0, b"foo\n", [(0, 3)]),
    ]
    assert gt_context_2.do_grep(BytesIO(second_foo)) == [
        (0, -1, b"bar\n", None),
        (1, 0, b"foo\n", [(0, 3)]),
        (2, 1, b"bar\n", None),
        (3, 1, b"bar\n", None),
    ]
    assert gt_context_2.do_grep(BytesIO(second_last_foo)) == [
        (1, -1, b"bar\n", None),
        (2, -1, b"bar\n", None),
        (3, 0, b"foo\n", [(0, 3)]),
        (4, 1, b"bar\n", None),
    ]
    assert gt_context_2.do_grep(BytesIO(middle_foo)) == [
        (0, -1, b"bar\n", None),
        (1, -1, b"bar\n", None),
        (2, 0, b"foo\n", [(0, 3)]),
        (3, 1, b"bar\n", None),
        (4, 1, b"bar\n", None),
    ]
    assert gt_context_2.do_grep(BytesIO(small_gap)) == [
        (0, -1, b"bar\n", None),
        (1, -1, b"bar\n", None),
        (2, 0, b"foo\n", [(0, 3)]),
        (3, 1, b"bar\n", None),
        (4, 0, b"foo\n", [(0, 3)]),
        (5, 1, b"bar\n", None),
        (6, 1, b"bar\n", None),
    ]
    assert gt_context_2.do_grep(BytesIO(no_eol)) == [(0, 0, b"foo", [(0, 3)])]
    assert gt_context_2.do_grep(BytesIO(middle_of_line)) == [
        (0, -1, b"bar\n", None),
        (1, -1, b"bar\n", None),
        (2, 0, b"barfoobar\n", [(3, 6)]),
        (3, 1, b"bar\n", None),
        (4, 1, b"bar\n", None),
    ]


def test_1_line_of_before_context_no_lines_after():

    gt_before_context_1 = grin.GrepText(
        re.compile(b"foo"), options=grin.Options(before_context=1, after_context=0)
    )
    assert gt_before_context_1.do_grep(BytesIO(all_foo)) == [
        (0, 0, b"foo\n", [(0, 3)]),
        (1, 0, b"foo\n", [(0, 3)]),
        (2, 0, b"foo\n", [(0, 3)]),
        (3, 0, b"foo\n", [(0, 3)]),
        (4, 0, b"foo\n", [(0, 3)]),
    ]
    assert gt_before_context_1.do_grep(BytesIO(first_foo)) == [
        (0, 0, b"foo\n", [(0, 3)])
    ]
    assert gt_before_context_1.do_grep(BytesIO(last_foo)) == [
        (3, -1, b"bar\n", None),
        (4, 0, b"foo\n", [(0, 3)]),
    ]
    assert gt_before_context_1.do_grep(BytesIO(second_foo)) == [
        (0, -1, b"bar\n", None),
        (1, 0, b"foo\n", [(0, 3)]),
    ]
    assert gt_before_context_1.do_grep(BytesIO(second_last_foo)) == [
        (2, -1, b"bar\n", None),
        (3, 0, b"foo\n", [(0, 3)]),
    ]
    assert gt_before_context_1.do_grep(BytesIO(middle_foo)) == [
        (1, -1, b"bar\n", None),
        (2, 0, b"foo\n", [(0, 3)]),
    ]
    assert gt_before_context_1.do_grep(BytesIO(small_gap)) == [
        (1, -1, b"bar\n", None),
        (2, 0, b"foo\n", [(0, 3)]),
        (3, -1, b"bar\n", None),
        (4, 0, b"foo\n", [(0, 3)]),
    ]
    assert gt_before_context_1.do_grep(BytesIO(no_eol)) == [(0, 0, b"foo", [(0, 3)])]
    assert gt_before_context_1.do_grep(BytesIO(middle_of_line)) == [
        (1, -1, b"bar\n", None),
        (2, 0, b"barfoobar\n", [(3, 6)]),
    ]


def test_1_line_of_before_context_no_lines_before():

    gt_after_context_1 = grin.GrepText(
        re.compile(b"foo"), options=grin.Options(before_context=0, after_context=1)
    )
    assert gt_after_context_1.do_grep(BytesIO(all_foo)) == [
        (0, 0, b"foo\n", [(0, 3)]),
        (1, 0, b"foo\n", [(0, 3)]),
        (2, 0, b"foo\n", [(0, 3)]),
        (3, 0, b"foo\n", [(0, 3)]),
        (4, 0, b"foo\n", [(0, 3)]),
    ]
    assert gt_after_context_1.do_grep(BytesIO(first_foo)) == [
        (0, 0, b"foo\n", [(0, 3)]),
        (1, 1, b"bar\n", None),
    ]
    assert gt_after_context_1.do_grep(BytesIO(last_foo)) == [(4, 0, b"foo\n", [(0, 3)])]
    assert gt_after_context_1.do_grep(BytesIO(second_foo)) == [
        (1, 0, b"foo\n", [(0, 3)]),
        (2, 1, b"bar\n", None),
    ]
    assert gt_after_context_1.do_grep(BytesIO(second_last_foo)) == [
        (3, 0, b"foo\n", [(0, 3)]),
        (4, 1, b"bar\n", None),
    ]
    assert gt_after_context_1.do_grep(BytesIO(middle_foo)) == [
        (2, 0, b"foo\n", [(0, 3)]),
        (3, 1, b"bar\n", None),
    ]
    assert gt_after_context_1.do_grep(BytesIO(small_gap)) == [
        (2, 0, b"foo\n", [(0, 3)]),
        (3, 1, b"bar\n", None),
        (4, 0, b"foo\n", [(0, 3)]),
        (5, 1, b"bar\n", None),
    ]
    assert gt_after_context_1.do_grep(BytesIO(no_eol)) == [(0, 0, b"foo", [(0, 3)])]
    assert gt_after_context_1.do_grep(BytesIO(middle_of_line)) == [
        (2, 0, b"barfoobar\n", [(3, 6)]),
        (3, 1, b"bar\n", None),
    ]
