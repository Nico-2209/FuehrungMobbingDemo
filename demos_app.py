import streamlit as st
import time

BAD_WORDS = {"idiot", "loser", "hässlich"}

def rethink(text: str) -> bool:
    """Testet, ob der Text ein böses Wort enthält."""
    return any(b in text.lower() for b in BAD_WORDS)

def run_demos():
    st.header("App-Demos 🚀")

    demo = st.selectbox(
        "App wählen:",
        ["ReThink (Nachricht stoppen)", "Bark (Alarm an Eltern)", "STOPit HELPme (Soforthilfe)"]
    )

    # 1 · ReThink
    if demo.startswith("ReThink"):
        msg = st.text_input("Deine Nachricht:")
        if st.button("Senden"):
            if rethink(msg):
                st.warning("ReThink: ❗  Möchtest du das wirklich schicken?")
            else:
                st.success("Nachricht verschickt ✅")

    # 2 · Bark
    elif demo.startswith("Bark"):
        msg = st.text_input("Chat-Nachricht:")
        if st.button("Senden"):
            if rethink(msg):
                st.error("Bark-Alarm!  Eltern erhalten Meldung 🚨")
            else:
                st.success("Kein Alarm 🙂")

    # 3 · STOPit
    else:
        st.info("Fühlst du dich unsicher?")
        if st.button("HILFE ✚"):
            st.success("Verbinde mit Crisis Text Line …")
            with st.spinner("Chat wird geöffnet …"):
                time.sleep(1.5)
            st.write("📲 24/7 Chat: **#741741** (USA) / **116 111** (DE)")

    st.caption("⚠️ Nur Demo-Funktionen – keine echten Daten werden gesendet.")
