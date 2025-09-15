# Fitune – Fitness & Nutrition Tracker 🏋️‍♂️🥗

Fitune is a personal side project to build a **fitness and nutrition tracking app** using **Python** and **SQLite**.  
Its goal is to help users log their daily nutrition, workouts, and body metrics, then generate insights and progress visualizations.

## 🔑 Features (Current)

- **User Profile & Metrics:** Weight, BMI, BMR, activity level, daily goals  
- **Session Logging:** Record daily nutrition and workouts in a local SQLite database  
- **TDEE Calculation:** Automatically calculate Total Daily Energy Expenditure  
- **Basic Reporting:** Print summary of records for quick review  

## 🛠️ Tech Stack

- **Python 3**
- **SQLite3** for data storage

## 🧭 Roadmap

- [ ] Add dashboard visualization (Matplotlib / Plotly)
- [ ] Implement goal tracking & weekly progress summary
- [ ] Build simple web frontend (Flask or Streamlit)
- [ ] Export data to CSV for external analysis

## 📂 Project Structure

```text
fitune/
├── main.py           # CLI entry point
├── database.py       # SQLite schema & CRUD helpers
├── analysis.py       # Data analysis & visualization
├── config.py         # Configurations & constants
├── main.db           # Local SQLite database (ignored in .gitignore)
├── ideas.txt         # Future feature brainstorming
└── README.md
