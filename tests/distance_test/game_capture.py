import cv2
import numpy as np
import win32.win32gui as win32gui
from mss import mss

from distance_test.constants import GAME_WINDOW_NAME


def get_window_geometry(name: str) -> tuple:

    hwnd = win32gui.FindWindow(None, name)

    if hwnd == 0:
        raise ValueError(f"Window not found: '{name}'")
    
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)

    return left + 10, top + 40, right - 10, bottom - 10


class GameViewer:
    
    def __init__(self, n_rays: int = 16, window_name: str = None) -> None:
        self.window_name = window_name or GAME_WINDOW_NAME
        self.sct = mss()
        self.n_rays = n_rays

    @property
    def bounding_box(self):
        return get_window_geometry(self.window_name)

    def process_screen(self, screenshot: np.ndarray) -> np.ndarray:

        # Convert to grayscale
        gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        
        # Binary threshold - keep bright pixels
        _, binary = cv2.threshold(gray, 32, 255, cv2.THRESH_BINARY)
        
        # Edge detection
        edges = cv2.Canny(binary, threshold1=100, threshold2=300)
        
        # Dilate edges to make them thicker
        kernel = cv2.getStructuringElement(shape=cv2.MORPH_RECT, ksize=(5, 5))
        dilated = cv2.dilate(edges, kernel, iterations=3)
        
        # Blur and threshold to clean up
        blurred = cv2.GaussianBlur(dilated, (3, 3), 0)
        _, cleaned = cv2.threshold(blurred, 1, 255, cv2.THRESH_BINARY)
        
        # Resize and crop to bottom portion (where the road is)
        resized = cv2.resize(cleaned, (128, 128))
        height = len(resized)
        cropped = resized[height // 2 : height // 2 + 32, :]
        
        return cropped

    def is_inbounds(self, x: int, y: int, frame: np.ndarray) -> bool:
        return 0 <= x < len(frame[0]) and 0 <= y < len(frame)

    def find_end(self, direction: float, frame: np.ndarray) -> list:

        dx = np.cos(direction)
        dy = np.sin(direction)

        cur_x = len(frame[0]) // 2  # Start at center
        cur_y = len(frame) - 1       # Start at bottom

        # Walk along ray until hitting white pixel (edge) or going out of bounds
        while self.is_inbounds(int(cur_x), int(cur_y), frame):
            if frame[int(cur_y)][int(cur_x)] != 0:
                break
            cur_x += dx
            cur_y -= dy

        return [int(cur_x), int(cur_y)]

    def _scaling_func(self, angle: float) -> float:
        return (1 + 3 * np.sin(angle)) / 4

    def get_distance(self, point: list, ref_size: float, ref_point: tuple = (64, 127), angle: float = 0) -> float:

        raw_distance = np.linalg.norm(np.array(point) - np.array(ref_point), 2)
        
        return self._scaling_func(angle) * raw_distance / ref_size

    def get_rays(self, frame: np.ndarray, keep_horizontal: bool = True) -> tuple:
        rays = []
        angles = []
        iterator = range(self.n_rays) if keep_horizontal else range(1, self.n_rays - 1)
        
        for i in iterator:
            angle = i * np.pi / (self.n_rays - 1)
            rays.append(self.find_end(angle, frame))
            angles.append(angle)
            
        return rays, angles

    def get_obs(self) -> np.ndarray:
        processed_img = self.get_frame()
        ref_size = np.hypot(processed_img.shape[0], processed_img.shape[1]) / 2
        rays, angles = self.get_rays(processed_img)
        ref_point = (len(processed_img[0]) // 2, len(processed_img) - 1)
        
        distances = [
            self.get_distance(ray, ref_size, ref_point, angle)
            for ray, angle in zip(rays, angles)
        ]

        return np.array(distances).astype(np.float32)

    def get_frame(self, size: tuple = (256, 256)) -> np.ndarray:

        raw = self.get_raw_frame()
        resized = cv2.resize(raw, size)

        return self.process_screen(resized)

    def get_raw_frame(self) -> np.ndarray:

        screenshot = self.sct.grab(self.bounding_box)

        return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    def show_rays(self, frame: np.ndarray) -> np.ndarray:

        rays, _ = self.get_rays(frame, keep_horizontal=False)
        ref_point = (len(frame[0]) // 2, len(frame) - 1)
        
        for ray in rays:
            cv2.line(frame, ref_point, tuple(ray), (255, 0, 0), 1)

        return frame
