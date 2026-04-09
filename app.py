import streamlit as st
import os

# Robust import handling for MoviePy
try:
    from moviepy.editor import ImageClip, CompositeVideoClip, concatenate_videoclips, TextClip
except ImportError:
    try:
        from moviepy.video.VideoClip import ImageClip, TextClip
        from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
        from moviepy.video.compositing.concatenate import concatenate_videoclips
    except ImportError:
        st.error("MoviePy library not found. Please add 'moviepy' to your requirements.txt file.")

# Page configuration
st.set_page_config(page_title="Slideshow Generator", layout="centered")

st.title("📸 Slideshow Video Generator")

uploaded_files = st.file_uploader("Upload Images", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)

if uploaded_files:
    labels = []
    st.subheader("Add Labels for your images")
    
    for i, file in enumerate(uploaded_files):
        label = st.text_input(f"Label for {file.name}", key=f"input_{i}", value=f"Image {i+1}")
        labels.append(label)

    if st.button("🚀 Generate Video"):
        if not uploaded_files:
            st.error("Please upload some images first!")
        else:
            with st.spinner("Processing video... this might take a minute."):
                try:
                    clips = []
                    temp_files = []

                    for i, file in enumerate(uploaded_files):
                        img_path = f"temp_{i}.jpg"
                        with open(img_path, "wb") as f:
                            f.write(file.getbuffer())
                        temp_files.append(img_path)

                        img_clip = ImageClip(img_path).set_duration(3)
                        
                        if img_clip.w is None or img_clip.w == 0:
                            img_clip = img_clip.set_res((1280, 720))

                        try:
                            # Attempt to create text overlay
                            txt_clip = TextClip(
                                labels[i], 
                                fontsize=50, 
                                color='white', 
                                bg_color='black',
                                size=(img_clip.w, 100)
                            ).set_duration(3).set_position(("center", "bottom"))
                            
                            video_segment = CompositeVideoClip([img_clip, txt_clip])
                        except Exception:
                            # Fallback if ImageMagick is not configured on server
                            video_segment = img_clip

                        clips.append(video_segment)

                    final_video = concatenate_videoclips(clips, method="compose")
                    output_path = "output_video.mp4"
                    
                    final_video.write_videofile(output_path, fps=24, codec="libx264", audio=False)

                    st.success("✅ Video Generated!")
                    st.video(output_path)

                    for f in temp_files:
                        if os.path.exists(f):
                            os.remove(f)

                except Exception as err:
                    st.error(f"Error: {err}")
