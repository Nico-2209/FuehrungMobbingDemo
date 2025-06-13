import streamlit as st
import pandas as pd
import plotly.express as px

# ─── 1. Szenen ──────────────────────────────────────────────────────────────
SCENES = [
    # 1
    "Die Klasse plant über WhatsApp einen Überraschungsausflug. Alle werden in die Gruppe eingeladen – außer Leon. "
    "Als er später nachfragt, fluten Mitschüler den Chat mit dem Sticker „Forever Alone 😂“.",
    # 2
    "Chiara stellt im Moodle-Forum eine Frage zu Integral­rechnung. Mehrere Antworten lauten nur „RTFM 📚“. "
    "Ein Screenshot ihrer Frage taucht in einer Meme-Gruppe auf, Caption: „Sleeping Beauty ist wieder wach.“",
    # 3
    "Lisa nennt in einem privaten Chat eine Mitschülerin „Zicke“. Ein Screenshot wird ohne Zustimmung in die Kurs-Gruppe gepostet: "
    "„🔍 Fake Friend spotted!“ Die Hälfte lacht, die andere schweigt.",
    # 4
    "Der Lehrer bildet aus 11 Schülern 5 Zweier­gruppen – Maria bleibt übrig. Er sagt nur: "
    "„Wir regeln das später.“ Die Gruppen starten, Maria sitzt allein am Tisch.",
    # 5
    "Ein hitziges Wort­gefecht auf dem Gang wird gefilmt und als TikTok hochgeladen. "
    "Dazu startet ein Poll „Team A oder B?“; nach zwei Stunden über 2 000 Stimmen und Kommentare wie „LOL loser“.",
    # 6
    "Petra (55) keucht nach fünf Stockwerken ins Büro. Im Slack chattet ein Kollege: "
    "„GIF von Oma mit Rollator – Petra next year? 😜“. HR bekommt davon nichts mit.",
    # 7
    "Eine Freundin postet Linas ungefiltertes Selfie in der Instagram-Story mit dem Sticker "
    "„Real Beauty Filter OFF 💅“. Später startet sie eine Umfrage „Glow up nötig?“. Lina sieht 68 % Ja.",
    # 8
    "In der Nachbarschafts-WhatsApp bittet Maya um Ruhe nach 22 Uhr. Antworten: "
    "Memes „OK Karen“, „Boomer Alert 🚨“. Manche Nachbarn reagieren mit 😂.",
    # 9
    "Jedes Wochenende verschickt die Kurs­leitung Zoom-Links für eine Lerngruppe – "
    "Tim bekommt sie nie. Auf Nachfrage: „Room war voll, vielleicht nächste Woche.“",
    #10
    "Ein PDF mit angeblicher Noten­liste kursiert: Tom steht allein mit „F“. "
    "Das Fake-Dokument landet in 200 Downloads, Mitschüler fragen: „Musst du nach­schreiben? 😬“"
]

# ─── 2. globaler Store ──────────────────────────────────────────────────────
store = st.session_state.setdefault("_GLOBAL", {"idx": 0, "votes": []})

# ─── 3. Passwort für Moderator ──────────────────────────────────────────────
MOD_PASS = "mod123"          # hier ändern

def run_slider():
    # ███ Sidebar – Login
    with st.sidebar:
        st.subheader("🔐 Moderator-Login")
        if "is_mod" not in st.session_state:
            pw = st.text_input("Passwort", type="password")
            if pw == MOD_PASS:
                st.session_state.is_mod = True
                st.success("Moderator-Modus aktiviert")
        is_mod = st.session_state.get("is_mod", False)

    # ███ Szenensteuerung (nur Mod)
    if is_mod:
        new_idx = st.sidebar.selectbox(
            "Szene wählen", range(len(SCENES)),
            index=store["idx"],
            format_func=lambda i: SCENES[i][:60] + "…"
        )
        if st.sidebar.button("🚀 Übernehmen"):
            store["idx"], store["votes"] = new_idx, []
            st.session_state.pop("voted", None)
            st.rerun()
        if st.sidebar.button("🗑 Votes reset"):
            store["votes"].clear()
            st.session_state.pop("voted", None)
            st.rerun()

    # ███ Titel & Szene
    st.title("🎯 GrenzCheck – Wie schlimm findest du das?")
    st.write(f"### 📝 Situation {store['idx']+1}/10")
    st.write(SCENES[store["idx"]])

    # ███ Abstimm-Status für diesen Tab
    voted = st.session_state.get("voted", False)
    if st.session_state.get("scene_loaded") != store["idx"]:
        st.session_state.voted = False
        st.session_state.scene_loaded = store["idx"]
        voted = False

    # ███ Abstimmen
    col_vote, col_btn = st.columns([4,1])
    with col_vote:
        val = st.slider("0 = OK … 100 = klares Mobbing", 0, 100, 50, disabled=voted)
    with col_btn:
        if st.button("✅ Abstimmen", disabled=voted):
            store["votes"].append(val)
            st.session_state.voted = True
            st.rerun()

    st.markdown(f"**{len(store['votes'])} Stimmen**")

    if st.button("🔄 Aktualisieren"):
        st.rerun()

    if st.session_state.get("voted"):
        st.success("Danke, dein Vote wurde gespeichert!")

    # ███ Histogramm – nur Mod
    if store["votes"] and is_mod:
        df = pd.DataFrame({"Score": store["votes"]})
        bins = list(range(0, 101, 5))
        labels = [f"{b}-{b+4}" for b in bins[:-1]]
        df["Bin"] = pd.cut(df.Score, bins=bins, labels=labels, include_lowest=True)

        fig = px.histogram(
            df, x="Bin", color_discrete_sequence=["#3E7CB1"],
            category_orders={"Bin": labels}
        )
        fig.update_layout(
            title="Verteilung der Stimmen",
            xaxis_title="Schweregrad", yaxis=dict(dtick=1), yaxis_title="Anzahl"
        )
        st.plotly_chart(fig, use_container_width=True)
