import streamlit as st
import os

# Robust import handling for MoviePy v1 and v2
try:
    from moviepy.editor import ImageClip, CompositeVideoClip, concatenate_videoclips, TextClip
except ImportError:
    try:
        from moviepy.video.VideoClip import ImageClip, TextClip
        from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
        from moviepy.video.compositing.concatenate import concatenate_videoclips
    except ImportError:
        # This will show if requirements.txt is missing or hasn't finished installing
        st.error("MoviePy library not found. Please ensure 'moviepy' is in your requirements.txt and the app has finished deployment.")
        # Define placeholders to prevent NameError before the app stops
        ImageClip = CompositeVideoClip = concatenate_videoclips = TextClip = None

# Helper function to handle MoviePy v1 vs v2 method naming differences
def apply_attribute(clip, attr_v1, attr_v2, value):
    if hasattr(clip, attr_v2): # MoviePy v2.0+ (e.g., with_duration)
        return getattr(clip, attr_v2)(value)
    elif hasattr(clip, attr_v1): # MoviePy v1.0 (e.g., set_duration)
        return getattr(clip, attr_v1)(value)
    return clip

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
        elif concatenate_videoclips is None:
            st.error("MoviePy is not properly installed. Check your requirements.txt")
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

                        # Create Image Clip
                        img_clip = ImageClip(img_path)
                        img_clip = apply_attribute(img_clip, "set_duration", "with_duration", 3)
                        
                        # Handle resolution/size
                        if img_clip.w is None or img_clip.w == 0:
                            if hasattr(img_clip, "with_size"):
                                img_clip = img_clip.with_size((1280, 720))
                            else:
                                img_clip = img_clip.set_res((1280, 720))

                        try:
                            # Handling TextClip arguments for v1 vs v2
                            text_kwargs = {
                                "text": labels[i],
                                "color": 'white',
                                "bg_color": 'black',
                                "size": (img_clip.w, 100)
                            }
                            
                            if hasattr(TextClip, "font_size"): # v2
                                text_kwargs["font_size"] = 50
                            else: # v1
                                text_kwargs["fontsize"] = 50
                                
                            txt_clip = TextClip(**text_kwargs)
                            txt_clip = apply_attribute(txt_clip, "set_duration", "with_duration", 3)
                            
                            # Set position
                            if hasattr(txt_clip, "with_position"):
                                txt_clip = txt_clip.with_position(("center", "bottom"))
                            else:
                                txt_clip = txt_clip.set_position(("center", "bottom"))
                            
                            video_segment = CompositeVideoClip([img_clip, txt_clip])
                        except Exception as e:
                            st.warning(f"Text overlay failed for {labels[i]}. Image only used.")
                            video_segment = img_clip

                        clips.append(video_segment)

                    # Combine and write
                    # Using the correctly imported concatenate_videoclips
                    final_video = concatenate_videoclips(clips, method="compose")
                    output_path = "output_video.mp4"
                    
                    final_video.write_videofile(output_path, fps=24, codec="libx264", audio=False)

                    st.success("✅ Video Generated!")
                    st.video(output_path)

                    # Cleanup
                    for f in temp_files:
                        if os.path.exists(f):
                            os.remove(f)

                except Exception as err:
                    st.error(f"Error during generation: {err}")
