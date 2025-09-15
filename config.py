# config.py
# Central place for defaults and lookup tables.


ACTIVITY_FACTORS = {
    1: 1.2,
    2: 1.375,
    3: 1.55,
    4: 1.725,
    5: 1.9,
}


GOAL_CALORIE_MODIFIER = {
    "cut": 0.8,
    "bulk": 1.1,
    "maintain": 1.0,
}


MACRO_DISTRIBUTION = {
    "cut":      {"carb": 0.35, "protein": 0.40, "fat": 0.25},
    "bulk":     {"carb": 0.50, "protein": 0.30, "fat": 0.20},
    "maintain": {"carb": 0.45, "protein": 0.30, "fat": 0.25},
}

# Validation ranges (you can tweak later)
WEIGHT_KG_MIN, WEIGHT_KG_MAX = 10.0, 400.0
HEIGHT_M_MIN, HEIGHT_M_MAX   = 0.5, 4.0
AGE_MIN, AGE_MAX             = 1, 120
