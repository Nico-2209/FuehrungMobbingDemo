import streamlit as st
import matplotlib.pyplot as plt
import random

EXAMPLES = [
    "„Haha, wie du wieder aussiehst!“",
    "Jemand wird jeden Tag ignoriert.",
    "„Schreib mir die Hausaufgaben, sonst …“",
    "Foto ohne Einwilligung gepostet."
]

def run_slider():
    st.header("GrenzCheck 🔍")

    # Szene festlegen (einmalig)
    if "scene" not in st.session_state:
        st.session_state.scene = random.choice(EXAMPLES)

    # Moderator-Tools (Seitenleiste)
    if st.sidebar.checkbox("Moderator", False):
        st.session_state.scene = st.sidebar.selectbox(
            "Satz wählen", EXAMPLES,
            index=EXAMPLES.index(st.session_state.scene)
        )
        if st.sidebar.button("Stimmen zurücksetzen"):
            st.session_state.votes = []

    # Satz anzeigen
    st.subheader(st.session_state.scene)

    # Slider + Vote-Button
    vote = st.slider("Wie schlimm? 0 = OK … 100 = Mobbing", 0, 100, 50)
    if st.button("Abstimmen"):
        st.session_state.setdefault("votes", []).append(vote)

    votes = st.session_state.get("votes", [])
    st.write(f"Abgegebene Stimmen: **{len(votes)}**")

    # Live-Histogramm
    if votes:
        fig, ax = plt.subplots()
        ax.hist(votes, bins=10, edgecolor="white")
        ax.set_xlabel("Schweregrad")
        ax.set_ylabel("Anzahl")
        st.pyplot(fig)
        st.metric("Durchschnitt", f"{sum(votes)/len(votes):.1f} / 100")
    else:
        st.info("Noch keine Stimmen.")
