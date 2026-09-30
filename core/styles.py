"""Standard KML style definitions used across the app."""

STYLES = {
    "land":         ("ff000000", "16000000", 2),
    "sector":       ("ff00ffff", "1400ffff", 2),
    "zone1":        ("ff00aa00", "5500cc00", 2),
    "zone2":        ("ff0080ff", "5500a5ff", 2),
    "zone3":        ("ffcc0000", "55ff0000", 2),
    "basin":        ("ffff0000", "550000ff", 5),
    "mainline":     ("ff0000ff", None, 4),
    "submain":      ("ffff8800", None, 2),
    "row_line":     ("ff00ff00", None, 1.5),
    "manifold_line":("ffffff00", None, 2),
    "conn_line":    ("ff8800ff", None, 1),
    "dripline":     ("ff00aa00", None, 1),
}

POINT_STYLES = {
    "water":        ("ffff00ff", 1.1),
    "tree_pt":      ("ff008000", 0.4),
    "valve_mv1":    ("ff00ff00", 1.4),
    "valve_mv2":    ("ff00ffff", 1.4),
    "valve_mv3":    ("ffff00ff", 1.4),
    "valve_zv1":    ("ff00aa00", 0.9),
    "valve_zv2":    ("ff0080ff", 0.9),
    "valve_zv3":    ("ffcc0000", 0.9),
}