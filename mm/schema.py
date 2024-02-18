
import pydantic
import pathlib
import json
from typing import Tuple
from typing_extensions import Annotated
import logging

class ConfigParent(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(
        validate_assignment=True,
        revalidate_instances="always",
        validate_default=True,
        validate_return=True
    )


# data model
class MemoryRegion(ConfigParent):

    memory_region_origin: Annotated[
        str,
        pydantic.Field(..., description="Origin address of the MemoryMap. In hex format string."),
    ]
    memory_region_size: Annotated[
        str,
        pydantic.Field(..., description="Size (in bytes) of the MemoryMap. In hex format string."),
    ]
    memory_region_links: list[tuple[str,str]] = pydantic.Field(
        [],
        description="""Links to other memory regions. E.g. """
        """\n["""
        """\n\n{'ParentMemoryMap1': 'ChildMemoryRegion1'}"""
        """\n\n..."""
        """\n\n{'ParentMemoryMapN': 'ChildMemoryRegionN'}"""
        """\n]""")
    
    remain: Annotated[
        str,
        pydantic.Field("", description="Internal Use")
    ]

    collisions: Annotated[
        dict,
        pydantic.Field({}, Description="Internal Use")
    ]

    @pydantic.field_validator("memory_region_origin", "memory_region_size")
    @classmethod
    def check_empty_str(cls, v: str):
        
        assert v, "Empty string found!"
        assert v[:2] == "0x"

        return v


class MemoryMap(ConfigParent):

    memory_regions: Annotated[
        dict[str, MemoryRegion],
        pydantic.Field(description="Memory map containing memory regions.")
    ]
    map_height: Annotated[
        int,
        pydantic.Field(..., description="The height of the memory map.")
    ]
    map_width: Annotated[
        int,
        pydantic.Field(..., description="The width of the memory map.")
    ]

class Diagram(ConfigParent):

    # diagram_name: str = pydantic.Field(description="The name of the diagram.")
    diagram_name: Annotated[
        str, 
        pydantic.Field(..., description="The name of the diagram.")
    ]
    diagram_height: Annotated[
        int,
        pydantic.Field(..., description="The height of the diagram.")
    ]
    diagram_width: Annotated[
        int,
        pydantic.Field(..., description="The width of the diagram.")
    ]
    memory_maps: Annotated[
        dict[str, MemoryMap],
        pydantic.Field(..., description="The diagram frame. Can contain many memory maps.")
    ]

    @pydantic.field_validator("diagram_name")
    @classmethod
    def check_empty_str(cls, v: str):
        assert v, "Empty string found!"
        return v

    @pydantic.field_validator("memory_maps")
    @classmethod
    def check_dangling_region_links(cls, v: dict[str, MemoryMap]):
        found_memory_regions = []
        found_region_links = []
        

        # get all region_link properties from the data
        for mmap in v.values():
            for region in mmap.memory_regions.items():
                found_memory_regions.append(region)
                
                for regionlink in region[1].memory_region_links:
                    found_region_links.append({"link": regionlink, "region_size": region[1].memory_region_size})
                    

        # check found links ref existing memmaps and memregions
        for regionlink in found_region_links:

            region_link_parent_memmap = regionlink['link'][0]
            assert any(
                (mm_name == region_link_parent_memmap) for mm_name in v.keys()),\
                f"Parent MemoryMap '{region_link_parent_memmap}' in {regionlink['link']} is a dangling reference!"
            
            # also check the from/to memoryregions are the same size
            region_link_child_memregion = regionlink['link'][1]     
            assert any(
                (mr[0] == region_link_child_memregion and
                mr[1].memory_region_size == regionlink['region_size']) 
                for mr in found_memory_regions),\
                f"Child MemoryRegion '{region_link_child_memregion}' in {regionlink['link']} is a dangling reference!"

        return v
    
    @pydantic.model_validator(mode="after")
    def calc_nearest_region(self):
        """Find the nearest neighbour region and if they have collided"""

        # process each memory map independently
        for memory_map in self.memory_maps.values():
            non_collision_distances = {}
            
            neighbour_region_list = memory_map.memory_regions.items()
            
            for memory_region_name, memory_region in memory_map.memory_regions.items(): 

                logging.debug(f"Calculating nearest distances to {memory_region_name} region:")
                this_region_end = 0

                other_region: Tuple[str, MemoryRegion]
                for other_region in neighbour_region_list:
                    # calc the end address of this and inspected region
                    other_region_name = other_region[0]
                    other_region_origin = other_region[1].memory_region_origin
                    other_region_size = other_region[1].memory_region_size

                    this_region_end: int = int(memory_region.memory_region_origin,16) + int(memory_region.memory_region_size, 16)
                    other_region_end: int = int(other_region_origin,16) + int(other_region_size,16)

                    # skip calculating distance from yourself.
                    if memory_region_name == other_region_name:
                        continue

                    # skip if 'this' region origin is ahead of the probed region end address
                    if int(memory_region.memory_region_origin,16) > other_region_end:
                        continue

                    distance_to_other_region: int = int(other_region_origin,16) - this_region_end
                    logging.debug(f"\t{hex(distance_to_other_region)} bytes to {other_region_name}")

                    # collision detected
                    if distance_to_other_region < 0:
                        # was the region that collided into us at a lower or higher origin address
                        if int(other_region_origin,16) < int(memory_region.memory_region_origin, 16):
                            # lower so use our origin address as the collion point
                            memory_region.collisions[other_region_name] = memory_region.memory_region_origin
                        else:
                            # higher so use their origin address as the collision point
                            memory_region.collisions[other_region_name] = other_region_origin

                        if int(memory_region.memory_region_origin, 16) < int(other_region_origin, 16):
                            # no distance left
                            memory_region.remain = hex(distance_to_other_region)
                            pass

                    else:
                        # record the distance for later
                        non_collision_distances[other_region_name] = distance_to_other_region
                        # set a first value while we have it (in case there are no future collisions)
                        if not memory_region.remain and not memory_region.collisions:
                            memory_region.remain = hex(distance_to_other_region)
                        # # if remain not already set to no distance left then set the positive remain distance
                        elif not memory_region.remain:
                            memory_region.remain = hex(distance_to_other_region)

                logging.debug(f"Non-collision distances - {non_collision_distances}")

                # after probing each region we must now pick the lowest distance ()
                if not memory_region.collisions:
                    if non_collision_distances:
                        lowest = min(non_collision_distances, key=non_collision_distances.get)
                        memory_region.remain = hex(non_collision_distances[lowest])
                    else:
                        memory_region.remain = hex(memory_map.map_height - this_region_end)
                elif memory_region.collisions and not memory_region.remain:
                    memory_region.remain = hex(memory_map.map_height - this_region_end)

    
# helper functions
def generate_schema(path: pathlib.Path):
    myschema = Diagram.model_json_schema()

    with path.open("w") as fp:
        fp.write(json.dumps(myschema, indent=2))

if __name__  == "__main__":
    generate_schema(pathlib.Path("./mm/schema.json"))



