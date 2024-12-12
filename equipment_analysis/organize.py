import pandas as pd
import numpy as np
import re  # Import regex module

# Load the CSV file
ticket_data_path = 'extracted_data.csv'  # Replace with your file path
df = pd.read_csv(ticket_data_path)

# Remove specified columns (if you still want to drop them)
columns_to_remove = ['Product - Service Desk Tool', 'Action Taken', 'Ticket group']
df.drop(columns=columns_to_remove, inplace=True, errors='ignore')  # Use errors='ignore' to avoid errors if any column is not found


# Define the values for the new columns
equipment_statuses = [
    "Returned",
    "Picked up/Shipped",
    "New Employee Hire",
    "Broken Hardware"
]

# Initialize the Equipment Category and Status columns
df['Equipment Category'] = ''  # Initialize the Equipment Category column
df['Equipment Status'] = ''  # Initialize the Equipment Status column

# Copy the existing columns for Ticket solved - Date and Solved tickets
df['Ticket solved - Date'] = df.get('Ticket solved - Date', '')  # Copy if exists, otherwise initialize to empty
df['Solved tickets'] = df.get('Solved tickets', '')  # Copy if exists, otherwise initialize to empty

# Define categories and corresponding keywords with regex patterns
category_keywords = {
    "Laptop": [r'.*laptop.*', r'.*computer.*', r'.*bitlocker.*', r'.*reimage.*', r'.*chromebook.*', r'.*chromebooks.*', r'.*windows.*', r'.*HP.*', r'.*autopilot.*', r'.*latpop.*'], 
    "Mobile Device": [r'.*cellphone.*', r'.*cell phone.*', r'.*mobile.*', r'.*mobile phone.*', r'.*tablet.*', r'.*SIM.*', r'.*phone.*', r'.*work phone.*', r'.*iphone.*', r'.*android.*', r'.*note.*', r'.*spare.*', r'.*MD.*', r'.*cases.*', r'.*galaxy.*', r'.*ipad.*', r'.*devices.*'],
    "Desktop": [r'.*monitor.*', r'.*desktop.*', r'.*desk top.*', r'.*PC.*'],
    "Printer/Scanner/Copier": [r'.*camera.*', r'.*scanner.*', r'.*printer.*', r'.*copier.*', r'.*epson.*'],
    'Landline': [r'.*deskphone.*', r'.*deskphones.*', r'.*Desk phone.*', r'.*landline.*', r'.*land line.*'],
    "Peripheral Equipment": [r'.*charging.*', r'.*charger.*', r'.*keyboard.*', r'.*dock.*', r'.*docking.*', r'.*mouse.*', r'.*blue tooth.*', r'.*head phone.*', r'.*headset.*', r'.*USB.*', r'.*USBs.*', r'.*Peripheral.*', r'.*dongle.*', r'.*yealink.*', r'.*hdmi.*', r'.*cord.*'],
    "New Employee Hire": [r'.*new hire.*', r'.*hire.*'],
    "New Acquisitions": [r'.*New Acquisitions.*', r'.*New Acquisition.*', r'.*Acquisitions.*', r'.*Acquisition.*']
}

# Define statuses and corresponding keywords with regex patterns
status_keywords = {
    "Picked up/Shipped": [r'.*picked up.*', r'.*shipped.*', r'.*address.*', r'.*approval.*', r'.*pickup.*', r'.*pick up.*', r'.*ship.*', r'.*Amazon.*', r'.*waiting stock.*'],
    "Returned": [r'.*return.*', r'.*returned.*', r'.*termed.*', r'.*replace.*', r'.*replacement.*'],
    "New Employee Hire": [r'.*new hire.*', r'.*hire.*'],
    "Broken Hardware": [r'.*broken.*', r'.*broke.*', r'.*destroyed.*', r'.*damaged.*'],
    "New Acquisitions": [r'.*New Acquisitions.*', r'.*New Acquisition.*', r'.*Acquisitions.*', r'.*Acquisition.*']
}

# Function to determine Equipment Category based on Ticket subject
def determine_category(ticket_subject):
    # Check if ticket_subject is NaN
    if pd.isna(ticket_subject):
        return 'Other'
    
    for category, keywords in category_keywords.items():
        # Check if any keyword regex pattern matches the ticket subject
        if any(re.search(keyword, ticket_subject, re.IGNORECASE) for keyword in keywords):
            return category
            
    return 'Other'  # Return 'Other' if no match found

# Function to determine Equipment Status based on Ticket subject
def determine_status(ticket_subject):
    # Check if ticket_subject is NaN
    if pd.isna(ticket_subject):
        return 'Other'
    
    for status, keywords in status_keywords.items():
        # Check if any keyword regex pattern matches the ticket subject
        if any(re.search(keyword, ticket_subject, re.IGNORECASE) for keyword in keywords):
            return status
            
    return 'Picked up/Shipped'  # Return 'Other' if no match found

# Apply the functions to the Ticket subject column to determine Equipment Category and Status
df['Equipment Category'] = df['Ticket subject'].apply(determine_category)
df['Equipment Status'] = df['Ticket subject'].apply(determine_status)

# Save the updated DataFrame back to a new CSV file
updated_ticket_data_path = 'organized_data.csv'  # Replace with your desired output file path
df.to_csv(updated_ticket_data_path, index=False)

print("New columns added and specified columns removed. Updated data saved to organized_data.csv")

# Debugging: Check how many tickets are in 'Other'
print(f"Total 'Other' categories: {df['Equipment Category'].value_counts().get('Other', 0)}")
