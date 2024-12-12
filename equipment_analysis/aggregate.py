import pandas as pd

# Load the updated CSV file with Equipment Category and Status
updated_ticket_data_path = 'organized_data.csv'  # Replace with your file path
df = pd.read_csv(updated_ticket_data_path)

# Ensure relevant columns are treated as strings and handle possible NaN values
if 'Ticket created - Day of month' in df.columns:
    df['Ticket created - Day of month'] = df['Ticket created - Day of month'].astype(float).fillna(0).astype(int)
if 'Ticket created - Month' in df.columns:
    df['Ticket created - Month'] = df['Ticket created - Month'].astype(str).str.strip()
if 'Ticket created - Year' in df.columns:
    df['Ticket created - Year'] = df['Ticket created - Year'].astype(str).str.strip()  # Ensure year is string

# Combine 'Ticket created - Day of month', 'Ticket created - Month', and 'Ticket created - Year' into a single 'Date' column
if all(col in df.columns for col in ['Ticket created - Day of month', 'Ticket created - Month', 'Ticket created - Year']):
    df['Date'] = df.apply(lambda row: f"{row['Ticket created - Month']}/{row['Ticket created - Day of month']:02d}/{row['Ticket created - Year']}", axis=1)

    # Replace month names with numerical values for proper datetime conversion
    month_mapping = {
        'January': '01', 'February': '02', 'March': '03', 'April': '04', 'May': '05', 'June': '06',
        'July': '07', 'August': '08', 'September': '09', 'October': '10', 'November': '11', 'December': '12'
    }
    df['Date'] = df['Date'].replace(month_mapping, regex=True)

    # Convert the 'Date' column to a datetime format
    df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y', errors='coerce')

    # Drop rows where 'Date' is NaT (Not a Time) after conversion
    df = df.dropna(subset=['Date'])
else:
    print("Date columns not found, skipping Date creation.")

# We will now handle 'Ticket solved - Date'
df['Ticket solved - Date'] = pd.to_datetime(df['Ticket solved - Date'], errors='coerce')

# Create a column 'Solved Tickets' where if 'Ticket solved - Date' is not NaT, it is considered solved
df['Solved Tickets'] = df['Ticket solved - Date'].notna().astype(int)

# Now, select the required columns: 'Date', 'Tickets', 'Ticket subject', 'Equipment Status', 'Equipment Category'
required_columns = ['Date', 'Ticket subject', 'Tickets', 'Equipment Status', 'Equipment Category']
available_columns = [col for col in required_columns if col in df.columns]

if len(available_columns) == len(required_columns):
    final_aggregated_data = df[required_columns]
else:
    missing_columns = [col for col in required_columns if col not in df.columns]
    print(f"Warning: The following required columns are missing: {missing_columns}")
    final_aggregated_data = df[available_columns]  # Select whatever is available

# Format the 'Date' column to include only the date part (YYYY-MM-DD)
final_aggregated_data['Date'] = final_aggregated_data['Date'].dt.strftime('%Y-%m-%d')

# Ensure 'Tickets' column contains whole numbers
if 'Tickets' in final_aggregated_data.columns:
    final_aggregated_data['Tickets'] = final_aggregated_data['Tickets'].astype(float).fillna(0).astype(int)

# Check the final selected data before calculating totals
print("\nFinal Aggregated Data before totals:")
print(final_aggregated_data.head())

# Calculate the total of the 'Tickets' column
if 'Tickets' in final_aggregated_data.columns:
    total_tickets = final_aggregated_data['Tickets'].sum()

    # Use the first date value from the original data for the total row
    total_date = final_aggregated_data['Date'].iloc[0] if not final_aggregated_data['Date'].empty else 'Total'
    total_row = pd.DataFrame({'Date': [total_date], 'Tickets': [total_tickets], 'Ticket subject': ['Total'], 'Equipment Status': [''], 'Equipment Category': ['']})

    # Calculate totals by Equipment Status and Equipment Category
    status_totals = final_aggregated_data.groupby(['Equipment Status', 'Equipment Category'])['Tickets'].sum().reset_index()
    
    # Create "Status Total" DataFrame with the date included
    status_totals['Date'] = total_date
    status_totals['Ticket subject'] = 'Status Total'
    status_totals = status_totals[['Date', 'Ticket subject', 'Tickets', 'Equipment Status', 'Equipment Category']]

    # Append the status totals and the total row
    final_aggregated_data = pd.concat([final_aggregated_data, status_totals], ignore_index=True)
    final_aggregated_data = pd.concat([final_aggregated_data, total_row], ignore_index=True)

# Ensure that the Total column also contains whole numbers
if 'Total' in final_aggregated_data.columns:
    final_aggregated_data['Total'] = final_aggregated_data['Total'].astype(float).fillna(0).astype(int)

# Save the final aggregated DataFrame to a new CSV file
aggregated_output_path = 'aggregated_data.csv'  # Replace with your desired output file path
final_aggregated_data.to_csv(aggregated_output_path, index=False)

print("Final aggregated data saved to aggregated_data.csv")
