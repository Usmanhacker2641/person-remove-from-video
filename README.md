[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/Lud9vfHq)

Person Removal from Video
This Python script removes persons from a video by processing each frame individually. Simply provide a folder containing video frames, and the script will process them to remove any detected persons.

Requirements
Python 3.8 or later

Required libraries will be installed automatically

How to Run
Place all your video frames in a folder (supported formats: JPG, JPEG, PNG)

Run the script with the following command:

bash
python main.py --input_folder /path/to/your/frames --output_folder /path/to/output
Output
The script will:

Process each frame to remove detected persons

Save processed frames to the output folder

Create a video file (output_video.mp4) from the processed frames

Notes
Processing time depends on the number of frames and your hardware

For best results, use high-quality input frames

The algorithm works best with clear person