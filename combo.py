import win32gui
import threading
import tkinter as tk
from tkinter import ttk
import keyboard
import time
import dxcam, cv2
import pyautogui
import easyocr
import numpy as np
import enchant
import itertools


# Keybinds
keybind_toggle = '.'

# Bot Stuff
bot_active = False
delay_cpu = 0.5
active = False
# Dictionary
d = enchant.Dict("en_US")
custom_words = {'beadwork', 'memoranda', 'bromine', 'witchhunt'}


################# Word Correction #################
def is_valid_word(word):
    return d.check(word) or word in custom_words


swaps = [ # (old, new)
    ('n', 'm'),
    ('m', 'n'),
    ('u', 'w'),
    ('w', 'u'),
    ('u', 'y'),
    ('y', 'u'),
    ('vv', 'w'),
    ('e', 'o'),
    ('o', 'e'),
    ('k', 'r'),
    ('r', 'k'),
]

def fix_word(word):
    candidates = set()
    candidates.add(word)

    # Single swaps
    for old, new in swaps:
        candidates.add(word.replace(old, new))

    # Double swaps
    for (o1, n1), (o2, n2) in itertools.combinations(swaps, 2):
        candidates.add(word.replace(o1, n1).replace(o2, n2))

    # Triple swaps
    for (o1, n1), (o2, n2), (o3, n3) in itertools.combinations(swaps, 3):
        candidates.add(word.replace(o1, n1).replace(o2, n2).replace(o3, n3))

    for candidate in candidates:
        if is_valid_word(candidate):
            return candidate

    return None


def get_best_word(word):
    if is_valid_word(word):
        return word

    # Try character swaps first
    fixed = fix_word(word)
    if fixed:
        return fixed

    # Fall back to enchant suggestions
    suggestions = d.suggest(word)
    if suggestions:
        top = suggestions[0].lower().strip()
        # Only accept if similar length and no spaces
        if abs(len(top) - len(word)) <= 2 and ' ' not in top:
            return top

    # Last resort: return swap result even if not in dictionary
    if fixed:
        return fixed

    return None


################# Label Isolation #################
def isolate_labels(frame):
    """Use neutral color detection to find white text labels."""
    b, g, r = cv2.split(frame)

    rg_diff = cv2.absdiff(r, g)
    rb_diff = cv2.absdiff(r, b)
    gb_diff = cv2.absdiff(g, b)
    max_diff = cv2.max(cv2.max(rg_diff, rb_diff), gb_diff)
    brightness = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Isolate bright neutral pixels (white text)
    bright_neutral = cv2.bitwise_and(
        cv2.threshold(max_diff, 15, 255, cv2.THRESH_BINARY_INV)[1],
        cv2.threshold(brightness, 180, 255, cv2.THRESH_BINARY)[1]
    )

    cv2.imwrite("debug_bright_neutral.png", bright_neutral)  # add this
    
    # Connect nearby letters into word blobs
    # In isolate_labels, replace the kernel and dilation:
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (10, 5))  # wider and taller
    dilated = cv2.dilate(bright_neutral, kernel, iterations=2)   # more iterations
    cv2.imwrite("debug_dilated.png", dilated)
    
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    boxes = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        aspect_ratio = w / h if h > 0 else 0
        # print(f"Contour: w={w} h={h} ratio={aspect_ratio:.1f} {'✅' if aspect_ratio > 1.5 and w > 40 and 15 < h < 60 else '❌'}")
        
        if aspect_ratio > 1.5 and w > 40 and 15 < h < 60:
            boxes.append((x, y, w, h))
            
    # print(f"Total boxes accepted: {len(boxes)}")
    return boxes


################# Crop Cleanup #################
def trim_vertical_noise(img):
    """Trim rows with no text content."""
    row_darkness = np.sum(img == 0, axis=1)
    text_rows = np.where(row_darkness > 3)[0]
    if len(text_rows) == 0:
        return img
    top = max(0, text_rows[0] - 2)
    bottom = min(img.shape[0], text_rows[-1] + 2)
    return img[top:bottom, :]


def preprocess_crop(word_crop):
    """Upscale, threshold, invert, clean and pad a word crop for EasyOCR."""
    upscaled = cv2.resize(word_crop, None, fx=6, fy=6, interpolation=cv2.INTER_CUBIC)
    _, upscaled = cv2.threshold(upscaled, 100, 255, cv2.THRESH_BINARY)

    # Always invert - text is white on black
    upscaled = cv2.bitwise_not(upscaled)

    # Remove small noise blobs
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    upscaled = cv2.morphologyEx(upscaled, cv2.MORPH_OPEN, kernel)

    # Trim artifact rows above/below text
    upscaled = trim_vertical_noise(upscaled)

    # Add horizontal border only
    upscaled = cv2.copyMakeBorder(upscaled, 10, 10, 20, 20, cv2.BORDER_CONSTANT, value=255)

    return upscaled


################# GUI Functions #################
def start_bot():
    global active
    if active == False:
        active = True
        window_name = window_entry.get()
        if not window_name:
            status_label.config(text="ENTER WINDOW TITLE", fg="orange")
            return
        hwnd = win32gui.FindWindow(None, window_name)
        if hwnd == 0:
            status_label.config(text="WINDOW NOT FOUND", fg="red")
            return
        status_label.config(text="READY", fg="blue")
        keyboard.add_hotkey(keybind_toggle, toggle_bot)
        threading.Thread(target=typer_bot, daemon=True).start()
    else:
        print(f"Bot has already started!")


def toggle_bot():
    global bot_active
    bot_active = not bot_active
    if bot_active:
        print("✅ Bot Started!")
        status_label.config(text="✅ RUNNING", fg="green")
    else:
        print("⏸️ Pausing...")
        status_label.config(text="⏸️ PAUSED", fg="blue")


################# Main Loop #################
def typer_bot():
    window_name = window_entry.get()
    hwnd = win32gui.FindWindow(None, window_name)
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    width = right - left
    height = bottom - top
    crop_region = (
        left + int(width * 0.05),
        top + int(height * 0.35),
        right - int(width * 0.05),
        bottom - int(height * 0.12)
    )

    camera = dxcam.create()
    # EasyOCR — better with pixel/game fonts than Tesseract
    reader = easyocr.Reader(['en'], gpu=True)
    camera.start(region=crop_region, target_fps=60)
    history = {}

    while True:
        if bot_active:
            current_time = time.time()
            frame = camera.get_latest_frame()

            if frame is not None:
                # Convert for color isolation (needs BGR) and grayscale crop
                bgr_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

                boxes = isolate_labels(bgr_frame)

                best_fallback = None
                best_fallback_conf = 0

                for (x, y, w, h) in boxes:
                    pad_x = 4
                    y1 = max(0, y)
                    y2 = min(gray.shape[0], y + h)
                    x1 = max(0, x - pad_x + 3)
                    x2 = min(gray.shape[1], x + w + pad_x)
                    word_crop = gray[y1:y2, x1:x2]

                    upscaled = preprocess_crop(word_crop)

                    mean_val = cv2.mean(upscaled)[0]
                    # print(f"Box w={w} h={h} mean={mean_val:.1f} {'SKIP' if mean_val < 190 else 'OK'}")
                    if mean_val < 190:
                        continue

                    cv2.imwrite("debug_crop.png", upscaled)
                    

                    results = reader.readtext(
                        upscaled,
                        detail=1,
                        paragraph=False,
                        allowlist='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
                    )

                    for (bbox, word, confidence) in results:
                        word = word.lower().strip()
                        # print(f"RAW: '{word}' conf={confidence:.2f}")

                        if len(word) < 2:
                            continue

                        if confidence >= 0.45:
                            best = get_best_word(word)
                            if best is None:
                                best = word
                            if ' ' not in best and best not in history:
                                print(f"BEST: {best} | RAW: {word}")
                                win32gui.SetForegroundWindow(hwnd)
                                time.sleep(0.01)
                                pyautogui.write(best)
                                pyautogui.press("backspace", presses=len(best))
                                pyautogui.write(word)
                                pyautogui.press("backspace", presses=len(word))
                                # history[best] = current_time
                                # history[word] = current_time
                        else:
                            # Track best low confidence read as fallback
                            best = get_best_word(word)
                            if best and ' ' not in best and confidence > best_fallback_conf:
                                best_fallback = best
                                best_fallback_conf = confidence

                # # Use fallback if nothing was typed this frame
                # if best_fallback and best_fallback not in history:
                #     print(f"FALLBACK ({best_fallback_conf:.2f}): {best_fallback}")
                #     win32gui.SetForegroundWindow(hwnd)
                #     time.sleep(0.01)
                #     pyautogui.write(best_fallback)
                #     pyautogui.press("backspace", presses=len(best_fallback))
                #     history[best_fallback] = current_time

                # Expire history
                old_count = len(history)
                history = {w: t for w, t in history.items() if current_time - t < 3}
                if len(history) < old_count:
                    print(f"Expired {old_count - len(history)} words from history")

        else:
            time.sleep(delay_cpu)


################### GUI ###################
root = tk.Tk()
root.title("Michael's Type Knight Bot")

tk.Label(root, text="Game Window:").grid(row=0, column=0, padx=5, pady=5)
window_entry = tk.Entry(root)
window_entry.insert(0, "Type Knight")
window_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(root, text=f"Toggle Key: [ {keybind_toggle} ]").grid(row=2, column=0, padx=5, pady=5)

status_label = tk.Label(root, text="ENTER WINDOW TITLE", fg="orange")
status_label.grid(row=3, column=0, padx=5, pady=5)

start_button = ttk.Button(root, text=" ✅ Start ", command=start_bot)
start_button.grid(row=4, column=0, padx=5, pady=5)

quit_button = ttk.Button(root, text=" 🚫 Quit ", command=root.destroy)
quit_button.grid(row=4, column=1, padx=5, pady=5)

root.mainloop()