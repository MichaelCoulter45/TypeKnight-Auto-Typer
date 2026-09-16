What is Type Knight?
- Type Knight is an arcade-y 2D sidescrolling videogame by Chaikadev that I found on the Steam platform. It features multiple difficulties ranging from super easy to super difficult. The player plays as a knight that encounters skeletons, bats, liches, treasure, etc. and the player has to type out the words above all of those entities to score points and not die to the enemies. It's a really neat typing game that's simple to understand and very difficult to master. It's a great tool to improve typing capabilities.






Why did you build it?
- I built this auto typer for the game as a challenge and learning project for my coding skills. I enjoy learning more techniques and libraries and I used Type Knight as a coding exercise to see if I could have it be fully automated.

How does it work?
- My script works by DXCam taking screenshots of the game window, tosses into a function that pre-process each frame it captures and isolates just the text on the screen, the screenshot now only has text on it which then gets fed into EasyOCR to read the text, EasyOCR then feeds the text it genereates into pyautogui to be written to the game as if the user is writing it.

What technologies does it use?
- win32gui
- threading
- tkinter
- keyboard
- time
- dxcam
- cv2
- pyautogui
- easyocr
- numpy
- enchant
- itertools

What does it currently do?
- Essentially, the script reads the text above the eneimes and types it into the game.
  
What are its limitations?
- The script certainly not perfect. It's greatest limitation is definately that it can't quite read the game text perfetly. It reads it pretty well, but the game has a font style that is not optimized for EasyOCR, so EasyOCR makes mistakes and detects incorrect characters and words. I have a correction system in the script but it's also limited and only fixes some edge cases.

What's next?
- Further optimization. The core of the script works great, but further optimization to reading the game text would improve the script and functionality.