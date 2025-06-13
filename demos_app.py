import streamlit as st, time, random
from pathlib import Path

BAD = {w.strip().lower() for w in Path(__file__).with_name("badwords.txt").read_text(encoding="utf-8").splitlines()}

def contains_bad(t): return any(b in t.lower() for b in BAD)

def run_demos():
    st.header("🛡️ Interaktive Schutz-Demos")
    demo = st.radio("App wählen:", ["ReThink", "Bark", "STOPit HELPme"], horizontal=True)

    # ReThink
    if demo == "ReThink":
        msg = st.text_input("Nachricht eintippen:")
        if st.button("Senden"):
            if contains_bad(msg):
                st.error("🚫 ReThink – Nachricht gestoppt!")
                st.toast("Nachricht NICHT gesendet", icon="⚠️")
            else:
                st.success("✅ Nachricht verschickt")

    # Bark
    elif demo == "Bark":
        msg = st.text_input("Chat-Nachricht:")
        if st.button("Senden"):
            if contains_bad(msg):
                st.warning("🚨 Bark meldet einen Bullying-Alarm!")
                st.balloons()
            else:
                st.success("🙂 Alles okay, kein Alarm")

    # STOPit
    else:
        st.info("Fühlst du dich unsicher oder gemobbt?")
        if st.button("HILFE ✚"):
            with st.spinner("Verbinde …"):
                time.sleep(1.2)
            st.success("📲 24/7 Chat bereit – DE 116 111 | US #741741")
            st.snow()

    st.caption("Demomodus – es werden keine echten Daten versendet.")
