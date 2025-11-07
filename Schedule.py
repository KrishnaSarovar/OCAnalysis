import pandas as pd
from datetime import datetime, timedelta

# Load the data from CSV or Excel
file_path = "lectures.xlsx"  # Change to "lectures.csv" if using CSV
df = pd.read_excel(file_path)  # Use pd.read_csv(file_path) if using CSV

# Define start date (Monday-based week start)
start_date = datetime(2025, 3, 31)  # First Monday after March 27, 2025
week_max_minutes = 400  # Maximum minutes per week

# Initialize variables
weekly_schedule = []
current_week = []
current_week_minutes = 0
week_start = start_date

# Iterate over lectures
for index, row in df.iterrows():
    lecture_name = row["Lecture Name"]
    minutes = row["Time"]

    if current_week_minutes + minutes > week_max_minutes:
        # Save completed week
        week_end = week_start + timedelta(days=6)
        weekly_schedule.append([week_start.strftime("%d-%b-%y"), week_end.strftime("%d-%b-%y"), current_week, current_week_minutes])

        # Start a new week
        week_start += timedelta(days=7)
        current_week = []
        current_week_minutes = 0

    # Add lecture to current week
    current_week.append((lecture_name, minutes))
    current_week_minutes += minutes

# Add the last week if it contains any lectures
if current_week:
    week_end = week_start + timedelta(days=6)
    weekly_schedule.append([week_start.strftime("%d-%b-%y"), week_end.strftime("%d-%b-%y"), current_week, current_week_minutes])

# Create an output DataFrame
output_data = []
for week in weekly_schedule:
    week_start, week_end, lectures, total_minutes = week
    for lecture in lectures:
        output_data.append([week_start, week_end, lecture[0], lecture[1], total_minutes])

output_df = pd.DataFrame(output_data, columns=["Week Start", "Week End", "Lecture Name", "Time", "Total Week Minutes"])

# Save the output to an Excel file
output_df.to_excel("weekly_schedule.xlsx", index=False)

print("Schedule saved as 'weekly_schedule.xlsx'")
