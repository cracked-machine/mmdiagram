import unittest
import pytest
import PIL.Image
import pydantic

from tests.fixtures.common import test_setup
from tests.fixtures.input_data import input

import mm.diagram

def test_no_args():
    with unittest.mock.patch("sys.argv", ["mm.diagram", ""]):
        with pytest.raises(SystemExit):
            mm.diagram.Diagram()


def test_missing_required_args():
    with unittest.mock.patch(
        "sys.argv", 
        [
            "mm.diagram", 
            "a", "0x10", "0x10"
        ]
    ):
        with pytest.raises(SystemExit):
            mm.diagram.Diagram()

    with unittest.mock.patch(
        "sys.argv", 
        [
            "mm.diagram", 
            "-l", hex(1000),
        ]
    ):
        with pytest.raises(SystemExit):
            mm.diagram.Diagram()


def test_arg_tuple():
    with unittest.mock.patch(
        "sys.argv", 
        [
            "mm.diagram", 
            "-l", hex(1000),
            "0x10"
        ]
    ):
        with pytest.raises(SystemExit):
            mm.diagram.Diagram()

    with unittest.mock.patch(
        "sys.argv", 
        [
            "mm.diagram", 
            "-l", hex(1000),
            "0x10", "0x10"
        ]
    ):
        with pytest.raises(SystemExit):
            mm.diagram.Diagram()

    with unittest.mock.patch(
        "sys.argv", 
        [
            "mm.diagram", 
            "-l", hex(1000),
            "a", "0x10", "0x10"
        ]
    ):
        mm.diagram.Diagram()

    name = "My Memeory Map"
    with unittest.mock.patch(
        "sys.argv", 
        [
            "mm.diagram", 
            "-l", hex(1000),
            "b", "0x10", "0x10", 
            "-n", name
        ]
    ):
        mm.diagram.Diagram()
        assert name in mm.diagram.Diagram.model.memory_maps


def test_invalid_region_data_format1():
    """Note: output for these test will default to  ./out"""
    with unittest.mock.patch(
        "sys.argv", 
        [
            "mm.diagram", 
            "-l", hex(1000),
            "a", "10", "0x10"
        ]
    ):
        with pytest.raises(pydantic.ValidationError):
            mm.diagram.Diagram()


def test_invalid_region_data_format2():
    """Note: output for these test will default to  ./out"""
    with unittest.mock.patch(
        "sys.argv", 
        [
            "mm.diagram", 
            "-l", hex(1000),
            "a", "10", "0x10"
        ]
    ):
        with pytest.raises(pydantic.ValidationError):
            mm.diagram.Diagram()


def test_invalid_region_data_formatBoth():
    """Note: output for these test will default to  ./out"""
    with unittest.mock.patch(
        "sys.argv", 
        [
            "mm.diagram", 
            "-l", hex(1000),
            "a", "10", "10"
        ]
    ):
        with pytest.raises(pydantic.ValidationError):
            mm.diagram.Diagram()


def test_invalid_out_arg():
    """output path should end in .md"""
    with unittest.mock.patch(
        "sys.argv", 
        [
            "mm.diagram", 
            "-l", hex(1000),
            "a", "0x10", "0x10", 
            "-o", f"/tmp/pytest/{__name__}.txt"
        ]
    ):
        with pytest.raises(NameError):
            mm.diagram.Diagram()


def test_invalid_duplicate_name_arg():
    
    with unittest.mock.patch(
        "sys.argv", 
        [
            "mm.diagram", 
            "-l", hex(1000),
            "a", "0x10", "0x10", 
            "a", "0x10", "0x10"
        ]
    ):
        d = mm.diagram.Diagram()
        # the second memregion would have been skipped so we should only have one mem region
        memmap_name = list(d.model.memory_maps.keys())[0]
        assert len(d.model.memory_maps[memmap_name].memory_regions) == 1

def test_voidthresh_arg():
    with unittest.mock.patch(
        "sys.argv", 
        ["mm.diagram", 
         "a", "0x10", "0x10", 
         "-l", hex(1000),
         "-t", "1000"
        ]
    ):
        
        with pytest.raises(SystemExit):
            mm.diagram.Diagram()

    with unittest.mock.patch(
        "sys.argv", 
        ["mm.diagram", 
         "a", "0x10", "0x10", 
         "-l", hex(1000),
         "-t", "0x3e8"
        ]
    ):
        
        mm.diagram.Diagram()

@pytest.mark.parametrize("test_setup", [{"file_path": "out/tmp/invalid_2000_limit_arg_format"}], indirect=True)
def test_invalid_2000_limit_arg_format(test_setup):
    with unittest.mock.patch(
        "sys.argv", 
        ["mm.diagram", 
         "a", "0x10", "0x10", 
         "-l", "2000"
        ]
    ):
        
        with pytest.raises(SystemExit):
            mm.diagram.Diagram()

@pytest.mark.parametrize("test_setup", [{"file_path": "out/tmp/default_limit_arg_format"}], indirect=True)
def test_default_limit_arg_format(test_setup):
    """should create custom report dir/files"""

    with unittest.mock.patch(
        "sys.argv", 
        [
            "mm.diagram", 
            "a", "0x10", "0x10", 
            "-l", hex(2000),
            "-o", str(test_setup["report"]),
        ]
    ):

        mm.diagram.Diagram()
        default_limit = mm.diagram.Diagram.pargs.limit

        # this test assumes the default 'threshold' is 0x3e8 (1000)
        assert mm.diagram.Diagram.pargs.threshold == hex(10)
        assert not mm.diagram.Diagram.pargs.threshold == 200

        assert test_setup["report"].exists()

        assert test_setup["diagram_image"].exists()
        outimg = PIL.Image.open(str(test_setup["diagram_image"]))
        assert outimg.height == 2000

        assert test_setup["table_image"].exists()
        
@pytest.mark.parametrize("test_setup", [{"file_path": "out/tmp/valid_2000_limit_arg_format"}], indirect=True)
def test_valid_2000_limit_arg_format(test_setup):
    """should create custom report dir/files"""

    with unittest.mock.patch(
        "sys.argv", 
        [
            "mm.diagram", 
            "a", "0x10", "0x10", 
            "-o", str(test_setup["report"]), 
            "-l", hex(2000),
            
        ]
    ):

        mm.diagram.Diagram()

        # make sure arg was set as hex
        assert mm.diagram.Diagram.pargs.limit == hex(2000)
        assert not mm.diagram.Diagram.pargs.limit == 2000

        assert test_setup["report"].exists()

        assert test_setup["diagram_image"].exists()
        outimg = PIL.Image.open(str(test_setup["diagram_image"]))
        assert outimg.size[1] == 2000

        assert test_setup["table_image"].exists()

