import unittest
import pytest
import mmdiagram.generator
import pathlib

# Check the output report at /tmp/pytest/tests.test_args.md


def test_no_args():
    with unittest.mock.patch('sys.argv',
                             ['mmap_digram.diagram',
                              '']):
        with pytest.raises(SystemExit):
            mmdiagram.generator.Diagram()


def test_arg_tuple():
    with unittest.mock.patch('sys.argv',
                             ['mmap_digram.diagram',
                              '0x10']):
        with pytest.raises(SystemExit):
            mmdiagram.generator.Diagram()

    with unittest.mock.patch('sys.argv',
                             ['mmap_digram.diagram',
                              '0x10',
                              '0x10']):
        with pytest.raises(SystemExit):
            mmdiagram.generator.Diagram()

    with unittest.mock.patch('sys.argv',
                             ['mmap_digram.diagram',
                              'a',
                              '0x10',
                              '0x10']):
        mmdiagram.generator.Diagram()


def test_invalid_out_arg():
    ''' output path should end in .md  '''
    with unittest.mock.patch('sys.argv',
                             ['mmap_digram.diagram',
                              'a',
                              '0x10',
                              '0x10',
                              "-o",
                              f"/tmp/pytest/{__name__}.txt"]):
        with pytest.raises(NameError):
            mmdiagram.generator.Diagram()


def test_valid_default_out_arg():
    ''' should create default report dir/files  '''
    with unittest.mock.patch('sys.argv',
                             ['mmap_digram.diagram',
                              'a',
                              '0x10',
                              '0x10']):
        mmdiagram.generator.Diagram()
        assert pathlib.Path("out/report.md").exists()
        assert pathlib.Path("out/report.png").exists()


def test_invalid_duplicate_name_arg():
    """there can only be one."""
    with unittest.mock.patch('sys.argv',
                             ['mmap_digram.diagram',
                              'a',
                              '0x10',
                              '0x10',
                              'a',
                              '0x10',
                              '0x10']):
        with pytest.warns(RuntimeWarning):
            mmdiagram.generator.Diagram()


def test_valid_custom_out_arg():
    ''' should create custom report dir/files '''
    with unittest.mock.patch('sys.argv',
                             ['mmap_digram.diagram',
                              'a',
                              '0x10',
                              '0x10',
                              "-o",
                              f"/tmp/pytest/{__name__}.md"]):
        mmdiagram.generator.Diagram()
        assert pathlib.Path(f"/tmp/pytest/{__name__}.md").exists()
        assert pathlib.Path(f"/tmp/pytest/{__name__}.png").exists()