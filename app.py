import streamlit as st
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Robust import handling for MoviePy
try:
    from moviepy.editor import ImageClip, CompositeVideoClip, concatenate_videoclips
except ImportError:
    try:
        from moviepy.video.VideoClip import ImageClip
        from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
        from moviepy.video.compositing.concatenate import concatenate_videoclips
    except ImportError:
        st.error("MoviePy library not found. Please add 'moviepy' to your requirements.txt")
        ImageClip = CompositeVideoClip = concatenate_videoclips = None

# Helper function to handle MoviePy v1 vs v2 method naming differences
def apply_attribute(clip, attr_v1, attr_v2, value):
    if clip is None: return None
    if hasattr(clip, attr_v2): # MoviePy v2.0+
        return getattr(clip, attr_v2)(value)
    elif hasattr(clip, attr_v1): # MoviePy v1.0
        return getattr(clip, attr_v1)(value)
    return clip

# Function to create text overlay using Pillow (Works without ImageMagick)
def create_text_overlay_pill(text, width, height):
    # Create a transparent layer
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Simple rectangle background for text at the bottom
    rect_h = 80
    draw.rectangle([0, height - rect_h, width, height], fill=(0, 0, 0, 180))
    
    # Try to use a default font
    try:
        # On most linux servers, this path exists
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
    except:
        font = ImageFont.load_default()
    
    # Draw text
    draw.text((width//2, height - rect_h//2), text, font=font, fill="white", anchor="mm")
    
    # Convert back to numpy array for MoviePy
    return np.array(img.convert('RGB'))

# Page configuration
st.set_page_config(page_title="Slideshow Generator", layout="centered")

st.title("📸 Slideshow Video Generator")
st.info("Note: This version uses Pillow for text overlays to avoid ImageMagick errors.")

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
            st.error("MoviePy is not properly installed.")
        else:
            with st.spinner("Processing video..."):
                try:
                    clips = []
                    temp_files = []

                    for i, file in enumerate(uploaded_files):
                        img_path = f"temp_{i}.jpg"
                        with open(img_path, "wb") as f:
                            f.write(file.getbuffer())
                        temp_files.append(img_path)

                        # Load image with Pillow to get dimensions and add text
                        main_img = Image.open(img_path).convert("RGB")
                        
                        # Resize to a standard HD if too large or small
                        main_img = main_img.resize((1280, 720))
                        w, h = main_img.size
                        
                        # Add text using our custom function
                        text_img_array = create_text_overlay_pill(labels[i], w, h)
                        
                        # Combine main image and text bar (Simple merge)
                        final_frame = Image.fromarray(text_img_array)
                        main_img.paste(final_frame, (0,0), mask=Image.new('L', (w,h), 255))
                        
                        # Convert to MoviePy Clip
                        img_array = np.array(main_img)
                        img_clip = ImageClip(img_array)
                        img_clip = apply_attribute(img_clip, "set_duration", "with_duration", 3)
                        
                        clips.append(img_clip)

                    # Combine and write
                    final_video = concatenate_videoclips(clips, method="compose")
                    output_path = "output_video.mp4"
                    
                    final_video.write_videofile(output_path, fps=24, codec="libx264")

                    st.success("✅ Video Generated!")
                    st.video(output_path)

                    # Cleanup
                    for f in temp_files:
                        if os.path.exists(f):
                            os.remove(f)

                except Exception as err:
                    st.error(f"Error during generation: {err}")
