# -*- coding: utf-8

""" Test the file recognizer capabilities.
"""

from __future__ import print_function, unicode_literals


import contextlib
import gzip
import os
import shutil
import socket
import sys

from io import open

from functools import partial

import nose

from grin import FileRecognizer, GZIP_MAGIC

printerr = partial(print, file=sys.stderr)

ALL_BYTES = bytes(bytearray(range(256)))


def empty_file(filename, open=open):
    open(filename, "a").close()


def binary_file(filename, open=open):
    with open(filename, "wb") as f:
        f.write(ALL_BYTES)


def text_file(filename, open=open):
    lines = [b"foo\n", b"bar\n"] * 100
    lines.append(b"baz\n")
    lines.extend([b"foo\n", b"bar\n"] * 100)
    with open(filename, "wb") as f:
        f.writelines(lines)


def fake_gzip_file(filename, open=open):
    """ Write out a binary file that has the gzip magic header bytes, but is not
    a gzip file.
    """
    with open(filename, "wb") as f:
        f.write(GZIP_MAGIC)
        f.write(ALL_BYTES)


def binary_middle(filename, open=open):
    """ Write out a file that is text for the first 100 bytes, then 100 binary
    bytes, then 100 text bytes to test that the recognizer only reads some of
    the file.
    """
    text = b"a" * 100 + b"\0" * 100 + b"b" * 100
    f = open(filename, "wb")
    f.write(text)
    f.close()


def socket_file(filename):
    s = socket.socket(socket.AF_UNIX)
    s.bind(filename)


def unreadable_file(filename):
    """ Write a file that does not have read permissions.
    """
    text_file(filename)
    os.chmod(filename, 0o200)
    try:
        with open(filename) as f:
            pass
    except IOError as e:
        if "Permission denied" not in str(e):
            raise
    else:
        raise RuntimeError(
            "grin tests cannot run on a filesystem that doesn't support chmod(). "
            "You will encounter false negative"
        )


def unreadable_dir(filename):
    """ Make a directory that does not have read permissions.
    """
    os.mkdir(filename)
    os.chmod(filename, 0o300)


def unexecutable_dir(filename):
    """ Make a directory that does not have execute permissions.
    """
    os.mkdir(filename)
    os.chmod(filename, 0o600)


def totally_unusable_dir(filename):
    """ Make a directory that has neither read nor execute permissions.
    """
    os.mkdir(filename)
    os.chmod(filename, 0o100)


def setup():
    # Make sure we don't have files remaining from previous tests
    teardown()

    # Make files to test individual recognizers.
    empty_file(b"empty")
    binary_file(b"binary")
    binary_middle(b"binary_middle")
    text_file(b"text")
    text_file(b"text~")
    text_file(b"text#")
    text_file(b"foo.bar.baz")
    os.mkdir(b"dir")
    binary_file(b".binary")
    text_file(b".text")
    empty_file(b"empty.gz", open=gzip.open)
    binary_file(b"binary.gz", open=gzip.open)
    text_file(b"text.gz", open=gzip.open)
    binary_file(b".binary.gz", open=gzip.open)
    text_file(b".text.gz", open=gzip.open)
    fake_gzip_file("fake.gz")
    os.mkdir(b".dir")
    os.symlink(b"binary", b"binary_link")
    os.symlink(b"text", b"text_link")
    os.symlink(b"dir", b"dir_link")
    os.symlink(b".binary", b".binary_link")
    os.symlink(b".text", b".text_link")
    os.symlink(b".dir", b".dir_link")
    unreadable_file(b"unreadable_file")
    unreadable_dir(b"unreadable_dir")
    unexecutable_dir(b"unexecutable_dir")
    totally_unusable_dir(b"totally_unusable_dir")
    os.symlink(b"unreadable_file", b"unreadable_file_link")
    os.symlink(b"unreadable_dir", b"unreadable_dir_link")
    os.symlink(b"unexecutable_dir", b"unexecutable_dir_link")
    os.symlink(b"totally_unusable_dir", b"totally_unusable_dir_link")
    text_file(b"text.skip_ext")
    os.mkdir(b"dir.skip_ext")
    text_file(b"text.dont_skip_ext")
    os.mkdir(b"skip_dir")
    text_file(b"fake_skip_dir")
    socket_file("socket_test")

    # Make a directory tree to test tree-walking.
    os.mkdir(b"tree")
    os.mkdir(b"tree/.hidden_dir")
    os.mkdir(b"tree/dir")
    os.mkdir(b"tree/dir/subdir")
    text_file(b"tree/dir/text")
    text_file(b"tree/dir/subdir/text")
    text_file(b"tree/text")
    text_file(b"tree/text.skip_ext")
    os.mkdir(b"tree/dir.skip_ext")
    text_file(b"tree/dir.skip_ext/text")
    text_file(b"tree/text.dont_skip_ext")
    binary_file(b"tree/binary")
    os.mkdir(b"tree/skip_dir")
    text_file(b"tree/skip_dir/text")
    os.mkdir(b"tree/.skip_hidden_dir")
    text_file(b"tree/.skip_hidden_file")
    os.mkdir(b"tree/unreadable_dir")
    text_file(b"tree/unreadable_dir/text")
    os.chmod("tree/unreadable_dir", 0o300)
    os.mkdir(b"tree/unexecutable_dir")
    text_file(b"tree/unexecutable_dir/text")
    os.chmod(b"tree/unexecutable_dir", 0o600)
    os.mkdir(b"tree/totally_unusable_dir")
    text_file(b"tree/totally_unusable_dir/text")
    os.chmod(b"tree/totally_unusable_dir", 0o100)

@contextlib.contextmanager
def catch_and_log_env_error(message=None, ignore="No such file or directory", args=()):
    """ Catch IOError, print a message, optionnaly reraise. Ignore some types """
    try:
        yield
    except EnvironmentError as e:
        if ignore not in str(e):
            if message is None:
                raise e
            printerr(message % (tuple(args) + (e,)))


def teardown():
    files_to_delete = [
        b"empty",
        b"binary",
        b"binary_middle",
        b"text",
        b"text~",
        b"empty.gz",
        b"binary.gz",
        b"text.gz",
        b"dir",
        b"binary_link",
        b"text_link",
        b"dir_link",
        b".binary",
        b".text",
        b".binary.gz",
        b".text.gz",
        b"fake.gz",
        b".dir",
        b".binary_link",
        b".text_link",
        b".dir_link",
        b"unreadable_file",
        b"unreadable_dir",
        b"unexecutable_dir",
        b"totally_unusable_dir",
        b"unreadable_file_link",
        b"unreadable_dir_link",
        b"unexecutable_dir_link",
        b"totally_unusable_dir_link",
        b"text.skip_ext",
        b"text.dont_skip_ext",
        b"dir.skip_ext",
        b"skip_dir",
        b"fake_skip_dir",
        b"text#",
        b"foo.bar.baz",
        b"tree",
        b"socket_test"
    ]
    for filename in files_to_delete:

        with catch_and_log_env_error():
            os.chmod(filename, 0o777)

        if os.path.isdir(filename):

            if not filename.startswith(b'/'):

                # Make sure we have permission to delete everything
                for dirname, dirs, files in os.walk(filename, followlinks=True):
                    paths = [os.path.join(dirname, p) for p in (dirs + files)]
                    os.chmod(dirname, 0o777)
                    for path in paths:
                        os.chmod(path, 0o777)

            with catch_and_log_env_error("Could not delete %r: %r", args=(filename,)):
                shutil.rmtree(filename)

        else:
            with catch_and_log_env_error("Could not delete %r: %r", args=(filename,)):
                os.unlink(filename)

def test_binary():
    fr = FileRecognizer()
    assert fr.is_binary(b"binary")
    assert fr.recognize_file(b"binary") == "binary"
    assert fr.recognize(b"binary") == "binary"


def test_text():
    fr = FileRecognizer()
    assert not fr.is_binary(b"text")
    assert fr.recognize_file(b"text") == "text"
    assert fr.recognize(b"text") == "text"


def test_gzipped():
    fr = FileRecognizer()
    assert fr.is_binary(b"text.gz")
    assert fr.recognize_file(b"text.gz") == "gzip"
    assert fr.recognize(b"text.gz") == "gzip"
    assert fr.is_binary(b"binary.gz")
    assert fr.recognize_file(b"binary.gz") == "binary"
    assert fr.recognize(b"binary.gz") == "binary"
    assert fr.is_binary(b"fake.gz")
    assert fr.recognize_file(b"fake.gz") == "binary"
    assert fr.recognize(b"fake.gz") == "binary"


def test_binary_middle():
    fr = FileRecognizer(binary_bytes=100)
    assert not fr.is_binary(b"binary_middle")
    assert fr.recognize_file(b"binary_middle") == "text"
    assert fr.recognize(b"binary_middle") == "text"
    fr = FileRecognizer(binary_bytes=101)
    assert fr.is_binary(b"binary_middle")
    assert fr.recognize_file(b"binary_middle") == "binary"
    assert fr.recognize(b"binary_middle") == "binary"


def test_socket():
    fr = FileRecognizer()
    assert fr.recognize(b"socket_test") == "skip"


def test_dir():
    fr = FileRecognizer()
    assert fr.recognize_directory(b"dir") == "directory"
    assert fr.recognize(b"dir") == "directory"


def test_skip_symlinks():
    fr = FileRecognizer(skip_symlink_files=True, skip_symlink_dirs=True)
    assert fr.recognize(b"binary_link") == "link"
    assert fr.recognize_file(b"binary_link") == "link"
    assert fr.recognize(b"text_link") == "link"
    assert fr.recognize_file(b"text_link") == "link"
    assert fr.recognize(b"dir_link") == "link"
    assert fr.recognize_directory(b"dir_link") == "link"


def test_do_not_skip_symlinks():
    fr = FileRecognizer(skip_symlink_files=False, skip_symlink_dirs=False)
    assert fr.recognize(b"binary_link") == "binary"
    assert fr.recognize_file(b"binary_link") == "binary"
    assert fr.recognize(b"text_link") == "text"
    assert fr.recognize_file(b"text_link") == "text"
    assert fr.recognize(b"dir_link") == "directory"
    assert fr.recognize_directory(b"dir_link") == "directory"


def test_skip_hidden():
    fr = FileRecognizer(skip_hidden_files=True, skip_hidden_dirs=True)
    assert fr.recognize(b".binary") == "skip"
    assert fr.recognize_file(b".binary") == "skip"
    assert fr.recognize(b".text") == "skip"
    assert fr.recognize_file(b".text") == "skip"
    assert fr.recognize(b".dir") == "skip"
    assert fr.recognize_directory(b".dir") == "skip"
    assert fr.recognize(b".binary_link") == "skip"
    assert fr.recognize_file(b".binary_link") == "skip"
    assert fr.recognize(b".text_link") == "skip"
    assert fr.recognize_file(b".text_link") == "skip"
    assert fr.recognize(b".dir_link") == "skip"
    assert fr.recognize_directory(b".dir_link") == "skip"
    assert fr.recognize(b".text.gz") == "skip"
    assert fr.recognize_file(b".text.gz") == "skip"
    assert fr.recognize(b".binary.gz") == "skip"
    assert fr.recognize_file(b".binary.gz") == "skip"


def test_skip_backup():
    fr = FileRecognizer(skip_backup_files=True)
    assert fr.recognize_file(b"text~") == "skip"


def test_do_not_skip_backup():
    fr = FileRecognizer(skip_backup_files=False)
    assert fr.recognize_file(b"text~") == "text"


def test_skip_weird_exts():
    fr = FileRecognizer(skip_exts=set())
    assert fr.recognize_file(b"text#") == "text"
    assert fr.recognize_file(b"foo.bar.baz") == "text"
    fr = FileRecognizer(skip_exts=set([b"#", b".bar.baz"]))
    assert fr.recognize_file(b"text#") == "skip"
    assert fr.recognize_file(b"foo.bar.baz") == "skip"


def test_do_not_skip_hidden_or_symlinks():
    fr = FileRecognizer(
        skip_hidden_files=False,
        skip_hidden_dirs=False,
        skip_symlink_dirs=False,
        skip_symlink_files=False,
    )
    assert fr.recognize(b".binary") == "binary"
    assert fr.recognize_file(b".binary") == "binary"
    assert fr.recognize(b".text") == "text"
    assert fr.recognize_file(b".text") == "text"
    assert fr.recognize(b".dir") == "directory"
    assert fr.recognize_directory(b".dir") == "directory"
    assert fr.recognize(b".binary_link") == "binary"
    assert fr.recognize_file(b".binary_link") == "binary"
    assert fr.recognize(b".text_link") == "text"
    assert fr.recognize_file(b".text_link") == "text"
    assert fr.recognize(b".dir_link") == "directory"
    assert fr.recognize_directory(b".dir_link") == "directory"
    assert fr.recognize(b".text.gz") == "gzip"
    assert fr.recognize_file(b".text.gz") == "gzip"
    assert fr.recognize(b".binary.gz") == "binary"
    assert fr.recognize_file(b".binary.gz") == "binary"


def test_do_not_skip_hidden_but_skip_symlinks():
    fr = FileRecognizer(
        skip_hidden_files=False,
        skip_hidden_dirs=False,
        skip_symlink_dirs=True,
        skip_symlink_files=True,
    )
    assert fr.recognize(b".binary") == "binary"
    assert fr.recognize_file(b".binary") == "binary"
    assert fr.recognize(b".text") == "text"
    assert fr.recognize_file(b".text") == "text"
    assert fr.recognize(b".dir") == "directory"
    assert fr.recognize_directory(b".dir") == "directory"
    assert fr.recognize(b".binary_link") == "link"
    assert fr.recognize_file(b".binary_link") == "link"
    assert fr.recognize(b".text_link") == "link"
    assert fr.recognize_file(b".text_link") == "link"
    assert fr.recognize(b".dir_link") == "link"
    assert fr.recognize_directory(b".dir_link") == "link"
    assert fr.recognize(b".text.gz") == "gzip"
    assert fr.recognize_file(b".text.gz") == "gzip"
    assert fr.recognize(b".binary.gz") == "binary"
    assert fr.recognize_file(b".binary.gz") == "binary"


def test_lack_of_permissions():
    fr = FileRecognizer()
    assert fr.recognize(b"unreadable_file") == "unreadable"
    assert fr.recognize_file(b"unreadable_file") == "unreadable"
    assert fr.recognize(b"unreadable_dir") == "directory"
    assert fr.recognize_directory(b"unreadable_dir") == "directory"
    assert fr.recognize(b"unexecutable_dir") == "directory"
    assert fr.recognize_directory(b"unexecutable_dir") == "directory"
    assert fr.recognize(b"totally_unusable_dir") == "directory"
    assert fr.recognize_directory(b"totally_unusable_dir") == "directory"


def test_symlink_src_unreadable():
    fr = FileRecognizer(skip_symlink_files=False, skip_symlink_dirs=False)
    assert fr.recognize(b"unreadable_file_link") == "unreadable"
    assert fr.recognize_file(b"unreadable_file_link") == "unreadable"
    assert fr.recognize(b"unreadable_dir_link") == "directory"
    assert fr.recognize_directory(b"unreadable_dir_link") == "directory"
    assert fr.recognize(b"unexecutable_dir_link") == "directory"
    assert fr.recognize_directory(b"unexecutable_dir_link") == "directory"
    assert fr.recognize(b"totally_unusable_dir_link") == "directory"
    assert fr.recognize_directory(b"totally_unusable_dir_link") == "directory"


def test_skip_ext():
    fr = FileRecognizer(skip_exts=set([b".skip_ext"]))
    assert fr.recognize(b"text.skip_ext") == "skip"
    assert fr.recognize_file(b"text.skip_ext") == "skip"
    assert fr.recognize(b"text") == "text"
    assert fr.recognize_file(b"text") == "text"
    assert fr.recognize(b"text.dont_skip_ext") == "text"
    assert fr.recognize_file(b"text.dont_skip_ext") == "text"
    assert fr.recognize(b"dir.skip_ext") == "directory"
    assert fr.recognize_directory(b"dir.skip_ext") == "directory"


def test_skip_dir():
    fr = FileRecognizer(skip_dirs=set([b"skip_dir", b"fake_skip_dir"]))
    assert fr.recognize(b"skip_dir") == "skip"
    assert fr.recognize_directory(b"skip_dir") == "skip"
    assert fr.recognize(b"fake_skip_dir") == "text"
    assert fr.recognize_file(b"fake_skip_dir") == "text"


def test_walking():
    fr = FileRecognizer(
        skip_hidden_files=True,
        skip_hidden_dirs=True,
        skip_exts=set([b".skip_ext"]),
        skip_dirs=set([b"skip_dir"]),
    )
    truth = [
        (b"tree/binary", "binary"),
        (b"tree/dir.skip_ext/text", "text"),
        (b"tree/dir/subdir/text", "text"),
        (b"tree/dir/text", "text"),
        (b"tree/text", "text"),
        (b"tree/text.dont_skip_ext", "text"),
    ]
    result = sorted(fr.walk(b"tree"))
    assert result == truth


def predot():
    os.chdir(b"tree")


def postdot():
    os.chdir(b"..")


@nose.with_setup(predot, postdot)
def test_dot():
    fr = FileRecognizer(
        skip_hidden_files=True,
        skip_hidden_dirs=True,
        skip_exts=set([b".skip_ext"]),
        skip_dirs=set([b"skip_dir"]),
    )
    truth = [
        (b"./binary", "binary"),
        (b"./dir.skip_ext/text", "text"),
        (b"./dir/subdir/text", "text"),
        (b"./dir/text", "text"),
        (b"./text", "text"),
        (b"./text.dont_skip_ext", "text"),
    ]
    result = sorted(fr.walk(b"."))
    assert result == truth


def predotdot():
    os.chdir(b"tree")
    os.chdir(b"dir")


def postdotdot():
    os.chdir(b"..")
    os.chdir(b"..")


@nose.with_setup(predotdot, postdotdot)
def test_dot_dot():
    fr = FileRecognizer(
        skip_hidden_files=True,
        skip_hidden_dirs=True,
        skip_exts=set([b".skip_ext"]),
        skip_dirs=set([b"skip_dir"]),
    )
    truth = [
        (b"../binary", "binary"),
        (b"../dir.skip_ext/text", "text"),
        (b"../dir/subdir/text", "text"),
        (b"../dir/text", "text"),
        (b"../text", "text"),
        (b"../text.dont_skip_ext", "text"),
    ]
    result = sorted(fr.walk(b".."))
    assert result == truth
