import re

name_vessel = {
    "field": "name_vessel",
    "keyword": [
        "vessel",
        "ship",
        "master",
        "crew",
        "owner",
        ],
    "pattern": [],
    "valid_condition": lambda x: True,
    "max_values": 1,
    "normalize_text": lambda x: re.sub("\W", "", x).lower(),
    'out_table': {
        'direction': ["right"],
        'range': 2000,
        'horizontal_extend': 10,
        'vertical_extend': 1,
        'intersect_threshold': 0.3,
        'alignment': ["bottom"]
    },
    'loosen_enable': False,
    'threshold': 0.5
}

NOR = {
    "field": "NOR",
    "keyword": [
        "notice of readiness tender",
        "NOR tender",
        ],
    "pattern": [],
    "valid_condition": lambda x: True,
    "normalize_text": lambda x: re.sub("\W", "", x).lower(),
    'out_table': {
        'direction': ["right", "left"],
        'range': 2000,
        'horizontal_extend': 10,
        'vertical_extend': 1,
        'intersect_threshold': 0.3,
        'alignment': ["bottom", "top"]
    },
    'loosen_enable': False,
    'threshold': 0.5
}

commenced_discharging = {
    "field": "commenced_discharging",
    "keyword": [
        "Commenced Discharging",
        ],
    "pattern": [],
    "valid_condition": lambda x: True,
    "normalize_text": lambda x: re.sub("\W", "", x).lower(),
    'out_table': {
        'direction': ["right", "left"],
        'range': 2000,
        'horizontal_extend': 10,
        'vertical_extend': 1,
        'intersect_threshold': 0.3,
        'alignment': ["bottom", "top"]
    },
    'loosen_enable': False,
    'threshold': 0.5
}

commenced_loading = {
    "field": "commenced_loading",
    "keyword": [
        "Commenced Loading",
        ],
    "pattern": [],
    "valid_condition": lambda x: True,
    "normalize_text": lambda x: re.sub("\W", "", x).lower(),
    'out_table': {
        'direction': ["right", "left"],
        'range': 2000,
        'horizontal_extend': 10,
        'vertical_extend': 1,
        'intersect_threshold': 0.3,
        'alignment': ["bottom", "top"]
    },
    'loosen_enable': False,
    'threshold': 0.5
}

completed_discharging = {
    "field": "completed_discharging",
    "keyword": [
        "Completed Discharging",
        ],
    "pattern": [],
    "valid_condition": lambda x: True,
    "normalize_text": lambda x: re.sub("\W", "", x).lower(),
    'out_table': {
        'direction': ["right", "left"],
        'range': 2000,
        'horizontal_extend': 10,
        'vertical_extend': 1,
        'intersect_threshold': 0.3,
        'alignment': ["bottom", "top"]
    },
    'loosen_enable': False,
    'threshold': 0.5
}

completed_loading = {
    "field": "completed_loading",
    "keyword": [
        "Completed Loading",
        ],
    "pattern": [],
    "valid_condition": lambda x: True,
    "normalize_text": lambda x: re.sub("\W", "", x).lower(),
    'out_table': {
        'direction': ["right", "left"],
        'range': 2000,
        'horizontal_extend': 10,
        'vertical_extend': 1,
        'intersect_threshold': 0.3,
        'alignment': ["bottom", "top"]
    },
    'loosen_enable': False,
    'threshold': 0.5
}