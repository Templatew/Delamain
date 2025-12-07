from tminterface.interface import TMInterface
from tminterface.client import Client, run_client
import sys

class TestClient(Client):
    def __init__(self):
        super().__init__()
        self.step_count = 0
        
    def on_registered(self, iface: TMInterface):
        print("Connected to TMInterface!")
        print("Waiting for race steps...")
        print()
        # Set a longer timeout so we don't disconnect
        iface.set_timeout(10000)
        
    def on_run_step(self, iface: TMInterface, time: int):
        """Called during normal gameplay - try to inject inputs"""
        self.step_count += 1
        
        # Always press accelerate!
        iface.set_input_state(accelerate=True)
        
        # Print every second
        if self.step_count % 100 == 0:
            try:
                state = iface.get_simulation_state()
                vel = state.velocity
                speed = (vel[0]**2 + vel[1]**2 + vel[2]**2)**0.5 * 3.6
                print(f"Time: {time}ms | Speed: {speed:.1f} km/h | Holding ACCELERATE")
            except:
                print(f"Time: {time}ms | Holding ACCELERATE")
        
    def on_simulation_begin(self, iface: TMInterface):
        print("\n=== SIMULATION MODE (validating replay) ===")
        self.step_count = 0
        
    def on_simulation_step(self, iface: TMInterface, time: int):
        """Called during replay validation - full control here!"""
        self.step_count += 1
        
        # Full control in simulation mode
        iface.set_input_state(accelerate=True, brake=False, left=False, right=False)
        
        if self.step_count % 100 == 0:
            state = iface.get_simulation_state()
            vel = state.velocity
            speed = (vel[0]**2 + vel[1]**2 + vel[2]**2)**0.5 * 3.6
            print(f"[SIM] Time: {time}ms | Speed: {speed:.1f} km/h")
        
    def on_simulation_end(self, iface: TMInterface, result: int):
        print(f"\nSimulation ended (result: {result})")
        
    def on_checkpoint_count_changed(self, iface: TMInterface, current: int, target: int):
        print(f"*** CHECKPOINT {current}/{target} ***")

def main():
    print("=" * 50)
    print("TMInterface Control Test")
    print("=" * 50)
    print()
    print("This script will TRY to control your car.")
    print()
    print("For GUARANTEED control:")
    print("  1. Watch a replay and click 'Validate'")  
    print("  2. This triggers SIMULATION mode")
    print("  3. The script will have full control")
    print()
    print("Press Ctrl+C to exit")
    print()
    
    client = TestClient()
    run_client(client, "TMInterface0")

if __name__ == "__main__":
    main()
