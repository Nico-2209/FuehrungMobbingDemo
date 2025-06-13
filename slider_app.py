import streamlit as st
import pandas as pd
import plotly.express as px

# ---------- 1.  Szenen ---------- #
RAW_SCENES = [
    # 1) Grenzübertritt vs. Humor
    "Die Klasse plant im WhatsApp-Chat einen Ausflug. Leon wird nicht eingeladen. Später erscheint das Meme »Leon = Forever Alone 😂«. 23 Mitschüler reagieren mit 🤣.",
    # 2) Ironie vs. Verletzung
    "Chiara fragt im Moodle nach einer Formel. Antworten: »Frag doch in der Google-Gruppe«. Abends DM: »Schlafmütze, verschlafen?«",
    # 3) Privates öffentlich gemacht
    "Ein Screenshot aus Lisas Privat-Chat (sie nennt jmd. »Zicke«) wird im Uni-Chat geteilt. Alle lachen.",
    # 4) Ausgrenzung durch Gruppeneinteilung
    "Der Lehrer teilt 11 Schüler in Zweiergruppen – Maria bleibt allein übrig. Er »vergisst« sie.",
    # 5) Viral-Shitstorm
    "Ein heimlicher Streit wird als TikTok gepostet. 1 500 Likes & Kommentare wie »LOL loser« binnen Stunden.",
    # 6) Alterswitz vs. Respekt
    "Im Büro muss Petra täglich fünf Treppen steigen. Slack-Scherz: »Petra braucht bald eine Rollator-Auffahrt!«",
    # 7) Schönheits-Diktat
    "In der Insta-Story taucht Linas ungefiltertes Selfie auf: »Real-Beauty filter off« – sie fühlt sich bloßgestellt.",
    # 8) “Karen”-Label
    "Maya bittet in der Nachbarschafts-Gruppe um Ruhe nach 22 Uhr. Sofort wird sie als »Karen« betitelt & verlacht.",
    # 9) Study-Group-Exklusion
    "Bei jeder Lernrunde werden die gleichen 5 Leute eingeladen. Tim (gleicher Kurs) bleibt außen vor – ohne Grund.",
    # 10) Fake-News-PDF
    "Gefälschtes PDF behauptet, Tom sei durchgefallen. 200 Downloads; Mitschüler spotten vor ihm."
]

# ---------- 2.  Globaler Store ---------- #
@st.cache_resource
def get_store():
    return {"scene_idx": 0, "votes": []}

store = get_store()

# ---------- 3.  Mod-Passwort ---------- #
PASSWORD = "mod123"        # → hier eigenes Passwort setzen

st.header("🎯 GrenzCheck – wie schlimm findest du das?")

# ---------- 4.  Moderator-Login ---------- #
with st.sidebar:
    st.subheader("🔑 Moderator-Login")
    pw_input = st.text_input("Passwort", type="password")
    is_mod = st.session_state.get("is_mod", False)
    if pw_input == PASSWORD:
        st.session_state.is_mod = True
        is_mod = True
    if is_mod:
        st.success("Moderator-Modus aktiviert")

# ---------- 5.  Szenen-Wechsel (nur Mod) ---------- #
if is_mod:
    new_idx = st.sidebar.selectbox(
        "Szene wählen",
        options=list(range(len(RAW_SCENES))),
        index=store["scene_idx"],
        format_func=lambda i: RAW_SCENES[i][:40] + "…"
    )
    if st.sidebar.button("🚀 Szene übernehmen"):
        store["scene_idx"] = new_idx
        store["votes"].clear()
        st.session_state.voted = False
        st.experimental_rerun()

    if st.sidebar.button("🗑 Stimmen zurücksetzen"):
        store["votes"].clear()
        st.session_state.voted = False
        st.experimental_rerun()

# ---------- 6.  Session-Flags ---------- #
if "voted" not in st.session_state:
    st.session_state.voted = False
if "loaded_idx" not in st.session_state:
    st.session_state.loaded_idx = store["scene_idx"]

# ---------- 7.  Szene anzeigen ---------- #
idx = store["scene_idx"]
st.subheader("📝 Situation")
st.write(RAW_SCENES[idx])

if st.session_state.loaded_idx != idx:
    st.session_state.voted = False
    st.session_state.loaded_idx = idx

# ---------- 8.  Voting ---------- #
col1, col2 = st.columns([4, 1])
with col1:
    rating = st.slider(
        "Deine Einschätzung (0 = OK, 100 = klar Mobbing)",
        0, 100, 50, step=1,
        disabled=st.session_state.voted
    )
with col2:
    if st.button("✅ Abstimmen", disabled=st.session_state.voted):
        store["votes"].append(rating)
        st.session_state.voted = True
        st.experimental_rerun()

st.markdown(f"**{len(store['votes'])} Stimmen abgegeben**")

# ---------- 9.  Refresh-Button ---------- #
if st.button("🔄 Aktualisieren"):
    st.experimental_rerun()

# ---------- 10. Feedback ---------- #
if st.session_state.voted:
    st.success("Danke! Dein Vote zählt ✨")

# ---------- 11. Histogramm (nur Mod) ---------- #
if store["votes"] and is_mod:
    df = pd.DataFrame({"Score": store["votes"]})
    bins = list(range(0, 101, 5))
    labels = [f"{b}-{b+4}" for b in bins[:-1]]
    df["Bin"] = pd.cut(df["Score"], bins=bins, labels=labels, include_lowest=True)

    fig = px.histogram(
        df, x="Bin",
        category_orders={"Bin": labels},
        color_discrete_sequence=["#3E7CB1"]
    )
    fig.update_layout(
        title="Verteilung der Stimmen",
        xaxis_title="Schweregrad",
        yaxis_title="Anzahl Stimmen",
        yaxis=dict(dtick=1)  # nur ganze Zahlen
    )
    st.plotly_chart(fig, use_container_width=True)
    st.metric("Durchschnitt", f"{sum(store['votes'])/len(store['votes']):.1f}/100")
