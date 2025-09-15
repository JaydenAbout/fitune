# main.py
from database import init_db, insert_user_profile, insert_user_record
from analysis import (
    normalize_gender, age_from_birthday, calc_bmi, classify_bmi,
    calc_bmr_mifflin, calc_tdee, calculate_macros, compute_record_fields
)
from config import (
    GOAL_CALORIE_MODIFIER, MACRO_DISTRIBUTION,
    WEIGHT_KG_MIN, WEIGHT_KG_MAX, HEIGHT_M_MIN, HEIGHT_M_MAX
)

# --- init DB ---
init_db()

# --- input helpers (keep your existing ones, below is a minimal version) ---

user_name = input('Please tell me your name: ')
print(f'Hi, {user_name}.\n')

# gender first (so profile is complete)
def choose_gender():
    while True:
        g = input("Enter F or M: ").strip()
        try:
            return "Female" if g.lower().startswith("f") else "Male" if g.lower().startswith("m") else (_ for _ in ()).throw(ValueError)
        except ValueError:
            print("Invalid input. Please enter F or M.\n")

user_gender = choose_gender()
print(f'You selected: {user_gender}.\n')

# birthday
from datetime import datetime, date
def input_birthday():
    while True:
        s = input('Please enter your birthday (YYYY-MM-DD): ').strip()
        try:
            _ = datetime.strptime(s, '%Y-%m-%d')  # validate
            age = age_from_birthday(s)
            if 1 <= age <= 120:
                return s, age
        except ValueError:
            pass
        print('Invalid date or age out of range. Try again.\n')

user_birthday, user_age = input_birthday()
print(f'Your birthday is {user_birthday}, and you are {user_age} years old.\n')

# height (meters in storage, like your current formulas)
def input_height():
    while True:
        try:
            cm = float(input('Enter your height in cm: '))
            m = cm / 100.0
            if HEIGHT_M_MIN <= m <= HEIGHT_M_MAX:
                return round(m, 2)
        except ValueError:
            pass
        print(f'Height out of range ({HEIGHT_M_MIN*100:.0f}–{HEIGHT_M_MAX*100:.0f} cm) or invalid. Try again.\n')

user_height = input_height()
print(f'Your height is: {user_height} m.\n')

# --- create profile in DB ---
user_id = insert_user_profile(user_name, user_birthday, user_gender, user_height)
print(f'Profile created. user_id={user_id}\n')

# weight for this record
def input_weight():
    while True:
        unit = input("Type 'kg' or 'lb': ").strip().lower()
        if unit not in {"kg", "lb"}:
            print("Invalid unit.\n")
            continue
        try:
            w = float(input(f'Enter your weight in {unit}: '))
            if unit == 'lb':
                w *= 0.453592
            if WEIGHT_KG_MIN <= w <= WEIGHT_KG_MAX:
                return round(w, 2)
        except ValueError:
            pass
        print(f'Weight out of range ({WEIGHT_KG_MIN}-{WEIGHT_KG_MAX} kg) or invalid. Try again.\n')

user_weight = input_weight()
print(f'Your weight is: {user_weight} kg.\n')

# activity level
activity_descriptions = {
    1: 'Sedentary (little to no exercise)',
    2: 'Lightly active (light exercise/sports 1–3 days/week)',
    3: 'Moderately active (moderate exercise/sports 3–5 days/week)',
    4: 'Very active (hard exercise/sports 6–7 days/week)',
    5: 'Super active (very hard exercise & physical job or 2× training)'
}
def choose_activity_level():
    print('Activity Level is critical in calculating your daily calories.')
    for k, v in activity_descriptions.items():
        print(f"Type {k} if you are {v}.")
    while True:
        try:
            lvl = int(input('Enter a number from 1 to 5: '))
            if lvl in activity_descriptions:
                return lvl
        except ValueError:
            pass
        print('Invalid input. Try again.\n')

user_activity_level = choose_activity_level()
print(f'You selected: {user_activity_level} – {activity_descriptions[user_activity_level]}.\n')

# goal
goals = {1: 'cut', 2: 'bulk', 3: 'maintain'}
def choose_goal():
    print('Macronutrient grams are based on TDEE and your goal.')
    for k, v in goals.items():
        print(f"Type {k} if you want to {v}.")
    while True:
        try:
            c = int(input('Enter 1–3: '))
            if c in goals:
                return goals[c]
        except ValueError:
            pass
        print('Invalid input. Try again.\n')

user_goal = choose_goal()

# --- analysis using functions from analysis.py ---
# quick on-screen feedback (BMI class etc.)
bmi = calc_bmi(user_weight, user_height)
print(f'Your BMI Index is: {bmi} — {classify_bmi(bmi)}\n')

# build all record fields in one shot
record_fields = compute_record_fields(
    user_gender=user_gender,
    user_height_m=user_height,
    user_birthday=user_birthday,
    user_weight_kg=user_weight,
    user_activity_level=user_activity_level,
    user_goal=user_goal,
)

# optional: show macros to the user (not stored in current DB schema)
tdee = record_fields["user_tdee"]
macros = calculate_macros(tdee, user_goal)
print(f'Goal: {user_goal}. TDEE: {tdee} kcal.')
print('Recommended macros (grams):',
      f"Carb {macros['carb']}, Protein {macros['protein']}, Fat {macros['fat']}")

# --- write one record for this user ---
insert_user_record(
    user_id=user_id,
    user_weight=record_fields["user_weight"],
    user_bmi=record_fields["user_bmi"],
    user_bmr=record_fields["user_bmr"],
    user_activity_level=record_fields["user_activity_level"],
    user_tdee=record_fields["user_tdee"],
    user_goal=record_fields["user_goal"],
)

print("\nSaved this session as a new record for your profile.")


from database import init_db, get_profile_core, insert_user_record
from analysis import compute_record_fields, calc_bmi, classify_bmi, calculate_macros

def log_session_for_user_id(user_id: int):
    """For an existing user: input today's data -> compute -> store one record."""
    init_db()

    core = get_profile_core(user_id)
    if not core:
        print(f"No profile found for user_id={user_id}.")
        return
    user_birthday, user_gender, user_height = core

    # ---- today’s inputs (reuse your existing input helpers) ----
    user_weight = input_weight()                 # kg (your existing function)
    user_activity_level = choose_activity_level()# 1..5
    user_goal = choose_goal()                    # 'cut'/'bulk'/'maintain'

    # ---- compute all fields that go into user_record ----
    fields = compute_record_fields(
        user_gender=user_gender,
        user_height_m=user_height,
        user_birthday=user_birthday,
        user_weight_kg=user_weight,
        user_activity_level=user_activity_level,
        user_goal=user_goal,
    )

    # quick feedback on screen (optional)
    bmi = calc_bmi(fields["user_weight"], user_height)
    print(f"BMI: {bmi} — {classify_bmi(bmi)}")
    print(f"BMR: {fields['user_bmr']}  TDEE: {fields['user_tdee']}  Goal: {fields['user_goal']}")
    macros = calculate_macros(fields["user_tdee"], user_goal)
    print(f"Macros (g)  Carb: {macros['carb']}  Protein: {macros['protein']}  Fat: {macros['fat']}")

    # ---- store one new record (record_id auto-increments per user inside your insert) ----
    new_rec_no = insert_user_record(
        user_id=user_id,
        user_weight=fields["user_weight"],
        user_bmi=fields["user_bmi"],
        user_bmr=fields["user_bmr"],
        user_activity_level=fields["user_activity_level"],
        user_tdee=fields["user_tdee"],
        user_goal=fields["user_goal"],
    )

    print(f"Saved. user_id={user_id}, record_no(within user)={new_rec_no}")


if __name__ == "__main__":
    uid = int(input("Enter your user_id: ").strip())
    log_session_for_user_id(uid)
