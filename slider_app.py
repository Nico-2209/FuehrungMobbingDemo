# slider_app.py
import streamlit as st
import random
import pandas as pd
import plotly.express as px

def run_slider():
    # — globaler Zustand —
    STORE = st.session_state.setdefault("shared_store", {
        "scene_idx": 0,
        "votes": []
    })

    # — Erzählsituationen —
    RAW_SCENES = [
        "Die Klasse plant im WhatsApp-Chat einen Ausflug. Leon wird nicht eingeladen. Später postet jemand ein Meme: „Leon = Forever Alone 😂“. 23 Mitschüler reagieren mit „🤣“.",
        "Chiara fragt im Moodle nach einer Formel. Einige antworten: „Googeln hilft 😉“. Abends erhält sie die DM: „Erst denken, Brainlet!“",
        "Im Valorant-Voicechat gibt's Beleidigungen: „Halt die Klappe, Mädel!“ und Drohungen mit Doxx.",
        "Ein TikTok-Video von Tom (Mensa) geht viral (#WhaleWatch). Tausende Kommentare wie „Diät gefällig?“. ",
        "Drei Studis arbeiten im Google-Doc, laden Sarah nicht ein und zerreißen später ihre Ideen.",
        "Im Firmen-Slack wird Max‘ Party-Foto gepostet („Quality Assurance 🍻“). Das Bild bleibt angepinnt."
    ]

    # — Session-Flags —
    if "voted" not in st.session_state:
        st.session_state.voted = False
    if "scene_at_load" not in st.session_state:
        st.session_state.scene_at_load = STORE["scene_idx"]

    st.header("GrenzCheck 🔍 – Wie schlimm findest du das?")

    # — Moderator-Panel —
    is_mod = st.sidebar.checkbox("Moderator-Ansicht", False)
    if is_mod:
        chosen = st.sidebar.selectbox(
            "Szene wählen:",
            options=list(range(len(RAW_SCENES))),
            index=STORE["scene_idx"],
            format_func=lambda i: RAW_SCENES[i][:40] + "…"
        )
        if chosen != STORE["scene_idx"]:
            STORE["scene_idx"] = chosen
            STORE["votes"].clear()
            st.session_state.voted = False
            st.session_state.scene_at_load = chosen

        if st.sidebar.button("Stimmen zurücksetzen"):
            STORE["votes"].clear()
            st.session_state.voted = False

    # — Szene anzeigen —
    idx = STORE["scene_idx"]
    st.subheader("📝 Situation")
    st.write(RAW_SCENES[idx])

    # — Reset Vote-Flag bei Szenenwechsel —
    if st.session_state.scene_at_load != idx:
        st.session_state.voted = False
        st.session_state.scene_at_load = idx

    # — Voting UI —
    col1, col2 = st.columns([3,1])
    with col1:
        vote = st.slider(
            "Bewertung (0 = OK … 100 = klares Mobbing)",
            0, 100, 50,
            disabled=st.session_state.voted
        )
    with col2:
        if st.button("✅ Abstimmen", disabled=st.session_state.voted):
            STORE["votes"].append(vote)
            st.session_state.voted = True
            st.rerun()  # aktuelle Session neu laden

    st.markdown(f"**{len(STORE['votes'])} Stimmen insgesamt**")

    # — Manuelles Refresh für alle —
    if st.button("🔄 Seite aktualisieren"):
        st.rerun()

    # — Feedback für User —
    if st.session_state.voted:
        st.success("Danke! Dein Vote wurde gespeichert.")
    else:
        st.info("Bitte abstimmen, um das Ergebnis zu sehen.")

    # — Chart nur für Moderator —
    if STORE["votes"] and is_mod:
        df = pd.DataFrame({"Score": STORE["votes"]})
        bins = list(range(0, 101, 5))
        labels = [f"{b}-{b+4}" for b in bins[:-2]] + ["95-100"]
        df["Bin"] = pd.cut(
            df["Score"], bins=bins, labels=labels,
            right=True, include_lowest=True
        )
        fig = px.histogram(
            df, x="Bin",
            labels={"Bin": "Bewertung"},
            category_orders={"Bin": labels},
            color_discrete_sequence=["#3E7CB1"],
            title="Stimmenverteilung"
        )
        fig.update_layout(yaxis_title="Anzahl", bargap=0.05, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
        st.metric("Durchschnitt", f"{sum(STORE['votes'])/len(STORE['votes']):.1f} / 100")
