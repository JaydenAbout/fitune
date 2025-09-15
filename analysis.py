# analysis.py
# Pure functions for calculations and small helpers.

from datetime import datetime, date
from typing import Dict
from config import ACTIVITY_FACTORS, GOAL_CALORIE_MODIFIER, MACRO_DISTRIBUTION

def normalize_gender(g: str) -> str:
    """Return 'Male' or 'Female'."""
    g = (g or "").strip().lower()
    if g.startswith("m"):
        return "Male"
    elif g.startswith("f"):
        return "Female"
    raise ValueError("Gender must be 'M'/'F' or 'Male'/'Female'.")

def age_from_birthday(birthday_str: str) -> int:
    """birthday_str format: 'YYYY-MM-DD'"""
    b = datetime.strptime(birthday_str, "%Y-%m-%d").date()
    today = date.today()
    return today.year - b.year - ((today.month, today.day) < (b.month, b.day))

def calc_bmi(weight_kg: float, height_m: float) -> float:
    return round(weight_kg / (height_m ** 2), 2)

def classify_bmi(bmi: float) -> str:
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal weight"
    elif bmi < 30:
        return "Overweight"
    return "Obese"

def calc_bmr_mifflin(gender: str, weight_kg: float, height_m: float, age: int) -> float:
    """Mifflin-St Jeor. Height in meters."""
    base = 10 * weight_kg + 6.25 * (height_m * 100) - 5 * age
    if normalize_gender(gender) == "Male":
        return round(base + 5, 2)
    else:
        return round(base - 161, 2)

def calc_tdee(bmr: float, activity_level: int) -> float:
    factor = ACTIVITY_FACTORS.get(activity_level, 1.55)
    return round(bmr * factor, 2)

def calculate_macros(tdee: float, goal: str) -> Dict[str, float]:
    goal = goal.strip().lower()
    ratios = MACRO_DISTRIBUTION[goal]
    carb_kcal    = tdee * ratios["carb"]
    protein_kcal = tdee * ratios["protein"]
    fat_kcal     = tdee * ratios["fat"]
    return {
        "carb":    round(carb_kcal / 4, 1),
        "protein": round(protein_kcal / 4, 1),
        "fat":     round(fat_kcal / 9, 1),
    }

def compute_record_fields(
    user_gender: str,
    user_height_m: float,
    user_birthday: str,
    user_weight_kg: float,
    user_activity_level: int,
    user_goal: str,
) -> Dict[str, float | int | str]:
    """
    All-in-one: derive fields that will be stored into user_record.
    Returns a dict ready for DB insertion (your current schema).
    """
    age = age_from_birthday(user_birthday)
    bmi = calc_bmi(user_weight_kg, user_height_m)
    bmr = calc_bmr_mifflin(user_gender, user_weight_kg, user_height_m, age)
    tdee = calc_tdee(bmr, user_activity_level)
    # Note: macros are computed but not stored in DB by your current schema
    # macros = calculate_macros(tdee, user_goal)

    return {
        "user_weight": round(user_weight_kg, 2),
        "user_bmi": bmi,
        "user_bmr": bmr,
        "user_activity_level": user_activity_level,
        "user_tdee": tdee,
        "user_goal": user_goal,  # assumes TEXT column like "cut"/"bulk"/"maintain"
    }

