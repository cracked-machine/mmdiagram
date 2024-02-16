from pydantic import BaseModel, Field, ConfigDict
from pydantic.functional_validators import AfterValidator
import pathlib
import json
from typing import Optional, Dict, List
from typing_extensions import Annotated

# Validators
def check_empty_str(v: str, context: str):
    assert v, "Empty string found!"
    return v

def check_hex_str(v:str):
    assert v[:2] == "0x"
    return v

# data model
class MemoryRegion(BaseModel):
    memory_region_name: Annotated[
        str,
        Field(description="Name of the MemoryMap."),
        AfterValidator(check_empty_str)
    ]

    memory_region_origin: Annotated[
        str,
        Field(description="Origin address of the MemoryMap. In hex format string."),
        AfterValidator(check_empty_str),
        AfterValidator(check_hex_str)
    ]
    memory_region_size: Annotated[
        str,
        Field(description="Size (in bytes) of the MemoryMap. In hex format string."),
        AfterValidator(check_empty_str),
        AfterValidator(check_hex_str)
    ]
    memory_region_links: list[Dict[str,str]] = Field(
        [],
        description="""Links to other memory regions. E.g. """
        """\n["""
        """\n\n{'ParentMemoryMap1': 'ChildMemoryRegion1'}"""
        """\n\n..."""
        """\n\n{'ParentMemoryMapN': 'ChildMemoryRegionN'}"""
        """\n]""")

class MemoryMap(BaseModel):
    memory_map_name: Annotated[
        str,
        Field(description="Name of the memory map."),
        AfterValidator(check_empty_str)        
    ]
    memory_regions: list[MemoryRegion] = Field(description="Memory map containing memory regions.")


def check_region_link(v: list[MemoryMap]):
    found_memory_regions = []
    found_region_links = []

    # get all region_link properties from the data
    for memmap in v:
        for memregion in memmap.memory_regions:
            found_memory_regions.append(memregion)
            for regionlink in memregion.memory_region_links:
                found_region_links.append(regionlink)

    # check found links ref existing memmaps and memregions
    for regionlink in found_region_links:

        region_link_parent_memmap = [*regionlink.keys()][0]
        # check_empty_str(region_link_parent_memmap)
        assert any(mm.memory_map_name == region_link_parent_memmap for mm in v),\
        f"Parent MemoryMap '{region_link_parent_memmap}' in {regionlink} is a dangling reference!"
        
        region_link_child_memregion = [*regionlink.values()][0]
        # check_empty_str(region_link_child_memregion)
        assert any(rm.memory_region_name == region_link_child_memregion for rm in found_memory_regions),\
        f"Child MemoryRegion '{region_link_child_memregion}' in {regionlink} is a dangling reference!"


class Diagram(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
        validate_assignment=True,
        revalidate_instances="always",
        validate_default=True,
    )

    # diagram_name: str = Field(description="The name of the diagram.")
    diagram_name: Annotated[
        str, 
        Field(description="The name of the diagram."),
        AfterValidator(check_empty_str)
    ]
    memory_maps: Annotated[
        list[MemoryMap],
        Field(description="The diagram frame. Can contain many memory maps."),
        AfterValidator(check_region_link)
    ]

    
# helper functions
def generate_schema(path: pathlib.Path):
    schema_path = pathlib.Path("./mm/schema.json")
    myschema = Diagram.model_json_schema()

    with schema_path.open("w") as fp:
        fp.write(json.dumps(myschema, indent=2))


if __name__  == "__main__":
    generate_schema(pathlib.Path("./mm/schema.json"))


