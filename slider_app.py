import streamlit as st
import pandas as pd
import plotly.express as px

# ─── 1. Szenen ──────────────────────────────────────────────────────────────
SCENES = [
    "Die Klasse plant über WhatsApp einen Überraschungsausflug. Leon bleibt außen vor …",
    "Chiara fragt im Moodle nach Integralrechnen. Antwort-Meme: „RTFM 📚“ …",
    "Screenshot aus Lisas Privat-Chat (sie nennt jmd. „Zicke“) landet im Kurs-Chat …",
    "Lehrer stellt 11 Schüler in Zweierteams – Maria bleibt allein zurück …",
    "Streit-Video wird TikTok-Hit mit 1 500 Likes, Kommentar „LOL loser“ …",
    "Slack-Scherz: „Petra braucht wohl bald einen Rollator …“ …",
    "Insta-Story: Ungefiltertes Selfie + Sticker „Real Beauty Filter OFF“ …",
    "Nachbarschafts-Chat: Maya bittet um Ruhe → Memes „Okay Karen“ …",
    "Lernrunden-Links gehen immer an die gleichen 5 Personen, Tim nie …",
    "Fake-PDF: „Tom hat F-Note“ – 200 Downloads, Spott folgt …"
]

# ─── 2. Globaler Store ──────────────────────────────────────────────────────
store = st.session_state.setdefault("_GLOBAL", {"idx": 0, "votes": []})

# ─── 3. Passwort für Moderator ──────────────────────────────────────────────
MOD_PASS = "mod123"  # hier anpassen

# ─── Hauptfunktion ─────────────────────────────────────────────────────────
def run_slider():
    # Sidebar-Login
    with st.sidebar:
        st.subheader("🔐 Moderator-Login")
        if "is_mod" not in st.session_state:
            if st.text_input("Passwort", type="password") == MOD_PASS:
                st.session_state.is_mod = True
                st.success("Moderator-Modus aktiviert")
        is_mod = st.session_state.get("is_mod", False)

    # Szenenwahl (nur Mod)
    if is_mod:
        new_idx = st.sidebar.selectbox(
            "Szene wählen", range(len(SCENES)),
            index=store["idx"],
            format_func=lambda i: SCENES[i][:50] + "…"
        )
        if st.sidebar.button("🚀 Übernehmen"):
            store["idx"], store["votes"] = new_idx, []
            st.session_state.pop("voted", None)
            st.rerun()
        if st.sidebar.button("🗑 Votes reset"):
            store["votes"].clear()
            st.session_state.pop("voted", None)
            st.rerun()

    # Szene anzeigen
    st.title("🎯 GrenzCheck – Wie schlimm findest du das?")
    st.write(f"### 📝 Situation {store['idx']+1}/10")
    st.write(SCENES[store["idx"]])

    # Abstimmen
    voted = st.session_state.get("voted", False)
    col_val, col_btn = st.columns([4, 1])
    with col_val:
        score = st.slider("0 = OK … 100 = klares Mobbing", 0, 100, 50, disabled=voted)
    with col_btn:
        if st.button("✅ Abstimmen", disabled=voted):
            store["votes"].append(score)
            st.session_state.voted = True
            st.rerun()

    st.markdown(f"**{len(store['votes'])} Stimmen**")
    if st.button("🔄 Aktualisieren"): st.rerun()
    if st.session_state.get("voted"): st.success("Danke! Dein Vote wurde gespeichert.")

    # Histogramm (nur Mod)
    if store["votes"] and is_mod:
        df = pd.DataFrame({"Score": store["votes"]})

        # Bucket-Schema: 0-5, 5-10, …, 95-100
        edges  = list(range(0, 101, 5))           # 0,5,10,…,100
        labels = [f"{edges[i]}-{edges[i+1]}" for i in range(len(edges)-1)]
        df["Bin"] = pd.cut(
            df.Score, bins=edges, labels=labels,
            include_lowest=True, right=True      # 5 gehört zum ersten Bucket
        )

        fig = px.histogram(
            df, x="Bin",
            category_orders={"Bin": labels},
            color_discrete_sequence=["#3E7CB1"]
        )
        fig.update_layout(
            title="Verteilung der Stimmen",
            xaxis_title="Schweregrad",
            yaxis_title="Anzahl",
            yaxis=dict(dtick=1)                 # ganze Zahlen
        )
        st.plotly_chart(fig, use_container_width=True)
