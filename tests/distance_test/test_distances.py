import cv2
import numpy as np

from distance_test.game_capture import GameViewer


def print_distance_bar(distances: np.ndarray, width: int = 40):
    """Print a visual ASCII representation of distances."""
    print("\n" + "=" * 60)
    print("DISTANCE FROM OBSTACLES (0=close, 1=far)")
    print("=" * 60)
    
    n_rays = len(distances)
    labels = {0: "LEFT", n_rays // 2: "CENTER", n_rays - 1: "RIGHT"}
    
    for i, dist in enumerate(distances):
        bar_length = int(dist * width)
        bar = "█" * bar_length + "░" * (width - bar_length)
        
        # Status based on distance
        if dist < 0.1:
            status = "⚠️ DANGER"
        elif dist < 0.3:
            status = "⚡ CLOSE"
        else:
            status = "✓ SAFE"
        
        label = labels.get(i, f"Ray {i:02d}")
        print(f"{label:>6} | {bar} | {dist:.3f} {status}")
    
    print("=" * 60)
    print(f"MIN: {min(distances):.3f} | MAX: {max(distances):.3f} | AVG: {np.mean(distances):.3f}")
    print("=" * 60)

def draw_distance_overlay(frame: np.ndarray, distances: np.ndarray) -> np.ndarray:

    height, width = frame.shape[:2]
    
    # Draw distance graph
    points = []
    for i, dist in enumerate(distances):
        x = int((i / (len(distances) - 1)) * (width - 40)) + 20
        y = int((1 - dist) * 100) + 50
        points.append((x, y))
        
        # Color based on distance
        color = (0, 255, 0) if dist > 0.3 else (0, 165, 255) if dist > 0.1 else (0, 0, 255)
        cv2.circle(frame, (x, y), 5, color, -1)
        cv2.putText(frame, f"{dist:.2f}", (x - 15, y - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
    
    # Connect points with line
    for i in range(len(points) - 1):
        cv2.line(frame, points[i], points[i + 1], (255, 255, 0), 2)
    
    # Add labels
    cv2.putText(frame, "Distance Graph (top=far, bottom=close)",
               (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    cv2.putText(frame, f"MIN: {min(distances):.3f}",
               (20, 170), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
    
    return frame


def main():
    print("=" * 60)
    print("TRACKMANIA DISTANCE DETECTOR")
    print("=" * 60)
    print("Make sure TrackMania Nations Forever is running with TMInterface!")
    print("\nControls:")
    print("  q - Quit")
    print("  s - Save screenshot")
    print("  p - Print distances")
    print("=" * 60 + "\n")
    
    try:
        viewer = GameViewer(n_rays=16)
        print("✓ GameViewer initialized successfully")
        print(f"✓ Looking for window: '{viewer.window_name}'")
    except Exception as e:
        print(f"✗ Error: Could not initialize GameViewer")
        print(f"  Details: {e}")
        return
    
    # Test window detection
    try:
        bbox = viewer.bounding_box
        print(f"✓ Game window found at: {bbox}")
    except ValueError as e:
        print(f"✗ Error: {e}")
        print("\nTip: Check that the game window title matches constants.py")
        return
    
    print("\nStarting capture loop...\n")
    frame_count = 0
    
    while True:
        frame_count += 1
        
        try:
            # Capture frames
            raw_frame = viewer.get_raw_frame()
            processed_frame = viewer.get_frame()
            distances = viewer.get_obs()
            
            # Prepare display frames
            display_raw = cv2.resize(raw_frame, (640, 480))
            display_raw = draw_distance_overlay(display_raw, distances)
            cv2.putText(display_raw, f"Frame: {frame_count}",
                       (520, 470), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            raytrace_frame = viewer.show_rays(processed_frame.copy())
            display_processed = cv2.resize(raytrace_frame, (512, 192))
            
            # Show windows
            cv2.imshow("TrackMania - Raw + Distance Graph", display_raw)
            cv2.imshow("TrackMania - Edge Detection + Rays", display_processed)
            
            
            # Handle keys
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("\nQuitting...")
                break
            elif key == ord('s'):
                cv2.imwrite(f"screenshot_{frame_count}.png", raw_frame)
                cv2.imwrite(f"processed_{frame_count}.png", raytrace_frame)
                print(f"✓ Saved screenshot_{frame_count}.png")
            elif key == ord('p'):
                print_distance_bar(distances)
                
        except Exception as e:
            print(f"✗ Error: {e}")
            break
    
    cv2.destroyAllWindows()
    print("Test complete!")


if __name__ == "__main__":
    main()
