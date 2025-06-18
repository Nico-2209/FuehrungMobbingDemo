# slider_app.py
import streamlit as st
import pandas as pd
import plotly.express as px

# ─────────────────────────────────────────────────────────────
# 1) Sechs ambivalente Szenen für die Abstimmung
# ─────────────────────────────────────────────────────────────
SCENES = [
    # 1) Gruppen-Übrigbleiber
    "Der Dozent teilt 11 Studierende in Zweiergruppen ein. Am Ende bleibt Sophie übrig. "
    "Er sagt locker: »Mach einfach die Zusammenfassung für alle, ja?« Die Gruppe lacht; Sophie schweigt.",

    # 2) WhatsApp-Kommentar zum Outfit
    "Max postet ein Party-Selfie in die Kursgruppe. Kurz danach teilt jemand dasselbe Bild mit dem Spruch: "
    "»Hast wohl den Dresscode ›Altkleider‹ gewählt 😂.« Das Posting bekommt 15 Likes und drei besorgte Nachfragen.",

    # 3) Mikro-Kommentar im Livestream
    "Während Lisas Online-Präsentation rauscht ihr Ton. Im Zoom-Chat schreibt jemand öffentlich: "
    "»Bitte ein vernünftiges Mikro benutzen! 🙄« Der Satz bleibt für alle sichtbar, bis sie fertig ist.",

    # 4) Code-Vorwurf mitten im Meeting
    "In einem Projekt-Zoom ruft plötzlich ein Teammitglied: »Stopp, Sam hat den Algorithmus 1-zu-1 von GitHub geklaut!« "
    "Es entsteht eine Diskussion – einige glauben es sofort, andere verteidigen Sam.",

    # 5) Campus-Meme über Ben
    "Auf der anonymen Uni-Meme-Seite erscheint ein Foto von Ben, wie er in der Vorlesung kurz einnickt. "
    "Überschrift: »Wer Party macht, muss auch schlafen 😴.« Viele finden’s lustig – Ben sieht das erst am nächsten Tag.",

    # 6) Flirt-Gerücht über Anna
    "Im Insta-Account »CampusConfessions« steht: »Anna hat Statistik nur bestanden, weil sie den Tutor angeflirtet hat 😉.« "
    "Der Post macht die Runde; einige glauben es, andere verteidigen Anna."
]

# ─────────────────────────────────────────────────────────────
# 2) Globaler Server-weiter Speicher
#     idx   : aktuellen Szenen-Index
#     votes : Liste der abgegebenen Scores
#     reset : Zähler für Vote-Resets (damit Tabs ihr Flag erkennen)
# ─────────────────────────────────────────────────────────────
store = st.session_state.setdefault("_GLOBAL", {"idx": 0, "votes": [], "reset": 0})

# ─────────────────────────────────────────────────────────────
# 3) Passwort für Moderator
# ─────────────────────────────────────────────────────────────
MOD_PASS = "mod123"  # ← hier dein Wunsch­passwort einsetzen


# ─────────────────────────────────────────────────────────────
# 4) Hauptfunktion
# ─────────────────────────────────────────────────────────────
def run_slider():
    # ── 4.1 Sidebar-Login ───────────────────────────────────
    with st.sidebar:
        st.subheader("🔐 Moderator-Login")
        if "is_mod" not in st.session_state:
            if st.text_input("Passwort", type="password") == MOD_PASS:
                st.session_state.is_mod = True
                st.success("Moderator-Modus aktiviert")
        is_mod = st.session_state.get("is_mod", False)

    # ── 4.2 Szenen-Verwaltung (nur Mod) ─────────────────────
    if is_mod:
        new_idx = st.sidebar.selectbox(
            "Szene wählen", range(len(SCENES)),
            index=store["idx"],
            format_func=lambda i: SCENES[i][:45] + "…"
        )
        if st.sidebar.button("🚀 Übernehmen"):
            store["idx"], store["votes"] = new_idx, []
            st.session_state.pop("voted", None)
            st.rerun()

        # Votes zurücksetzen & globalen Reset-Counter erhöhen
        if st.sidebar.button("🗑 Votes reset"):
            store["votes"].clear()
            store["reset"] += 1
            st.rerun()

    # ── 4.3 Szene anzeigen ──────────────────────────────────
    st.title("🎯 GrenzCheck – Wie schlimm findest du das?")
    st.write(f"### 📝 Situation {store['idx'] + 1}/6")
    st.write(SCENES[store["idx"]])

    # ── 4.4 Pro Tab: Vote-Flag an Szene & Reset koppeln ─────
    if (st.session_state.get("scene_seen") != store["idx"]) or (
            st.session_state.get("reset_seen") != store["reset"]):
        st.session_state.voted = False
        st.session_state.scene_seen = store["idx"]
        st.session_state.reset_seen = store["reset"]

    voted = st.session_state.get("voted", False)

    # ── 4.5 Abstimmen ───────────────────────────────────────
    col_val, col_btn = st.columns([4, 1])
    with col_val:
        score = st.slider("0 = OK … 100 = klares Mobbing",
                          0, 100, 50, disabled=voted)
    with col_btn:
        if st.button("✅ Abstimmen", disabled=voted):
            store["votes"].append(score)
            st.session_state.voted = True
            st.rerun()

    st.markdown(f"**{len(store['votes'])} Stimmen abgegeben**")
    if st.button("🔄 Aktualisieren"):
        st.rerun()
    if voted:
        st.success("Danke! Dein Vote wurde gespeichert.")

    # ── 4.6 Histogramm (nur Mod) ────────────────────────────
    if store["votes"] and is_mod:
        df = pd.DataFrame({"Score": store["votes"]})
        edges = [0, 5] + list(range(10, 101, 5))  # 0-5, 5-10, …, 95-100
        labels = [f"{edges[i]}-{edges[i + 1]}" for i in range(len(edges) - 1)]
        df["Bin"] = pd.cut(df.Score, bins=edges, labels=labels,
                           include_lowest=True, right=True)

        fig = px.histogram(df, x="Bin",
                           category_orders={"Bin": labels},
                           color_discrete_sequence=["#3E7CB1"])
        fig.update_layout(
            title="Verteilung der Stimmen",
            xaxis_title="Schweregrad",
            yaxis_title="Anzahl Stimmen",
            yaxis=dict(dtick=1)  # ganze Zahlen
        )
        st.plotly_chart(fig, use_container_width=True)
