# Type Knight Auto-Typer

## What is Type Knight?

Type Knight is an arcade-style 2D side-scrolling game developed by Chaikadev and available on Steam. The player controls a knight who encounters enemies and other objects with words displayed above them. The player must type the displayed words to defeat enemies, score points, and survive.

The game features multiple difficulty levels and is simple to understand but very difficult to master. It's also a fun tool to practice and improve typing skills.

## Demo
https://github.com/user-attachments/assets/4b857617-7bd0-47fa-893e-b7a44f035bd2


## Why did you build it?

I built this auto typer as a challenge and learning project to improve my Python skills. I enjoy learning new techniques and libraries, and Type Knight gave me an interesting problem to solve: Could I write a program that could automate a typing game?

## How does it work?

Type Knight uses a computer-vision and OCR pipeline to identify and type the words displayed in the game.

1. DXCam captures frames from the Type Knight game window.
2. OpenCV processes each frame and isolates areas that are likely to have text.
3. The detected text regions are cropped, enlarged, thresholded, cleaned, and prepared for OCR
4. EasyOCR analyzes the processed image and attempts to recognize words.
5. The recognized words are validated and corrected using a dictionary and a custom OCR correction system.
6. PyAutoGUI sends the resulting keyboard input to the game.

This allows Type Knight to continuously detect words on the screen and automatically type them into the game.

## What technologies does it use?

- Python
- DXCam - Real-time screen capture
- OpenCV - Image processing and text-region isolation
- EasyOCR - Optical character recognition
- PyAutoGUI - Automated keyboard input
- PyEnchant - Dictionary validation and word suggestion
- Tkinter - Graphical User Interface (GUI)
- Win32GUI - Windows window detection and management
- Keyboard - global keyboard hotkeys
- NumPy - image/data processing
- Threading - Background bot execution
- Itertools - OCR correction combinations
- Time - Timing and delays

## What does it currently do?

This Type Knight script automatically detects the words displayed above enemies in the game and types them into the game without requiring the player to manually entering them.

The bot can be started and paused using a keyboard toggle and includes a small GUI for configuring the game window and controlling the bot.

## What are its limitations?

The script is functional but certainly not perfect.

The largest limitation is the OCR accuracy. Type Knight uses a stylized game font that is not always easy for EasyOCR to recognize. As a result, the OCR system can occasionally misread individual characters or entire words.

To compensate for this, the program includes a custom correction system that attempts to identify and correct common OCR mistakes using character substitutions, dictionary validation, and word suggestions. However, this system is still limited and cannot correct every incorrect recognition.

## What's next?

The primary area of future development is improving the text-recognition accuracy.

### Potential improvements include

- Further optimization of the OpenCV preprocessing pipeline.
- Improving OCR accuracy with additional preprocessing techniques.
- Expanding the OCR correction system.
- Improving handling of difficult or ambiguous words.
- Optimizing recognition speed and CPU/GPU usage.
- Making the program more configurable for different screen resolutions.

## Development History

This Type Knight script evolved through several iterations while experimenting with screen capture, image processing, OCR, and automated keyboard input.

The project began with basic keyboard automation before progressing into screen capture, Tesseract OCR experimentation, image preprocessing, OCR correction, and eventually the current EasyOCR-based implementation.
