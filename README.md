# Image to audio
Python package to convert image to audio. The system interpretates the images as raw spectrograms and synthetize the audio using customizable iFFT parameters.

## Install
```
conda create --name audio python=3.7 pyinstaller=5.1
conda activate audio
pip install -r requirements.txt
```
## Compile UI
### MacOS:
```
pyinstaller hello.py --onefile --noconfirm --windowed --hidden-import=mido,cv2.cv2 --paths=classes --add-data="model/MobileNetSSD_deploy.prototxt:model" --add-data="model/MobileNetSSD_deploy.caffemodel:model" --clean
```
