import streamlit as st

from search import search

st.set_page_config(page_title="vibeMax", page_icon="🎵")
st.title("vibeMax")
st.caption("Search music by vibe, not genre.")

mode = st.radio("Search by", ["Vibe phrase", "Song name"], horizontal=True)
as_song = mode == "Song name"
query = st.text_input("Song name" if as_song else "What are you feeling?")

energy_choice = st.selectbox("Energy filter (optional)", ["Any", "low", "medium", "high"])
energy_filter = None if energy_choice == "Any" else energy_choice

if st.button("Search") and query:
    spinner_text = "Building this song's vibe profile..." if as_song else "Searching..."
    with st.spinner(spinner_text):
        try:
            results = search(query, as_song=as_song, top_k=10, energy=energy_filter)
        except Exception as e:
            st.error(f"Something went wrong: {e}")
            results = None

    if results is not None and not results:
        st.warning("No matches found.")
    elif results:
        for match in results:
            meta = match.get("metadata", {})
            with st.container(border=True):
                st.subheader(f"{meta.get('name')} — {meta.get('artist')} ({meta.get('release_year')})")
                st.caption(f"match score: {match['score']:.2f}")
                st.write(meta.get("description"))
                st.markdown(
                    f"**Mood:** {meta.get('mood')} &nbsp;&nbsp; "
                    f"**Energy:** {meta.get('energy')} &nbsp;&nbsp; "
                    f"**Era feel:** {meta.get('era_feel')}"
                )
                st.markdown(f"**Best for:** {meta.get('best_for')}")
