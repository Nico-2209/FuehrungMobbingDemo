# slider_app.py
import streamlit as st, random, pandas as pd, plotly.express as px

STORE = {"scene": None, "votes": []}   # global
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

    # Per-Tab-State: hat dieser Nutzer schon abgestimmt?
    if "voted" not in st.session_state:
        st.session_state.voted = False

    # Moderator-Tools
    is_mod = st.sidebar.checkbox("Moderator-Ansicht", False)
    if is_mod:
        STORE["scene"] = st.sidebar.selectbox(
            "Beispiel wählen", EXAMPLES, index=EXAMPLES.index(STORE["scene"])
        )
        if st.sidebar.button("Stimmen zurücksetzen"):
            STORE["votes"].clear()
            st.session_state.voted = False    # auch lokalen Status zurücksetzen

    st.subheader(STORE["scene"])

    # Abstimmen
    col1, col2 = st.columns([3, 1])
    with col1:
        vote = st.slider("Wie schlimm findest du das?", 0, 100, 50, step=1)
    with col2:
        if st.button("✅ Abstimmen"):
            STORE["votes"].append(vote)
            st.session_state.voted = True
            st.rerun()               # nur dieser Tab rerendert sofort neu

    votes = STORE["votes"]
    st.write(f"**{len(votes)} Stimmen**")

    # Ergebnis-Logik
    if votes and is_mod:
        # ---- Diagramm nur für Moderator ----
        df = pd.DataFrame({"Score": votes})
        bins = list(range(0, 101, 5))
        labels = [f"{b}-{b+4}" for b in bins[:-2]] + ["95-100"]
        df["Bin"] = pd.cut(df["Score"], bins=bins, labels=labels,
                           right=True, include_lowest=True)

        chart = px.histogram(df, x="Bin",
            category_orders={"Bin": labels},
            labels={"Bin": "Schweregrad"},
            title="Verteilung der Stimmen",
            color_discrete_sequence=["#3E7CB1"])
        chart.update_layout(yaxis_title="Anzahl", bargap=0.05,
                            xaxis_tickangle=-45, xaxis_tickfont_size=11)
        st.plotly_chart(chart, use_container_width=True)
        st.metric("Durchschnitt", f"{sum(votes)/len(votes):.1f} / 100")

    elif st.session_state.voted:
        st.success("Danke fürs Abstimmen! Dein Ergebnis zählt ✅")
    else:
        st.info("Stimme ab, um zu sehen, wo du liegst!")
