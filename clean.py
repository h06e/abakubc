from pathlib import Path
import os

root = Path('.')
files = list(root.glob('**/*.png'))
for file in files:
	if 'geo' not in file.name:
		os.remove(file)
		print(file.name)
