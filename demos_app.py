import streamlit as st, time
from pathlib import Path
from html import escape

# ─── 1) Bad-Words laden (Fallback, falls Datei fehlt) ────────────────────────
try:
    RAW = Path(__file__).with_name("badwords.txt").read_text(encoding="utf-8").splitlines()
    BAD = {w.strip().lower() for w in RAW if w.strip()}
except FileNotFoundError:
    BAD = {"idiot", "loser", "dummkopf"}

def contains_bad(txt: str) -> bool:
    return any(b in txt.lower() for b in BAD)

def highlight_bad(txt: str) -> str:
    out = escape(txt)
    for word in BAD:
        out = out.replace(word, f'<span style="color:#e74c3c;font-weight:bold">{word}</span>')
    return out

# ─── 2) Demo-UI ──────────────────────────────────────────────────────────────
def run_demos():
    st.header("🛡️ Interaktive Schutz-Demos")

    demo = st.radio("App wählen:", ["ReThink", "Bark", "STOPit HELPme"], horizontal=True)
    st.markdown("---")

    # ══════════════ ReThink ══════════════
    if demo == "ReThink":
        st.subheader("🔄  ReThink – Nachricht prüfen")
        text = st.text_area("Nachricht eingeben …", height=120, max_chars=280, placeholder="Schreibe etwas …")
        st.caption(f"{len(text)}/280 Zeichen")

        if text:
            st.markdown("**Vorschau:**", help="Bad Words werden rot markiert")
            st.markdown(f"<div style='padding:0.5em;background:#f6f6f6;border-radius:6px'>{highlight_bad(text)}</div>",
                        unsafe_allow_html=True)

        col_send, col_clear = st.columns(2)
        if col_send.button("📤 Senden", use_container_width=True, disabled=not text):
            if contains_bad(text):
                st.error("🚫 Nachricht gestoppt – bitte Formulierung prüfen!")
            else:
                st.success("✅ Nachricht gesendet!")

        if col_clear.button("🗑 Eingabe leeren", use_container_width=True):
            st.experimental_rerun()

    # ══════════════ Bark ══════════════
    elif demo == "Bark":
        st.subheader("👀  Bark – Nachricht überwachen")
        chat = st.text_input("Chat-Nachricht:")
        if st.button("Senden"):
            if contains_bad(chat):
                st.warning("⚠️ Bark warnt: Möglicher Bullying-Inhalt erkannt!")
            else:
                st.success("✅ Kein Alarm – Nachricht akzeptiert.")

    # ══════════════ STOPit HELPme ══════════════
    else:
        st.subheader("🚑  STOPit HELPme – Soforthilfe")
        st.info("Fühlst du dich unsicher oder gemobbt? Hole dir sofort Hilfe.")
        if st.button("📞  Kontakt aufnehmen", use_container_width=True):
            with st.spinner("Verbinde dich mit Berater:innen …"):
                for pct in range(0, 101, 10):
                    time.sleep(0.15)
                    st.progress(pct)
            st.success("✅ Verbindung steht! – 24/7 Hilfe: DE 116 111  |  US #741741")

    st.markdown("---")
    st.caption("Demomodus – keine echten Daten werden versendet • Bad-Word-Liste lokal geladen")
