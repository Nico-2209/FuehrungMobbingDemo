import streamlit as st
from streamlit_autorefresh import st_autorefresh
import random, pandas as pd, plotly.express as px

STORE = st.session_state.setdefault("shared_store", {
    "scene_idx": 0,
    "votes": []
})

RAW_SCENES = [
    "Die Klasse plant im WhatsApp-Chat einen Geburtstagsausflug. Alle schreiben begeistert – nur Leon wird nicht eingeladen. Später postet jemand ein Meme: „Leon = Forever Alone 😂“. 23 Mitschüler reagieren mit „🤣“-Emoji.",
    "In Moodle fragt Chiara (1. Semester) nach einer Formel. Mehrere antworten ironisch: „Googeln hilft 😉“. Ein Thread mit 40 Upvotes macht sich lustig. Abends bekommt sie eine Direktnachricht: „Erst nachdenken, Brainlet!“",
    "Im Valorant-Discord ruft einer: „Halt die Klappe, Mädel, nimm Healer und kusch!“ Als sie protestiert, droht er: „Doxx dich gleich auf Twitter“. ",
    "In der Schulkantine wird heimlich ein Video von Tom beim Essen aufgenommen. Auf TikTok landet es mit #WhaleWatch. 12 000 Views, viele Kommentare wie „Diät gefällig?“. ",
    "Beim Gruppen-Referat teilen sich drei Studenten ein Google-Doc und laden Sarah nicht ein. Sie soll nur eine „Deko-Folie“ erstellen. Ihre Ideen werden danach öffentlich zerrissen.",
    "Im Firmen-Slack postet jemand ein Party-Foto von Max, betrunken beim Sommerfest. Kollegen kommentieren: „Quality Assurance 🍻“. Das Bild bleibt angepinnt."
]

if "voted" not in st.session_state:
    st.session_state.voted = False
if "scene_at_load" not in st.session_state:
    st.session_state.scene_at_load = STORE["scene_idx"]

st_autorefresh(interval=2000, key="global_refresh")

st.title("GrenzCheck 🔍 – Wie schlimm findest du das?")

is_mod = st.sidebar.checkbox("Moderator-Ansicht", False)
if is_mod:
    selected = st.sidebar.selectbox(
        "Szene auswählen", range(len(RAW_SCENES)),
        index=STORE["scene_idx"],
        format_func=lambda i: RAW_SCENES[i][:50] + "..."
    )
    if selected != STORE["scene_idx"]:
        STORE["scene_idx"] = selected
        STORE["votes"].clear()
        st.session_state.voted = False
        st.session_state.scene_at_load = selected
    if st.sidebar.button("Stimmen zurücksetzen"):
        STORE["votes"].clear()
        st.session_state.voted = False

idx = STORE["scene_idx"]
story = RAW_SCENES[idx]
st.subheader("📝 Situation")
st.write(story)

if st.session_state.scene_at_load != idx:
    st.session_state.voted = False
    st.session_state.scene_at_load = idx

col1, col2 = st.columns([3, 1])
with col1:
    vote = st.slider(
        "Wie schlimm findest du das?", 0, 100, 50, step=1,
        disabled=st.session_state.voted
    )
with col2:
    if st.button("✅ Abstimmen", disabled=st.session_state.voted):
        STORE["votes"].append(vote)
        st.session_state.voted = True
        st.rerun()

st.markdown(f"**{len(STORE['votes'])} Stimmen abgegeben**")

if st.session_state.voted:
    st.success("Danke! Dein Vote wurde gezählt.")
else:
    st.info("Bitte abstimmen, um das Ergebnis zu sehen.")

if STORE["votes"] and is_mod:
    df = pd.DataFrame({"Score": STORE["votes"]})
    bins = list(range(0, 101, 5))
    labels = [f"{b}-{b+4}" for b in bins[:-2]] + ["95-100"]
    df["Bin"] = pd.cut(df["Score"], bins=bins, labels=labels,
                       right=True, include_lowest=True)
    fig = px.histogram(
        df, x="Bin", labels={"Bin": "Bewertung"},
        category_orders={"Bin": labels},
        color_discrete_sequence=["#3E7CB1"],
        title="Verteilung der Einschätzungen"
    )
    fig.update_layout(yaxis_title="Anzahl", bargap=0.05, xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
    st.metric("Durchschnitt", f"{sum(STORE['votes']) / len(STORE['votes']):.1f} / 100")
