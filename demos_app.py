import streamlit as st
import time
from pathlib import Path

bad_path = Path(__file__).with_name("badwords.txt")
try:
    BAD = {w.strip().lower() for w in bad_path.read_text(encoding="utf-8").splitlines() if w.strip()}
except FileNotFoundError:
    BAD = {"idiot", "loser"}

def contains_bad(txt): return any(b in txt.lower() for b in BAD)

def run_demos():
    st.header("🛡️ App-Demos – Schutz vor Mobbing")

    demo = st.selectbox(
        "App wählen:",
        ["🔄 ReThink | Nachricht stoppen", "👀 Bark | Alarm an Eltern", "🚑 STOPit HELPme | Soforthilfe"]
    )

    if demo.startswith("🔄"):
        msg = st.text_input("Deine Nachricht:")
        if st.button("Senden"):
            st.error("❗ ReThink blockiert!") if contains_bad(msg) else st.success("✅ Nachricht verschickt")

    elif demo.startswith("👀"):
        msg = st.text_input("Chat-Nachricht:")
        if st.button("Senden"):
            st.warning("🚨 Bark-Alarm!") if contains_bad(msg) else st.success("🙂 Kein Alarm")

    else:
        st.info("Fühlst du dich unsicher?")
        if st.button("HILFE ✚"):
            with st.spinner("Verbinde …"):
                time.sleep(1.5)
            st.success("📲 24/7 Chat bereit")

    st.caption("Demo – es werden keine echten Daten versendet.")
