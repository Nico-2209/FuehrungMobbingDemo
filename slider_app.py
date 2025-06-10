# slider_app.py
import streamlit as st
import random
import pandas as pd
import plotly.express as px

# –––– Globaler Store –––––
# Module-Scope-Variable, geteilt über alle Sessions im selben Server-Prozess
STORE = {
    "scene_idx": 0,
    "votes": []
}

# –––– Erzählsituationen –––––
RAW_SCENES = [
    "Die Klasse plant im WhatsApp-Chat einen Geburtstagsausflug. Alle freuen sich – nur Leon wird nicht eingeladen. Später postet jemand ein Meme „Leon = Forever Alone 😂“. 23 Mitschüler reagieren mit „🤣“.",
    "In Moodle fragt Chiara nach einer Formel. Einige antworten ironisch: „Googeln hilft 😉“. Ein Thread mit 40 Upvotes verhöhnt sie. Abends erhält sie die DM: „Erst denken, Brainlet!“",
    "Im Valorant-Discord wird sie aufgefordert: „Halt die Klappe, Mädel!“ Als sie widerspricht, droht man ihr mit Doxxing auf Twitter.",
    "Ein heimliches Video von Tom in der Mensa landet auf TikTok (#WhaleWatch). 12 000 Views, Kommentare wie „Diät gefällig?“ folgen.",
    "Beim Gruppen-Referat teilen drei Studis ein Google-Doc, laden Sarah nicht ein und verteilen ihre Ideen für „Deko-Folie“ vor allen.",
    "Im Firmen-Slack postet jemand Max volltrunken beim Sommerfest. Die Gruppe schreibt: „Quality Assurance 🍻“ und pinnt das Bild."
]

def run_slider():
    st.header("GrenzCheck 🔍 – Wie schlimm ist das?")

    # Session-Flags: pro Tab merken, ob schon gevotet wurde
    if "voted" not in st.session_state:
        st.session_state.voted = False
    if "scene_at_load" not in st.session_state:
        st.session_state.scene_at_load = STORE["scene_idx"]

    # –––– Moderator-Panel –––––
    is_mod = st.sidebar.checkbox("Moderator-Ansicht", False)
    if is_mod:
        new_idx = st.sidebar.selectbox(
            "Szene auswählen",
            options=list(range(len(RAW_SCENES))),
            index=STORE["scene_idx"],
            format_func=lambda i: RAW_SCENES[i][:40] + "…"
        )
        if new_idx != STORE["scene_idx"]:
            STORE["scene_idx"] = new_idx
            STORE["votes"].clear()
            # Reset aller Tabs Vote-Flag, damit alle neu voten können
            st.session_state.voted = False
            st.session_state.scene_at_load = new_idx

        if st.sidebar.button("Stimmen zurücksetzen"):
            STORE["votes"].clear()
            st.session_state.voted = False

    # –––– Szene anzeigen –––––
    idx = STORE["scene_idx"]
    st.subheader("📝 Situation")
    st.write(RAW_SCENES[idx])

    # Reset Vote-Flag, falls Szene sich geändert hat
    if st.session_state.scene_at_load != idx:
        st.session_state.voted = False
        st.session_state.scene_at_load = idx

    # –––– Voting UI –––––
    col1, col2 = st.columns([3,1])
    with col1:
        vote = st.slider(
            "Bewertung 0=OK … 100=Mobbing",
            min_value=0, max_value=100, value=50,
            disabled=st.session_state.voted
        )
    with col2:
        if st.button("✅ Abstimmen", disabled=st.session_state.voted):
            STORE["votes"].append(vote)
            st.session_state.voted = True
            st.experimental_rerun()  # Tab erneuern

    st.markdown(f"**{len(STORE['votes'])} Stimmen insgesamt**")

    # –––– Seite aktualisieren für alle –––––
    if st.button("🔄 Seite aktualisieren"):
        st.experimental_rerun()

    # –––– Feedback an Nutzer –––––
    if st.session_state.voted:
        st.success("Danke! Dein Vote wurde gezählt.")
    else:
        st.info("Bitte abstimmen, um das Ergebnis zu sehen.")

    # –––– Chart nur für Moderator –––––
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
