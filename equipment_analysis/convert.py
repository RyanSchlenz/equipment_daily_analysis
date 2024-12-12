import pandas as pd

# Load the CSV file
csv_file = 'aggregated_data.csv'  # Replace with your CSV file path
xlsx_file = 'aggregated_data.xlsx'  # Replace with desired output file path

# Read the CSV file into a DataFrame
df = pd.read_csv(csv_file)

# Write the DataFrame to an Excel file
df.to_excel(xlsx_file, index=False, engine='openpyxl')

print(f"CSV file has been successfully converted to {xlsx_file}")
