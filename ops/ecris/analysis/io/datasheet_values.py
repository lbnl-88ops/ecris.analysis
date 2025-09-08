"""This module contains the ion source datasheet values in plain
english along with their settings key values from dsht files and 
VENUS database files."""

from dataclasses import dataclass
from collections import OrderedDict

@dataclass
class DataLabel:
    label: str
    units: str | None
    key: str

    @property
    def label_with_units(self) -> str:
        if self.units is None:
            return self.label
        else:
            return f"{self.label} ({self.units})"


_DATA_LABELS = OrderedDict(
    {
        "Vacuum": [
            ("Injection", "mbar", "inj_mbar"),
            ("Extraction", "mbar", "ext_mbar"),
            ("Beamline", "torr", "bl_mig2_torr"),
        ],
        "Superconductor": [
            ("Injection I", "A", "inj_i"),
            ("Middle I", "A", "mid_i"),
            ("Extraction I", "A", "ext_i"),
            ("Sextapole i", "A", "sext_i"),
        ],
        "High-Voltage": [
            ("Extraction V", "V", "extraction_v"),
            ("Extraction I", "A", "extraction_i"),
            ("Puller V", "V", "puller_v"),
            ("Puller I", "A", "puller_i"),
            ("Biased disk V", "V", "bias_v"),
            ("Biased disk I", "A", "bias_i"),
        ],
        "RF": [
            ("28 GHz, forward", "W", "g28_fw"),
            ("18 GHz (1), forward", "W", "k18_fw"),
            ("18 GHz (1), reflected", "W", "k18_ref"),
            ("18 GHz (2), forward", "W", "k18_2_fw"),
            ("18 GHz (2), reflected", "W", "k18_2_ref"),
        ],
        "Low temperature Oven": [
            ("Oven 1 set-point", "C", "lt_oven_1_sp"),
            ("Oven 1 temperature", "C", "lt_oven_1_temp"),
            ("Oven 2 set-point", "C", "lt_oven_2_sp"),
            ("Oven 2 temperature", "C", "lt_oven_2_temp"),
        ],
        "High temperature oven": [
            ("Resistive I", "A", "ht_oven_i"),
            ("Resistive V", "V", "ht_oven_v"),
            ("Inductive I", "A", "ind_oven_amps"),
            ("Inductive Power", "W", "ind_oven_watts")
        ],
        "Gasses": [(f"Gas Balzer {i + 1}", None, f"gas_balzer_{i}") 
                   for i in range(16)
                   ],
        "Misc": [
            ("Glaser", "A", "glaser_1"),
        ],
    }
)

DATA_LABELS = [
    DataLabel(label=f"{category} {data}", units=units, key=key)
    for category, key_data_pairs in _DATA_LABELS.items()
    for data, units, key in key_data_pairs
]

DATA_LABELS_IN_CATEGORIES = {
    category: [
        DataLabel(label=data, units=units, key=key)
        for data, units, key in key_data_pairs
    ]
    for category, key_data_pairs in _DATA_LABELS.items()
}

DATA_LABELS_BY_KEY = {d.key: d for d in DATA_LABELS}
