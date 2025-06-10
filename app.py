from slider_app import run_slider
from demos_app import run_demos
import streamlit as st

st.set_page_config(page_title="Mobbing-Tools", layout="wide")
st.title("📱 Interaktive Mobbing-Tools")
choice = st.radio("Modul wählen", ["GrenzCheck","App-Demos"], horizontal=True)
if choice=="GrenzCheck":
    run_slider()
else:
    run_demos()
