import streamlit as st
import plotly.express as px
import random
import pandas as pd

EXAMPLES = [
    "„Haha, wie du wieder aussiehst!“",
    "Ignoriert jede Meldung in der Gruppe.",
    "„Gib mir deine Hausaufgaben, sonst …“",
    "Peinliches Foto ohne Einwilligung gepostet.",
    "Abfälliger Spitzname vor der Klasse.",
    "Droht im Spielchat mit Bann, wenn …",
    "Verteilt fiese Memes über eine Person."
]

def run_slider():
    st.header("GrenzCheck 🔍")

    # Moderator-Panel
    if "scene" not in st.session_state:
        st.session_state.scene = random.choice(EXAMPLES)
    with st.sidebar:
        if st.checkbox("Moderator", False):
            st.session_state.scene = st.selectbox(
                "Satz wählen", EXAMPLES,
                index=EXAMPLES.index(st.session_state.scene)
            )
            if st.button("Stimmen zurücksetzen"):
                st.session_state.votes = []

    st.subheader(st.session_state.scene)

    # ---- Slider ----
    col1, col2 = st.columns([3, 1])
    with col1:
        vote = st.slider("Wie schlimm findest du das?", 0, 100, 50,
                         step=1, help="0 = OK, 100 = klares Mobbing")
    with col2:
        if st.button("✅ Abstimmen"):
            st.session_state.setdefault("votes", []).append(vote)

    votes = st.session_state.get("votes", [])
    st.write(f"**{len(votes)} Stimmen**")

    # ---- Grafik: gruppiert in 5er-Schritten ----
    if votes:
        df = pd.DataFrame({"Score": votes})
        bins = list(range(0, 105, 5))
        labels = [f"{b}-{b+4}" for b in bins[:-1]]
        df["Bin"] = pd.cut(df["Score"], bins=bins, labels=labels, right=False)

        chart = px.histogram(
            df,
            x="Bin",
            category_orders={"Bin": labels},
            labels={"Bin": "Schweregrad"},
            title="Verteilung der Stimmen",
            color_discrete_sequence=["#3E7CB1"]
        )
        chart.update_layout(
            yaxis_title="Anzahl",
            bargap=0.05,
            xaxis_tickangle=-45
        )
        st.plotly_chart(chart, use_container_width=True)

        st.metric("Durchschnitt", f"{sum(votes)/len(votes):.1f} / 100")

