# slider_app.py  – komplette Version
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import random, pandas as pd, plotly.express as px

# ---------- 1. Gemeinsamer Speicher ----------
STORE = {"scene_raw": None, "votes": []}

# ---------- 2. Komplexe Stories ----------
RAW_SCENES = [
    # 1 — WhatsApp + Meme
    """Die Klasse plant im WhatsApp-Chat einen Geburtstagsausflug. 
    Alle schreiben begeistert – nur Leon wird nicht eingeladen. 
    Später postet jemand ein Meme: „Leon = Forever Alone 😂“. 
    23 Mitschüler reagieren mit dem Lach-Emoji.""",

    # 2 — Uni-Forum + DM-Beleidigung
    """In Moodle fragt Chiara (1. Semester) nach einer Formel. 
    Mehrere antworten ironisch: „Googeln hilft 😉“. 
    Ein Thread mit 40 Upvotes macht sich lustig. 
    Abends bekommt sie eine Direktnachricht: „Erst nachdenken, Brainlet!“""",

    # 3 — Voice-Chat + Sexismus
    """Im Valorant-Team-Discord ruft einer: 
    „Halt die Klappe, Mädel, nimm Healer und kusch!“ 
    Als sie protestiert, droht er: „Doxx dich gleich auf Twitter“.""",

    # 4 — Tiktok-Video
    """In der Schulkantine wird heimlich ein Video von Tom (übergewichtig) 
    beim Essen aufgenommen. Auf TikTok landet es mit #WhaleWatch. 
    12 000 Views, viele Kommentare wie „Diät gefällig?“.""",

    # 5 — Projekt-Ausgrenzung
    """Beim Gruppen-Referat teilen sich drei Studenten ein Google-Doc 
    und laden Sarah nicht ein. Sie soll nur eine „Deko-Folie“ erstellen. 
    Ihre Ideen werden danach öffentlich zerrissen.""",

    # 6 — Firmen-Slack
    """Im Firmen-Slack postet jemand ein Party-Foto von Max, betrunken. 
    Kollegen kommentieren: „Quality Assurance 🍻“. 
    Das Bild bleibt im Channel angepinnt."""
]

# ---------- 3. Dummy-Schä​tzfunktion (fixe Tabelle) ----------
APP_ESTIMATE = {
    0: 75, 1: 60, 2: 85, 3: 90, 4: 65, 5: 55
}

# ---------- 4. Hauptfunktion ----------
def run_slider():
    st.header("GrenzCheck 🔍")

    # Szene initialisieren
    if STORE["scene_raw"] is None:
        idx = random.randrange(len(RAW_SCENES))
        STORE["scene_raw"] = RAW_SCENES[idx]
        STORE["scene_idx"] = idx

    # Session-State pro Tab
    st.session_state.setdefault("voted", False)
    st.session_state.setdefault("local_idx", STORE["scene_idx"])

    # Auto-Refresh bei Moderator
    is_mod = st.sidebar.checkbox("Moderator-Ansicht", False)
    if is_mod:
        st_autorefresh(interval=2000, key="refresh")
        new_idx = st.sidebar.selectbox(
            "Story wählen", range(len(RAW_SCENES)),
            index=STORE["scene_idx"],
            format_func=lambda i: RAW_SCENES[i][:40] + " …"
        )
        if new_idx != STORE["scene_idx"]:
            STORE["scene_raw"] = RAW_SCENES[new_idx]
            STORE["scene_idx"] = new_idx
            STORE["votes"].clear()
            st.session_state.voted = False

    # Reset-Knopf
    if is_mod and st.sidebar.button("Stimmen zurücksetzen"):
        STORE["votes"].clear()
        st.session_state.voted = False

    # Zeige Story (Teaser + Expander)
    st.subheader("📝 Situation:")
    st.markdown(f"**{STORE['scene_raw'][:80]}…**")
    with st.expander("Gesamte Geschichte lesen"):
        st.write(STORE["scene_raw"])

    # Abstimm-UI
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
            st.rerun()

    st.write(f"**{len(STORE['votes'])} Stimmen**")

    # Ergebnis- / Feedback-Bereich
    if st.session_state.voted:
        est = APP_ESTIMATE.get(STORE["scene_idx"], 70)
        st.info(f"📱 *Eine externe App würde diese Szene auf **{est}/100** einstufen.*")
        st.success("Danke! Deine Bewertung wurde gespeichert.")
    else:
        st.info("Stimme ab, um dein Ergebnis zu sehen!")

    # Diagramm nur für Moderator
    if STORE["votes"] and is_mod:
        df = pd.DataFrame({"Score": STORE["votes"]})
        bins = list(range(0, 101, 5))
        labels = [f"{b}-{b+4}" for b in bins[:-2]] + ["95-100"]
        df["Bin"] = pd.cut(df["Score"], bins=bins, labels=labels,
                           right=True, include_lowest=True)
        chart = px.histogram(
            df, x="Bin", category_orders={"Bin": labels},
            labels={"Bin": "Schweregrad"},
            color_discrete_sequence=["#3E7CB1"]
        )
        chart.update_layout(yaxis_title="Anzahl", bargap=0.05,
                            xaxis_tickangle=-45, xaxis_tickfont_size=11)
        st.plotly_chart(chart, use_container_width=True)
        st.metric("Durchschnitt", f"{sum(STORE['votes'])/len(STORE['votes']):.1f} / 100")
