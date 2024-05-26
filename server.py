import streamlit as st
import time
from streamlit_elements import elements, mui, html
from pytube import YouTube
import os
from yolo_game_detector import main
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from utils import read_video, save_video
from trackers import Tracker
import cv2
import numpy as np
from team_assigner import TeamAssigner
from player_ball_assigner import PlayerBallAssigner
from camera_movement_estimator import CameraMovementEstimator
from view_transformer import ViewTransformer
from speed_and_distance_estimator import SpeedAndDistance_Estimator
import json
st.set_page_config(layout="wide")
is_playing = False

#####################################
# Mistral model setup               #
#####################################




api_key = "MnOJOWe78ITuMe9VXRxhBTSnysQT9JvR"
model = "mistral-large-latest"

client = MistralClient(api_key=api_key)

whole_chat_content = []

initial_prompt = f"""
Context information is below.
---------------------
You are a very expressive and passionate soccer commentator. 
YOU write in CAPS the words that you deem very exciting. 
Each time I will give you a grid with players and the ball location.
You are supposed to comment on what's happening.
Here is the soccer legends: G is the goal, [number]A(speed) is player [number] on team 1, [number]B(speed) is the player [number] on team 2, O the ball and before each letter A or B there is the player number.After A or B , there is the player speed in parantheses
Do no exceed 4 phrases when commenting

---------------------
Here the map of the game:
"""

#####################################

st.title('MistralMatch : Ai football comentator')

# User input to play his/her soccer video
url = st.text_input("Youtube match url")

# Create two columns
col1, col2 = st.columns(2)


# Column 1 for the video
with col1:
    st.header("Video Stream")
    if st.button("Play"):
        is_playing = not is_playing
        output_path = "input_videos"
        downloaded_file = YouTube(url).streams.filter(res="1080p").first().download(output_path=output_path)
        file_extension = downloaded_file.split('.')[-1]
        # Create the new file name
        new_title="match"
        new_file_name = f"{new_title}.{file_extension}"

        # Create the full path for the new file name
        new_file_path = os.path.join(output_path, new_file_name)

        # Rename the file
        os.rename(downloaded_file, new_file_path)
        
        with col2:
            st.header("Game comments")
            # Placeholder for the text
             # Read Video
            video_frames = read_video("./input_videos/match.mp4")
            # Initialize Tracker
            tracker = Tracker("./models/best.pt")

            tracks = tracker.get_object_tracks(
                video_frames, read_from_stub=True, stub_path="stubs/track_stubs.pkl"
            )
            # Get object positions
            tracker.add_position_to_tracks(tracks)
            # camera movement estimator
            camera_movement_estimator = CameraMovementEstimator(video_frames[0])
            camera_movement_per_frame = camera_movement_estimator.get_camera_movement(
                video_frames, read_from_stub=True, stub_path="stubs/camera_movement_stub.pkl"
            )
            camera_movement_estimator.add_adjust_positions_to_tracks(
                tracks, camera_movement_per_frame
            )

            # View Trasnformer
            view_transformer = ViewTransformer()
            view_transformer.add_transformed_position_to_tracks(tracks)

            # Interpolate Ball Positions
            tracks["ball"] = tracker.interpolate_ball_positions(tracks["ball"])

            # Speed and distance estimator
            speed_and_distance_estimator = SpeedAndDistance_Estimator()
            speed_and_distance_estimator.add_speed_and_distance_to_tracks(tracks)

            # Assign Player Teams
            team_assigner = TeamAssigner()
            team_assigner.assign_team_color(video_frames[200], tracks["players"][0])
            for frame_num, player_track in enumerate(tracks["players"]):
                for player_id, track in player_track.items():
                    team = team_assigner.get_player_team(
                        video_frames[frame_num], track["bbox"], player_id
                    )
                    tracks["players"][frame_num][player_id]["team"] = team
                    tracks["players"][frame_num][player_id]["team_color"] = (
                        team_assigner.team_colors[team]
                    )

            # Assign Ball Aquisition
            player_assigner = PlayerBallAssigner()
            team_ball_control = []
            for frame_num, player_track in enumerate(tracks["players"]):
                ball_bbox = tracks["ball"][frame_num][1]["bbox"]
                assigned_player = player_assigner.assign_ball_to_player(player_track, ball_bbox)

                if assigned_player != -1:
                    tracks["players"][frame_num][assigned_player]["has_ball"] = True
                    team_ball_control.append(
                        tracks["players"][frame_num][assigned_player]["team"]
                    )
                else:
                    team_ball_control.append(team_ball_control[-1])
            team_ball_control = np.array(team_ball_control)

            container = st.container(height=300)
            whole_chat_content = initial_prompt
            for frame_num, frame in enumerate(video_frames[::10]):
                    try:
                        frame = frame.copy()
                        player_dict = tracks["players"][frame_num]
                        ball_dict = tracks["ball"][frame_num]
                        
                        player_data = player_dict
                        ball_data = ball_dict
                        # Define the field dimensions (in pixels)
                        field_width = 1920
                        field_height = 1080

                        # Define the grid cell size (in pixels)
                        cell_size = 50

                        # Calculate the number of cells in the grid
                        num_cells_width = field_width // cell_size
                        num_cells_height = field_height // cell_size

                        # Create an empty grid
                        grid = [['. ' for _ in range(num_cells_width)] for _ in range(num_cells_height)]

                        # Place the players on the grid
                        
                        for player_id, player in player_data.items():
                            x, y = player['position']
                            cell_x = x // cell_size
                            cell_y = y // cell_size
                            if('speed' in player):
                                player_speed = player['speed']
                                if player['team'] == 1:
                                    grid[cell_y][cell_x] = f'{player_id}A ({player_speed})'
                                else:
                                    grid[cell_y][cell_x] = f'{player_id}B ({player_speed})'
                            else:
                                if player['team'] == 1:
                                    grid[cell_y][cell_x] = f'{player_id}A ({player_speed})'
                                else:
                                    grid[cell_y][cell_x] = f'{player_id}B ({player_speed})'
                                
                        x1, y1,x2,y2 = ball_data[1]['bbox']
                        x , y = int((x1+x2)/2) , int((y1+y2)/2)
                        cell_x = x // cell_size
                        cell_y = y // cell_size
                        grid[cell_y][cell_x] = 'O '
                        game_map =""
                        # Print the grid
                        for row in grid:
                            game_map += ''.join(row)
                            game_map+="\n"
                            game_map += '#' * num_cells_width
                        whole_chat_content += game_map
                        chat_response = client.chat(
                            model=model,
                            messages=[ChatMessage(role="user", content=whole_chat_content)]
                        )
                        comment_content = chat_response.choices[0].message.content
                        def stream_game():
                            for word in comment_content.split(" "):
                                yield word + " "
                                time.sleep(0.1)
                        container.write_stream(stream_game)
                        whole_chat_content += comment_content
                    except Exception as err:
                        print(err)
                        pass
            


    with elements("media_player"):
        from streamlit_elements import media
        media.Player(url=url, controls=True,muted=True,playing=is_playing)

    
