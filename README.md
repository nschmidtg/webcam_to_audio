# Image to Midi
Python package to convert image to Midi.

## Install
```
conda create --name image_to_midi python=3.7 pyinstaller=5.1
conda activate image_to_midi
pip install -r requirements.txt
```
## Compile UI
### MacOS:
```
pyinstaller image_to_midi.py --onefile --noconfirm --windowed --hidden-import=mido,cv2.cv2 --paths=classes --add-data="model/MobileNetSSD_deploy.prototxt:model" --add-data="model/MobileNetSSD_deploy.caffemodel:model"
```
