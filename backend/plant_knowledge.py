"""Base de conocimiento agronómico por cultivo y enfermedad (PlantVillage + Colombia)."""
from __future__ import annotations

import re

# --- Plantas ---
PLANT_NAMES_ES: dict[str, tuple[str, str, str]] = {
    "Apple": ("Manzana", "Malus domestica", "Frutal"),
    "Blueberry": ("Arándano", "Vaccinium corymbosum", "Frutal"),
    "Cherry_(including_sour)": ("Cerezo", "Prunus avium", "Frutal"),
    "Corn_(maize)": ("Maíz", "Zea mays", "Cereal"),
    "Grape": ("Uva", "Vitis vinifera", "Frutal"),
    "Orange": ("Naranja / Cítrico", "Citrus × sinensis", "Frutal"),
    "Peach": ("Durazno", "Prunus persica", "Frutal"),
    "Pepper,_bell": ("Pimentón", "Capsicum annuum", "Hortícola"),
    "Potato": ("Papa", "Solanum tuberosum", "Tubérculo"),
    "Raspberry": ("Frambuesa", "Rubus idaeus", "Frutal"),
    "Soybean": ("Soya", "Glycine max", "Leguminosa"),
    "Squash": ("Calabaza", "Cucurbita pepo", "Hortícola"),
    "Strawberry": ("Fresa", "Fragaria × ananassa", "Frutal"),
    "Tomato": ("Tomate", "Solanum lycopersicum", "Hortícola"),
}

# --- Enfermedades / estados (clave normalizada → español) ---
CONDITION_ES: dict[str, str] = {
    "healthy": "Estado saludable — sin síntomas visibles de enfermedad o plaga",
    "Apple_scab": "Sarna del manzano (Venturia inaequalis)",
    "Black_rot": "Pudrición negra (hongo)",
    "Cedar_apple_rust": "Roya del cedro-manzano (Gymnosporangium)",
    "Powdery_mildew": "Oídio (hongo)",
    "Cercospora_leaf_spot Gray_leaf_spot": "Mancha foliar por Cercospora",
    "Common_rust_": "Roya común del maíz (Puccinia sorghi)",
    "Northern_Leaf_Blight": "Tizón foliar norteño del maíz",
    "Esca_(Black_Measles)": "Esca / measles negro de la vid",
    "Leaf_blight_(Isariopsis_Leaf_Spot)": "Tizón foliar / mancha Isariopsis",
    "Haunglongbing_(Citrus_greening)": "Huanglongbing / enverdecimiento de cítricos",
    "Bacterial_spot": "Mancha bacteriana (Xanthomonas)",
    "Early_blight": "Tizón temprano (Alternaria solani)",
    "Late_blight": "Tizón tardío (Phytophthora infestans)",
    "Leaf_scorch": "Quemadura foliar",
    "Leaf_Mold": "Moho foliar (Passalora fulva)",
    "Septoria_leaf_spot": "Mancha foliar por Septoria",
    "Spider_mites Two-spotted_spider_mite": "Daño por ácaro de dos manchas (Tetranychus urticae)",
    "Target_Spot": "Mancha anillada (Target spot)",
    "Tomato_mosaic_virus": "Virus del mosaico del tomate",
    "Tomato_Yellow_Leaf_Curl_Virus": "Virus del rizado amarillo de las hojas del tomate",
}

DISEASE_TEMPLATES: dict[str, dict] = {
    "fungal": {
        "treatment": [
            "Retirar y destruir hojas o frutos infectados",
            "Aplicar fungicida autorizado por ICA (cúprico, mancozeb o específico según cultivo)",
            "Mejorar ventilación y espaciamiento entre plantas",
            "Evitar riego por aspersión en horas de alta humedad",
        ],
        "causes": [
            "Humedad relativa alta (>80%) y lluvias prolongadas",
            "Rocío nocturno y poca ventilación del follaje",
            "Restos de cultivo infectados en el suelo",
            "Temperaturas moderadas favorables al hongo",
        ],
        "prevention": [
            "Variedades resistentes cuando existan",
            "Rotación de cultivos",
            "Desinfección de herramientas",
            "Monitoreo semanal en temporada de lluvias",
        ],
    },
    "bacterial": {
        "treatment": [
            "Eliminar plantas muy infectadas",
            "Aplicar bactericida cúprico según etiqueta ICA",
            "No trabajar el cultivo mojado (evitar dispersión)",
            "Usar semilla o plantín certificado",
        ],
        "causes": [
            "Salpicadura de agua de suelo a hojas",
            "Heridas en tejido por granizo o herramientas",
            "Semilla o material de propagación infectado",
            "Clima cálido-húmedo",
        ],
        "prevention": ["Trasplante de material sano", "Riego al suelo", "Rotación", "Higiene de herramientas"],
    },
    "viral": {
        "treatment": [
            "Eliminar plantas infectadas (no hay cura viral)",
            "Controlar vector (mosca blanca, pulgón, ácaros)",
            "Usar plantín certificado libre de virus",
            "Desinfectar herramientas con hipoclorito",
        ],
        "causes": [
            "Transmisión por insectos vectores (mosca blanca, pulgones)",
            "Material infectado de vivero",
            "Contacto con plantas enfermas",
            "No hay transmisión por semilla en la mayoría de casos",
        ],
        "prevention": ["Variedades tolerantes", "Mallas antiinsectos", "Control integrado de vectores"],
    },
    "pest": {
        "treatment": [
            "Confirmar plaga con lupa (huevo, larva, adulto)",
            "Jabón potásico o aceite hortícola en infestación leve",
            "Acaricida/insecticida según etiqueta ICA",
            "Liberar enemigos naturales si están disponibles",
        ],
        "causes": [
            "Falta de biodiversidad en el agroecosistema",
            "Plantas débiles por estrés hídrico o nutricional",
            "Temporada seca o clima favorable al insecto",
            "Uso previo de insecticidas de amplio espectro",
        ],
        "prevention": ["Monitoreo con trampas", "Plantas refugio", "Riego y nutrición adecuados"],
    },
    "healthy": {
        "treatment": [
            "Continuar buenas prácticas agronómicas",
            "Monitoreo preventivo cada 7–10 días",
            "Registrar estado del lote para trazabilidad",
        ],
        "causes": [],
        "prevention": [
            "Riego y drenaje adecuados",
            "Fertilización según análisis de suelo",
            "Sanidad en herramientas y viveros",
            "Rotación cuando aplique",
        ],
    },
    "citrus": {
        "treatment": [
            "Reportar al ICA / autoridad fitosanitaria (enfermedad cuarentenaria)",
            "Eliminar árboles muy infectados según protocolo oficial",
            "Control estricto del vector (psílido asiático)",
            "No trasplantar material de zonas infectadas",
        ],
        "causes": [
            "Bacteria Candidatus Liberibacter transmitida por psílido",
            "Material de propagación infectado",
            "Proximidad a huertos enfermos",
        ],
        "prevention": ["Plantín certificado", "Monitoreo de psílido", "Mallas en viveros"],
    },
}


def normalize_class_name(class_name: str) -> tuple[str, str, str, str, str, str, str]:
    """Parsea Tomato___Late_blight en metadatos agronómicos."""
    if "___" in class_name:
        plant_part, cond_part = class_name.split("___", 1)
    else:
        plant_part, cond_part = class_name, "healthy"

    plant_key = plant_part.strip()
    cond_key = cond_part.strip()

    if plant_key in PLANT_NAMES_ES:
        plant_es, scientific, category = PLANT_NAMES_ES[plant_key]
    else:
        plant_es = plant_key.replace("_", " ").replace(",", "").replace("(including sour)", "").strip()
        scientific = ""
        category = "Cultivo"

    cond_es = CONDITION_ES.get(cond_key)
    if not cond_es:
        cond_es = cond_key.replace("_", " ").replace("  ", " ").strip()

    kind = classify_condition(cond_key, cond_es)
    return plant_key, plant_es, scientific, category, cond_key, cond_es, kind


def classify_condition(cond_key: str, cond_es: str) -> str:
    lower = (cond_key + " " + cond_es).lower()
    if "healthy" in lower or cond_key == "healthy":
        return "healthy"
    if "mite" in lower or "spider" in lower or "ácaro" in lower:
        return "pest"
    if "virus" in lower or "mosaic" in lower or "curl" in lower:
        return "viral"
    if "bacterial" in lower or "bacteriana" in lower:
        return "bacterial"
    if "huanglongbing" in lower or "greening" in lower or "citrus" in lower:
        return "citrus"
    if any(x in lower for x in ("blight", "rust", "rot", "mildew", "spot", "scab", "esca", "mold", "scorch")):
        return "fungal"
    return "fungal"


def colombia_regions(category: str, plant_es: str) -> list[str]:
    mapping = {
        "Tomate": ["Boyacá", "Cundinamarca", "Antioquia", "Santander", "Nariño"],
        "Papa": ["Boyacá", "Nariño", "Cundinamarca", "Antioquia"],
        "Maíz": ["Huila", "Tolima", "Meta", "Córdoba", "Cundinamarca"],
        "Naranja / Cítrico": ["Meta", "Tolima", "Valle del Cauca", "Atlántico"],
        "Café": ["Eje Cafetero", "Huila", "Nariño"],
    }
    return mapping.get(plant_es, ["Altiplano cundiboyacense", "Eje Cafetero", "Valle del Cauca", "Santander", "Antioquia"])


def season_for(kind: str, plant_es: str) -> str:
    if kind == "healthy":
        return f"Monitoreo continuo del {plant_es.lower()}; siembra según calendario regional ICA"
    if kind in ("fungal", "bacterial"):
        return "Mayor riesgo en lluvias Andinas: marzo–junio y septiembre–diciembre"
    if kind == "viral":
        return "Vectores activos en época seca-cálida y en invernaderos todo el año"
    if kind == "pest":
        return "Picos de plaga en transición seca-lluviosa; monitoreo quincenal"
    return "Consultar calendario fitosanitario del municipio"
