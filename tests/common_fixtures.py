import pytest
from typing import Dict

@pytest.fixture
def input() -> Dict:
    valid = {
        "$schema": "/home/chris/projects/python/mmdiagram/mm/schema.json",
        "diagram_name": "TestDiagram",
        "diagram_height": 1000,
        "diagram_width": 400,
        "memory_maps": {
            "eMMC": {
                "map_height": 1000,
                "map_width": 400,
                "memory_regions": 
                {
                    "Blob1": {
                    "memory_region_origin": "0x10",
                    "memory_region_size": "0x10",
                    "memory_region_links": [
                        ["DRAM", "Blob2"],
                        ["DRAM", "Blob3"]
                    ]
                    }
                }
            },
            "DRAM": {
                "map_height": 1000,
                "map_width": 400,                
                "memory_regions": 
                {
                    "Blob2": {
                    "memory_region_origin": "0x10",
                    "memory_region_size": "0x10"
                    },
                    "Blob3": {
                    "memory_region_origin": "0x50",
                    "memory_region_size": "0x10"
                    }
                }
            }
        }
    }
        
    return valid