"""Especies que el modelo SÍ puede identificar (PlantVillage)."""
from __future__ import annotations

from plant_knowledge import PLANT_NAMES_ES

# Lista única en español para mostrar al usuario
SUPPORTED_SPECIES_ES: list[str] = sorted(
    {name for name, _, _ in PLANT_NAMES_ES.values()}
)

# Umbral: por debajo de esto NO afirmamos una especie (evita "uva" al 30% con orégano)
MIN_CLASS_CONFIDENCE = 0.55
MIN_SPECIES_CONFIDENCE = 0.48
MIN_GAP_TOP_TWO_SPECIES = 0.12


def get_supported_species() -> list[str]:
    return SUPPORTED_SPECIES_ES.copy()
