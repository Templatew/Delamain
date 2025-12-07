# Reinforcement Learning for Trackmania Nations Forever - Implementation Guide

## Project Overview
Building an RL agent in C++ to navigate a simple corner in **Trackmania Nations Forever (TMNF)**.

## Why Trackmania Nations Forever?
- ✅ **Free** - Available on Steam or standalone
- ✅ **TMInterface support** - Full game state access + input control
- ✅ **Lightweight** - Runs on minimal hardware, allows faster training
- ✅ **Deterministic physics** - Same inputs = same outputs (crucial for RL)
- ✅ **Active community** - Well-documented tools and resources

## Prerequisites

### 1. Install Trackmania Nations Forever
- **Steam**: https://store.steampowered.com/app/11020/TrackMania_Nations_Forever/
- **Standalone**: https://nadeo.com/

### 2. Install TMInterface
- **Download**: https://github.com/donadigo/TMInterface/releases
- Extract and run the installer
- TMInterface injects into TMNF and provides an API for:
  - Reading game state (position, velocity, rotation, etc.)
  - Sending inputs (steering, acceleration, braking)
  - Frame-by-frame simulation control
  - Save/load state functionality

### 3. Clone TMInterfacePublic (C++ Resources)
```bash
git clone https://github.com/donadigo/TMInterfacePublic.git
```
This contains C++ headers and examples for communicating with TMInterface.

## Architecture Overview

### 1. **TMInterface Communication**
TMInterface uses **named pipes** (Windows) for IPC:

```cpp
// TMInterface exposes these via shared memory / named pipes:
// - Game state every simulation tick (10ms)
// - Ability to inject inputs
// - Save state / load state commands
// - Simulation speed control

// Connection example (pseudocode):
TMInterfaceClient client;
client.connect();  // Connect to running TMNF + TMInterface

// Main loop
while (training) {
    State state = client.getState();      // Get car state
    Action action = agent.predict(state); // RL agent decides
    client.sendInput(action);             // Send to game
    client.advanceFrame();                // Step simulation
}
```

### Key TMInterface Features for RL:
- **`set_speed`**: Control simulation speed (train faster than real-time!)
- **`save_state` / `load_state`**: Instantly reset to checkpoints
- **`get_simulation_state`**: Access position, velocity, rotation, race time
- **`set_input_state`**: Control steering, gas, brake

### 2. **State Representation**
Data available from TMInterface for TMNF:

```cpp
struct State {
    // From TMInterface simulation state
    float position[3];      // x, y, z world coordinates
    float velocity[3];      // velocity vector (m/s)
    float rotation[4];      // quaternion (or euler angles)
    float angular_speed[3]; // rotation speed
    
    // Derived values
    float speed;            // magnitude of velocity (km/h)
    int current_checkpoint; // checkpoint index
    int race_time;          // current race time (ms)
    
    // Computed for RL
    float angle_to_checkpoint;  // Relative angle to next CP
    float distance_to_checkpoint;
    
    // Optional: Wheel contact / collision detection
    bool wheels_contact[4]; // Are wheels on ground?
};

// TMInterface provides these via GetSimulationState():
// - Position, Velocity, Rotation
// - AngularSpeed, WheelDirt, WheelWet
// - IsGroundContact, etc.
```

### 3. **Action Space**
TMInterface accepts binary inputs (like keyboard):

#### TMNF Input Model (Binary)
```cpp
// TMNF uses binary inputs (not analog):
struct TMInput {
    bool accelerate;  // Up arrow
    bool brake;       // Down arrow
    bool steer_left;  // Left arrow
    bool steer_right; // Right arrow
};

// This gives us discrete action combinations:
enum Action {
    NONE = 0,                    // No input
    ACCELERATE,                  // Gas only
    ACCELERATE_LEFT,             // Gas + Left
    ACCELERATE_RIGHT,            // Gas + Right
    BRAKE,                       // Brake only
    BRAKE_LEFT,                  // Brake + Left
    BRAKE_RIGHT,                 // Brake + Right
    LEFT,                        // Steer left only
    RIGHT,                       // Steer right only
    ACTION_COUNT = 9
};

// TMInterface set_input_state format:
// client.setInputState(accelerate, brake, steerLeft, steerRight);
```

**Note**: TMNF has **digital steering** - the car turns at a fixed rate when you hold left/right. This actually simplifies the action space compared to analog steering!

### 4. **Reward Function**
Critical component that shapes learning:

```cpp
float calculateReward(State current, State previous, bool finished) {
    float reward = 0.0f;
    
    // 1. Progress reward - distance traveled toward checkpoint
    float progress = previous.distance_to_checkpoint - current.distance_to_checkpoint;
    reward += progress * 1.0f;  // Positive when getting closer
    
    // 2. Speed bonus (encourage maintaining speed)
    reward += (current.speed / 300.0f) * 0.1f;  // Normalize by max speed ~300 km/h
    
    // 3. Checkpoint reached bonus
    if (current.current_checkpoint > previous.current_checkpoint) {
        reward += 100.0f;
    }
    
    // 4. Finish bonus
    if (finished) {
        reward += 500.0f;
        // Bonus for faster times
        reward += (30000.0f - current.race_time) * 0.01f;  // Bonus if under 30s
    }
    
    // 5. Crash / respawn penalty
    if (crashed_or_respawned) {
        reward -= 50.0f;
    }
    
    // 6. Time penalty (encourage finishing quickly)
    reward -= 0.01f;  // Small penalty each step
    
    return reward;
}
```

### Terminal Conditions for TMNF:
```cpp
bool isEpisodeOver(State state, int step_count) {
    // Finished the track
    if (state.finished) return true;
    
    // Timeout (e.g., 30 seconds for a simple corner)
    if (state.race_time > 30000) return true;
    
    // Step limit (prevent infinite episodes)
    if (step_count > 3000) return true;  // 3000 * 10ms = 30s
    
    // Car is stuck (speed near 0 for too long)
    if (state.speed < 5.0f && step_count > 100) return true;
    
    return false;
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

#### Phase 1: TMInterface Setup (Week 1)
1. ✅ Install TMNF (Steam or standalone)
2. ✅ Install TMInterface from GitHub releases
3. ✅ Clone TMInterfacePublic for C++ headers
4. Create a simple test map in the track editor:
   - Start block → straight → one 90° corner → finish
5. Test TMInterface manually:
   - Open TMNF, load your map
   - Open TMInterface console (F3)
   - Test commands: `set_speed 2`, `save_state`, `load_state`

#### Phase 2: C++ TMInterface Wrapper (Week 1-2)
1. Study TMInterfacePublic code structure
2. Implement named pipe communication:
   ```cpp
   class TMInterfaceClient {
   public:
       bool connect();
       void disconnect();
       SimulationState getState();
       void setInput(bool accel, bool brake, bool left, bool right);
       void saveState(int slot);
       void loadState(int slot);
       void setSpeed(float speed);
   };
   ```
3. Test: Read state and print position/velocity
4. Test: Send inputs and verify car responds

#### Phase 3: RL Environment (Week 2)
1. Implement OpenAI Gym-style interface:
   ```cpp
   class TMEnvironment {
   public:
       State reset();                    // Load saved state, return initial state
       std::tuple<State, float, bool> step(Action action);  // Execute action
   private:
       TMInterfaceClient client;
       State computeState();
       float computeReward(State prev, State curr);
       bool isTerminal(State state);
   };
   ```
2. Implement reward function
3. Test with random agent (verify environment works)

#### Phase 4: RL Algorithm (Week 2-3)
1. Set up LibTorch (PyTorch C++ API)
2. Implement neural network:
   ```cpp
   struct PolicyNet : torch::nn::Module {
       PolicyNet() {
           fc1 = register_module("fc1", torch::nn::Linear(STATE_DIM, 256));
           fc2 = register_module("fc2", torch::nn::Linear(256, 256));
           fc3 = register_module("fc3", torch::nn::Linear(256, ACTION_COUNT));
       }
       torch::Tensor forward(torch::Tensor x);
   };
   ```
3. Implement PPO or DQN algorithm
4. Create training loop with experience buffer

#### Phase 5: Training (Week 3-4)
1. Train on simple corner map
2. Use TMInterface `set_speed 10` to train 10x faster!
3. Log rewards and success rate
4. Tune hyperparameters
5. Save best models

## Code Structure

```
Delamain/
├── include/
│   ├── TMInterfaceClient.hpp   // Named pipe communication with TMInterface
│   ├── Environment.hpp          // RL environment wrapper
│   ├── State.hpp                // State representation
│   ├── Agent.hpp                // RL agent (PPO/DQN)
│   ├── NeuralNetwork.hpp        // LibTorch neural network
│   └── Trainer.hpp              // Training loop & logging
├── src/
│   ├── TMInterfaceClient.cpp
│   ├── Environment.cpp
│   ├── Agent.cpp
│   ├── NeuralNetwork.cpp
│   ├── Trainer.cpp
│   └── main.cpp
├── maps/                        // Custom TMNF maps for training
│   └── simple_corner.Challenge.Gbx
├── models/                      // Saved neural network weights
├── logs/                        // Training logs & metrics
├── external/
│   └── TMInterfacePublic/       // Git submodule
└── CMakeLists.txt
```

## Key Libraries/Dependencies

```cmake
# CMakeLists.txt
cmake_minimum_required(VERSION 3.18)
project(Delamain)

set(CMAKE_CXX_STANDARD 17)

# LibTorch (PyTorch C++)
find_package(Torch REQUIRED)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${TORCH_CXX_FLAGS}")

# Windows named pipes (for TMInterface)
# Built-in on Windows, no extra dependency needed

# Optional: spdlog for logging
find_package(spdlog)

add_executable(${PROJECT_NAME}
    src/main.cpp
    src/TMInterfaceClient.cpp
    src/Environment.cpp
    src/Agent.cpp
    src/NeuralNetwork.cpp
    src/Trainer.cpp
)

target_include_directories(${PROJECT_NAME} PRIVATE include external/TMInterfacePublic)
target_link_libraries(${PROJECT_NAME} ${TORCH_LIBRARIES})
```

## TMInterface Quick Reference

### Console Commands (in-game F3)
```
set_speed <multiplier>    # e.g., set_speed 10 for 10x training speed
save_state <slot>         # Save current state to slot (0-9)
load_state <slot>         # Load state from slot
set_input <up> <down> <left> <right>  # Binary inputs (0 or 1)
get_simulation_state      # Print current position/velocity
```

### Key TMInterface Callbacks
When implementing your client, TMInterface triggers these events:
- `on_simulation_begin` - Race started
- `on_simulation_step` - Every 10ms tick
- `on_simulation_end` - Race finished
- `on_checkpoint` - Checkpoint crossed

## Training Tips for TMNF

1. **Use `set_speed`**: Train at 10-20x speed to collect experience faster
2. **Save States**: Save a state right at the corner entry, load it to practice just the corner
3. **Simple Map First**: Create the simplest possible map (start → corner → finish)
4. **Deterministic Physics**: TMNF physics are deterministic - use this for reproducible debugging
5. **Episode Length**: Limit to 30 seconds (3000 steps at 10ms/step)
6. **Reward Shaping**: Distance-to-checkpoint is your friend - provides dense rewards
7. **Checkpoint Positions**: You may need to hardcode checkpoint positions for reward calculation
8. **Normalize Inputs**: Scale position/velocity to reasonable ranges (e.g., [-1, 1])

## Creating a Training Map

1. Open TMNF → Track Editor
2. Create minimal track:
   - Place start block
   - Add 2-3 straight pieces
   - Add one 90° corner (Stadium Road Turn)
   - Add finish line after corner
3. Save as `simple_corner`
4. Validate (test drive) to ensure it's completable

## Common Pitfalls

1. **Sparse Rewards**: Without distance-to-checkpoint rewards, agent may never reach the goal
2. **Reward Hacking**: Agent might find it rewarding to drive backwards if reward is poorly designed
3. **Stuck in Local Minima**: Agent learns to stop before the corner instead of turning
4. **TMInterface Connection Issues**: Ensure TMNF is running before connecting
5. **Named Pipe Timeouts**: Handle connection drops gracefully
6. **Speed vs Quality**: Training too fast might cause input/state sync issues

## Alternative: Python Prototype First

For faster iteration, consider this hybrid approach:

1. **Use TMInterfaceClientPython** (donadigo's Python client)
2. **Use stable-baselines3** for RL (PPO implementation ready to use)
3. **Prototype and validate** your reward function
4. **Port to C++** once the approach is proven

```python
# Python prototype example
from tminterface.interface import TMInterface
from stable_baselines3 import PPO

class TMEnv(gym.Env):
    def __init__(self):
        self.interface = TMInterface()
        self.action_space = gym.spaces.Discrete(9)
        self.observation_space = gym.spaces.Box(low=-np.inf, high=np.inf, shape=(STATE_DIM,))
    
    def reset(self):
        self.interface.load_state(0)
        return self._get_obs()
    
    def step(self, action):
        self._apply_action(action)
        obs = self._get_obs()
        reward = self._compute_reward()
        done = self._is_done()
        return obs, reward, done, {}

model = PPO("MlpPolicy", TMEnv(), verbose=1)
model.learn(total_timesteps=100000)
```

## Resources

- **TMInterface Releases**: https://github.com/donadigo/TMInterface/releases
- **TMInterfacePublic (C++)**: https://github.com/donadigo/TMInterfacePublic
- **TMInterfaceClientPython**: https://github.com/donadigo/TMInterfaceClientPython
- **TMNF on Steam**: https://store.steampowered.com/app/11020/
- **LibTorch**: https://pytorch.org/cppdocs/
- **PPO Paper**: "Proximal Policy Optimization Algorithms" (Schulman et al., 2017)
- **Stable Baselines3**: https://stable-baselines3.readthedocs.io/

## Immediate Next Steps

1. ⬜ Install Trackmania Nations Forever
2. ⬜ Install TMInterface (download from releases page)
3. ⬜ Clone TMInterfacePublic: `git clone https://github.com/donadigo/TMInterfacePublic.git`
4. ⬜ Test TMInterface in-game (F3 console, try `set_speed 2`)
5. ⬜ Create simple test map with one corner
6. ⬜ Study TMInterfacePublic C++ code to understand the API
7. ⬜ Implement basic TMInterfaceClient wrapper
8. ⬜ Test reading state and sending inputs

## Estimated Timeline

| Phase | Description | Duration |
|-------|-------------|----------|
| 1 | TMNF + TMInterface setup & testing | 3-5 days |
| 2 | C++ TMInterface wrapper | 1 week |
| 3 | RL Environment implementation | 1 week |
| 4 | RL Algorithm (PPO/DQN) | 1-2 weeks |
| 5 | Training & iteration | 1-2 weeks |
| **Total** | **Working agent on simple corner** | **4-6 weeks** |

Good luck! Start simple, iterate fast, and enjoy the process! 🏎️
