import shutil
from ultralytics import YOLO
from roboflow import Roboflow

rf = Roboflow(api_key="<Paste Your Roboflow API Key here>")
project = rf.workspace("roboflow-jvuqo").project("football-players-detection-3zvbc")
version = project.version(1)
dataset = version.download("yolov8n")

shutil.move('./football-players-detection-1/train', './football-players-detection-1/football-players-detection-1/train')
shutil.move('./football-players-detection-1/valid', './football-players-detection-1/football-players-detection-1/valid')
shutil.move('./football-players-detection-1/test', './football-players-detection-1/football-players-detection-1/test')

# Load a model
model = YOLO("yolov8n.pt")

# Train the model
results = model.train(data=f"{dataset.location}/data.yaml", epochs=100, imgsz=640)






