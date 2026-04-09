import streamlit as st
import os
from moviepy.editor import ImageClip, CompositeVideoClip, concatenate_videoclips, TextClip

# Page configuration
st.set_page_config(page_title="Slideshow Generator", layout="centered")

st.title("📸 Slideshow Video Generator")

uploaded_files = st.file_uploader("Upload Images", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)

if uploaded_files:
    labels = []
    st.subheader("Add Labels for your images")
    
    # Create input fields for each image
    for i, file in enumerate(uploaded_files):
        label = st.text_input(f"Label for {file.name}", key=f"input_{i}", value=f"Image {i+1}")
        labels.append(label)

    if st.button("🚀 Generate Video"):
        with st.spinner("Processing video... please wait."):
            try:
                clips = []
                temp_files = []

                for i, file in enumerate(uploaded_files):
                    # Save uploaded file temporarily
                    img_path = f"temp_{i}.jpg"
                    with open(img_path, "wb") as f:
                        f.write(file.getbuffer())
                    temp_files.append(img_path)

                    # Create Image Clip (3 seconds)
                    img_clip = ImageClip(img_path).set_duration(3)
                    
                    # Ensure the clip has a size for text positioning
                    if img_clip.w is None:
                        img_clip = img_clip.set_res((1280, 720))

                    # Create Text Clip
                    try:
                        txt_clip = TextClip(
                            labels[i], 
                            fontsize=50, 
                            color='white', 
                            bg_color='black',
                            size=(img_clip.w, 100)
                        ).set_duration(3).set_position(("center", "bottom"))
                        
                        video_segment = CompositeVideoClip([img_clip, txt_clip])
                    except Exception as e:
                        st.warning(f"Text error for '{labels[i]}', using image only. (Error: {e})")
                        video_segment = img_clip

                    clips.append(video_segment)

                # Combine all clips
                final_video = concatenate_videoclips(clips, method="compose")
                output_path = "output.mp4"
                
                # Write file with standard settings
                final_video.write_videofile(output_path, fps=24, codec="libx264", audio=False)

                # Show video
                st.success("✅ Video Generated Successfully!")
                st.video(output_path)

                # Cleanup temp files
                for f in temp_files:
                    if os.path.exists(f):
                        os.remove(f)

            except Exception as err:
                st.error(f"An error occurred: {err}")
