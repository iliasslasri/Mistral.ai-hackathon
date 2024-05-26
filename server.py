import streamlit as st
import time
from streamlit_elements import elements, mui, html
from pytube import YouTube
import os
from main import main
st.set_page_config(layout="wide")
is_playing = False

st.title('MistralMatch : Ai footbal comentator')
GRIDS = []

# Create two columns
col1, col2 = st.columns(2)

url = st.text_input("Youtube match url")


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