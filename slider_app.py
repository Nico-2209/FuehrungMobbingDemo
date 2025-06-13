import streamlit as st
import pandas as pd
import plotly.express as px

# ─────────────────────────
#  Szenen (10 polarisierende Fälle)
# ─────────────────────────
SCENES = [
    "1) WhatsApp-Meme: „Leon = Forever Alone 😂“ – 23 Mitschüler lachen.",
    "2) Moodle-Antwort: „Frag doch in der Google-Gruppe, Schlafmütze!“",
    "3) Screenshot aus Lisas Privat-Chat (sie nennt jmd. „Zicke“) wird geteilt.",
    "4) Lehrer bildet 2er-Teams für 11 Schüler → Maria bleibt allein übrig.",
    "5) Streit-Video auf TikTok – 1 500 Likes & Kommentare wie „LOL loser“.",
    "6) Slack-Scherz: „Petra braucht wohl bald einen Rollator …“",
    "7) Insta-Story: Ungefiltertes Selfie – Kommentar „Real Beauty Filter Off“.",
    "8) Nachbarschafts-Chat: Maya bittet um Ruhe ⇒ „Ok Karen 🙄“",
    "9) Lernrunden-Einladungen – Tim wird systematisch ignoriert.",
    "10) Fake-PDF: „Tom durchgefallen“, 200 Downloads, Spott folgt."
]

MOD_PASS = "mod123"          # ← hier eigenes Passwort setzen

# ─────────────────────────
#  Haupt-Funktion
# ─────────────────────────
def run_slider():
    # Globaler Speicher im Session-State
    store = st.session_state.setdefault("_GLOBAL", {"idx": 0, "votes": []})

    # -------- Moderator-Login --------
    with st.sidebar:
        st.subheader("🔐 Moderator-Login")
        if "is_mod" not in st.session_state:
            pw = st.text_input("Passwort", type="password")
            if pw == MOD_PASS:
                st.session_state.is_mod = True
                st.success("Moderator-Rechte aktiviert!")
        is_mod = st.session_state.get("is_mod", False)

    # -------- Szenenverwaltung (nur Mod) --------
    if is_mod:
        new_idx = st.sidebar.selectbox(
            "Szene wählen", range(len(SCENES)),
            index=store["idx"],
            format_func=lambda i: SCENES[i][:40] + "…"
        )
        if st.sidebar.button("🚀 Szene übernehmen"):
            store["idx"], store["votes"] = new_idx, []
            st.session_state.pop("voted", None)
            st.rerun()

        if st.sidebar.button("🗑 Stimmen löschen"):
            store["votes"].clear()
            st.session_state.pop("voted", None)
            st.rerun()

    # -------- Titel & Szene --------
    st.title("🎯 GrenzCheck – wie schlimm findest du das?")
    st.subheader("📝 Situation")
    st.write(SCENES[store["idx"]])

    # -------- Abstimm-Status für diesen Tab --------
    voted = st.session_state.get("voted", False)
    if st.session_state.get("scene_loaded") != store["idx"]:
        st.session_state.voted = False
        st.session_state.scene_loaded = store["idx"]
        voted = False

    # -------- Abstimmen --------
    c1, c2 = st.columns([4, 1])
    with c1:
        val = st.slider("0 = OK … 100 = klares Mobbing", 0, 100, 50, disabled=voted)
    with c2:
        if st.button("✅ Abstimmen", disabled=voted):
            store["votes"].append(val)
            st.session_state.voted = True
            st.rerun()

    st.markdown(f"**{len(store['votes'])} Stimmen**")

    # Refresh für alle
    if st.button("🔄 Aktualisieren"):
        st.rerun()

    if st.session_state.get("voted"):
        st.success("Danke, dein Vote zählt!")

    # -------- Histogramm (nur Mod) --------
    if store["votes"] and is_mod:
        df = pd.DataFrame({"Score": store["votes"]})
        bins = list(range(0, 101, 5))
        labels = [f"{b}-{b+4}" for b in bins[:-1]]
        df["Bin"] = pd.cut(df.Score, bins=bins, labels=labels, include_lowest=True)

        fig = px.histogram(
            df, x="Bin",
            category_orders={"Bin": labels},
            color_discrete_sequence=["#3E7CB1"]
        )
        fig.update_layout(
            title="Verteilung der Stimmen",
            xaxis_title="Schweregrad",
            yaxis_title="Anzahl Stimmen",
            yaxis=dict(dtick=1)      # nur ganze Zahlen
        )
        st.plotly_chart(fig, use_container_width=True)
        st.metric("Ø-Wert", f"{sum(store['votes'])/len(store['votes']):.1f} / 100")
