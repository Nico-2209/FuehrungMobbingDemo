# slider_app.py
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import random, pandas as pd, plotly.express as px

# 1) Gemeinsamer Speicher
STORE = {"scene_idx": None, "votes": []}

# 2) Komplexe Stories
RAW_SCENES = [
    "Die Klasse plant im WhatsApp-Chat einen Geburtstagsausflug. Alle schreiben begeistert – nur Leon wird nicht eingeladen. Später postet jemand ein Meme: „Leon = Forever Alone 😂“. 23 Mitschüler reagieren mit „🤣“-Emoji.",
    "In Moodle fragt Chiara (1. Semester) nach einer Formel. Mehrere antworten ironisch: „Googeln hilft 😉“. Ein Thread mit 40 Upvotes macht sich lustig. Abends bekommt sie eine Direktnachricht: „Erst nachdenken, Brainlet!“",
    "Im Valorant-Discord ruft einer: „Halt die Klappe, Mädel, nimm Healer und kusch!“ Als sie protestiert, droht er: „Doxx dich gleich auf Twitter“.",
    "In der Schulkantine wird heimlich ein Video von Tom beim Essen aufgenommen. Auf TikTok landet es mit #WhaleWatch. 12 000 Views, viele Kommentare wie „Diät gefällig?“.",
    "Beim Gruppen-Referat teilen sich drei Studenten ein Google-Doc und laden Sarah nicht ein. Sie soll nur eine „Deko-Folie“ erstellen. Ihre Ideen werden danach öffentlich zerrissen.",
    "Im Firmen-Slack postet jemand ein Party-Foto von Max, betrunken beim Sommerfest. Kollegen kommentieren: „Quality Assurance 🍻“. Das Bild bleibt angepinnt."
]

# 3) Helper: Szene & Vote-Logik
def init_scene():
    if STORE["scene_idx"] is None:
        STORE["scene_idx"] = random.randrange(len(RAW_SCENES))
        STORE["votes"].clear()

def current_story():
    idx = STORE["scene_idx"]
    text = RAW_SCENES[idx]
    return idx, text

# 4) Hauptfunktion
def run_slider():
    # a) Autorefresh für alle (2 Sek)
    st_autorefresh(interval=2000, key="global_refresh")

    st.header("GrenzCheck 🔍")

    # b) Init Scene & Session-State
    init_scene()
    idx, story = current_story()
    st.session_state.setdefault("voted", False)
    st.session_state.setdefault("scene_at_load", idx)

    # c) Detect Scene-Change → Vote zurücksetzen
    if st.session_state.scene_at_load != idx:
        st.session_state.voted = False
        st.session_state.scene_at_load = idx

    # d) Moderator-Panel
    is_mod = st.sidebar.checkbox("Moderator-Ansicht", False)
    if is_mod:
        new_idx = st.sidebar.selectbox(
            "Story wählen",
            list(range(len(RAW_SCENES))),
            index=idx,
            format_func=lambda i: RAW_SCENES[i][:40] + "…"
        )
        if new_idx != idx:
            STORE["scene_idx"] = new_idx
            STORE["votes"].clear()
            st.session_state.voted = False
        if st.sidebar.button("Stimmen zurücksetzen"):
            STORE["votes"].clear()
            st.session_state.voted = False

    # e) Show Story (Teaser + Expander)
    st.subheader("📝 Situation (Kurz-Teaser):")
    st.markdown(f"> {story[:100]}…")
    with st.expander("Gesamten Text anzeigen"):
        st.write(story)

    # f) Voting UI
    col1, col2 = st.columns([3,1])
    with col1:
        vote = st.slider(
            "Wie schlimm findest du das?", 0, 100, 50, step=1,
            disabled=st.session_state.voted
        )
    with col2:
        if st.button("✅ Abstimmen", disabled=st.session_state.voted):
            STORE["votes"].append(vote)
            st.session_state.voted = True
            st.rerun()  # eigener Tab neu

    st.write(f"**{len(STORE['votes'])} Stimmen insgesamt**")

    # g) Feedback für User
    if st.session_state.voted:
        st.success("Danke! Dein Vote ist gespeichert.")
    else:
        st.info("Abstimmen, um dein Ergebnis zu sehen!")

    # h) Chart nur für Moderator
    if STORE["votes"] and is_mod:
        df = pd.DataFrame({"Score": STORE["votes"]})
        bins = list(range(0, 101, 5))
        labels = [f"{b}-{b+4}" for b in bins[:-2]] + ["95-100"]
        df["Bin"] = pd.cut(df["Score"], bins=bins, labels=labels,
                           right=True, include_lowest=True)
        fig = px.histogram(
            df, x="Bin", labels={"Bin": "Schweregrad"},
            category_orders={"Bin": labels},
            color_discrete_sequence=["#3E7CB1"],
            title="Verteilung der Stimmen"
        )
        fig.update_layout(yaxis_title="Anzahl",
                          bargap=0.05, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
        st.metric("Durchschnitt", f"{sum(STORE['votes'])/len(STORE['votes']):.1f} / 100")
