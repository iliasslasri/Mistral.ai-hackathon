import streamlit as st
import time
from streamlit_elements import elements, mui, html
from pytube import YouTube
import os
from main import main
st.set_page_config(layout="wide")
is_playing = False

#####################################
# Mistral model setup               #
#####################################

import os
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

api_key = "MnOJOWe78ITuMe9VXRxhBTSnysQT9JvR"
model = "mistral-large-latest"

client = MistralClient(api_key=api_key)

whole_chat_content = []

initial_prompt = f"""
Context information is below.
---------------------
You are a very expressive and passionate soccer commentator. 
Each time I will give you a grid with players and the ball location.
You are supposed to comment on what's happening.
Here is the soccer legends: G is the goal, A is player on team 1, B is the player on team 2, O the ball and before each letter A or B there is the player number
---------------------
Here the map of the game:
"""

#####################################

st.title('MistralMatch : Ai football comentator')
GRIDS = []

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
            st.header("Commentator")
            # Placeholder for the text
            GRIDS = main()
            st.write(GRIDS[0:5])
        

    with elements("media_player"):
        from streamlit_elements import media
        media.Player(url=url, controls=True,muted=True,playing=is_playing)

# Column 2 for the streaming text
# Column 2 for the streaming text
with col2:
    st.header("Game comments")

    container = st.container(height=300)

    def stream_game():
        for word in comment_content.split(" "):
            yield word + " "
            time.sleep(0.1)

    # Here generate the map
    # To change with Json files
    game_map = f"""
    G    12A   23B     34B      G
    G    2B O  15A              G
    G      5B                   G
    """

    # Ask the bot to generate the comments
    whole_chat_content = initial_prompt + game_map
    chat_response = client.chat(
        model=model,
        messages=[ChatMessage(role="user", content=whole_chat_content)]
    )
    comment_content = chat_response.choices[0].message.content

    container.write_stream(stream_game)

    whole_chat_content += comment_content

    game_map = f"""
    G    12A   23B     34B      G
    G    2B   15A              G
    G      5BO                   G
    """

    whole_chat_content += game_map

    # Ask the bot to generate the comments
    whole_chat_content = initial_prompt + game_map
    chat_response = client.chat(
        model=model,
        messages=[ChatMessage(role="user", content=whole_chat_content)]
    )
    comment_content = chat_response.choices[0].message.content

    container.write_stream(stream_game)

    
