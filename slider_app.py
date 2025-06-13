import streamlit as st
import pandas as pd
import plotly.express as px

# ---------- Szenen ---------- #
SCENES = [
    "1) WhatsApp-Meme: „Leon = Forever Alone 😂“ – 23 Mitschüler lachen.",
    "2) Moodle-Antwort: „Frag doch Google, Schlafmütze!“ per DM.",
    "3) Screenshot aus Lisas Privat-Chat (Wort „Zicke“) wird herumgereicht.",
    "4) Lehrer teilt 11 Schüler in 2er-Teams – Maria bleibt allein zurück.",
    "5) Heimliches Streit-Video wird TikTok-Hit (1 500 Likes, „LOL loser“).",
    "6) Slack-Scherz: „Petra braucht bald Rampen für ihre Knie!“",
    "7) Insta-Story: Selfie von Lina → „Real Beauty Filter Off“.",
    "8) Nachbarschaft-Chat: Maya nennt Lärm, wird sofort „Karen“ genannt.",
    "9) Lernrunden-Einladungen – Tim wird systematisch ignoriert.",
    "10) Fake-PDF: „Tom durchgefallen“ – 200 Downloads, alle spotten."
]

# ---------- globaler Store ---------- #
store = st.session_state.setdefault("GLOBAL", {"idx": 0, "votes": []})

# ---------- Moderator-Passwort ---------- #
MOD_PW = "mod123"   # <-- eigenes PW hier ändern

# ---------- Titel ---------- #
st.title("🎯 GrenzCheck – wie schlimm findest du das?")

# ---------- Moderator-Login ---------- #
with st.sidebar:
    pw = st.text_input("Moderator-Passwort", type="password")
    if pw == MOD_PW:
        st.session_state["MOD"] = True
    is_mod = st.session_state.get("MOD", False)

# ---------- Szenenwahl (nur Mod) ---------- #
if is_mod:
    new_idx = st.sidebar.selectbox("Szene wählen", range(len(SCENES)), index=store["idx"])
    if st.sidebar.button("🚀 Szene übernehmen"):
        store["idx"], store["votes"] = new_idx, []
        st.session_state.pop("voted", None)
        st.rerun()
    if st.sidebar.button("🗑 Stimmen zurücksetzen"):
        store["votes"].clear()
        st.session_state.pop("voted", None)
        st.rerun()

# ---------- Szene anzeigen ---------- #
st.subheader("📝 Situation")
st.write(SCENES[store["idx"]])

# ---------- Abstimmen ---------- #
voted = st.session_state.get("voted", False)
col1, col2 = st.columns([4,1])
with col1:
    val = st.slider("0 = OK … 100 = Mobbing", 0, 100, 50, disabled=voted)
with col2:
    if st.button("✅ Abstimmen", disabled=voted):
        store["votes"].append(val)
        st.session_state["voted"] = True
        st.rerun()

st.markdown(f"**{len(store['votes'])} Stimmen**")

# ---------- Refresh-Button ---------- #
if st.button("🔄 Seite aktualisieren"):
    st.rerun()

# ---------- Feedback ---------- #
if st.session_state.get("voted"):
    st.success("Danke, dein Vote zählt!")

# ---------- Histogramm (nur Mod) ---------- #
if store["votes"] and is_mod:
    df = pd.DataFrame({"Score": store["votes"]})
    bins = list(range(0,101,5))
    df["Bin"] = pd.cut(df.Score, bins=bins, include_lowest=True)
    fig = px.histogram(df, x="Bin", color_discrete_sequence=["#3E7CB1"])
    fig.update_layout(yaxis=dict(dtick=1), xaxis_title="Schweregrad", yaxis_title="Stimmen")
    st.plotly_chart(fig, use_container_width=True)
    st.metric("Ø-Wert", f"{sum(store['votes'])/len(store['votes']):.1f} / 100")
