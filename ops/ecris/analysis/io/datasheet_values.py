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
            ("Injection I", None, "inj_i"),
            ("Extraction I", None, "ext_i"),
            ("Mid I", None, "mid_i"),
            ("sext i", None, "sext_i"),
        ],
        "High-Voltage": [
            ("Extraction V", None, "extraction_v"),
            ("Extraction I", None, "extraction_i"),
            ("Puller V", None, "puller_v"),
            ("Puller I", None, "puller_i"),
            ("Biased disk V", None, "bias_v"),
            ("Biased disk I", None, "bias_i"),
        ],
        "RF": [
            ("28 GHz, forward", None, "g28_fw"),
            ("18 GHz (1), forward", None, "k18_fw"),
            ("18 GHz (1), reflected", None, "k18_ref"),
            ("18 GHz (2), forward", None, "k18_2_fw"),
            ("18 GHz (2), reflected", None, "k18_2_ref"),
        ],
        "Low temperature Oven": [
            ("Oven 1 set-point", None, "lt_oven_1_sp"),
            ("Oven 1 temperature", None, "lt_oven_1_temp"),
            ("Oven 2 set-point", None, "lt_oven_2_sp"),
            ("Oven 2 temperature", None, "lt_oven_2_temp"),
        ],
        "Misc": [
            ("Glaser", None, "glaser_1"),
        ],
    }
)

DATA_LABELS = [
    DataLabel(label=f"{category} {data}", units=units, key=key)
    for category, key_data_pairs in _DATA_LABELS.items()
    for data, units, key in key_data_pairs
]

DATA_LABELS_BY_KEY = {d.key: d for d in DATA_LABELS}
