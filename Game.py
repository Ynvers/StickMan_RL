from random import randint
import random
import numpy as np

class StickGame(object):
    """
        StickGame.
    """

    def __init__(self, nb):
        # @nb Number of stick to play with
        self.original_nb = nb
        self.nb = nb

    def is_finished(self):
        # Check if the game is over @return Boolean
        if self.nb <= 0:
            return True
        return False

    def reset(self):
        # Reset the state of the game
        self.nb = self.original_nb
        return self.nb

    def display(self):
        # Display the state of the game
        print ("| " * self.nb)

    def step(self, action):
        # @action either 1, 2 or 3. Take an action into the environement
        self.nb -= action
        if self.nb <= 0:
            return None, -1
        else:
            return self.nb, 0

class StickPlayer(object):
    """
        Stick Player
    """

    def __init__(self, is_human, size, trainable=True):
        # @nb Number of stick to play with
        super(StickPlayer, self).__init__()
        self.is_human = is_human
        self.history = []
        self.V = {}
        for s in range(1, size+1):
            self.V[s] = 0.
        self.win_nb = 0.
        self.lose_nb = 0.
        self.rewards = []
        self.eps = 0.99
        self.trainable = trainable

    def reset_stat(self):
        # Reset stat
        self.win_nb = 0
        self.lose_nb = 0
        self.rewards = []

    def greedy_step(self, state):
        # Greedy step
        actions = [1, 2, 3]
        vmin = None
        vi = None
        for i in range(0, 3):
            a = actions[i]
            if state - a > 0 and (vmin is None or vmin > self.V[state - a]):
                vmin = self.V[state - a]
                vi = i
        return actions[vi if vi is not None else 1]

    def play(self, state):
        # PLay given the @state (int)
        if self.is_human is False:
            # Take random action
            if random.uniform(0, 1) < self.eps:
                action = randint(1, 3)
            else: # Or greedy action
                action = self.greedy_step(state)
        else:
            action = int(input("$>"))
        return action

    def add_transition(self, n_tuple):
        # Add one transition to the history: tuple (s, a , r, s')
        self.history.append(n_tuple)
        s, a, r, sp = n_tuple
        self.rewards.append(r)

    def train(self):
        if not self.trainable or self.is_human is True:
            return

        # Update the value function if this player is not human
        for transition in reversed(self.history):
            s, a, r, sp = transition
            if r == 0:
                self.V[s] = self.V[s] + 0.001*(self.V[sp] - self.V[s])
            else:
                self.V[s] = self.V[s] + 0.001*(r - self.V[s])

        self.history = []

def play(game, human, p2, train=True):
    print("Vous êtes le joueur 1")
    state = game.reset()
    players = [human, p2]
    random.shuffle(players)
    p = 0
    while True:
        if game.is_finished():
            break

        if players[p%2].is_human:
            game.display()

        action = players[p%2].play(state)
        n_state, reward = game.step(action)

        #  Game is over. Ass stat
        if (reward != 0):
            # Update stat of the current player
            players[p%2].lose_nb += 1. if reward == -1 else 0
            players[p%2].win_nb += 1. if reward == 1 else 0
            # Update stat of the other player
            players[(p+1)%2].lose_nb += 1. if reward == 1 else 0
            players[(p+1)%2].win_nb += 1. if reward == -1 else 0

            # Add the reversed reward and the new state to the other player
            if p != 0:
                s, a, r, sp = players[(p+1)%2].history[-1]
                players[(p+1)%2].history[-1] = (s, a, reward * -1, n_state)

            players[p%2].add_transition((state, action, reward, None))

            if human.win_nb > p2.win_nb:
                print("Le joueur 1 a gagné !")
            elif p2.win_nb > human.win_nb:
                print("Le joueur 2 a gagné !")
            else:
                print("C'est une égalité !")
            break

            
        state = n_state
        p += 1

    if train:
        human.train()
        p2.train()
if __name__ == '__main__':
    game = StickGame(12)

    # PLayers to train
    p2 = StickPlayer(is_human=False, size=12, trainable=True)
    human = StickPlayer(is_human=True, size=12, trainable=False)

    # Train the agent
    for i in range(0, 10000):
        if i % 10 == 0:
            p2.eps = max(p2.eps*0.996, 0.05)
        play(game, human, p2)

    # Display the value function
    for key in p2.V:
        print(key, p2.V[key])
    print("--------------------------")

    # Play agains a random player
    random_player = StickPlayer(is_human=False, size=12, trainable=False)
    for _ in range(0, 1000):
        play(game, human, random_player, train=False)
    
    # Play agains us
    while True:
        play(game, human, p2, train=False)
        rejouer = input("Voulez-vous rejouer ? (o/n): ")
        if rejouer.lower() != 'o':
            break