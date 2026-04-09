import streamlit as st
from moviepy.editor import ImageClip, CompositeVideoClip, concatenate_videoclips, TextClip

st.title("📸 Slideshow Video Generator")

uploaded_files = st.file_uploader("Upload Images", accept_multiple_files=True)

labels = []

if uploaded_files:
    for i, file in enumerate(uploaded_files):
        label = st.text_input(f"Label for {file.name}", key=i)
        labels.append(label)

    if st.button("Generate Video"):
        clips = []

        for i, file in enumerate(uploaded_files):
            img_path = f"temp_{i}.jpg"
            with open(img_path, "wb") as f:
                f.write(file.read())

            img_clip = ImageClip(img_path).set_duration(3)

            txt_clip = TextClip(labels[i], fontsize=50, color='white', bg_color='black')
            txt_clip = txt_clip.set_position(("center", "bottom")).set_duration(3)

            clips.append(CompositeVideoClip([img_clip, txt_clip]))

        final = concatenate_videoclips(clips, method="compose")
        final.write_videofile("output.mp4", fps=24)

        st.video("output.mp4")
