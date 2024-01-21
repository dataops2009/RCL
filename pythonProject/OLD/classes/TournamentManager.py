
class TournamentManager:
    def __init__(self, conn):
        self.conn = conn
        self.cursor = self.conn.cursor()

    def get_initial_winners(self, tournament_id):
        self.cursor.execute("""
            SELECT WinnerTeamID
            FROM MatchProgression
            WHERE TournamentID = %s AND Stage = 'initial'
        """, (tournament_id,))
        return [row[0] for row in self.cursor.fetchall()]

    def pair_up_winners(self, winners):
        final_matches = []
        for i in range(len(winners)):
            for j in range(i + 1, len(winners)):
                final_matches.append((winners[i], winners[j]))
        return final_matches

    def close_connection(self):
        self.conn.close()
