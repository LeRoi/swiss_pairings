## Swiss pairings software
## King Xia
import os, random

## todo: scale according to tournament size
WIN_M = 100000000
WIN2_M = 10000000
WIN3_M = 1000000
DRAW_M = 100000
LOSS3_M = 10000
CONSTRAINT = 10000
OPP_DIV = 100000

DEFAULT_PAD = 8

class Match():
    """A single match between two players within a tournament."""
    def __init__(self, high_seed, low_seed):
        self.high_seed = high_seed
        self.low_seed = low_seed
        self.winner = None
        self.games = None

    def is_complete(self):
        """Return true if a winner has been marked for the match."""
        return self.winner != None

    def mark_winner(self, winner, games):
        """Marks the specified player as a winner.
        Throws an exception if the winner provided is not
        a player in the match."""
        if self.high_seed != winner and self.low_seed != winner:
            raise Exception("Illegal winner marked")
        self.winner = winner
        self.games = games

    def is_bye(self):
        """Returns true if the match is a bye."""
        return self.high_seed == None or self.low_seed == None

    def has_player(self, player):
        """Returns true if the player participated in the match."""
        return self.high_seed == player or self.low_seed == player

    def get_opponent(self, player):
        """Returns the player in the match who is not the given player.
        Throws an exception if the player provided did not
        participate in the match."""
        if not self.has_player(player):
            raise Exception("player provided did not participate in match.""")
        return self.high_seed if player != self.high_seed else self.low_seed

    def __str__(self):
        status = "COMPLETE" if self.is_complete() else "PENDING"
        return "%s vs. %s [%s]" % (str(self.high_seed), str(self.low_seed), status)

def make_bye(player):
    return Round(player, None, 2, player)

class Player():
    """Represents a single player in an event."""
    def __init__(self, name, id_):
        self.name = name
        self.id = int(id_)
        self.record = []
        self.constraints = []

    def get_win_loss(self):
        """Returns a tuple (wins, losses) with the player's record"""
        wins = 0
        losses = 0
        for match in self.record:
            if match.is_complete():
                if match.winner == self:
                    wins += 1
                else:
                    losses += 1
        return (wins, losses)

    def get_wins(self):
        return self.get_win_loss()[0]

    def score_match(self, match, ignore):
        opponent = match.get_opponent(self)
        score = 0
        if opponent in ignore or not match.is_complete():
            return score
        
        is_win = match.winner == self
        score += WIN_M if is_win else 0
        score += WIN2_M if is_win and match.games == 2 else 0
        score += WIN3_M if is_win and match.games == 3 else 0
        score += LOSS3_M if not is_win and match.games == 3 else 0
        score += DRAW if match.is_bye() else 0

        if match.is_bye():
            score += (WIN_M + WIN2_M) / OPP_DIV
        else:
            score += opponent.get_score(ignore) / OPP_DIV

        return score

    def get_score(self, ignore):
        score = 0
        for match in self.record:
            ignore_copy = [player for player in ignore]
            ignore_copy.append(self)
            score += self.score_match(match, ignore_copy)
        return score

    def get_constraints_score(self):
        constraints = 0
        opponents = []
        for match in self.record:
            if match.get_opponent(self) not in opponents:
                opponents.append(match.get_opponent(self))
        for player in self.constraints:
            if player in opponents:
                constraints += 1
        return constraints * CONSTRAINT

    def score(self):
        return self.get_score([self]) + self.get_constraints_score()

    def clear_constraints(self):
        self.constraints = []

    def set_constraints(self, constraints):
        self.constraints = [constraint for constraint in constraints]

    def has_played(self, player):
        """Returns true if this player has had a prior match with the given player."""
        for match in self.record:
            opponent = match.get_opponent(self)
            if opponent == player and opponent != None:
                return True
        return False

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.id == other.id and self.name == other.name
        else:
            return False

    def __lt__(self, other):
        """P1 < P2 iff P1 is a higher seed than P2"""
        if not isinstance(other, self.__class__):
            raise Exception("Invalid value comparison for Player.")
        ## todo: randomize sorts s.t. the same player does not
        ## always get a bye over mulitple matches
        return self.score() > other.score()

    def __str__(self):
        win_loss = self.get_win_loss()
        return "%s (#%d)" % (pad_to_x(self.name, DEFAULT_PAD), self.id)

def pad_to_x(string, x):
    while len(string) < x:
        string += " "
    return string

def generate_id(start=10, end=99):
    return random.randint(start, end)

def get_players():
    global DEFAULT_PAD
    players = []
    input_ = "default"
    print "Press ENTER to finish player entry."
    longest = 0
    while input_ != "":
        input_ = raw_input("player name: ")
        if input_ != "":
            id_ = generate_id()
            players.append(Player(input_, id_))
            print "\tyour id is %d" % id_
            longest = longest if len(input_) < longest else len(input_)
    DEFAULT_PAD = longest
    return players

##def match_entry(players):
##    p1 = raw_input("p1 id: ")
##    p2 = raw_input("p2 id: ")
##    games = raw_input("games: ")
##    winner = raw_input("winner id: ")
##    least = get_lowest_matches(players)
##    p1_ = lookup(players, p1)
##    p2_ = lookup(players, p2)
##    winner_ = lookup(players, winner)
##    if len(p1.record) != least or (p2_ != None and len(p2.record) != least):
##        return
##    record_match(p1_, p2_, int(games), winner_)

def group_players(players):
    """Returns sorted lists of players, sorted by win record.
    Assumes all players have an equal number of rounds played."""
    rounds = len(players[0].record)
    for player in players:
        if len(player.record) != rounds:
            raise Exception("Attempted to sort player with incomplete match.")
    player_groups = [[] for i in range(rounds + 1)]
    for player in players:
        player_groups[rounds - player.get_wins()].append(player)
    for group in player_groups:
        for player in group:
            player.set_constraints(group)
        group.sort()
        for player in group:
            player.clear_constraints()
    return player_groups
    
def assign_matches(players):
    random.shuffle(players)
    players.sort()
    matches = []
    player_groups = group_players(players)
    for i in range(len(player_groups)):
        group = player_groups[i]
        player_marks = [False for player in group]
        while any(mark == False for mark in player_marks):
            high_seed_idx = get_highest_valid_seed(group, player_marks)
            low_seed_idx = get_highest_valid_seed(group, player_marks, group[high_seed_idx])
            if low_seed_idx == None:
                if i < len(player_groups) - 1:
                    player_groups[i+1].insert(0, group[high_seed_idx])
                    break
                    
            high_seed = group[high_seed_idx]
            low_seed = group[low_seed_idx] if low_seed_idx >= 0 else None
            player_marks[high_seed_idx] = True
            if low_seed_idx >= 0:
                player_marks[low_seed_idx] = True
            match = Match(high_seed, low_seed)
            matches.append(match)
    return matches

def get_highest_valid_seed(players, marks, player=None):
    """Returns the index of the first player who has not yet been assigned a match."""
    for i in range(len(marks)):
        if marks[i]:
            continue
        ## only valid as long as byes get higher seeds to avoid
        ## future byes. Otherwise can assign multiple byes to a player
        ## does not work when players are forced into rematches
        if players[i].has_played(player) or players[i] == player:
            continue
        return i
    return -1

def get_round_output(matches):
    output = ""
    for i in range(len(matches)):
        output += "[%d]: %s\n" % (i, str(matches[i]))
    return output

def round_complete(matches):
    for match in matches:
        if not match.is_complete():
            return False
    return True

def int_prompt(prompt, start=None, end=None, accepted_nums=[]):
    """Prompts for a number between start and end (inclusive)."""
    input_ = -1
    while not ((start == None or input_ >= start) and (end == None or input_ <= end) and (len(accepted_nums) == 0 or input_ in accepted_nums)):
        try:
            input_ = int(raw_input(prompt))
        except ValueError:
            continue
    return input_

def adjucate_round(round_num, players, matches):
    os.system('cls')
    while not round_complete(matches):
        print "---ROUND %d---" % round_num
        print get_round_output(matches)
        match_select = int_prompt("match: ", 0, len(matches)-1)
        match = matches[match_select]
        if not match.is_complete():
            os.system('cls')
            print "---ROUND %d---" % round_num
            print get_round_output(matches)
            print match
            victor = int_prompt("victor [id]: ", accepted_nums = [match.high_seed.id, match.low_seed.id])
            games = int_prompt("games: ", 2, 3)
            match.mark_winner(match.high_seed if victor == match.high_seed.id else match.low_seed, games)
            match.high_seed.record.append(match)
            match.low_seed.record.append(match)
            os.system('cls')
    print "---ROUND %d COMPLETE---" % round_num
    print get_standings(players)
    raw_input("Press ENTER to continue...")

def get_standings(players):
    output = ""
    random.shuffle(players)
    players.sort()
    for player in players:
        record = player.get_win_loss()
        output += "%s\t%d-%d\n" % (str(player), record[0], record[1])
    return output

def main():
    rounds = int_prompt("rounds: ", 1)
    rounds_remaining = rounds
    players = get_players()
    while rounds_remaining > 0:
        matches = assign_matches(players)
        adjucate_round(rounds - rounds_remaining + 1, players, matches)
        rounds_remaining -= 1
    print get_standings(players)

if __name__ == "__main__":
    main()
