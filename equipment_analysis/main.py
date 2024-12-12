import os
import subprocess
import time
from project_config import config

# Load configuration from project_config
scripts = config['scripts']
csv_files = config['csv_files']

# Function to get the full path of a file in the same directory as the script
def get_file_path(filename):
    return os.path.join(os.path.dirname(__file__), filename)

# Function to run a script
def run_script(script):
    script_path = get_file_path(script)
    try:
        print(f"Running {script_path}...")
        subprocess.check_call(['python', script_path])
        print(f"Successfully ran {script_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to run {script_path}: {e}")
        return False

# Function to check if required CSV files exist
def check_csv_files(files, retries=3, delay=2):
    for attempt in range(retries):
        missing_files = [get_file_path(file) for file in files if not os.path.isfile(get_file_path(file))]
        if not missing_files:
            return True
        print(f"Attempt {attempt + 1}: Missing files: {', '.join(missing_files)}")
        time.sleep(delay)
    return False

# Function to delete all created CSV and XLSX files except zendesk_ticket_analysis.xlsx
def delete_files(files):
    # Specify the file to exclude from deletion (only exclude zendesk_ticket_analysis.xlsx)
    files_to_exclude = {'zendesk_ticket_analysis.xlsx'}  # Modify this list as needed

    # Delete only .csv and .xlsx files
    for file in files:
        file_path = get_file_path(file)
        if os.path.isfile(file_path) and os.path.basename(file_path) not in files_to_exclude and (file_path.endswith('.csv') or file_path.endswith('.xlsx')):
            os.remove(file_path)
            print(f"Deleted {file_path}")
    
    # Delete any extra .csv or .xlsx files not explicitly listed in config
    dir_path = os.path.dirname(__file__)
    for file in os.listdir(dir_path):
        if (file.endswith('.csv') or file.endswith('.xlsx')) and file not in files_to_exclude:
            file_to_delete = os.path.join(dir_path, file)
            os.remove(file_to_delete)
            print(f"Deleted {file_to_delete}")

# Function to run all scripts and check CSV and XLSX file existence
def run_all_scripts():
    retries = 0
    while retries == 0:
        # Run the main scripts
        success = True
        
        for script in scripts:
            if not run_script(script):
                success = False  # If any script fails, set success to False

        # Add a short delay before checking for CSV files
        time.sleep(2)
        
        # Check if all required CSV files exist
        if success and check_csv_files(csv_files):
            print("All scripts ran successfully and all required CSV files are present.")
            
            # Ensure upload.py runs successfully before proceeding to delete files
            if run_script('upload.py'):
                print("upload.py ran successfully.")
                
                # Wait 3 minutes before deleting CSV and XLSX files
                print("Waiting for 1 minute before deleting CSV and XLSX files...")
                time.sleep(60)
                
            else:
                print("upload.py failed. Proceeding to delete files anyway.")
        
        # Delete all CSV and XLSX files created during the script execution, except for zendesk_ticket_analysis.xlsx
        delete_files(csv_files)
        break  # Exit after processing

if __name__ == "__main__":
    run_all_scripts()
