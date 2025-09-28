from PIL import Image
import os
import numpy as np

def read_images_from_folder(folder_path):
	image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')
	images = []
	for filename in os.listdir(folder_path):
		if filename.lower().endswith(image_extensions):
			file_path = os.path.join(folder_path, filename)
			try:
				img = Image.open(file_path)
				images.append(img)
				print(f"Loaded: {filename} | Size: {img.size} | Mode: {img.mode}")
			except Exception as e:
				print(f"Error loading {filename}: {e}")
	return images

if __name__ == "__main__":
	folder_path = "c:\\Users\\Dell\\Downloads\\Augmented_person-20250913T062128Z-1-001\\Augmented_person"
	folder_path = input("Enter the path to the folder containing images: ").strip()
	# Remove quotes if user pastes path with them
	if folder_path.startswith('"') and folder_path.endswith('"'):
		folder_path = folder_path[1:-1]
	if not os.path.isdir(folder_path):
		print(f"Invalid folder path: {folder_path}")
	else:
		images = read_images_from_folder(folder_path)
		print(f"Total images loaded: {len(images)}")