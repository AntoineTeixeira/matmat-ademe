"""
Presentation
************

Constants related to the business domain
"""

# EXTENSION NAMES
# ---------------
GHG_EMISSIONS = "ghg_emissions"
GHG_COMBUSTION = "ghg_combustion"
GHG_OTHER = "ghg_other"
RAW_MATERIALS = "raw_materials"
LABOR = "labor"
VALUE_ADDED = "value_added"
WATER = "water"
LAND_USE = "land_use"
BIOGEOCHEMICAL = "biogeochemical"
ENERGY = "energy"

# EXTENSIONS MAPPING BY CATEGORY, SUBCATEGORY AND/OR SECTOR
RAW_MATERIAL_CATEGORY_MAPPING = {
    "Biomass": [
        "Crop residues",
        "Fishery",
        "Fodder crops",
        "Forestry",
        "Grazing",
        "Grazed biomass",
        "Primary Crops",
    ],
    "Fossil Fuels": ["Fossil Fuel: Total", "Fossil Fuels"],
    "Metal Ores": ["Metal Ores"],
    "Non-Metallic Minerals": ["Non-Metallic Minerals"],
}

# UNIT NAMES
# ----------------
UNIT_GHG_EMISSIONS = "MtCO2eq"
UNIT_RAW_MATERIALS = "kt"

# UNIT CONVERSIONS
# ----------------
MULT_TO_CO2EQ = {
    "CO2": 1,
    "CH4": 28,
    "N2O": 265,
    "SF6": 23500,
    "HFC": 1,
    "PFC": 1,
}
