"""
import pandas as pd

# Replace 'your_excel_file.xlsx' with the path to your actual Excel file


# Load the Excel file
print("Loading Excel file...")
df = pd.read_excel(excel_file_path, sheet_name=0)  # Assumes that your data is in the first sheet
print("Excel file loaded.")

# Assuming that the usernames and points are in the second column
column_index = 1  # This is 'B' in Excel

# Initialize a dictionary to hold our username and points pairs
usernames_and_points = {}
# Initialize a variable to keep track of the current username
current_username = None

# Initialize HTML strings for Team 1 and Team 2 tables
team1_html = "<table><tr><th>Username</th><th>Points</th></tr>"
team2_html = "<table><tr><th>Username</th><th>Points</th></tr>"

# Iterate over each cell in the second column
print("Processing data...")
for index, cell in enumerate(df.iloc[:, column_index], start=1):
    if isinstance(cell, str) and not cell.isdigit():  # If the cell contains text with letters, it's a username
        # Split at the hashtag and keep only the part before it
        username = cell.split('#')[0].strip()
        current_username = username
        print(f"Found username: {current_username}")
    elif isinstance(cell, str) and cell.isdigit() and current_username is not None:  # If the cell contains only digits, it's points
        # Check if the current_username is a team name
        if current_username in ('REVOLTERS', 'ENFORCERS'):
            # Check if the cell above contains points
            points_above = df.iloc[index - 1, column_index]
            if isinstance(points_above, int):
                points = points_above
            else:
                # If not, use the points in the current cell
                points = int(cell)
        else:
            # Convert points to an integer
            points = int(cell)
        # Add the username and points to the dictionary
        usernames_and_points[current_username] = points
        print(f"Found points: {cell} for username: {current_username}")
        current_username = None  # Reset the current username

# Output the dictionary of usernames and their points
print("Data processed. Results:")
print(usernames_and_points)

# Define a dictionary of team names
team_names_dict = {'REVOLTERS': 'Team 1', 'ENFORCERS': 'Team 2'}
# Initialize variables to keep track of teams
team1 = None
team2 = None
current_team = None

# Process usernames_and_points dictionary
for username, points in usernames_and_points.items():
    if username in team_names_dict:
        current_team = team_names_dict[username]
    elif current_team:
        if username not in ('REVOLTERS', 'ENFORCERS'):  # Skip team names
            if current_team == 'Team 1':
                team1_html += f"<tr><td>{username}</td><td>{points}</td></tr>"
            elif current_team == 'Team 2':
                team2_html += f"<tr><td>{username}</td><td>{points}</td></tr>"
    else:
        current_team = "Team 1"  # Assign to "Team 1" if not already set

# Close the HTML tables
team1_html += "</table>"
team2_html += "</table>"

# Print the HTML tables
print("Team 1 Scores:")
print(team1_html)
print("Team 2 Scores:")
print(team2_html)
# Define a function to generate HTML tables
def generate_html_tables():
    team1_html = "<table><tr><th>Username</th><th>Points</th></tr>"
    team2_html = "<table><tr><th>Username</th><th>Points</th></tr>"

    # Initialize current_team to "Team 1"
    current_team = "Team 1"

    # Process usernames_and_points dictionary
    for username, points in usernames_and_points.items():
        if username in team_names_dict:
            current_team = team_names_dict[username]
        elif current_team:
            if username not in ('REVOLTERS', 'ENFORCERS'):  # Skip team names
                if current_team == 'Team 1':
                    team1_html += f"<tr><td>{username}</td><td>{points}</td></tr>"
                elif current_team == 'Team 2':
                    team2_html += f"<tr><td>{username}</td><td>{points}</td></tr>"

    # Close the HTML tables
    team1_html += "</table>"
    team2_html += "</table>"

    return team1_html, team2_html

"""

import pandas as pd

# Replace with the path to your actual Excel file
excel_file_path = 'C:\\Users\\prabb\\OneDrive\\Documents\\RCL\\pythonProject\\classes\\ocr_results.xlsx'

# Load the Excel file
df = pd.read_excel(excel_file_path, sheet_name=0)  # Assumes data is in the first sheet

# Function to find points for a given team
def find_points(team_name, df):
    for i in range(len(df)):
        if df.iloc[i, 1] == team_name:
            if team_name == 'REVOLTERS' and i+1 < len(df):
                return df.iloc[i+1, 1]  # Points below 'REVOLTERS'
            elif team_name == 'ENFORCERS' and i-1 >= 0:
                return df.iloc[i-1, 1]  # Points above 'ENFORCERS'
    return None

# Get points for 'REVOLTERS' and 'ENFORCERS'
points_for_revolters = find_points('REVOLTERS', df)
points_for_enforcers = find_points('ENFORCERS', df)

# Print results
print("Points for REVOLTERS:", points_for_revolters)
print("Points for ENFORCERS:", points_for_enforcers)
