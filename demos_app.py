import streamlit as st
import time
from pathlib import Path

# ---------- 1. Bad-Word-Liste laden ----------
BAD_WORDS_PATH = Path(__file__).with_name("badwords.txt")
try:
    BAD_WORDS = {w.strip().lower() for w in BAD_WORDS_PATH.read_text(encoding="utf-8").splitlines() if w.strip()}
except FileNotFoundError:
    BAD_WORDS = {"idiot", "loser"}  # Fallback

def contains_bad_word(text: str) -> bool:
    return any(b in text.lower() for b in BAD_WORDS)

# ---------- 2. UI ----------
def run_demos():
    st.header("🛡️  App-Demos – Schutz vor Mobbing")

    demo = st.selectbox(
        "App wählen:",
        ["🔄 ReThink | Nachricht stoppen",
         "👀 Bark | Alarm an Eltern",
         "🚑 STOPit HELPme | Soforthilfe"]
    )

    # -------- ReThink --------
    if demo.startswith("🔄"):
        msg = st.text_input("Deine Nachricht:")
        if st.button("Senden"):
            if contains_bad_word(msg):
                st.error("❗ ReThink – überlege nochmal, das klingt verletzend!")
                st.toast("Nachricht **NICHT** gesendet.", icon="⚠️")
            else:
                st.success("✅ Nachricht verschickt")

    # -------- Bark --------
    elif demo.startswith("👀"):
        msg = st.text_input("Chat-Nachricht:")
        if st.button("Senden"):
            if contains_bad_word(msg):
                st.warning("🚨 Bark-Alarm! Eltern bzw. Aufsicht werden informiert.")
                st.balloons()  # kleines Easter-Egg
            else:
                st.success("🙂 Kein Alarm")

    # -------- STOPit --------
    else:
        st.info("Fühlst du dich unsicher oder gemobbt?")
        if st.button("HILFE ✚"):
            st.success("Verbinde mit Crisis Text Line …")
            with st.spinner("Chat startet …"):
                time.sleep(1.5)
            st.toast("📲 24/7 CHAT – DE 116 111 | US #741741", icon="💬")

    st.caption("📝 Demo-Funktionen – keine echten Daten werden gesendet.")
