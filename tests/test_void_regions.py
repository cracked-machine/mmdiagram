import mm.diagram
import unittest
import mm.image
import pathlib
import PIL.Image
import pytest


@pytest.fixture
def setup():
    report = pathlib.Path(f"/tmp/pytest/{__name__}.md")
    report.unlink(missing_ok=True)

    image_full = pathlib.Path(f"/tmp/pytest/{__name__}_full.png")
    image_full.unlink(missing_ok=True)

    image_cropped = pathlib.Path(f"/tmp/pytest/{__name__}_cropped.png")
    image_cropped.unlink(missing_ok=True)

    return {"report": report, "image_full": image_full, "image_cropped": image_cropped}


def test_void_region_default(setup):
    """ """

    diagram_height = 2000
    with unittest.mock.patch(
        "sys.argv",
        [
            "mm.diagram",
            "kernel",
            "0x10",
            "0x30",
            "rootfs",
            "0x50",
            "0x30",
            "dtb",
            "0x190",
            "0x30",
            "-o",
            str(setup["report"]),
            "-l",
            hex(diagram_height),
        ],
    ):

        d = mm.diagram.Diagram()

        # assumes the defaults haven't changed
        assert mm.diagram.Diagram.pargs.scale == 1
        assert mm.diagram.Diagram.pargs.voidthreshold == hex(1000)

        for region_image in d.mm.image_list:
            if region_image.name == "kernel":
                assert region_image.origin_as_hex == "0x10"
                assert region_image.size_as_hex == "0x30"
                assert region_image.freespace_as_hex == "0x10"
            if region_image.name == "rootfs":
                assert region_image.origin_as_hex == "0x50"
                assert region_image.size_as_hex == "0x30"
                assert region_image.freespace_as_hex == "0x110"
            if region_image.name == "dtb":
                assert region_image.origin_as_hex == "0x190"
                assert region_image.size_as_hex == "0x30"
                assert region_image.freespace_as_hex == "0x610"

        assert setup["report"].exists()

        assert setup["image_full"].exists()
        found_size = PIL.Image.open(str(setup["image_full"])).size
        assert found_size == (400, diagram_height)

        assert setup["image_cropped"].exists()
        found_size = PIL.Image.open(str(setup["image_cropped"])).size
        assert found_size == (400, 528)


def test_void_region_uservalue_500(setup):
    """ """

    diagram_height = 1000
    with unittest.mock.patch(
        "sys.argv",
        [
            "mm.diagram",
            "kernel",
            "0x10",
            "0x30",
            "rootfs",
            "0x50",
            "0x30",
            "dtb",
            "0x190",
            "0x30",
            "-o",
            str(setup["report"]),
            "-l",
            hex(diagram_height),
            "-v",
            hex(500),
        ],
    ):

        d = mm.diagram.Diagram()

        # assumes the defaults haven't changed
        assert mm.diagram.Diagram.pargs.scale == 1

        for region_image in d.mm.image_list:
            
            if region_image.name == "kernel":
                assert region_image.origin_as_hex == "0x10"
                assert region_image.size_as_hex == "0x30"
                assert region_image.freespace_as_hex == "0x10"
            if region_image.name == "rootfs":
                assert region_image.origin_as_hex == "0x50"
                assert region_image.size_as_hex == "0x30"
                assert region_image.freespace_as_hex == "0x110"
            if region_image.name == "dtb":
                assert region_image.origin_as_hex == "0x190"
                assert region_image.size_as_hex == "0x30"
                assert region_image.freespace_as_hex == "0x228"

        assert setup["report"].exists()

        assert setup["image_full"].exists()
        found_size = PIL.Image.open(str(setup["image_full"])).size
        assert found_size == (400, diagram_height)

        # empty section between rootfs and dtb should be retained
        assert setup["image_cropped"].exists()
        found_size = PIL.Image.open(str(setup["image_cropped"])).size
        assert found_size == (400, 528)


def test_void_region_uservalue_200(setup):
    """ """

    diagram_height = 1000
    with unittest.mock.patch(
        "sys.argv",
        [
            "mm.diagram",
            "kernel",
            "0x10",
            "0x30",
            "rootfs",
            "0x50",
            "0x30",
            "dtb",
            "0x190",
            "0x30",
            "-o",
            str(setup["report"]),
            "-l",
            hex(diagram_height),
            "-v",
            hex(200),
        ],
    ):

        d = mm.diagram.Diagram()

        # assumes the defaults haven't changed
        assert mm.diagram.Diagram.pargs.scale == 1

        for region_image in d.mm.image_list:
            
            if region_image.name == "kernel":
                assert region_image.origin_as_hex == "0x10"
                assert region_image.size_as_hex == "0x30"
                assert region_image.freespace_as_hex == "0x10"
            if region_image.name == "rootfs":
                assert region_image.origin_as_hex == "0x50"
                assert region_image.size_as_hex == "0x30"
                assert region_image.freespace_as_hex == "0x110"
            if region_image.name == "dtb":
                assert region_image.origin_as_hex == "0x190"
                assert region_image.size_as_hex == "0x30"
                assert region_image.freespace_as_hex == "0x228"

        assert setup["report"].exists()

        assert setup["image_full"].exists()
        found_size = PIL.Image.open(str(setup["image_full"])).size
        assert found_size == (400, diagram_height)

        # reduced void threshold, so empty section between rootfs and dtb should be voided, making the file smaller
        assert setup["image_cropped"].exists()
        found_size = PIL.Image.open(str(setup["image_cropped"])).size
        assert found_size == (400, 316)
