"""Script to create sample Excel file for testing."""
import pandas as pd
from datetime import datetime, timedelta

# Create sample employee data
employees = []
start_date = datetime(2024, 1, 1)

for i in range(1, 31):
    employees.append({
        "employee_id": f"EMP{i:03d}",
        "name": f"Employee {i}",
        "department": ["Sales", "Marketing", "Engineering", "HR", "Finance"][i % 5],
        "position": ["Manager", "Analyst", "Developer", "Coordinator", "Specialist"][i % 5],
        "hire_date": (start_date + timedelta(days=i*10)).strftime("%Y-%m-%d"),
        "salary": 50000 + (i * 1000),
        "active": i % 10 != 0  # Every 10th employee is inactive
    })

# Create DataFrame
df_employees = pd.DataFrame(employees)

# Create sample project data
projects = []
for i in range(1, 16):
    projects.append({
        "project_id": f"PRJ{i:03d}",
        "project_name": f"Project {i}",
        "budget": 100000 + (i * 5000),
        "start_date": (start_date + timedelta(days=i*5)).strftime("%Y-%m-%d"),
        "end_date": (start_date + timedelta(days=i*5 + 90)).strftime("%Y-%m-%d"),
        "status": ["Planning", "In Progress", "Completed", "On Hold"][i % 4],
        "team_size": 3 + (i % 5)
    })

df_projects = pd.DataFrame(projects)

# Create Excel file with multiple sheets
with pd.ExcelWriter("employees_projects.xlsx", engine="openpyxl") as writer:
    df_employees.to_excel(writer, sheet_name="Employees", index=False)
    df_projects.to_excel(writer, sheet_name="Projects", index=False)

print("Excel file 'employees_projects.xlsx' created successfully!")
print(f"Employees sheet: {len(df_employees)} rows")
print(f"Projects sheet: {len(df_projects)} rows")
