import streamlit as st
from streamlit_autorefresh import st_autorefresh  #  NEW
import random, pandas as pd, plotly.express as px

# ------- gemeinsamer Speicher für alle Sessions -------
STORE = {"scene": None, "votes": []}

# ------- realistische Beispiele -------
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

    # Szene einmalig setzen
    if STORE["scene"] is None:
        STORE["scene"] = random.choice(EXAMPLES)

    # Session-State pro Browser-Tab
    st.session_state.setdefault("voted", False)
    st.session_state.setdefault("current_scene", STORE["scene"])

    # Szene gewechselt → Vote zurücksetzen
    if st.session_state.current_scene != STORE["scene"]:
        st.session_state.voted = False
        st.session_state.current_scene = STORE["scene"]

    # -------- Moderator-Panel --------
    is_mod = st.sidebar.checkbox("Moderator-Ansicht", False)
    if is_mod:
        # Auto-Refresh alle 2 s (nur beim Moderator)
        st_autorefresh(interval=2000, key="live_refresh")

        STORE["scene"] = st.sidebar.selectbox(
            "Beispiel wählen", EXAMPLES,
            index=EXAMPLES.index(STORE["scene"])
        )
        if st.sidebar.button("Stimmen zurücksetzen"):
            STORE["votes"].clear()
            st.session_state.voted = False

    # -------- Voting --------
    st.subheader(STORE["scene"])

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
            st.rerun()                      # sofortiges Redraw für diesen Tab

    st.write(f"**{len(STORE['votes'])} Stimmen**")

    # -------- Ergebnisanzeige --------
    if STORE["votes"] and is_mod:
        df = pd.DataFrame({"Score": STORE["votes"]})
        bins = list(range(0, 101, 5))
        labels = [f"{b}-{b+4}" for b in bins[:-2]] + ["95-100"]
        df["Bin"] = pd.cut(df["Score"], bins=bins, labels=labels,
                           right=True, include_lowest=True)

        chart = px.histogram(
            df, x="Bin", category_orders={"Bin": labels},
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
