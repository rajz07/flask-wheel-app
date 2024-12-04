from flask import Flask, render_template, request, jsonify
import random
import pandas as pd
import os

app = Flask(__name__)

# Load the name list from Excel
name_file = "AD_NameList.xlsx"
df = pd.read_excel(name_file)

# Ensure there is a TableNumber column
if "TableNumber" not in df.columns:
    df["TableNumber"] = None

# Recalculate table capacity based on the existing Excel data
table_capacity = {i: 0 for i in range(1, 8)}
for table_number in df["TableNumber"].dropna().astype(int):
    if table_number in table_capacity:
        table_capacity[table_number] += 1


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

        # Get available tables that are not full
        available_tables = [table for table, count in table_capacity.items() if count < 10]

        # Ensure there are available tables
        if not available_tables:
            return jsonify({"error": "All tables are full!"}), 400

        # Assign a random available table
        table = random.choice(available_tables)
        df.loc[df["NameList"] == name, "TableNumber"] = table
        table_capacity[table] += 1
        df.to_excel(name_file, index=False)  # Update the Excel file
        return jsonify({"table": table})

    return jsonify({"error": "Invalid name"}), 400


@app.route("/available_tables")
def available_tables():
    # Refresh the data from the Excel sheet
    df = pd.read_excel(name_file)

    # Count table assignments and filter tables with capacity < 10
    table_status = {i: (df["TableNumber"] == i).sum() for i in range(1, 8)}
    available_tables = [table for table, count in table_status.items() if count < 10]

    return jsonify({"available_tables": available_tables})






@app.route("/update_assignment", methods=["POST"])
def update_assignment():
    data = request.json
    name = data.get("name")
    table = data.get("table")

    if name in df["NameList"].values:
        assigned_table = df.loc[df["NameList"] == name, "TableNumber"].values[0]
        if pd.notna(assigned_table):
            return jsonify({"error": f"{name} is already assigned to Table {int(assigned_table)}"}), 400

        if table_capacity[int(table)] >= 10:
            return jsonify({"error": f"Table {int(table)} is full"}), 400

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
    
@app.route("/clear_all_data", methods=["POST"])
def clear_all_data():
    try:
        df["TableNumber"] = None
        df.to_excel(name_file, index=False)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/manually_assign_table", methods=["POST"])
def manually_assign_table():
    data = request.json
    name = data.get("name")
    table = data.get("table")

    if name not in df["NameList"].values:
        return jsonify({"error": "Name not found"}), 400

    try:
        df.loc[df["NameList"] == name, "TableNumber"] = int(table)
        df.to_excel(name_file, index=False)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/clear_person_table", methods=["POST"])
def clear_person_table():
    data = request.json
    name = data.get("name")

    if name not in df["NameList"].values:
        return jsonify({"error": "Name not found"}), 400

    try:
        df.loc[df["NameList"] == name, "TableNumber"] = None
        df.to_excel(name_file, index=False)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
