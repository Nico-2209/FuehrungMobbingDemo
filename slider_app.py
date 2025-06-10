import streamlit as st
import random
import pandas as pd
import plotly.express as px

def run_slider():
    # — gemeinsamer, globaler Speicher —
    STORE = st.session_state.setdefault("shared_store", {
        "scene_idx": 0,
        "votes": []
    })

    # — realistische Szenen —
    RAW_SCENES = [
        "Die Klasse plant im WhatsApp-Chat einen Ausflug. Leon wird nicht eingeladen. Später erscheint ein Meme: „Leon = Forever Alone 😂“. 23 Mitschüler reagieren mit „🤣“.",
        "Chiara fragt im Moodle nach einer Formel. Einige reagieren ironisch: „Googeln hilft 😉“. Abends erhält sie die Nachricht: „Erst denken, Brainlet!“",
        "Im Valorant-Discord wird sie beschimpft: „Halt die Klappe, Mädel!“ und es folgt die Drohung: „Ich doxxe dich.“",
        "Ein heimliches Video von Tom in der Mensa landet auf TikTok (#WhaleWatch). 12 000 Views, Kommentare wie „Diät gefällig?“.",
        "Beim Gruppen-Referat laden drei Studis Sarah nicht ins Google-Doc ein, lassen sie nur die Deko-Folie gestalten und lästern später über ihre Ideen.",
        "Im Firmen-Slack postet jemand Max volltrunken. Die Gruppe kommentiert: „Quality Assurance 🍻“ und pinnt das Bild."
    ]

    # — Session-Flags pro Tab —
    if "voted" not in st.session_state:
        st.session_state.voted = False
    if "scene_at_load" not in st.session_state:
        st.session_state.scene_at_load = STORE["scene_idx"]

    st.header("GrenzCheck 🔍 – Wie schlimm findest du das?")

    # — Moderator-Panel —
    is_mod = st.sidebar.checkbox("Moderator-Ansicht", False)
    if is_mod:
        new_idx = st.sidebar.selectbox(
            "Szene wählen",
            range(len(RAW_SCENES)),
            index=STORE["scene_idx"],
            format_func=lambda i: RAW_SCENES[i][:40] + "…"
        )
        if new_idx != STORE["scene_idx"]:
            STORE["scene_idx"] = new_idx
            STORE["votes"].clear()
            st.session_state.voted = False
            st.session_state.scene_at_load = new_idx

        if st.sidebar.button("Stimmen zurücksetzen"):
            STORE["votes"].clear()
            st.session_state.voted = False

    # — Szene anzeigen —
    idx = STORE["scene_idx"]
    st.subheader("📝 Situation")
    st.write(RAW_SCENES[idx])

    # — Vote-Flag zurücksetzen bei Szenenwechsel —
    if st.session_state.scene_at_load != idx:
        st.session_state.voted = False
        st.session_state.scene_at_load = idx

    # — Voting UI —
    c1, c2 = st.columns([3, 1])
    with c1:
        vote = st.slider(
            "Bewertung 0=OK … 100=Mobbing",
            0, 100, 50,
            disabled=st.session_state.voted
        )
    with c2:
        if st.button("✅ Abstimmen", disabled=st.session_state.voted):
            STORE["votes"].append(vote)
            st.session_state.voted = True
            st.rerun()  # diese Session neu laden

    st.markdown(f"**{len(STORE['votes'])} Stimmen insgesamt**")

    # — Manuelles Refresh für alle —
    if st.button("🔄 Seite aktualisieren"):
        st.rerun()

    # — Nutzer-Feedback —
    if st.session_state.voted:
        st.success("Danke! Dein Vote wurde gespeichert.")
    else:
        st.info("Bitte abstimmen, um das Ergebnis zu sehen.")

    # — Diagramm nur für Moderator —
    if STORE["votes"] and is_mod:
        df = pd.DataFrame({"Score": STORE["votes"]})
        bins = list(range(0, 101, 5))
        labels = [f"{b}-{b+4}" for b in bins[:-2]] + ["95-100"]
        df["Bin"] = pd.cut(
            df["Score"], bins=bins,
            labels=labels,
            right=True,
            include_lowest=True
        )
        fig = px.histogram(
            df, x="Bin",
            labels={"Bin": "Bewertung"},
            category_orders={"Bin": labels},
            color_discrete_sequence=["#3E7CB1"],
            title="Stimmenverteilung"
        )
        fig.update_layout(
            yaxis_title="Anzahl",
            bargap=0.05,
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig, use_container_width=True)
        st.metric("Durchschnitt", f"{sum(STORE['votes'])/len(STORE['votes']):.1f} / 100")
