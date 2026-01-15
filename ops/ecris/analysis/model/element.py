from dataclasses import dataclass


@dataclass(eq=True, frozen=True)
class Element:
    name: str
    symbol: str
    atomic_mass: float
    atomic_number: int


PERSISTANT_ELEMENTS = [
    Element(name=n, symbol=s, atomic_mass=a, atomic_number=z)
    for n, s, a, z in [
        ("Carbon", "C", 12, 6),
        ("Nitrogen", "N", 14, 7),
        ("Oxygen", "O", 16, 8),
    ]
]

VARIABLE_ELEMENTS = [
    Element(name=n, symbol=s, atomic_mass=a, atomic_number=z)
    for n, s, a, z in [
        ("Vanadium", "V", 51, 23),
        ("Titanium", "Ti", 50, 22),
        ("Uranium", "U", 238, 92),
    ]
]

