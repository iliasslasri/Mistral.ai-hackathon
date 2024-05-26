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


def main():
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
    team_assigner.assign_team_color(video_frames[500], tracks["players"][0])
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
    GRIDS = []
    
    for frame_num, frame in enumerate(video_frames):
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
                text =""
                # Print the grid
                for row in grid:
                    text += ''.join(row)
                    text+="\n"
                    text += '#' * num_cells_width
                print(text)
                GRIDS.append(text)
            except Exception as err:
                
                pass
    print(len(GRIDS))
    return GRIDS
            
    


if __name__ == "__main__":
    main()
