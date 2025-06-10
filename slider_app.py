# slider_app.py  – Live-Refresh & Vote-Sperre
import streamlit as st
import random, pandas as pd, plotly.express as px

# ------------------ 1. Gemeinsamer Speicher ------------------
STORE = {"scene": None, "votes": []}           # global für alle Sessions

# ------------------ 2. Beispiele ------------------
EXAMPLES = [
    "Im Klassenchat: »Junge, du stinkst – setz dich woanders!«",
    "Screenshot vom schlechten Zeugnis wird in die Gruppe gestellt.",
    "Im Gaming-Voicechat brüllt jemand: »Du Hurensohn, lern spielen!«",
    "Auf Insta kursiert ein Meme, das dein Gesicht als „Fail“ zeigt.",
    "In der Mensa ruft jemand laut: »Fette Sau, lass das Dessert stehen!«",
    "Beim Sport wird dir ständig der Ball weggekickt und gelacht.",
    "Lehrkraft nennt dich vor allen nur noch „Professor Schlaumeier“."
]

def run_slider():
    st.header("GrenzCheck 🔍")

    # (a) Szene setzen
    if STORE["scene"] is None:
        STORE["scene"] = random.choice(EXAMPLES)

    # -------- Per-Tab State initialisieren --------
    if "voted" not in st.session_state:
        st.session_state.voted = False
    if "current_scene" not in st.session_state:
        st.session_state.current_scene = STORE["scene"]

    # Wenn Moderator die Szene gewechselt hat → Vote zurücksetzen
    if st.session_state.current_scene != STORE["scene"]:
        st.session_state.voted = False
        st.session_state.current_scene = STORE["scene"]

    # -------- Moderator-Seitenleiste --------
    is_mod = st.sidebar.checkbox("Moderator-Ansicht", False)
    if is_mod:
        # Auto-Refresh alle 2 Sek, damit Chart live updatet

        st.autorefresh(interval=2000, key="refresh")

        # Szene wählen
        STORE["scene"] = st.sidebar.selectbox(
            "Beispiel wählen", EXAMPLES,
            index=EXAMPLES.index(STORE["scene"])
        )
        # Reset
        if st.sidebar.button("Stimmen zurücksetzen"):
            STORE["votes"].clear()
            st.session_state.voted = False

    # -------- Scene Display & Voting --------
    st.subheader(STORE["scene"])

    col1, col2 = st.columns([3, 1])
    with col1:
        vote = st.slider(
            "Wie schlimm findest du das?", 0, 100, 50, step=1,
            help="0 = alles okay · 100 = klares Mobbing",
            disabled=st.session_state.voted      # Slider deaktiviert nach Vote
        )
    with col2:
        if st.button("✅ Abstimmen", disabled=st.session_state.voted):
            STORE["votes"].append(vote)
            st.session_state.voted = True
            st.rerun()    # nur eigener Tab – Moderator wird via Auto-Refresh aktualisiert

    st.write(f"**{len(STORE['votes'])} Stimmen**")

    # -------- Ergebnisanzeige --------
    if STORE["votes"] and is_mod:          # Chart nur für Moderator
        df = pd.DataFrame({"Score": STORE["votes"]})
        bins = list(range(0, 101, 5))
        labels = [f"{b}-{b+4}" for b in bins[:-2]] + ["95-100"]
        df["Bin"] = pd.cut(df["Score"], bins=bins, labels=labels,
                           right=True, include_lowest=True)

        chart = px.histogram(
            df, x="Bin",
            category_orders={"Bin": labels},
            labels={"Bin": "Schweregrad"},
            title="Verteilung der Stimmen",
            color_discrete_sequence=["#3E7CB1"]
        )
        chart.update_layout(
            yaxis_title="Anzahl", bargap=0.05,
            xaxis_tickangle=-45, xaxis_tickfont_size=11
        )
        st.plotly_chart(chart, use_container_width=True)
        st.metric("Durchschnitt", f"{sum(STORE['votes'])/len(STORE['votes']):.1f} / 100")

    elif st.session_state.voted:
        st.success("Danke fürs Abstimmen! Dein Vote ist gespeichert.")
    else:
        st.info("Stimme ab, um zu sehen, wie die Gruppe bewertet.")
