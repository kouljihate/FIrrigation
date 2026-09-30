"""Naming and placement rules for valves."""

MV_GROUPS = {
    "MV1": ["S1", "S2", "S3", "S4", "S5"],
    "MV2": ["S6", "S7"],
    "MV3": ["S8"],
}

MV_OF_SECTOR: dict[str, str] = {}
for mv, sectors in MV_GROUPS.items():
    for s in sectors:
        MV_OF_SECTOR[s] = mv


def mv_name(sector_code: str) -> str:
    return MV_OF_SECTOR[sector_code]


def zv_name(sector_code: str, zone_index: int) -> str:
    return f"{sector_code}-ZV{zone_index}"