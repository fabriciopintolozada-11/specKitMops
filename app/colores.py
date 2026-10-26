"""Paleta predefinida de colores para las materias (FR-003)."""

PALETA: list[dict[str, str]] = [
    {"nombre": "Azul", "codigo": "#1E66F5"},
    {"nombre": "Rojo", "codigo": "#D20F39"},
    {"nombre": "Verde", "codigo": "#40A02B"},
    {"nombre": "Naranja", "codigo": "#FE640B"},
    {"nombre": "Morado", "codigo": "#8839EF"},
    {"nombre": "Rosa", "codigo": "#EA76CB"},
    {"nombre": "Turquesa", "codigo": "#179299"},
    {"nombre": "Gris", "codigo": "#6C6F85"},
]

CODIGOS_VALIDOS: frozenset[str] = frozenset(color["codigo"] for color in PALETA)
