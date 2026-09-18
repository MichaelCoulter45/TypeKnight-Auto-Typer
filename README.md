# TypeKnight Auto Typer

An experimental Windows computer-vision project that reads on-screen words from **Type Knight** and sends matching keyboard input. It was built to explore screen capture, image preprocessing, OCR reliability, and input automation in one real-time pipeline.

## Demo

[Watch the demo](./demo/TypeKnight%20Project%20Demo.mp4)

## How it works

```text
Game window
  -> DXCam screen capture
  -> OpenCV text-region isolation
  -> crop cleanup and enlargement
  -> EasyOCR recognition
  -> dictionary-based correction
  -> PyAutoGUI keyboard input
```

The program captures a configurable region of the game window, isolates bright neutral text, groups it into likely word regions, and prepares each crop for OCR. A correction layer checks words against a dictionary and tries common character substitutions before sending input.

## What I learned

- Text recognition quality depends heavily on preprocessing, not just the OCR library.
- Real-time automation needs deliberate tradeoffs between accuracy, capture rate, and CPU/GPU work.
- Stylized fonts make OCR uncertain, so validation and recovery strategies matter.
- A small interface and a hotkey make an experimental automation tool safer to start and pause.

## Technology

- Python
- DXCam for real-time screen capture
- OpenCV and NumPy for image processing
- EasyOCR for optical character recognition
- PyEnchant for dictionary validation and suggestions
- PyAutoGUI and Keyboard for input control
- Tkinter and Win32GUI for the Windows interface and window selection

## Run locally

**Requirements:** Windows, Python, and the Type Knight game window. EasyOCR is configured to use a GPU in the current prototype.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python combo.py
```

Enter the game window title in the interface, select **Start**, then use `.` to toggle automation on or off.

## Limitations

- Recognition can be inaccurate with Type Knight's stylized font.
- The crop region and thresholds are tuned for a particular window layout and screen resolution.
- The current EasyOCR configuration expects GPU support.
- Debug image files are written while the pipeline runs.

## Responsible use

This is a learning project for controlled, single-player experimentation. Use input automation only where it is permitted and avoid using it in competitive or multiplayer environments.

## Next steps

- Make the capture region and thresholds configurable
- Improve OCR correction scoring instead of relying on the first acceptable candidate
- Add a CPU fallback for OCR
- Reduce debug output and measure end-to-end recognition latency
