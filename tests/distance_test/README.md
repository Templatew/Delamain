# Distance Test - TrackMania Screen Capture

A minimal module to test distance detection from TrackMania screen capture using ray-casting.

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Update `constants.py` with your TMInterface window name if needed:
   ```python
   GAME_WINDOW_NAME = "TrackMania Nations Forever (TMInterface 1.4.3)"
   ```

## Usage

1. Start TrackMania Nations Forever with TMInterface
2. Run the test from the parent directory:
   ```bash
   python -m distance_test.test_distances
   ```

## Controls

- `q` - Quit
- `s` - Save screenshot
- `p` - Print current distances

## How It Works

1. **Screen Capture**: Uses `mss` to capture the game window
2. **Edge Detection**: Applies Canny edge detection to find track boundaries
3. **Ray-casting**: Casts 16 rays from bottom-center of the processed image
4. **Distance Calculation**: Measures distance to first edge hit (normalized 0-1)

## Output

- Two OpenCV windows showing raw feed and processed image with rays
- Console output with ASCII distance bars every ~1 second
