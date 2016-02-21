## Draft Software
import random

WIN_M = 100000000
WIN2_M = 10000000
WIN3_M = 1000000
DRAW_M = 100000
OPP_DIV = 100000

class Round():
    def __init__(self, p1, p2, games, winner):
        self.p1 = p1
        self.p2 = p2
        self.games = games
        self.winner = winner

    def is_winner(self, player):
        return self.winner == player

    def opponent(self, player):
        return self.p1 if self.p1 != player else self.p2

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        p1eq = self.p1 == other.p1
        p2eq = self.p2 == other.p2
        geq = self.games == other.games
        weq = self.winner == other.winner
        return p1eq and p2eq and geq and weq

def make_bye(player):
    return Round(player, None, 2, player)

class Player():
    """Represents a single player in an event."""
    def __init__(self, name, id_):
        self.name = name
        self.id_ = id_
        self.record = []

    def score_match(self, n, ignore_player=None):
        match = self.record[n]
        if match.opponent(self) == ignore_player:
            return 0
        
        score = 0
        is_win = match.is_winner(self)
        score += WIN_M if is_win else 0
        score += WIN2_M if is_win and match.games == 2 else 0
        score += WIN3_M if is_win and match.games == 3 else 0
        score += DRAW if match.is_winner(None)

        if match.opponent(self) == None:
            score += (WIN_M + WIN2_M) / OPP_DIV
        else:
            score += match.opponent(self).get_score(self) / OPP_DIV

        return score

    def get_score(self, ignore_player=None):
        score = 0
        for i in len(self.record):
            score += self.score_match(i, ignore_player)
        return score

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.id_ == other.id_ and self.name == other.name
        else:
            return False

    def __lt__(self, other):
        """P1 < P2 iff P1 is a lower seed than P2"""
        if not isinstance(other, self.__class__):
            raise Exception("Invalid value comparison for Player.")

def generate_id(endpoint=100):
    return random.randint(1, endpoint)

def get_players():
    players = []
    input_ = "default"
    print "Press ENTER to finish player entry."
    while input_ != "":
        input_ = raw_input("player name: ")
        if input_ != "":
            id_ = generate_id()
            players.append(Player(input_, id_))
            print "\tyour id is %d" % id_
    return players

def record_match(p1, p2, games, winner):
    match = Round(p1, p2, games, winner)
    p1.record.append(match)
    if p2 != None:
        p2.record.append(match)

def lookup(players, id_):
    for player in players:
        if player.id_ == id_:
            return player
    return None

def get_lowest_matches(players):
    least = len(players[0].record)
    for player in players:
        if len(player.record) < least:
            least = len(player.record)
    return least

def match_entry(players):
    p1 = raw_input("p1 id: ")
    p2 = raw_input("p2 id: ")
    games = raw_input("games: ")
    winner = raw_input("winner id: ")
    least = get_lowest_matches(players)
    p1_ = lookup(players, p1)
    p2_ = lookup(players, p2)
    winner_ = lookup(players, winner)
    if len(p1.record) != least or (p2_ != None and len(p2.record) != least):
        return
    record_match(p1_, p2_, int(games), winner_)

def main():
    players = get_players()
    

if __name__ == "__main__":
    main()
