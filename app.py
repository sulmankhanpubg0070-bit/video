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
        ImageClip = CompositeVideoClip = concatenate_videoclips = None

# Helper function to handle MoviePy v1 vs v2 method naming differences
def apply_attribute(clip, attr_v1, attr_v2, value):
    if clip is None: return None
    if hasattr(clip, attr_v2): # MoviePy v2.0+
        return getattr(clip, attr_v2)(value)
    elif hasattr(clip, attr_v1): # MoviePy v1.0
        return getattr(clip, attr_v1)(value)
    return clip

# Enhanced function to create high-quality text overlay using Pillow
def create_text_overlay_pill(text, width, height):
    # Create a transparent layer (RGBA)
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Modern Gradient-like semi-transparent black bar
    rect_h = int(height * 0.15)  # Responsive height
    if rect_h < 60: rect_h = 60
    
    # Draw a stylish semi-transparent overlay at the bottom
    overlay_color = (0, 0, 0, 160) # Black with transparency
    draw.rectangle([0, height - rect_h, width, height], fill=overlay_color)
    
    # Try multiple font paths common on Streamlit/Linux servers
    font = None
    font_size = int(rect_h * 0.5)
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "arial.ttf"
    ]
    
    for path in font_paths:
        try:
            font = ImageFont.truetype(path, font_size)
            break
        except:
            continue
            
    if font is None:
        font = ImageFont.load_default()
    
    # Draw text with a subtle shadow for better readability
    text_pos = (width // 2, height - (rect_h // 2))
    # Shadow
    draw.text((text_pos[0]+2, text_pos[1]+2), text, font=font, fill=(0,0,0,255), anchor="mm")
    # Main Text
    draw.text(text_pos, text, font=font, fill="white", anchor="mm")
    
    return np.array(img.convert('RGB'))

# Page configuration for a "High-End" look
st.set_page_config(
    page_title="Pro Slideshow Studio", 
    page_icon="🎬", 
    layout="wide"
)

# Custom Styling - FIXED unsafe_allow_html
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #FF4B4B;
        color: white;
        font-weight: bold;
    }
    .img-card {
        background: white;
        padding: 10px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🎬 Pro Slideshow Video Studio")

# Check if MoviePy is missing
if concatenate_videoclips is None:
    st.error("⚠️ MoviePy library not detected!")
    st.markdown("""
    ### 🛠️ Important Fix Required:
    Aapki app ko chalne ke liye kuch libraries ki zaroorat hai jo abhi install nahi hain.
    
    **Ye steps follow karein:**
    1. Apni GitHub repository mein ek nayi file banayein jis ka naam **`requirements.txt`** rakhein.
    2. Us file ke andar ye charo (4) lines copy karke paste kar dein:
       ```text
       streamlit
       moviepy
       numpy
       Pillow
       ```
    3. File ko **Commit (Save)** karein.
    4. Streamlit dashboard par ja kar **Manage App** par click karein aur phir **Reboot App** kar dein.
    """)
    st.stop()

st.markdown("---")

# Layout with two columns
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📤 Step 1: Upload Your Media")
    uploaded_files = st.file_uploader("Drop images here", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)

with col2:
    st.subheader("⚙️ Step 2: Customize Labels")
    labels = []
    if uploaded_files:
        for i, file in enumerate(uploaded_files):
            label = st.text_input(f"Text for: {file.name}", key=f"input_{i}", value=f"Memory {i+1}")
            labels.append(label)
    else:
        st.info("Upload images to start labeling.")

if uploaded_files:
    st.markdown("---")
    if st.button("🚀 Generate High-Quality Video"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            clips = []
            temp_files = []
            total_files = len(uploaded_files)

            for i, file in enumerate(uploaded_files):
                status_text.text(f"Processing image {i+1} of {total_files}...")
                
                img_path = f"temp_{i}.jpg"
                with open(img_path, "wb") as f:
                    f.write(file.getbuffer())
                temp_files.append(img_path)

                # Process with Pillow
                with Image.open(img_path) as main_img:
                    main_img = main_img.convert("RGB")
                    
                    # High-quality resize
                    main_img = main_img.resize((1280, 720), Image.Resampling.LANCZOS)
                    w, h = main_img.size
                    
                    # Add Text Overlay
                    text_layer = create_text_overlay_pill(labels[i], w, h)
                    
                    # Merge text bar onto image
                    final_frame_pil = Image.fromarray(text_layer)
                    main_img.paste(final_frame_pil, (0,0), mask=None) 
                    
                    # Convert to MoviePy
                    img_array = np.array(main_img)
                    img_clip = ImageClip(img_array)
                    img_clip = apply_attribute(img_clip, "set_duration", "with_duration", 3)
                    
                    clips.append(img_clip)
                
                progress_bar.progress((i + 1) / total_files * 0.5)

            status_text.text("Merging clips into final video...")
            final_video = concatenate_videoclips(clips, method="compose")
            output_path = "final_slideshow.mp4"
            
            # Write file with professional settings
            final_video.write_videofile(output_path, fps=24, codec="libx264", preset="medium")
            progress_bar.progress(1.0)
            
            st.success("✨ Your video is ready!")
            st.video(output_path)
            
            # Download Button
            with open(output_path, "rb") as file:
                st.download_button(
                    label="💾 Download Video",
                    data=file,
                    file_name="my_slideshow.mp4",
                    mime="video/mp4"
                )

            # Cleanup
            for f in temp_files:
                if os.path.exists(f): os.remove(f)

        except Exception as err:
            st.error(f"Something went wrong: {err}")
