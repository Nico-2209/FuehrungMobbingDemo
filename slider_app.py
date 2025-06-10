import streamlit as st
import random
import pandas as pd
import plotly.express as px

# 1) Stories
RAW_SCENES = [
    # 1) Grenzübertritt vs. Humor
    "In der Klassen-WhatsApp-Gruppe postet jemand ein GIF, das Sarah als ‚Müllabfuhr‘ veralbert. Einige lachen, andere fühlen sich gedemütigt, niemand greift ein.",
    # 2) Ironie vs. Verletzung
    "Chiara fragt im Moodle nach einer Formel. Ein paar antworten schlampig: ‚Frag doch in der Google-Gruppe.‘ Später kommt eine DM: ‚Schlafmütze, hast wieder verschlafen?‘",
    # 3) Privates öffentlich gemacht
    "In einer Uni-Chatgruppe teilt jemand einen Screenshot aus Lisas privatem Gruppenchat, in dem sie eine Mitschülerin ‚Zicke‘ nennt. Die Originalnachricht wird heimlich weitergeleitet und alle lachen.",
    # 4) Ausgrenzung in 2er-Gruppen
    "Der Lehrer teilt 11 Schüler in Zweiergruppen ein – Maria bleibt als Einzige übrig und wird ohne Erklärung ausgeschlossen. Sie fühlt sich gezielt gemobbt.",
    # 5) Viral-Shitstorm
    "Ein heimlicher Streit zweier Mitschüler wird als TikTok-Video veröffentlicht. Binnen Stunden 1 500 Likes, Kommentare wie ‚LOL loser‘ folgen.",
    # 6) Alterswitz vs. Respekt
    "Im Büro muss Petra jeden Tag fünf Treppen steigen. Kollegen scherzen im Slack: ‚Petra braucht bald eine Rollator auffahrt!‘",
    # 7) Schönheits-Diktat
    "In der Klassen-Instagram-Story postet jemand ein unbearbeitetes Selfie von Lina mit dem Kommentar ‚Real Beauty Filter Off‘. Lina fühlt sich öffentlich bloßgestellt.",
    # 8) ‚Karen‘-Beispiel
    "In der Nachbarschafts-WhatsApp-Gruppe kritisiert Maya die lauten Kinder auf der Straße. Schnell wird sie als ‚Karen‘ beschimpft und ausgelacht.",
    # 9) Study-Group-Exklusion
    "In jeder Lernrunde werden immer dieselben eingeladen – Tim gehört nie dazu, obwohl er im selben Kurs ist. Er bleibt regelmäßig außen vor.",
    # 10) Fake News als Mobbing
    "Ein gefälschtes PDF behauptet, Tom sei beim letzten Test durchgefallen. Über 200 Studis laden es herunter und machen sich vor ihm lustig."
]


# 2) Globaler Store für Szene+Votes
@st.cache_resource
def get_store():
    return {"scene_idx": 0, "votes": []}

def run_slider():
    store = get_store()

    # Session-Flags
    if "voted" not in st.session_state:
        st.session_state.voted = False
    if "loaded_idx" not in st.session_state:
        st.session_state.loaded_idx = store["scene_idx"]

    st.header("GrenzCheck 🔍 – Wie schlimm findest du das?")

    # Moderator-Panel
    is_mod = st.sidebar.checkbox("Moderator-Ansicht", False)
    if is_mod:
        choice = st.sidebar.selectbox(
            "Szene wählen",
            options=list(range(len(RAW_SCENES))),
            index=store["scene_idx"],
            format_func=lambda i: RAW_SCENES[i][:40] + "…"
        )
        if st.sidebar.button("🚀 Szene übernehmen"):
            store["scene_idx"] = choice
            store["votes"].clear()
            st.session_state.voted = False
            st.session_state.loaded_idx = choice
            st.rerun()
        if st.sidebar.button("🗑️ Stimmen zurücksetzen"):
            store["votes"].clear()
            st.session_state.voted = False
            st.rerun()

    # Szene anzeigen
    idx = store["scene_idx"]
    st.subheader("📝 Situation")
    st.write(RAW_SCENES[idx])

    # Reset Vote-Flag bei Szenenwechsel
    if st.session_state.loaded_idx != idx:
        st.session_state.voted = False
        st.session_state.loaded_idx = idx

    # Voting UI
    c1, c2 = st.columns([3, 1])
    with c1:
        vote = st.slider(
            "Bewertung (0 = OK … 100 = Mobbing)",
            0, 100, 50,
            disabled=st.session_state.voted
        )
    with c2:
        if st.button("✅ Abstimmen", disabled=st.session_state.voted):
            store["votes"].append(vote)
            st.session_state.voted = True
            st.rerun()

    st.markdown(f"**{len(store['votes'])} Stimmen insgesamt**")

    # Manual refresh for all
    if st.button("🔄 Seite aktualisieren"):
        st.rerun()

    # User feedback
    if st.session_state.voted:
        st.success("Danke! Dein Vote wurde gespeichert.")
    else:
        st.info("Bitte abstimmen, um das Ergebnis zu sehen.")

    # Chart only for moderator
    if store["votes"] and is_mod:
        df = pd.DataFrame({"Score": store["votes"]})
        bins = list(range(0, 101, 5))
        labels = [f"{b}-{b+4}" for b in bins[:-1]]
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
        st.metric(
            "Durchschnitt",
            f"{sum(store['votes'])/len(store['votes']):.1f}"
        )
