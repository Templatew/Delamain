# Reinforcement Learning for Trackmania - Implementation Guide

## Project Overview
Building an RL agent in C++ to navigate a simple corner in Trackmania.

## Architecture Overview

### 1. **Environment Interface**
You need to connect C++ to Trackmania:

#### Option A: TMInterface (Recommended)
- **TMInterface** is a plugin for Trackmania that provides:
  - Game state access (position, velocity, rotation, etc.)
  - Input control (steering, acceleration, braking)
  - Frame-by-frame execution control
  - Save state / load state functionality
- Available on GitHub: `donadigo/TMInterface`
- Provides TCP/Named Pipe communication

#### Option B: Screen Capture + Input Simulation
- Less reliable but more universal
- Use computer vision for state extraction
- Simulate keyboard/gamepad inputs
- Higher latency, not recommended for RL

### 2. **State Representation**
Define what information the agent receives:

```cpp
struct State {
    // Vehicle state
    float position[3];      // x, y, z coordinates
    float velocity[3];      // velocity vector
    float rotation[3];      // pitch, yaw, roll
    float speed;            // magnitude of velocity
    
    // Track information
    float distance_to_checkpoint;
    float angle_to_checkpoint;  // Relative angle to next checkpoint
    float distance_from_center; // Distance from track center
    
    // Optional: Ray-casting for track boundaries
    float track_rays[8];    // 8 rays detecting distance to walls
};
```

### 3. **Action Space**
Define what the agent can do:

#### Discrete Actions (Simpler to start)
```cpp
enum Action {
    NO_INPUT,
    ACCELERATE,
    ACCELERATE_LEFT,
    ACCELERATE_RIGHT,
    BRAKE,
    BRAKE_LEFT,
    BRAKE_RIGHT
};
// Total: 7 discrete actions
```

#### Continuous Actions (More realistic)
```cpp
struct Action {
    float steering;     // [-1.0, 1.0] - left to right
    float throttle;     // [0.0, 1.0] - gas
    float brake;        // [0.0, 1.0] - brake
};
```

**Recommendation**: Start with discrete actions, migrate to continuous later.

### 4. **Reward Function**
Critical component that shapes learning:

```cpp
float calculateReward(State current, State previous) {
    float reward = 0.0f;
    
    // Progress reward (most important)
    float progress = current.distance_to_checkpoint - previous.distance_to_checkpoint;
    reward += progress * 10.0f;  // Scale appropriately
    
    // Speed bonus (encourage fast driving)
    reward += current.speed * 0.1f;
    
    // Penalty for being off-center
    reward -= abs(current.distance_from_center) * 0.5f;
    
    // Large penalty for crashes/going off-track
    if (crashed || off_track) {
        reward -= 100.0f;
    }
    
    // Bonus for reaching checkpoint
    if (checkpoint_reached) {
        reward += 50.0f;
    }
    
    return reward;
}
```

### 5. **RL Algorithm Selection**

#### For Discrete Actions:
**DQN (Deep Q-Network)** or **PPO (Proximal Policy Optimization)**
- DQN: Simpler, good for discrete actions
- PPO: More stable, better for continuous control

#### For Continuous Actions:
**PPO** or **SAC (Soft Actor-Critic)**
- PPO: Stable, widely used
- SAC: Sample efficient, handles continuous actions well

**Recommendation**: Start with **PPO** (works for both discrete and continuous).

### 6. **Neural Network Architecture**

```cpp
// Input layer: State vector (e.g., 20 features)
// Hidden layers: 2-3 layers with 128-256 neurons each
// Output layer: 
//   - For discrete: 7 neurons (one per action)
//   - For continuous: 3 neurons (steering, throttle, brake)

// Example architecture:
Input(20) -> Dense(256, ReLU) -> Dense(256, ReLU) -> Output(7, Softmax for discrete)
```

### 7. **Implementation Strategy**

#### Phase 1: Setup (Week 1)
1. Install TMInterface and test connection
2. Create C++ wrapper for TMInterface communication
3. Implement State extraction from game
4. Implement Action execution to game
5. Create simple test: manual control through your wrapper

#### Phase 2: Environment (Week 1-2)
1. Implement Environment class with:
   - `reset()` - restart the track
   - `step(action)` - execute action, return next state and reward
   - `isTerminal()` - check if episode ended
2. Design and implement reward function
3. Test with random actions to ensure stability

#### Phase 3: RL Integration (Week 2-3)
1. Choose RL library:
   - **libtorch** (PyTorch C++ API) - Recommended
   - **TensorFlow C++**
   - **Caffe2**
2. Implement or integrate PPO algorithm
3. Create training loop

#### Phase 4: Training (Week 3-4)
1. Start with simple straight section first
2. Then progress to simple corner
3. Tune hyperparameters:
   - Learning rate (try 3e-4)
   - Batch size (2048-4096)
   - Episode length (limit to avoid infinite episodes)
   - Reward scaling

#### Phase 5: Evaluation & Iteration (Week 4+)
1. Log training metrics (reward, success rate)
2. Visualize learning progress
3. Adjust reward function based on behavior
4. Add curriculum learning (harder tracks gradually)

## Code Structure

```
Delamain/
├── include/
│   ├── Environment.hpp      // RL environment interface
│   ├── Agent.hpp             // RL agent (PPO)
│   ├── NeuralNetwork.hpp     // Neural network wrapper
│   ├── TMInterface.hpp       // Trackmania communication
│   ├── State.hpp             // State representation
│   └── Trainer.hpp           // Training loop
├── src/
│   ├── Environment.cpp
│   ├── Agent.cpp
│   ├── NeuralNetwork.cpp
│   ├── TMInterface.cpp
│   ├── Trainer.cpp
│   └── main.cpp              // Entry point
├── models/                   // Saved neural network weights
├── logs/                     // Training logs
└── CMakeLists.txt
```

## Key Libraries/Dependencies

```cmake
# CMakeLists.txt additions
find_package(Torch REQUIRED)  # PyTorch C++

# For TMInterface communication
# TCP sockets (built-in) or named pipes

# Optional: Logging
find_package(spdlog)
```

## Training Tips

1. **Start Simple**: Train on a straight line first, then a gentle curve, then sharper corners
2. **Episode Length**: Limit episodes to prevent infinite loops (e.g., 1000 steps)
3. **Reward Shaping**: The reward function is 80% of success - iterate on it
4. **Save Frequently**: Save model checkpoints every N episodes
5. **Visualization**: Log and plot rewards to monitor learning
6. **Curriculum Learning**: Gradually increase difficulty
7. **Reset States**: Use save states in TMInterface to reset to exact positions

## Common Pitfalls

1. **Sparse Rewards**: If rewards are too sparse, agent won't learn. Add intermediate rewards.
2. **Reward Hacking**: Agent finds unintended ways to maximize reward (e.g., driving backwards)
3. **Unstable Training**: Use reward clipping and normalize observations
4. **Overfitting**: Train on multiple track variations
5. **Exploration**: Ensure sufficient exploration in early training

## Alternative: Python + C++ Hybrid

Consider prototyping in Python first:
- Python for RL algorithm (stable-baselines3)
- C++ wrapper for TMInterface
- Use pybind11 to bridge them

Benefits: Faster iteration, proven libraries, easier debugging

## Resources

- **TMInterface**: https://github.com/donadigo/TMInterface
- **LibTorch**: https://pytorch.org/cppdocs/
- **PPO Paper**: "Proximal Policy Optimization Algorithms" (Schulman et al., 2017)
- **Spinning Up in Deep RL**: https://spinningup.openai.com/
- **Stable Baselines3**: https://stable-baselines3.readthedocs.io/ (Python reference)

## Next Immediate Steps

1. ✅ Install TMInterface for Trackmania
2. ✅ Create a simple test map with one corner
3. ✅ Implement TMInterface wrapper in C++
4. ✅ Extract basic state (position, velocity, angle to checkpoint)
5. ✅ Test sending inputs to the game
6. ✅ Implement basic reward function
7. ✅ Set up LibTorch
8. 🔄 Start with random agent baseline
