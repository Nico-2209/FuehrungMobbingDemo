# slider_app.py   (nur globale STORE, keine experiment-APIs nötig)
import streamlit as st
import random, pandas as pd, plotly.express as px

# ------------------ 1. Gemeinsamer Speicher ------------------
STORE = {"scene": None, "votes": []}

# ------------------ 2. Realistischere Beispiele ------------------
EXAMPLES = [
    "Im Klassenchat: »Junge, du stinkst – setz dich woanders!«",
    "Screenshot vom schlechten Zeugnis wird in die Gruppe gestellt.",
    "Im Gaming-Voicechat brüllt jemand: »Du Hurensohn, lern spielen!«",
    "Auf Insta kursiert ein Meme, das dein Gesicht als ‚Fail‘ zeigt.",
    "In der Mensa ruft jemand laut: »Fette Sau, lass das Dessert stehen!«",
    "Beim Sport wird dir ständig der Ball weggekickt und gelacht.",
    "Lehrkraft nennt dich vor allen nur noch „Professor Schlaumeier“."
]

# ------------------ 3. Haupt-Funktion ------------------
def run_slider():
    st.header("GrenzCheck 🔍")

    # (a) Szene festlegen
    if STORE["scene"] is None:
        STORE["scene"] = random.choice(EXAMPLES)

    # (b) Moderator-Checkbox (nur lokal pro Gerät)
    is_mod = st.sidebar.checkbox("Moderator-Ansicht", False)

    # Moderator-Optionen
    if is_mod:
        STORE["scene"] = st.sidebar.selectbox(
            "Beispiel wählen", EXAMPLES,
            index=EXAMPLES.index(STORE["scene"])
        )
        if st.sidebar.button("Stimmen zurücksetzen"):
            STORE["votes"].clear()

    # (c) Szene anzeigen
    st.subheader(STORE["scene"])

    # (d) Abstimmen
    cols = st.columns([3, 1])
    with cols[0]:
        vote = st.slider(
            "Wie schlimm findest du das?",
            0, 100, 50, step=1,
            help="0 = alles okay · 100 = klares Mobbing"
        )
    with cols[1]:
        if st.button("✅ Abstimmen"):
            STORE["votes"].append(vote)
            st.rerun()   # alle Tabs sofort aktualisieren

    votes = STORE["votes"]
    st.write(f"**{len(votes)} Stimmen**")

    # ------------------ 4. Ergebnisse ------------------
    if votes and is_mod:        # 👉 nur Moderator sieht Diagramm
        df = pd.DataFrame({"Score": votes})

        # Bins: 0–4, 5–9, …, 95–100
        bins = list(range(0, 101, 5))
        labels = [f"{b}-{b+4}" for b in bins[:-2]] + ["95-100"]
        df["Bin"] = pd.cut(df["Score"], bins=bins, labels=labels,
                           right=True, include_lowest=True)

        chart = px.histogram(
            df, x="Bin",
            category_orders={"Bin": labels},
            labels={"Bin": "Schweregrad"},
            title="Verteilung der Stimmen",
            color_discrete_sequence=["#3E7CB1"]
        )
        chart.update_layout(
            yaxis_title="Anzahl", bargap=0.05,
            xaxis_tickangle=-45, xaxis_tickfont_size=11
        )
        st.plotly_chart(chart, use_container_width=True)
        st.metric("Durchschnitt", f"{sum(votes)/len(votes):.1f} / 100")

    elif not votes:
        st.info("Noch keine Stimmen abgegeben.")
    else:
        st.success("Danke fürs Abstimmen! Das Ergebnis sieht nur der Moderator.")
