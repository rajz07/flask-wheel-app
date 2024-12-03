from flask import Flask, render_template, request, jsonify
import random
import pandas as pd

app = Flask(__name__)

# Load the name list from Excel
name_file = "AD_NameList.xlsx"
df = pd.read_excel(name_file)

# Ensure there is a TableNumber column
if "TableNumber" not in df.columns:
    df["TableNumber"] = None

name_list = df["NameList"].tolist()

# Initialize table capacity
table_capacity = {i: 0 for i in range(1, 8)}  # Tables 1 to 7 with max capacity of 10

@app.route("/")
def index():
    # Exclude names that already have an assigned table
    available_names = df[df["TableNumber"].isna()]["NameList"].tolist()
    return render_template("index.html", names=available_names)

@app.route("/wheel")
def wheel():
    return render_template("wheel.html")

@app.route("/assign_table", methods=["POST"])
def assign_table():
    name = request.json.get("name")
    if name in df["NameList"].values:
        # Check if the name already has a table assigned
        assigned_table = df.loc[df["NameList"] == name, "TableNumber"].values[0]
        if pd.notna(assigned_table):
            return jsonify({"error": f"{name} is already assigned to Table {int(assigned_table)}"}), 400

        # Assign a random table
        while True:
            table = random.randint(1, 7)
            if table_capacity[table] < 10:  # Ensure table isn't full
                df.loc[df["NameList"] == name, "TableNumber"] = table
                table_capacity[table] += 1
                df.to_excel(name_file, index=False)  # Update the Excel file
                return jsonify({"table": table})
    return jsonify({"error": "Invalid name"}), 400


@app.route("/update_assignment", methods=["POST"])
def update_assignment():
    data = request.json
    name = data.get("name")
    table = data.get("table")

    if name in df["NameList"].values:
        assigned_table = df.loc[df["NameList"] == name, "TableNumber"].values[0]
        if pd.notna(assigned_table):
            return jsonify({"error": f"{name} is already assigned to Table {int(assigned_table)}"}), 400

        df.loc[df["NameList"] == name, "TableNumber"] = table  # Assign table
        table_capacity[int(table)] += 1
        df.to_excel(name_file, index=False)  # Save to Excel
        return jsonify({"success": True})

    return jsonify({"error": "Invalid name or already assigned"}), 400

@app.route("/view_assignments")
def view_assignments():
    # Read the updated Excel file
    updated_df = pd.read_excel(name_file)
    
    # Convert table number to integers for display (removing decimals)
    updated_df["TableNumber"] = updated_df["TableNumber"].apply(
        lambda x: int(x) if pd.notna(x) else None
    )
    
    # Calculate table status
    table_status = {i: (updated_df["TableNumber"] == i).sum() for i in range(1, 8)}
    
    # Convert to a list of dictionaries for easier rendering in HTML
    assignments = updated_df.to_dict(orient="records")
    return render_template("view_assignments.html", assignments=assignments, table_status=table_status)



if __name__ == "__main__":
    app.run(debug=True)
