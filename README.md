# 🎮 Enhanced Hand Gesture Control System

A powerful multi-mode hand gesture recognition system that lets you control your computer using just your webcam and hand movements!

## ✨ Features

### 🎯 **4 Control Modes:**
1. **Media Control** - Control music/video players
2. **Mouse Control** - Control cursor and clicks
3. **Window Management** - Manage windows and desktop
4. **Presentation Mode** - Control PowerPoint/slides

### 🤚 **Advanced Gestures:**
- **Fist** (closed hand)
- **Open Hand** (fully extended)
- **Pointing** (index finger only)
- **Peace Sign** (index + middle fingers)
- **Thumbs Up**
- **Pinch** (thumb + index touching)
- **Rotation** (rotate hand left/right)
- **Swipes** (left, right, up, down)
- **Push/Pull** (move hand toward/away from camera)

### ⚙️ **Adjustable Sensitivity:**
- Change from 0.3x to 3.0x
- More sensitive = faster response
- Less sensitive = more deliberate control

---

## 📦 Installation

### 1. Install Dependencies

```bash
pip install mediapipe opencv-python numpy pyautogui
```

**For Windows users (for volume control):**
```bash
pip install pycaw comtypes
```

### 2. Download Files

You need these files:
- `main_with_gestures.py` (main program)
- `gesture_controller.py` (gesture detection)
- `hand_overlay.py` (visual HUD)
- `utils.py` (helper functions)

### 3. Run

```bash
python main_with_gestures.py
```

---

## 🎮 Control Modes

### 1️⃣ Media Control Mode

Perfect for controlling Spotify, YouTube, VLC, etc.

| Gesture | Action |
|---------|--------|
| 🤛 **Fist** | Pause/Play |
| ✋ **Open Hand** | Play/Pause |
| 🔄 **Rotate Left** | Volume Down |
| 🔄 **Rotate Right** | Volume Up |
| ⬅️ **Swipe Left** | Previous Track |
| ➡️ **Swipe Right** | Next Track |
| ⬆️ **Swipe Up** | Volume Up (Fast) |
| ⬇️ **Swipe Down** | Volume Down (Fast) |
| ✌️ **Peace Sign** | Space Bar (Play/Pause) |
| 👍 **Thumbs Up** | Increase Playback Speed |

**Great for:**
- Watching movies in bed
- Following workout videos
- Cooking while watching recipes
- Listening to music while working

---

### 2️⃣ Mouse Control Mode

Control your cursor without touching the mouse!

| Gesture | Action |
|---------|--------|
| ✋ **Open Hand** | Move Cursor (palm tracks cursor) |
| 👉 **Pointing** | Move Cursor (fingertip tracks) |
| 🤏 **Pinch** | Left Click |
| ✌️ **Peace Sign** | Right Click |
| 🤛 **Fist** | Scroll (move hand up/down) |
| 👍 **Thumbs Up** | Drag (hold for drag & drop) |

**Great for:**
- Touchless presentations
- Hands busy situations
- Accessibility needs
- Cool demos

---

### 3️⃣ Window Management Mode

Manage your desktop and windows with gestures.

| Gesture | Action |
|---------|--------|
| ⬅️ **Swipe Left** | Snap Window Left (Win + ←) |
| ➡️ **Swipe Right** | Snap Window Right (Win + →) |
| ⬆️ **Swipe Up** | Maximize Window (Win + ↑) |
| ⬇️ **Swipe Down** | Minimize/Restore (Win + ↓) |
| 🤛 **Fist** | Close Window (Alt + F4) |
| ✌️ **Peace Sign** | Switch Window (Alt + Tab) |
| ✋ **Open Hand** | Show Desktop (Win + D) |
| 👍 **Thumbs Up** | Task View (Win + Tab) |

**Great for:**
- Quick window organization
- Multitasking workflows
- Touchless desktop management

---

### 4️⃣ Presentation Mode

Perfect for PowerPoint, Google Slides, Keynote.

| Gesture | Action |
|---------|--------|
| ➡️ **Swipe Right** | Next Slide |
| 👉 **Pointing** | Next Slide |
| ⬅️ **Swipe Left** | Previous Slide |
| 🤛 **Fist** | Black Screen (hide slide) |
| ✋ **Open Hand** | White Screen (blank) |
| ✌️ **Peace Sign** | First Slide (Home) |
| 👍 **Thumbs Up** | Last Slide (End) |

**Great for:**
- Professional presentations
- Teaching/lectures
- Keeping distance from computer
- Stage presentations

---

## ⌨️ Keyboard Controls

| Key | Action |
|-----|--------|
| **C** | Toggle gesture control ON/OFF |
| **M** | Cycle through modes |
| **1** | Switch to Media Control |
| **2** | Switch to Mouse Control |
| **3** | Switch to Window Management |
| **4** | Switch to Presentation Mode |
| **+/=** | Increase sensitivity |
| **-/_** | Decrease sensitivity |
| **H** | Show help |
| **ESC** | Quit application |

---

## 🎚️ Sensitivity Guide

Adjust sensitivity based on your preference:

- **0.5x** - Very deliberate (good for beginners)
- **1.0x** - Default (balanced)
- **1.5x** - Faster response
- **2.0x** - Very responsive (for experienced users)
- **3.0x** - Maximum speed

**Tip:** Start at 1.0x and adjust up/down as needed!

---

## 💡 Tips for Best Performance

### Camera Setup:
- ✅ Good lighting (avoid backlighting)
- ✅ Plain background (not too busy)
- ✅ Camera at chest/face height
- ✅ Hand clearly visible in frame

### Gesture Tips:
- ✅ Make deliberate, clear gestures
- ✅ Hold gestures for 0.3 seconds
- ✅ Keep hand at comfortable distance (arm's length)
- ✅ Avoid rapid, jerky movements
- ✅ Practice each gesture before using

### Performance:
- ✅ Close unnecessary applications
- ✅ Use adequate CPU/GPU
- ✅ Adjust sensitivity if gestures are too sensitive/slow

---

## 🐛 Troubleshooting

### Problem: Gestures not detected
**Solution:**
- Improve lighting
- Move hand closer/farther
- Make gestures more deliberate
- Increase sensitivity with `+` key

### Problem: Too many false triggers
**Solution:**
- Decrease sensitivity with `-` key
- Make slower, clearer gestures
- Pause control with `C` key when not in use

### Problem: Mouse control is jumpy
**Solution:**
- This is normal due to hand tracking
- Try holding hand more steady
- Adjust sensitivity down slightly

### Problem: Volume control not working (Windows)
**Solution:**
```bash
pip install pycaw comtypes
```

### Problem: Media keys not working
**Solution:**
- Make sure pyautogui is installed
- Test with a media player open
- Some apps may not respond to media keys

---

## 🎯 Use Cases

### At Home:
- 🎬 Watch movies without remote
- 🏋️ Follow workout videos hands-free
- 👨‍🍳 Cook while watching recipes
- 🎵 Control music while working

### At Work:
- 📊 Professional presentations
- 🖥️ Quick window management
- 👥 Demo applications touchlessly
- ♿ Accessibility solution

### For Content Creators:
- 🎥 Control recording without keyboard
- 🎮 Stream with gesture controls
- 📹 Create demo videos
- ✨ Impressive visual effects

---

## 🔧 Customization

Want to add your own gestures or actions?

Edit `gesture_controller.py`:

1. Add gesture to `Gesture` enum
2. Add detection logic in `detect_gesture()`
3. Add action in appropriate mode function
4. Test and adjust sensitivity

---

## 📊 System Requirements

- **OS:** Windows 10/11, macOS, Linux
- **Python:** 3.8+
- **Webcam:** Any USB or built-in camera
- **RAM:** 4GB minimum, 8GB recommended
- **CPU:** Multi-core processor recommended

---

## 🎓 Learning Curve

- **Beginner:** 5-10 minutes to learn basic gestures
- **Intermediate:** 30 minutes to master all modes
- **Advanced:** 1 hour to customize and optimize

---

## 🤝 Contributing

Found a bug? Have an idea? Contributions welcome!

1. Test your changes
2. Document new features
3. Submit pull request

---

## 📜 License

MIT License - Feel free to use, modify, and distribute!

---

## 🙏 Credits

Built with:
- **MediaPipe** (Google) - Hand tracking
- **OpenCV** - Computer vision
- **PyAutoGUI** - System control
- **PyCaw** - Windows audio control

---

## 🎉 Have Fun!

Start simple, practice gestures, and gradually explore different modes. The more you use it, the more natural it becomes! @ Perfect-J

**Happy Gesturing! 👋**
