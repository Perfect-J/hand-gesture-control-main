import os
import cv2
import mediapipe as mp
import numpy as np
import time
from hand_overlay import (
    draw_skeleton,
    draw_palm_radial_ui,
    draw_rotation_text,
    draw_cube_and_grid,
    draw_fingertip_gears,
    draw_palm_data_text,
    landmarks_to_pixel,
)
from utils import Smoother, angle_between
from gesture_controller import EnhancedGestureController, Gesture, ControlMode

# Quiet TensorFlow
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

mp_hands = mp.solutions.hands

# Smoothing objects
palm_smoother = Smoother(alpha=0.6)
rot_smoother = Smoother(alpha=0.6)
openess_smoother = Smoother(alpha=0.4)


def compute_palm_rotation(landmarks):
    """Estimate palm rotation using vector from wrist (0) to middle_finger_mcp (9)"""
    w = np.array(landmarks[0][:2])
    m = np.array(landmarks[9][:2])
    v = m - w
    angle = np.degrees(np.arctan2(v[1], v[0]))
    angle = float(angle % 360)
    return angle


def draw_enhanced_ui(img, gesture, action_taken, mode_name, sensitivity, control_enabled, w, h):
    """Draw enhanced UI with mode and sensitivity info"""
    
    # Top left: FPS and Gesture
    y_pos = 24
    gesture_text = gesture.value.replace('_', ' ').upper()
    color = (0, 255, 0) if action_taken else (180, 180, 180)
    
    cv2.putText(img, f"Gesture: {gesture_text}", (10, y_pos), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2, cv2.LINE_AA)
    
    if action_taken:
        cv2.circle(img, (260, y_pos - 7), 6, (0, 255, 0), -1, cv2.LINE_AA)
    
    # Mode indicator
    y_pos += 30
    mode_color = (0, 255, 255) if control_enabled else (100, 100, 100)
    cv2.putText(img, f"Mode: {mode_name}", (10, y_pos), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, mode_color, 2, cv2.LINE_AA)
    
    # Sensitivity
    y_pos += 30
    sens_text = f"Sensitivity: {sensitivity:.1f}x"
    cv2.putText(img, sens_text, (10, y_pos), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 100), 2, cv2.LINE_AA)
    
    # Control status (top right)
    if control_enabled:
        status_color = (0, 255, 0)
        status_text = "● ACTIVE"
    else:
        status_color = (0, 0, 255)
        status_text = "○ PAUSED"
    
    cv2.putText(img, status_text, (w - 140, 24), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2, cv2.LINE_AA)
    
    # Bottom: Controls
    controls = [
        "C: Toggle | M: Mode | +/-: Sensitivity | H: Help | ESC: Quit"
    ]
    
    for i, text in enumerate(controls):
        cv2.putText(img, text, (10, h - 20 - (i * 25)), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1, cv2.LINE_AA)


def print_controls():
    """Print available keyboard controls"""
    print("\n" + "="*60)
    print("KEYBOARD CONTROLS")
    print("="*60)
    print("  C          - Toggle gesture control ON/OFF")
    print("  M          - Cycle through control modes")
    print("  +/=        - Increase sensitivity")
    print("  -/_        - Decrease sensitivity")
    print("  1          - Media Control mode")
    print("  2          - Mouse Control mode")
    print("  3          - Window Management mode")
    print("  4          - Presentation mode")
    print("  H          - Show this help")
    print("  ESC        - Quit application")
    print("="*60 + "\n")


def run():
    cap = cv2.VideoCapture(0)
    
    # Get actual camera resolution
    cam_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    cam_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    prev = time.time()
    fps = 0.0
    
    # Initialize enhanced gesture controller
    gesture_controller = EnhancedGestureController(
        mode=ControlMode.MEDIA, 
        sensitivity=1.0
    )
    
    control_enabled = True
    show_help = False
    
    with mp_hands.Hands(
        static_image_mode=False, 
        max_num_hands=1, 
        min_detection_confidence=0.6, 
        min_tracking_confidence=0.6
    ) as hands:
        
        print("\n" + "="*60)
        print("ENHANCED HAND GESTURE CONTROL")
        print("="*60)
        print(f"\nStarting in {gesture_controller.get_mode_name()} mode")
        print(f"Sensitivity: {gesture_controller.sensitivity:.1f}x")
        print("\nPress 'H' for help")
        print("="*60 + "\n")
        
        try:
            while True:
                ok, frame = cap.read()
                if not ok:
                    break
                
                now = time.time()
                dt = now - prev if now - prev > 0 else 1e-6
                prev = now
                fps = 0.9 * fps + 0.1 * (1.0 / dt)

                h, w = frame.shape[:2]
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = hands.process(frame_rgb)

                overlay = frame.copy()
                t = now
                
                current_gesture = Gesture.NONE
                action_taken = False
                
                if results.multi_hand_landmarks:
                    hand = results.multi_hand_landmarks[0]
                    lm = [(l.x, l.y, l.z) for l in hand.landmark]
                    pix = landmarks_to_pixel(lm, w, h)

                    # Compute palm center
                    palm = ((pix[0][0] + pix[9][0]) // 2, (pix[0][1] + pix[9][1]) // 2)
                    palm = tuple(map(int, palm_smoother.update(palm)))

                    # Rotation
                    rot = compute_palm_rotation(lm)
                    rot = float(rot_smoother.update(rot))

                    # Estimate openness
                    tips = [4, 8, 12, 16, 20]
                    dists = []
                    for ti in tips:
                        tx = int(lm[ti][0] * w)
                        ty = int(lm[ti][1] * h)
                        dists.append(np.hypot(tx - palm[0], ty - palm[1]))
                    
                    openness = 0
                    if dists:
                        mean_dist = float(np.mean(dists))
                        closed_ref = max(12.0, min(40.0, min(w, h) * 0.04))
                        open_ref = max(60.0, min(w, h) * 0.55)
                        raw_openness = (mean_dist - closed_ref) / (open_ref - closed_ref) * 100.0
                        raw_openness = float(np.clip(raw_openness, 0.0, 100.0))
                        openness = float(openess_smoother.update(raw_openness))
                    
                    # Get palm depth (z coordinate)
                    palm_z = lm[9][2]  # Middle finger base z
                    
                    # ENHANCED GESTURE CONTROL
                    if control_enabled:
                        current_gesture, action_taken = gesture_controller.process_frame(
                            openness, rot, palm[0], palm[1], palm_z, lm
                        )
                    
                    # Draw HUD
                    draw_palm_radial_ui(overlay, palm, rot, t=t, width=1.0 + openness / 160.0)
                    draw_skeleton(overlay, pix, t=t)
                    
                    try:
                        from hand_overlay import draw_decorative_bones
                        draw_decorative_bones(overlay, pix)
                    except Exception:
                        pass
                    
                    draw_rotation_text(overlay, palm, rot)
                    
                    # Cube near wrist
                    wrist_anchor = (pix[0][0] - 80, pix[0][1] + 40)
                    draw_cube_and_grid(overlay, wrist_anchor, t=t)
                    draw_fingertip_gears(overlay, pix, rot, t=t)
                    draw_palm_data_text(overlay, wrist_anchor, openness)

                # Draw enhanced UI
                cv2.putText(overlay, f"FPS: {int(fps)}", (10, h - 50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180, 180, 180), 2, cv2.LINE_AA)
                
                draw_enhanced_ui(
                    overlay, 
                    current_gesture, 
                    action_taken, 
                    gesture_controller.get_mode_name(),
                    gesture_controller.sensitivity,
                    control_enabled,
                    w, h
                )

                cv2.imshow('Enhanced Hand Gesture Control', overlay)
                key = cv2.waitKey(1) & 0xFF
                
                # Keyboard controls
                if key == 27:  # ESC
                    break
                
                elif key == ord('c') or key == ord('C'):
                    control_enabled = not control_enabled
                    status = "ENABLED" if control_enabled else "DISABLED"
                    print(f"\n{'='*60}")
                    print(f"Gesture Control: {status}")
                    print(f"{'='*60}\n")
                    if control_enabled:
                        gesture_controller._print_mode_help()
                
                elif key == ord('m') or key == ord('M'):
                    # Cycle through modes
                    modes = list(ControlMode)
                    current_idx = modes.index(gesture_controller.mode)
                    next_idx = (current_idx + 1) % len(modes)
                    gesture_controller.set_mode(modes[next_idx])
                    gesture_controller._print_mode_help()
                
                elif key == ord('1'):
                    gesture_controller.set_mode(ControlMode.MEDIA)
                    gesture_controller._print_mode_help()
                
                elif key == ord('2'):
                    gesture_controller.set_mode(ControlMode.MOUSE)
                    gesture_controller._print_mode_help()
                
                elif key == ord('3'):
                    gesture_controller.set_mode(ControlMode.WINDOW)
                    gesture_controller._print_mode_help()
                
                elif key == ord('4'):
                    gesture_controller.set_mode(ControlMode.PRESENTATION)
                    gesture_controller._print_mode_help()
                
                elif key in [ord('+'), ord('=')]:
                    gesture_controller.set_sensitivity(gesture_controller.sensitivity + 0.2)
                
                elif key in [ord('-'), ord('_')]:
                    gesture_controller.set_sensitivity(gesture_controller.sensitivity - 0.2)
                
                elif key == ord('h') or key == ord('H'):
                    print_controls()
                    gesture_controller._print_mode_help()
                        
        except KeyboardInterrupt:
            pass
        finally:
            cap.release()
            cv2.destroyAllWindows()
            print("\n" + "="*60)
            print("Thank you for using Enhanced Hand Gesture Control!")
            print("="*60 + "\n")


if __name__ == '__main__':
    print_controls()
    run()