import random

class tournament:
    def __init__(self):
        self.tName = input('Enter a name for the Tournament:')
        self.id = int(input('Enter an ID number:'))
        self.duration_days = int(input('Enter the duration in days:'))
        self.prize_pool = int(input("What's the prize pool in £:"))
        self.game_type = input('Enter the gametype:')
        self.teamRankings = [{'team':'test', 'score':0, 'wins':0, 'losses':0, 'draws':0}]
        #print all the attributes
        print('Tournament has been created!')
        print('')
        print('Tournament Name: ' + self.tName)
        print('Tournament ID: ' + str(self.id))
        print('Tournament Duration: ' + str(self.duration_days) + ' days')
        print('Tournament Prize Pool: £' + str(self.prize_pool))
        print('Tournament Game Type: ' + self.game_type)
        print('')

    
    def create_match_ups(self, ActiveTeamList):
        self.ActiveTeamList = ActiveTeamList
        self.match_ups = []
        for i in range(0, len(ActiveTeamList), 2):
            self.match_ups.append([ActiveTeamList[i], ActiveTeamList[i + 1]])
        return self.match_ups
    
    def initialise_team_rankings(self, ActiveTeamList):
        self.ActiveTeamList = ActiveTeamList
        self.teamRankings = []
        for i in range(len(self.ActiveTeamList)):
            self.teamRankings.append({'team':self.ActiveTeamList[i], 'score':0, 'wins':0, 'losses':0, 'draws':0})
        print(f'Team Rankings have been initialised!')
        print(f'Total teams: {len(self.teamRankings)}')
        print('')
        return self.teamRankings
    
    def update_team_rankings(self, match_results):
        self.match_results = match_results
        for i in range(len(self.match_results)):
            team1, team2, team1_score, team2_score, winner = self.match_results[i]
            for j in range(len(self.teamRankings)):
                if self.teamRankings[j]['team'] == team1:
                    if winner == team1:
                        self.teamRankings[j]['score'] += 3
                        self.teamRankings[j]['wins'] += 1
                    elif winner == team2:
                        self.teamRankings[j]['losses'] += 1
                    else:  # It's a draw
                        self.teamRankings[j]['score'] += 1
                        self.teamRankings[j]['draws'] += 1
                elif self.teamRankings[j]['team'] == team2:
                    if winner == team2:
                        self.teamRankings[j]['score'] += 3
                        self.teamRankings[j]['wins'] += 1
                    elif winner == team1:
                        self.teamRankings[j]['losses'] += 1
                    else:  # It's a draw
                        self.teamRankings[j]['score'] += 1
                        self.teamRankings[j]['draws'] += 1
        print('')
        print('Team Rankings have been updated!')
        print('')

        return self.teamRankings
    
    def get_match_results(self, match_ups):
        self.match_ups = match_ups
        self.match_results = []
        for i in range(len(self.match_ups)):
            team1_score = random.randint(0, 7)
            team2_score = random.randint(0, 7)
            if team1_score > team2_score:
                winner = self.match_ups[i][0]
            elif team1_score < team2_score:
                winner = self.match_ups[i][1]
            else:
                winner = "Draw"
            self.match_results.append([self.match_ups[i][0], self.match_ups[i][1], team1_score, team2_score, winner])
        return self.match_results
    def log_match_results(self, match_results):
        self.match_results = match_results
        for i in range(len(self.match_results)):
            print(self.match_results[i][0] + " " + str(self.match_results[i][2]) + " - " + str(self.match_results[i][3]) + " " + self.match_results[i][1])
            print("Winner: " + self.match_results[i][4])
            print(" ")

    def print_league_table(self, teamRankings):
        self.teamRankings = teamRankings
        print("Team\t\tScore\tWins\tLosses\tDraws")
        for i in range(len(self.teamRankings)):
            print(self.teamRankings[i]['team'] + "\t\t" + str(self.teamRankings[i]['score']) + "\t" + str(self.teamRankings[i]['wins']) + "\t" + str(self.teamRankings[i]['losses']) + "\t" + str(self.teamRankings[i]['draws']))
    def select_top_8_teams(self, teamRankings):
        self.teamRankings = teamRankings
        self.top_8_teams = []
        self.teamRankings.sort(key=lambda x: x['score'], reverse=True)
        for i in range(8):
            self.top_8_teams.append(self.teamRankings[i]['team'])
        return self.top_8_teams
    
    def remove_losing_team_from_top_8(self, match_results, top_8_teams):
        self.match_results = match_results
        self.top_8_teams = top_8_teams
        for i in range(len(self.match_results)):
            if self.match_results[i][4] != "Draw":
                if self.match_results[i][4] == self.match_results[i][0]:
                    self.top_8_teams.remove(self.match_results[i][1])
                else:
                    self.top_8_teams.remove(self.match_results[i][0])
        return self.top_8_teams
    def run_tournament_phase_prefinal(self, teama):
        self.teama = teama
        self.create_match_ups(teama)
        self.get_match_results(self.match_ups)
        self.log_match_results(self.match_results)
        self.update_team_rankings(self.match_results)
        print('')
        print(self.teamRankings)
        print('')
        self.print_league_table(self.teamRankings)
        print('')

    def run_tournament_phase_final(self, top_8_teams):
        self.top_8_teams = top_8_teams
        self.create_match_ups(self.top_8_teams)
        self.get_match_results(self.match_ups)
        self.log_match_results(self.match_results)
        self.update_team_rankings(self.match_results)
        self.remove_losing_team_from_top_8(self.match_results,self.top_8_teams)
        print(self.top_8_teams)
        print(' Move on to the next round!')
        print('')
    
    def transition_to_final(self):
        self.select_top_8_teams(self.teamRankings)
        print('Top 8 teams are:')
        print(self.top_8_teams)
        print('')

    def customise_tournament(self):
        self.tName = input('Enter a name for the Tournament:')
        self.id = int(input('Enter an ID number:'))
        self.duration_days = int(input('Enter the duration in days:'))
        self.prize_pool = int(input("What's the prize pool in £:"))
        self.game_type = input('Enter the gametype:')
        print('Tournament has been customised!')
        print('')
    