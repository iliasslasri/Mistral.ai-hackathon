import ultralytics
from roboflow import Roboflow

rf = Roboflow(api_key="2Hf3Pt8ooS9MrfgPQDIC")
project = rf.workspace("roboflow-jvuqo").project("football-players-detection-3zvbc")
version = project.version(1)
dataset = version.download("yolov5")

print(dataset.location)

import shutil

shutil.move('./football-players-detection-1/train', './football-players-detection-1/football-players-detection-1/train')
shutil.move('./football-players-detection-1/valid', './football-players-detection-1/football-players-detection-1/valid')
shutil.move('./football-players-detection-1/test', './football-players-detection-1/football-players-detection-1/test')


from ultralytics import YOLO

# Initialize the YOLO model with the pre-trained weights
model = YOLO('yolov5l.pt')

# Define the path to the dataset configuration file
data_config = f"{dataset.location}/data.yaml"

# Set the training parameters
epochs = 100
imgsz = 640

# Train the model
model.train(data=data_config, epochs=epochs, imgsz=imgsz)