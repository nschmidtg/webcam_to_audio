# Image to Midi
Python package to convert image to Midi.

## Install
Tested on Python 3.7
```
pip install -r requirements.txt
python image_to_midi.py
```
## Compile UI
### MacOS:
```
pyinstaller image_to_midi.py --onefile --noconfirm --windowed --hidden-import=mido,cv2.cv2 --paths=classes --add-data="model/MobileNetSSD_deploy.prototxt:model" --add-data="model/MobileNetSSD_deploy.caffemodel:model"
```

### Windows:
You will need the Visual Studio Developer Tools C++ 14
make sure you have python 3.7 and pyinstaller on the PATH environment variables.
```
pyinstaller image_to_midi.py --onefile --noconfirm --windowed --hidden-import=mido,cv2.cv2 --paths=classes --add-data="model/MobileNetSSD_deploy.prototxt:model" --add-data="model/MobileNetSSD_deploy.caffemodel:model"
```
