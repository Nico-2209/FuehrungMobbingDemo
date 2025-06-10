import streamlit as st
from slider_app import run_slider
from demos_app import run_demos

st.set_page_config(page_title="Mobbing-Tools", layout="wide")
st.title("📱 Interaktive Mobbing-Tools")

mode = st.radio("Modul wählen:", ["GrenzCheck", "App-Demos"], horizontal=True)
if mode == "GrenzCheck":
    run_slider()
else:
    run_demos()
