import pymssql

# Azure SQL Database connection details
server = 'rcldevelopmentserver.database.windows.net'
database = 'rcldevelopmentdatabase'
username = 'rcldeveloper'
password = 'media$2009'

# Connect to the database
conn = pymssql.connect(server, username, password, database)

# Create a cursor object
cursor = conn.cursor()


# Insert dummy data into Teams_Dim
insert_teams_dim = """
INSERT INTO Teams_Dim (ID, Name, CaptainID, CoCaptainID, NumOfPlayers, GamesPlayed, GamesWon, GamesLost, GamesDrawn, WinLostRatio) 
VALUES 
(1, 'Team Alpha', 101, 102, 5, 20, 12, 5, 3, 0.6),
(2, 'Team Beta', 103, 104, 5, 22, 14, 6, 2, 0.64),
(3, 'Team Gamma', 105, 106, 5, 18, 9, 7, 2, 0.5);
"""

# Insert dummy data into Players_Dim
insert_players_dim = """
INSERT INTO Players_Dim (ID, Name, TeamID, GamesPlayed, GamesWon, GamesLost, GamesDrawn, WinLostRatio) 
VALUES 
(101, 'Player A1', 1, 20, 10, 5, 5, 0.5),
(102, 'Player A2', 1, 20, 12, 4, 4, 0.6),
(103, 'Player B1', 2, 22, 14, 6, 2, 0.64),
(104, 'Player B2', 2, 22, 13, 5, 4, 0.59),
(105, 'Player C1', 3, 18, 8, 7, 3, 0.44),
(106, 'Player C2', 3, 18, 9, 6, 3, 0.5),
(107, 'Player A3', 1, 19, 9, 6, 4, 0.47),
(108, 'Player B3', 2, 21, 11, 7, 3, 0.52),
(109, 'Player C3', 3, 17, 7, 8, 2, 0.41),
(110, 'Player A4', 1, 18, 8, 7, 3, 0.44),
(111, 'Player B4', 2, 23, 15, 5, 3, 0.65),
(112, 'Player C4', 3, 19, 10, 6, 3, 0.53),
(113, 'Player A5', 1, 21, 11, 6, 4, 0.52),
(114, 'Player B5', 2, 20, 12, 5, 3, 0.6),
(115, 'Player C5', 3, 20, 9, 8, 3, 0.45);
"""

# Execute the insert commands
cursor.execute(insert_teams_dim)
cursor.execute(insert_players_dim)

# Commit the changes
conn.commit()

# Query and print the Teams_Dim data
print("Teams_Dim Data:")
cursor.execute("SELECT * FROM Teams_Dim")
for row in cursor:
    print(row)

# Query and print the Players_Dim data
print("\nPlayers_Dim Data:")
cursor.execute("SELECT * FROM Players_Dim")
for row in cursor:
    print(row)

# Close the connection
conn.close()
