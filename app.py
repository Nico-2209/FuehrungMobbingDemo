import streamlit as st
from slider_app import run_slider
from demos_app import run_demos

# Seiten-Meta
st.set_page_config(page_title="Mobbing-Tools", page_icon="🛡️", layout="wide")

st.title("📱 Interaktive Mobbing-Tools")

# Menü
choice = st.radio(
    "Wähle ein Modul:",
    ["GrenzCheck – Satz einschätzen", "Mobbing-App-Demos"],
    horizontal=True
)

# Router
if choice.startswith("GrenzCheck"):
    run_slider()
else:
    run_demos()
