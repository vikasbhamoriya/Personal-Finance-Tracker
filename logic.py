import csv

total_salary = int(input("Enter your salary: "))
total_expense = 0
expenses = {
    "EMI": {},
    "Groceries": {},
    "Bills": {},
    "Investment": {},
    "Udhari": {},
    "Other": {}
}

print("\n--- Enter your expenses category-wise (Press Enter to skip) ---")

for category in expenses:
    print(f"\n--- {category} ---")
    while True:
        name = input(f"Enter {category} name (or press Enter to stop): ")
        if name == "":
            break
        try:
            cost = int(input(f"Enter cost for '{name}': "))
            expenses[category][name] = cost
            total_expense += cost
        except ValueError:
            print("Please enter a valid number.")

# Summary
print("\n--- Expense Summary ---")
for category, items in expenses.items():
    if items:
        print(f"\n{category}:")
        for name, cost in items.items():
            print(f"  {name} - ₹{cost}")

print(f"\nTotal Expense: ₹{total_expense}")
print(f"Total Saving: ₹{total_salary - total_expense}")

with open("monthly_expenses.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Category", "Item", "Amount"])
    for category, items in expenses.items():
        for name, amount in items.items():
            writer.writerow([category, name, amount])