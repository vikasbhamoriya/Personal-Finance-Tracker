from flask import Flask, render_template, request, send_file
import csv
import os
from datetime import datetime
from collections import defaultdict

app = Flask(__name__)

# Ensure data directory exists
DATA_DIR = "expense_data"
os.makedirs(DATA_DIR, exist_ok=True)

def get_current_filename():
    """Generate filename with current date"""
    today = datetime.now().strftime("%Y-%m-%d")
    return os.path.join(DATA_DIR, f"expenses_{today}.csv")

def save_expenses(expenses):
    """Save expenses to today's CSV file, append if file exists"""
    filename = get_current_filename()
    file_exists = os.path.isfile(filename)
    
    with open(filename, "a", newline="") as file:
        writer = csv.writer(file)
        
        # Write header if new file
        if not file_exists:
            writer.writerow(["Timestamp", "Category", "Item", "Amount"])
            
        # Write each expense item
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for category, items in expenses.items():
            for name, amount in items.items():
                writer.writerow([timestamp, category, name, amount])

def get_all_expenses():
    """Combine all historical expense data"""
    all_expenses = defaultdict(lambda: defaultdict(dict))  # year -> month -> category -> items
    monthly_totals = defaultdict(lambda: defaultdict(int))  # year -> month -> total
    category_totals = defaultdict(lambda: defaultdict(int)) # year -> category -> total
    overall_totals = defaultdict(int)  # category -> total
    
    try:
        for filename in sorted(os.listdir(DATA_DIR)):
            if filename.endswith(".csv"):
                # Extract year and month from filename
                date_part = filename.split('_')[1].split('.')[0]
                year_month = datetime.strptime(date_part, "%Y-%m-%d").strftime("%Y-%m")
                year = datetime.strptime(date_part, "%Y-%m-%d").strftime("%Y")
                month = datetime.strptime(date_part, "%Y-%m-%d").strftime("%B")
                
                with open(os.path.join(DATA_DIR, filename), "r") as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        category = row["Category"]
                        amount = int(row["Amount"])
                        
                        # Store detailed data
                        item_name = row["Item"]
                        all_expenses[year][month][category][item_name] = amount
                        
                        # Calculate totals
                        monthly_totals[year][month] += amount
                        category_totals[year][category] += amount
                        overall_totals[category] += amount
                        
    except FileNotFoundError:
        pass
    
    return {
        "detailed": dict(all_expenses),
        "monthly_totals": dict(monthly_totals),
        "category_totals": dict(category_totals),
        "overall_totals": dict(overall_totals)
    }

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    expense_data = get_all_expenses()
    if not expense_data["detailed"]:  # If no data exists
        return render_template("dashboard.html", 
                            no_data=True,
                            detailed_expenses={},
                            monthly_totals={},
                            category_totals={},
                            overall_totals={})
    
    return render_template("dashboard.html",
                         no_data=False,
                         detailed_expenses=expense_data["detailed"],
                         monthly_totals=expense_data["monthly_totals"],
                         category_totals=expense_data["category_totals"],
                         overall_totals=expense_data["overall_totals"])

@app.route("/submit", methods=["POST"])
def submit():
    salary = int(request.form.get("salary"))
    categories = ["EMI", "Groceries", "Bills", "Investment", "Udhari", "Other"]
    expenses = {cat: {} for cat in categories}
    total_expense = 0

    for category in categories:
        names = request.form.getlist(f"{category}_name[]")
        costs = request.form.getlist(f"{category}_cost[]")
        for name, cost in zip(names, costs):
            if name and cost:
                cost_val = int(cost)
                expenses[category][name] = cost_val
                total_expense += cost_val

    # Save to daily CSV file
    save_expenses(expenses)
    
    saving = salary - total_expense
    return render_template("index.html", 
                         expenses=expenses, 
                         salary=salary, 
                         total=total_expense,
                         saving=saving)

@app.route("/download")
def download_csv():
    return send_file(get_current_filename(), as_attachment=True)

@app.route("/download-all")
def download_all_csv():
    # Create a combined file for download
    combined_filename = os.path.join(DATA_DIR, "all_expenses.csv")
    with open(combined_filename, "w", newline="") as outfile:
        writer = csv.writer(outfile)
        writer.writerow(["Timestamp", "Category", "Item", "Amount"])
        
        for filename in sorted(os.listdir(DATA_DIR)):
            if filename.endswith(".csv") and filename != "all_expenses.csv":
                with open(os.path.join(DATA_DIR, filename), "r") as infile:
                    reader = csv.reader(infile)
                    next(reader)  # Skip header
                    for row in reader:
                        writer.writerow(row)
    
    return send_file(combined_filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)