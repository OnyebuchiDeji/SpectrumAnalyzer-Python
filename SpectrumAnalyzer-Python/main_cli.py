from app_spectrum_visualizer import main_analyze_and_visualize_audio_spectrum

import sys
import shutil
import os


def analyze_and_visualize_audio_local(audioPath):
	#	TODO: Copy audio locally to this project's location at "_temp
	#	replace '\' with  '/'
	#	remove trailing "/"
	audioPath = audioPath.replace("\\", "/").strip("/").strip()

	ext = audioPath.split(".")[1]
	allowed_exts = ["wav"]
	if not ext in allowed_exts:
		print("Only .wav files can be visualized")
		return

	#	get name
	fname = os.path.basename(audioPath)
	target_path = f"./_temp/{fname}"

	shutil.copyfile(audioPath, target_path)

	#	Pass the locally copied audio's path here
	main_analyze_and_visualize_audio_spectrum(target_path)

	#	Delete local copy
	os.remove(target_path)



def analyze_and_visualize_audio_download():
	#	TODO: Download and save audio with temporary name
	#	in local path "_temp
	...

def main_pipeline():
	args = list(sys.argv)
	if len(args) == 1:
		print("Must provide path to .wav audio file")
		sys.exit()

	audio_path = args[1]

	if "https" in audio_path:
		analyze_and_visualize_audio_download(audio_path)
	else:
		analyze_and_visualize_audio_local(audio_path)
	

if __name__ == "__main__":
	main_pipeline()