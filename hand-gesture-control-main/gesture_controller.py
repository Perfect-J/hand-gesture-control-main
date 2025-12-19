"""
Enhanced Gesture recognition with multiple control modes
Supports: Media Control, Mouse Control, Window Management, and Presentation Mode
"""
import time
import platform
import math
from enum import Enum

# Platform-specific imports
if platform.system() == "Windows":
    try:
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        from comtypes import CLSCTX_ALL
        from ctypes import cast, POINTER
        WINDOWS_AUDIO_AVAILABLE = True
    except ImportError:
        WINDOWS_AUDIO_AVAILABLE = False
        print("Warning: pycaw not installed. Volume control won't work.")

try:
    import pyautogui
    pyautogui.FAILSAFE = False  # Disable failsafe for smoother control
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    print("Warning: pyautogui not installed.")


class ControlMode(Enum):
    """Different control modes"""
    MEDIA = "media_control"
    MOUSE = "mouse_control"
    WINDOW = "window_management"
    PRESENTATION = "presentation_mode"


class Gesture(Enum):
    """Recognized gestures"""
    FIST = "fist"
    OPEN_HAND = "open_hand"
    PEACE = "peace"  # Index + Middle extended
    POINTING = "pointing"  # Index only
    THUMBS_UP = "thumbs_up"
    PINCH = "pinch"  # Thumb + Index close
    ROTATE_LEFT = "rotate_left"
    ROTATE_RIGHT = "rotate_right"
    SWIPE_LEFT = "swipe_left"
    SWIPE_RIGHT = "swipe_right"
    SWIPE_UP = "swipe_up"
    SWIPE_DOWN = "swipe_down"
    PALM_PUSH = "palm_push"  # Hand moving toward camera
    PALM_PULL = "palm_pull"  # Hand moving away
    NONE = "none"


class EnhancedGestureController:
    """
    Multi-mode gesture controller with adjustable sensitivity
    """
    
    def __init__(self, mode=ControlMode.MEDIA, sensitivity=1.0):
        self.mode = mode
        self.sensitivity = sensitivity
        self.current_gesture = Gesture.NONE
        self.last_gesture = Gesture.NONE
        self.gesture_start_time = time.time()
        
        # Adjustable thresholds based on sensitivity
        self.cooldown_time = max(0.3, 0.8 / sensitivity)
        self.last_action_time = 0
        
        # Rotation tracking
        self.last_rotation = None
        self.rotation_threshold = max(15, 25 / sensitivity)
        self.rotation_accumulator = 0
        
        # Position tracking
        self.last_palm_x = None
        self.last_palm_y = None
        self.last_palm_z = None  # depth
        self.swipe_threshold = max(60, 100 / sensitivity)
        self.depth_threshold = 0.08 / sensitivity
        
        # Finger state tracking for complex gestures
        self.finger_states = [False] * 5  # thumb, index, middle, ring, pinky
        
        # Mouse control specifics
        self.mouse_smoothing = 0.3
        self.mouse_anchor = None
        self.is_clicking = False
        self.is_dragging = False
        
        # Screen dimensions
        if PYAUTOGUI_AVAILABLE:
            self.screen_w, self.screen_h = pyautogui.size()
        else:
            self.screen_w, self.screen_h = 1920, 1080
        
        # Windows volume control
        self.volume_control = None
        if platform.system() == "Windows" and WINDOWS_AUDIO_AVAILABLE:
            try:
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                self.volume_control = cast(interface, POINTER(IAudioEndpointVolume))
            except Exception as e:
                print(f"Could not initialize volume control: {e}")
    
    def set_mode(self, mode):
        """Change control mode"""
        self.mode = mode
        self.reset_state()
        print(f"\n{'='*50}")
        print(f"Switched to: {mode.value.upper().replace('_', ' ')}")
        print(f"{'='*50}")
        self._print_mode_help()
    
    def set_sensitivity(self, sensitivity):
        """Adjust sensitivity (0.5 = less sensitive, 2.0 = more sensitive)"""
        self.sensitivity = max(0.3, min(3.0, sensitivity))
        self.cooldown_time = max(0.3, 0.8 / self.sensitivity)
        self.rotation_threshold = max(15, 25 / self.sensitivity)
        self.swipe_threshold = max(60, 100 / self.sensitivity)
        self.depth_threshold = 0.08 / self.sensitivity
        print(f"Sensitivity: {self.sensitivity:.1f}x")
    
    def reset_state(self):
        """Reset tracking state"""
        self.last_palm_x = None
        self.last_palm_y = None
        self.last_palm_z = None
        self.last_rotation = None
        self.rotation_accumulator = 0
        self.mouse_anchor = None
        self.is_clicking = False
        self.is_dragging = False
    
    def _detect_finger_states(self, landmarks):
        """
        Detect which fingers are extended
        Returns: [thumb, index, middle, ring, pinky] - True if extended
        """
        # Simplified finger detection
        # Compare fingertip y-position with base joint
        fingers = [False] * 5
        
        # Thumb (special case - check x distance)
        thumb_tip = landmarks[4]
        thumb_base = landmarks[2]
        fingers[0] = abs(thumb_tip[0] - thumb_base[0]) > 0.04
        
        # Other fingers (check y distance)
        finger_tips = [8, 12, 16, 20]
        finger_bases = [6, 10, 14, 18]
        
        for i, (tip_idx, base_idx) in enumerate(zip(finger_tips, finger_bases)):
            tip = landmarks[tip_idx]
            base = landmarks[base_idx]
            fingers[i + 1] = tip[1] < base[1] - 0.03  # tip above base
        
        return fingers
    
    def _detect_pinch(self, landmarks):
        """Detect if thumb and index finger are pinching"""
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        distance = math.sqrt(
            (thumb_tip[0] - index_tip[0])**2 + 
            (thumb_tip[1] - index_tip[1])**2
        )
        return distance < 0.05
    
    def detect_gesture(self, openness, rotation, palm_x, palm_y, palm_z, landmarks):
        """
        Detect current gesture with finger state analysis
        """
        gesture = Gesture.NONE
        
        # Detect finger states
        self.finger_states = self._detect_finger_states(landmarks)
        extended_count = sum(self.finger_states)
        
        # Complex gestures (finger combinations)
        if self._detect_pinch(landmarks):
            gesture = Gesture.PINCH
        elif self.finger_states[1] and not any(self.finger_states[2:]):  # Only index
            gesture = Gesture.POINTING
        elif self.finger_states[1] and self.finger_states[2] and not any(self.finger_states[3:]):  # Index + Middle
            gesture = Gesture.PEACE
        elif self.finger_states[0] and not any(self.finger_states[1:]):  # Only thumb
            gesture = Gesture.THUMBS_UP
        # Basic openness gestures
        elif openness < 25:
            gesture = Gesture.FIST
        elif openness > 75:
            gesture = Gesture.OPEN_HAND
        
        # Depth gestures (push/pull)
        if self.last_palm_z is not None:
            z_diff = palm_z - self.last_palm_z
            if z_diff < -self.depth_threshold:
                gesture = Gesture.PALM_PUSH
            elif z_diff > self.depth_threshold:
                gesture = Gesture.PALM_PULL
        
        # Rotation gestures
        if self.last_rotation is not None:
            rot_diff = rotation - self.last_rotation
            if rot_diff > 180:
                rot_diff -= 360
            elif rot_diff < -180:
                rot_diff += 360
            
            self.rotation_accumulator += rot_diff
            
            if abs(self.rotation_accumulator) > self.rotation_threshold:
                if self.rotation_accumulator > 0:
                    gesture = Gesture.ROTATE_RIGHT
                else:
                    gesture = Gesture.ROTATE_LEFT
                self.rotation_accumulator = 0
        
        # Swipe gestures (prioritize over depth/rotation)
        if self.last_palm_x is not None and self.last_palm_y is not None:
            x_diff = palm_x - self.last_palm_x
            y_diff = palm_y - self.last_palm_y
            
            if abs(x_diff) > self.swipe_threshold and abs(x_diff) > abs(y_diff):
                gesture = Gesture.SWIPE_RIGHT if x_diff > 0 else Gesture.SWIPE_LEFT
                self.last_palm_x = palm_x
            elif abs(y_diff) > self.swipe_threshold and abs(y_diff) > abs(x_diff):
                gesture = Gesture.SWIPE_UP if y_diff < 0 else Gesture.SWIPE_DOWN
                self.last_palm_y = palm_y
        
        # Update tracking
        if gesture not in [Gesture.SWIPE_LEFT, Gesture.SWIPE_RIGHT, Gesture.SWIPE_UP, Gesture.SWIPE_DOWN]:
            if self.last_palm_x is None or abs(palm_x - self.last_palm_x) < 10:
                self.last_palm_x = palm_x
            if self.last_palm_y is None or abs(palm_y - self.last_palm_y) < 10:
                self.last_palm_y = palm_y
        
        self.last_rotation = rotation
        self.last_palm_z = palm_z
        self.current_gesture = gesture
        return gesture
    
    def execute_action(self, gesture, palm_x, palm_y):
        """Execute action based on mode and gesture"""
        if self.mode == ControlMode.MEDIA:
            return self._media_control(gesture)
        elif self.mode == ControlMode.MOUSE:
            return self._mouse_control(gesture, palm_x, palm_y)
        elif self.mode == ControlMode.WINDOW:
            return self._window_management(gesture)
        elif self.mode == ControlMode.PRESENTATION:
            return self._presentation_control(gesture)
        return False
    
    def _media_control(self, gesture):
        """Media control actions"""
        now = time.time()
        if now - self.last_action_time < self.cooldown_time:
            return False
        
        if not PYAUTOGUI_AVAILABLE:
            return False
        
        action_taken = False
        try:
            if gesture == Gesture.FIST:
                pyautogui.press('playpause')
                action_taken = True
                print("⏸️  PAUSE/PLAY")
            elif gesture == Gesture.OPEN_HAND:
                pyautogui.press('playpause')
                action_taken = True
                print("▶️  PLAY/PAUSE")
            elif gesture == Gesture.ROTATE_LEFT:
                self._adjust_volume(-0.05)
                action_taken = True
                print("🔉 VOLUME DOWN")
            elif gesture == Gesture.ROTATE_RIGHT:
                self._adjust_volume(0.05)
                action_taken = True
                print("🔊 VOLUME UP")
            elif gesture == Gesture.SWIPE_LEFT:
                pyautogui.press('prevtrack')
                action_taken = True
                print("⏮️  PREVIOUS")
            elif gesture == Gesture.SWIPE_RIGHT:
                pyautogui.press('nexttrack')
                action_taken = True
                print("⏭️  NEXT")
            elif gesture == Gesture.SWIPE_UP:
                self._adjust_volume(0.1)
                action_taken = True
                print("🔊 VOLUME UP (Fast)")
            elif gesture == Gesture.SWIPE_DOWN:
                self._adjust_volume(-0.1)
                action_taken = True
                print("🔉 VOLUME DOWN (Fast)")
            elif gesture == Gesture.PEACE:
                pyautogui.press('space')
                action_taken = True
                print("⏯️  SPACE (Play/Pause)")
            elif gesture == Gesture.THUMBS_UP:
                pyautogui.hotkey('ctrl', 'up')
                action_taken = True
                print("👍 INCREASE SPEED")
        
        except Exception as e:
            print(f"Error: {e}")
        
        if action_taken:
            self.last_action_time = now
        return action_taken
    
    def _mouse_control(self, gesture, palm_x, palm_y):
        """Mouse control actions"""
        if not PYAUTOGUI_AVAILABLE:
            return False
        
        action_taken = False
        
        try:
            # Move cursor with open hand or pointing
            if gesture in [Gesture.OPEN_HAND, Gesture.POINTING]:
                # Map palm position to screen
                target_x = int(palm_x * self.screen_w / 640)  # Assuming 640px webcam width
                target_y = int(palm_y * self.screen_h / 480)  # Assuming 480px webcam height
                
                # Smooth mouse movement
                current_x, current_y = pyautogui.position()
                new_x = int(current_x + (target_x - current_x) * (1 - self.mouse_smoothing))
                new_y = int(current_y + (target_y - current_y) * (1 - self.mouse_smoothing))
                
                pyautogui.moveTo(new_x, new_y)
                action_taken = True
            
            # Click with pinch
            elif gesture == Gesture.PINCH:
                if not self.is_clicking:
                    pyautogui.click()
                    self.is_clicking = True
                    print("🖱️  CLICK")
                action_taken = True
            else:
                self.is_clicking = False
            
            # Right click with peace sign
            if gesture == Gesture.PEACE and not self.is_clicking:
                pyautogui.rightClick()
                self.is_clicking = True
                print("🖱️  RIGHT CLICK")
                action_taken = True
            
            # Scroll with fist
            if gesture == Gesture.FIST:
                if self.last_palm_y is not None:
                    scroll_amount = int((palm_y - self.last_palm_y) * 2)
                    if abs(scroll_amount) > 5:
                        pyautogui.scroll(scroll_amount)
                        action_taken = True
            
            # Drag with thumbs up
            if gesture == Gesture.THUMBS_UP:
                if not self.is_dragging:
                    pyautogui.mouseDown()
                    self.is_dragging = True
                    print("🖱️  DRAG START")
                action_taken = True
            else:
                if self.is_dragging:
                    pyautogui.mouseUp()
                    self.is_dragging = False
                    print("🖱️  DRAG END")
        
        except Exception as e:
            print(f"Mouse error: {e}")
        
        return action_taken
    
    def _window_management(self, gesture):
        """Window management actions"""
        now = time.time()
        if now - self.last_action_time < self.cooldown_time:
            return False
        
        if not PYAUTOGUI_AVAILABLE:
            return False
        
        action_taken = False
        
        try:
            if gesture == Gesture.SWIPE_LEFT:
                pyautogui.hotkey('win', 'left')
                action_taken = True
                print("⬅️  SNAP LEFT")
            elif gesture == Gesture.SWIPE_RIGHT:
                pyautogui.hotkey('win', 'right')
                action_taken = True
                print("➡️  SNAP RIGHT")
            elif gesture == Gesture.SWIPE_UP:
                pyautogui.hotkey('win', 'up')
                action_taken = True
                print("⬆️  MAXIMIZE")
            elif gesture == Gesture.SWIPE_DOWN:
                pyautogui.hotkey('win', 'down')
                action_taken = True
                print("⬇️  MINIMIZE/RESTORE")
            elif gesture == Gesture.FIST:
                pyautogui.hotkey('alt', 'f4')
                action_taken = True
                print("❌ CLOSE WINDOW")
            elif gesture == Gesture.PEACE:
                pyautogui.hotkey('alt', 'tab')
                action_taken = True
                print("🔄 SWITCH WINDOW")
            elif gesture == Gesture.OPEN_HAND:
                pyautogui.hotkey('win', 'd')
                action_taken = True
                print("🖥️  SHOW DESKTOP")
            elif gesture == Gesture.THUMBS_UP:
                pyautogui.hotkey('win', 'tab')
                action_taken = True
                print("📊 TASK VIEW")
        
        except Exception as e:
            print(f"Window error: {e}")
        
        if action_taken:
            self.last_action_time = now
        return action_taken
    
    def _presentation_control(self, gesture):
        """Presentation mode actions"""
        now = time.time()
        if now - self.last_action_time < self.cooldown_time:
            return False
        
        if not PYAUTOGUI_AVAILABLE:
            return False
        
        action_taken = False
        
        try:
            if gesture == Gesture.SWIPE_RIGHT or gesture == Gesture.POINTING:
                pyautogui.press('right')
                action_taken = True
                print("➡️  NEXT SLIDE")
            elif gesture == Gesture.SWIPE_LEFT:
                pyautogui.press('left')
                action_taken = True
                print("⬅️  PREVIOUS SLIDE")
            elif gesture == Gesture.FIST:
                pyautogui.press('b')
                action_taken = True
                print("⬛ BLACK SCREEN")
            elif gesture == Gesture.OPEN_HAND:
                pyautogui.press('w')
                action_taken = True
                print("⬜ WHITE SCREEN")
            elif gesture == Gesture.PEACE:
                pyautogui.press('home')
                action_taken = True
                print("🏠 FIRST SLIDE")
            elif gesture == Gesture.THUMBS_UP:
                pyautogui.press('end')
                action_taken = True
                print("🏁 LAST SLIDE")
        
        except Exception as e:
            print(f"Presentation error: {e}")
        
        if action_taken:
            self.last_action_time = now
        return action_taken
    
    def _adjust_volume(self, change):
        """Adjust system volume"""
        if platform.system() == "Windows" and self.volume_control:
            try:
                current = self.volume_control.GetMasterVolumeLevelScalar()
                new_volume = max(0.0, min(1.0, current + change))
                self.volume_control.SetMasterVolumeLevelScalar(new_volume, None)
            except Exception:
                pass
        elif PYAUTOGUI_AVAILABLE:
            if change > 0:
                for _ in range(int(abs(change) * 20)):
                    pyautogui.press('volumeup')
            else:
                for _ in range(int(abs(change) * 20)):
                    pyautogui.press('volumedown')
    
    def process_frame(self, openness, rotation, palm_x, palm_y, palm_z, landmarks):
        """Process frame and execute actions"""
        gesture = self.detect_gesture(openness, rotation, palm_x, palm_y, palm_z, landmarks)
        
        if gesture != Gesture.NONE and gesture != self.last_gesture:
            self.gesture_start_time = time.time()
            self.last_gesture = gesture
        
        action_taken = False
        hold_time = 0.2 if self.mode == ControlMode.MOUSE else 0.3
        
        if gesture != Gesture.NONE and time.time() - self.gesture_start_time > hold_time:
            action_taken = self.execute_action(gesture, palm_x, palm_y)
        
        return gesture, action_taken
    
    def _print_mode_help(self):
        """Print help for current mode"""
        helps = {
            ControlMode.MEDIA: [
                "Fist - Pause/Play",
                "Open Hand - Play/Pause",
                "Rotate Left/Right - Volume",
                "Swipe Left/Right - Prev/Next Track",
                "Swipe Up/Down - Volume (Fast)",
                "Peace Sign - Space Bar",
                "Thumbs Up - Increase Speed"
            ],
            ControlMode.MOUSE: [
                "Open Hand/Pointing - Move Cursor",
                "Pinch - Click",
                "Peace Sign - Right Click",
                "Fist - Scroll (move hand up/down)",
                "Thumbs Up - Drag (hold to drag)"
            ],
            ControlMode.WINDOW: [
                "Swipe Left/Right - Snap Window",
                "Swipe Up - Maximize",
                "Swipe Down - Minimize/Restore",
                "Fist - Close Window",
                "Peace - Switch Window (Alt+Tab)",
                "Open Hand - Show Desktop",
                "Thumbs Up - Task View"
            ],
            ControlMode.PRESENTATION: [
                "Swipe Right/Pointing - Next Slide",
                "Swipe Left - Previous Slide",
                "Fist - Black Screen",
                "Open Hand - White Screen",
                "Peace - First Slide",
                "Thumbs Up - Last Slide"
            ]
        }
        
        for line in helps.get(self.mode, []):
            print(f"  {line}")
        print()
    
    def get_mode_name(self):
        """Get current mode name"""
        return self.mode.value.replace('_', ' ').upper()