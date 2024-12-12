import sys 
import io
import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import re
from project_config import zendesk_api_token, zendesk_api_url, zendesk_email, zendesk_subdomain, product_service_desk_tool_id, action_taken_id  

# Set the standard output to use utf-8 encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Zendesk credentials and details
subdomain = zendesk_subdomain
email = f'{zendesk_email}/token'
api_token = zendesk_api_token

# List of allowed group names
allowed_group_names = {
   'Equipment',
    'Equipment Waiting'
}

tickets = []
batch_size = 300  # Fetch 500 tickets at a time
pause_duration = 15  # Pause for 15 seconds after each batch

# Function to fetch groups from Zendesk
def fetch_groups():
    url = f'https://{subdomain}.zendesk.com/api/v2/groups.json'
    response = requests.get(url, auth=(email, api_token))
    
    if response.status_code != 200:
        print(f"Error fetching groups: {response.status_code}")
        return {}

    group_data = response.json()
    group_map = {group['id']: group['name'] for group in group_data['groups']}

    # Print all available group names
    print("Available Groups:")
    for group_name in group_map.values():
        print(group_name)

    return group_map

# Function to fetch tickets within a date range
def fetch_tickets_for_date_range(start_date, end_date, group_map):
    url = f'https://{subdomain}.zendesk.com/api/v2/search.json?query=type:ticket created>{start_date} created<{end_date}&per_page={batch_size}'
    tickets_fetched = []
    
    while url:
        response = requests.get(url, auth=(email, api_token))
        
        if response.status_code == 429:  # Rate limit hit
            print("Rate limit exceeded. Pausing for longer duration...")
            time.sleep(pause_duration)
            continue  # Retry the request after the pause

        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            print(response.json())
            return tickets_fetched  # Return whatever we have fetched so far

        data = response.json()
        tickets_data = data.get('results', [])
        tickets_fetched.extend(process_tickets(tickets_data, group_map))
        url = data.get('next_page')  # Get the next page URL

        if len(tickets_fetched) >= 500:
            save_tickets_to_csv(tickets_fetched)
            tickets_fetched.clear()
            time.sleep(pause_duration)  # Pause after every 500 tickets

    return tickets_fetched

def save_tickets_to_csv(tickets_batch):
    if tickets_batch:
        df = pd.DataFrame(tickets_batch)
        # Ensure the schema has header in the first write
        df.to_csv('extracted_data.csv', mode='a', index=False, header=not pd.io.common.file_exists('extracted_data.csv'))
        print(f"Saved {len(tickets_batch)} tickets to extracted_data.csv")

def filter_ticket(ticket, group_map):
    group_id = ticket.get('group_id')
    group_name = group_map.get(group_id, 'Unknown')

    if group_name not in allowed_group_names:
        return False
    
    return True

def process_tickets(tickets_data, group_map):
    filtered_tickets = []

    for ticket in tickets_data:
        # Print the entire ticket object for inspection
        print("\nFull Ticket Data:")
        print(ticket)  # Print the full ticket to see all fields
        
        if filter_ticket(ticket, group_map):
            created_at = ticket.get('created_at', ' ')
            ticket_id = ticket.get('id', ' ')
            group_id = ticket.get('group_id', ' ')
            group_name = group_map.get(group_id, 'Unknown')
            subject = ticket.get('subject', '')

            # Retrieve the product name and action taken from custom fields
            product_name = None  # Initialize to None if not found
            action_taken = None  # Initialize to None if not found
            
            for custom_field in ticket.get('custom_fields', []):
                if custom_field['id'] == product_service_desk_tool_id:  # Use the imported variable
                    product_name = custom_field.get('value', 'No Value')  # Use 'No Value' if field is empty
                elif custom_field['id'] == action_taken_id:  # Use the imported variable
                    action_taken = custom_field.get('value', 'No Action')  # Use 'No Action' if field is empty

            # Extract day, month, and year from created_at
            try:
                created_datetime = datetime.strptime(created_at, '%Y-%m-%dT%H:%M:%SZ')
                created_day = created_datetime.day
                created_month = created_datetime.month
                created_year = created_datetime.year  # Extract the year
                
                # Debug prints
                print(f"Created Date: {created_datetime}, Day: {created_day}, Month: {created_month}, Year: {created_year}")
                
            except Exception as e:
                print(f"Error parsing created_at: {created_at}. Error: {e}")
                continue  # Skip to the next ticket if there's an error

            # Append the filtered ticket data
            filtered_tickets.append({
                'Product - Service Desk Tool': product_name or 'No Product',  # Default to 'No Product' if None
                'Action Taken': action_taken or 'No Action',  # Default to 'No Action' if None
                'Ticket group': group_name,
                'Ticket subject': subject,
                'Ticket created - Day of month': created_day,
                'Ticket created - Month': created_month,
                'Ticket created - Year': created_year,  # Include the year in the output
                'Tickets': 1
            })

    # Print the schema and the first ticket for verification
    if filtered_tickets:
        print("Schema of pulled tickets:")
        print(", ".join(filtered_tickets[0].keys()))  # Print column names (schema)
        print("\nSample Ticket Data:")
        print(filtered_tickets[0])  # Print the first ticket for inspection

    return filtered_tickets

def main():
    # Fetch groups dynamically
    group_map = fetch_groups()

    # Fetch tickets for the previous day
    end_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    start_date = end_date - timedelta(days=1)

    # Fetch and process tickets
    fetched_tickets = fetch_tickets_for_date_range(start_date.isoformat() + 'Z', end_date.isoformat() + 'Z', group_map)

    # Save any remaining tickets to CSV
    save_tickets_to_csv(fetched_tickets)

if __name__ == "__main__":
    main()
