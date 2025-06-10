# slider_app.py  – mit st.rerun()
import streamlit as st
import random, pandas as pd, plotly.express as px

STORE = {"scene": None, "votes": []}

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

    if STORE["scene"] is None:
        STORE["scene"] = random.choice(EXAMPLES)

    with st.sidebar:
        if st.checkbox("Moderator", False):
            STORE["scene"] = st.selectbox(
                "Satz wählen", EXAMPLES,
                index=EXAMPLES.index(STORE["scene"])
            )
            if st.button("Stimmen zurücksetzen"):
                STORE["votes"].clear()

    st.subheader(STORE["scene"])

    col1, col2 = st.columns([3, 1])
    with col1:
        vote = st.slider(
            "Wie schlimm findest du das?", 0, 100, 50, step=1,
            help="0 = OK, 100 = klares Mobbing"
        )
    with col2:
        if st.button("✅ Abstimmen"):
            STORE["votes"].append(vote)
            st.rerun()   # alle Tabs neu zeichnen (Streamlit ≥1.25)

    votes = STORE["votes"]
    st.write(f"**{len(votes)} Stimmen**")

    if votes:
        df = pd.DataFrame({"Score": votes})
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
        st.metric("Durchschnitt", f"{sum(votes)/len(votes):.1f} / 100")
    else:
        st.info("Noch keine Stimmen abgegeben.")
