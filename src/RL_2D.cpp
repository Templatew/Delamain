// CAZAUBON Lorenz ROB5
// PART 2 - 2D Grid World

#include <iostream>
#include <vector>
#include <random>
#include <algorithm>
#include <iomanip>
#include <cmath>

using Coord = std::pair<int, int>;

const int nb_rows = 3;
const int nb_cols = 4;
const int nb_action = 4;  // 0 up, 1 down, 2 left, 3 right

double QTable[nb_rows][nb_cols][nb_action] = {{{0}}};
double reward[nb_rows][nb_cols] = {{0}};

// Void cell (obstacle)
const Coord void_cell = {1, 1};

// End states
const std::vector<Coord> end_states = {{0, 3}, {1, 3}};

// Start position
const Coord start_pos = {2, 0};

const double cost = 0.01;
const double alpha = 0.9;
const double gamma_val = 0.5;

const int nb_episodes = 10000;
double epsilon = 1.0;
const double decay = 0.99;

std::vector<double> episode_rewards;

// Random number generator
std::random_device rd;
std::mt19937 gen(rd());
std::uniform_real_distribution<> dis(0.0, 1.0);
std::uniform_int_distribution<> action_dis(0, nb_action - 1);

bool is_valid(int row, int col) {
    // Out of bounds
    if (row < 0 || row >= nb_rows || col < 0 || col >= nb_cols) {
        return false;
    }
    
    // Black Case (void cell)
    if (row == void_cell.first && col == void_cell.second) {
        return false;
    }
    
    return true;
}

int choose_action(int row, int col, double eps) {
    // Explore
    if (dis(gen) < eps) {
        return action_dis(gen);
    }
    // Exploit
    else {
        int best_action = 0;
        double best_value = QTable[row][col][0];
        for (int a = 1; a < nb_action; a++) {
            if (QTable[row][col][a] > best_value) {
                best_value = QTable[row][col][a];
                best_action = a;
            }
        }
        return best_action;
    }
}

bool reached_end(int row, int col) {
    for (const auto& end : end_states) {
        if (row == end.first && col == end.second) {
            return true;
        }
    }
    return false;
}

Coord move(int row, int col, int action) {
    int new_row = row, new_col = col;
    
    // 0 up, 1 down, 2 left, 3 right
    if (action == 0) {
        new_row = row - 1;
    } else if (action == 1) {
        new_row = row + 1;
    } else if (action == 2) {
        new_col = col - 1;
    } else {
        new_col = col + 1;
    }
    
    if (is_valid(new_row, new_col)) {
        return {new_row, new_col};
    } else {
        return {row, col};
    }
}

double max_q_value(int row, int col) {
    double max_val = QTable[row][col][0];
    for (int a = 1; a < nb_action; a++) {
        if (QTable[row][col][a] > max_val) {
            max_val = QTable[row][col][a];
        }
    }
    return max_val;
}

int argmax_q(int row, int col) {
    int best_action = 0;
    double best_value = QTable[row][col][0];
    for (int a = 1; a < nb_action; a++) {
        if (QTable[row][col][a] > best_value) {
            best_value = QTable[row][col][a];
            best_action = a;
        }
    }
    return best_action;
}

bool is_void(int row, int col) {
    return row == void_cell.first && col == void_cell.second;
}

bool is_end_state(int row, int col) {
    for (const auto& end : end_states) {
        if (row == end.first && col == end.second) {
            return true;
        }
    }
    return false;
}

int main() {
    // Initialize rewards
    reward[0][3] = 1.0;   // Goal
    reward[1][3] = -1.0;  // Trap
    
    // Training loop
    for (int episode = 0; episode < nb_episodes; episode++) {
        int row = start_pos.first;
        int col = start_pos.second;
        double total_reward = 0.0;
        
        while (!reached_end(row, col)) {
            int action = choose_action(row, col, epsilon);
            auto [new_row, new_col] = move(row, col, action);
            
            double r = reward[new_row][new_col] - cost;
            total_reward += r;
            
            // Q-learning update
            QTable[row][col][action] += alpha * (r + gamma_val * max_q_value(new_row, new_col) - QTable[row][col][action]);
            
            row = new_row;
            col = new_col;
        }
        
        episode_rewards.push_back(total_reward);
        epsilon = std::max(0.01, epsilon * decay);
    }
    
    // Print Q-Table
    std::cout << "Position | Q(up) | Q(down) | Q(left) | Q(right) | Best Action" << std::endl;
    const std::string action_names[] = {"Go Up", "Go Down", "Go Left", "Go Right"};
    
    for (int row = 0; row < nb_rows; row++) {
        for (int col = 0; col < nb_cols; col++) {
            if (is_void(row, col)) {
                std::cout << " (" << row << "," << col << ")  |  Void" << std::endl;
            } else if (is_end_state(row, col)) {
                std::string label = (reward[row][col] > 0) ? "Goal" : "Trap";
                std::cout << " (" << row << "," << col << ")  |  " << label << std::endl;
            } else {
                int best = argmax_q(row, col);
                std::cout << " (" << row << "," << col << ")  | " 
                          << std::fixed << std::setprecision(2) << std::setw(5) << QTable[row][col][0] << " | "
                          << std::setw(6) << QTable[row][col][1] << " | "
                          << std::setw(6) << QTable[row][col][2] << " | "
                          << std::setw(7) << QTable[row][col][3] << " | "
                          << action_names[best] << std::endl;
            }
        }
    }
    
    // Visual policy
    const std::string action_arrows[] = {"↑", "↓", "←", "→"};  // ASCII arrows for compatibility
    std::cout << "\nLearned Policy (Grid View):" << std::endl;
    std::cout << "-------------------------" << std::endl;
    
    for (int row = 0; row < nb_rows; row++) {
        std::cout << "| ";
        for (int col = 0; col < nb_cols; col++) {
            if (is_void(row, col)) {
                std::cout << " #  | ";
            } else if (row == 0 && col == 3) {
                std::cout << " G  | ";
            } else if (row == 1 && col == 3) {
                std::cout << " X  | ";
            } else {
                int best = argmax_q(row, col);
                std::cout << " " << action_arrows[best] << "  | ";
            }
        }
        std::cout << std::endl;
    }
    
    std::cout << "-------------------------" << std::endl;
    std::cout << "Legend: G=Goal, X=Trap, #=Wall" << std::endl;
    
    return 0;
}
