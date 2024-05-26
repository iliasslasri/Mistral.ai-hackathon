# Hey Mistral, comment me this match

This project aims to use the [MistralAI Large model](https://mistral.ai/fr/news/mistral-large/) to comment a football match.

<p><img height="400" width="1000" src="./docs/animationApp.gif" alt="demo"></p>

The app employs YOLO (You Only Look Once) object detection to conduct comprehensive analysis of football matches. The goal is to provide detailed insights into player performance, team dynamics, ball possession which are passed through the MistralAI Large model to comment the match.

## Installation

Before playing with the app, please install the requirements in your python environment
```
python -m pip install -r requirements.txt
```

As said below, the project uses a Yolov8n to detect players. <br>
To train the model on a football specific dataset, use the Roboflow framework and the "football-players-detection-3zvbc" dataset.
After the training, copy the `best.pt` model in the `models` folder at the root of this project.

## Usage

The project uses [Streamlit](https://streamlit.io/), so to run the app please run
```
streamlit run server.py
```

## Context of this project

This project has been conducted during the [MistralAI Hackathon](https://partiful.com/e/EFvUkVMiTCP2cVrRU1cD). <br>
The team was composed of:
- Chems
- Amir
- Iliass
- Vincent

## License

This repository has a MIT license, as found in the [LICENSE](./LICENSE) file.

## Acknowledgements

Special thanks to the Ultralytics team and the creator of the [Football Analysis repository](https://github.com/rajveersinghcse/Football-Analysis-using-YOLO) the contributors of the libraries used in this project for their valuable contributions to the field of object detection and analysis in computer vision.

