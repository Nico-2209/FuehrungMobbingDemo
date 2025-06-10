# slider_app.py
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import random, pandas as pd, plotly.express as px

# ——— Globaler Store (für alle Sessions im selben Prozess) ———
STORE = {
    "scene_idx": 0,
    "votes": []
}

# ——— Die Stories ———
RAW_SCENES = [
    "Die Klasse plant im WhatsApp-Chat einen Geburtstagsausflug. Alle freuen sich – nur Leon wird nicht eingeladen. Später postet jemand ein Meme: „Leon = Forever Alone 😂“. 23 Mitschüler reagieren mit „🤣“.",
    "In Moodle fragt Chiara (1. Sem.) nach einer Formel. Einige antworten ironisch: „Googeln hilft 😉“. Ein Thread mit 40 Upvotes macht sich darüber lustig. Abends erhält sie eine Direktnachricht: „Erst denken, Brainlet!“",
    "Im Valorant-Discord ruft einer: „Halt die Klappe, Mädel!“ Als sie widerspricht, droht er: „Ich doxxe dich auf Twitter.“",
    "Ein heimliches Video von Tom beim Essen wird auf TikTok gepostet (#WhaleWatch). 12 000 Views, Kommentare wie „Diät gefällig?“ folgen.",
    "Beim Gruppen-Referat teilen sich drei Studis ein Google-Doc und laden Sarah nicht ein. Sie soll nur die „Deko-Folie“ machen, dann zerreißt man ihre Ideen öffentlich.",
    "Im Firmen-Slack postet jemand ein Party-Foto von Max, betrunken. Kollegen kommentieren: „Quality Assurance 🍻“. Das Bild bleibt angepinnt."
]

def run_slider():
    # ——— Auto-Refresh alle 2 Sekunden (alle Sessions) ———
    st_autorefresh(interval=2000, key="global_refresh")

    st.header("GrenzCheck 🔍 – Wie schlimm findest du das?")

    # ——— Session-Flags initialisieren ———
    if "voted" not in st.session_state:
        st.session_state.voted = False
    if "scene_at_load" not in st.session_state:
        st.session_state.scene_at_load = STORE["scene_idx"]

    # ——— Moderator-Panel ———
    is_mod = st.sidebar.checkbox("Moderator-Ansicht", False)
    if is_mod:
        choice = st.sidebar.selectbox(
            "Szene wählen",
            list(range(len(RAW_SCENES))),
            index=STORE["scene_idx"],
            format_func=lambda i: RAW_SCENES[i][:40] + "…"
        )
        if choice != STORE["scene_idx"]:
            STORE["scene_idx"] = choice
            STORE["votes"].clear()
        if st.sidebar.button("Stimmen zurücksetzen"):
            STORE["votes"].clear()
        # nach Szene-Wechsel Vote-Flag resynchronisieren
        st.session_state.voted = False
        st.session_state.scene_at_load = STORE["scene_idx"]

    # ——— Szene anzeigen ———
    idx = STORE["scene_idx"]
    st.subheader("📝 Situation")
    st.write(RAW_SCENES[idx])

    # ——— Vote-Flag zurücksetzen, falls Szene sich global ändert ———
    if st.session_state.scene_at_load != idx:
        st.session_state.voted = False
        st.session_state.scene_at_load = idx

    # ——— Voting UI ———
    col1, col2 = st.columns([3,1])
    with col1:
        vote = st.slider(
            "Bewertung (0 = OK … 100 = klares Mobbing)",
            0, 100, 50, step=1,
            disabled=st.session_state.voted
        )
    with col2:
        if st.button("✅ Abstimmen", disabled=st.session_state.voted):
            STORE["votes"].append(vote)
            st.session_state.voted = True
            st.rerun()  # nur dieser Tab

    st.markdown(f"**{len(STORE['votes'])} Stimmen insgesamt**")

    # ——— User-Feedback ———
    if st.session_state.voted:
        st.success("Danke! Dein Vote wurde gezählt.")
    else:
        st.info("Bitte abstimmen, um das Ergebnis zu sehen.")

    # ——— Chart nur für Moderator ———
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
            labels={"Bin":"Bewertung"},
            category_orders={"Bin":labels},
            color_discrete_sequence=["#3E7CB1"],
            title="Verteilung der Einschätzungen"
        )
        fig.update_layout(
            yaxis_title="Anzahl", bargap=0.05,
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig, use_container_width=True)
        st.metric("Durchschnitt", f"{sum(STORE['votes'])/len(STORE['votes']):.1f} / 100")
