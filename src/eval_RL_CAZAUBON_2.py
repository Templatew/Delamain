#CAZAUBON Lorenz ROB5
#PART 2 - 2D Grid World

import numpy as np

nb_rows = 3
nb_cols = 4
nb_action = 4  # 0 up, 1 down, 2 left, 3 right

QTable = np.zeros((nb_rows, nb_cols, nb_action))

reward = np.zeros((nb_rows, nb_cols))
reward[0, 3] = 1    # Goal
reward[1, 3] = -1   # Trap
#print(reward)


void = (1,1)
end = [(0, 3), (1, 3)]
start_pos = (2, 0)

cost = 0.01
alpha = 0.9     # learning rate - should not be too high, e.g. between .5 and .9
gamma = 0.5     # discount factor that shows how much you care about future (remember 0 for myopic)

nb_episodes = 100
epsilon = 1
decay = 0.99

episode_rewards = []

def is_valid(row, col):

    # Out of bounds lol
    if (row < 0 or row >= nb_rows or col < 0 or col >= nb_cols):
        return False
    
    # Black Case
    if ((row, col) in void):
        return False
    
    return True

def choose_action(row, col, epsilon):

    # Explore
    if np.random.random() < epsilon:
        return np.random.randint(nb_action)
    
    # Exploit
    else:
        return np.argmax(QTable[row, col])

def reached_end(row, col):
    
    if ((row,col) == void):
        return True
    
    return False


def move(row, col, action):

    # 0 up, 1 down, 2 left, 3 right

    if action == 0:    
        new_row, new_col = row - 1, col

    elif action == 1:  
        new_row, new_col = row + 1, col

    elif action == 2:  
        new_row, new_col = row, col - 1

    else:              
        new_row, new_col = row, col + 1
    
    if (is_valid(new_row, new_col)):
        return new_row, new_col
    
    else:
        return row, col


for episode in range(nb_episodes):
    row, col = start_pos
    total_reward = 0
    
    while not reached_end(row, col):
        action = choose_action(row, col, epsilon)
        new_row, new_col = move(row, col, action)
        
        r = reward[new_row, new_col] - cost
        total_reward += r
        
        QTable[row, col, action] += alpha * (r + gamma * np.max(QTable[new_row, new_col]) - QTable[row, col, action])
        
        row, col = new_row, new_col
    
    episode_rewards.append(total_reward)
    epsilon = max(0.01, epsilon * decay)



print("Position | Q(up) | Q(down) | Q(left) | Q(right) | Best Action")
action_names = ["Go Up", "Go Down", "Go Left", "Go Right"]

for row in range(nb_rows):
    for col in range(nb_cols):

        pos = (row, col)

        if pos == void:
            print(f" ({row},{col})  |  Void")

        elif pos in end:

            if reward[row, col] > 0:
                label = "Goal"

            else:
                label = "Trap"

            print(f" ({row},{col})  |  {label}")

        else:

            best = np.argmax(QTable[row, col])
            q = QTable[row, col]
            print(f" ({row},{col})  | {q[0]:5.2f} | {q[1]:6.2f} | {q[2]:6.2f} | {q[3]:7.2f} | {action_names[best]}")




#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#The Following code was generated with Claude Opus 4.5 to get an easy, readable grid view of the best action for each state/pos


# Visual policy
action_arrows = ["↑", "↓", "←", "→"]
print("\nLearned Policy (Grid View):")
print("-" * 25)
for row in range(nb_rows):
    line = "| "
    for col in range(nb_cols):
        pos = (row, col)
        if pos == void:
            line += " ■  | "
        elif pos == (0, 3):
            line += " G  | "
        elif pos == (1, 3):
            line += " X  | "
        else:
            best = np.argmax(QTable[row, col])
            line += f" {action_arrows[best]}  | "
    print(line)
print("-" * 25)
print("Legend: G=Goal, X=Trap, ■=Wall")


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#



