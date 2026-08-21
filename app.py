import streamlit as st

from gemini_client import describe_image_vibe
from search import search


@st.cache_resource
def get_used_ips() -> set:
    """Shared across all users of this running server process. Resets on app restart."""
    return set()


def get_client_ip() -> str:
    """Best-effort client IP via Streamlit's internal (undocumented) header access."""
    try:
        from streamlit.web.server.websocket_headers import _get_websocket_headers

        headers = _get_websocket_headers()
        forwarded = headers.get("X-Forwarded-For")
        return forwarded.split(",")[0].strip() if forwarded else "unknown"
    except Exception:
        return "unknown"


st.set_page_config(page_title="vibeMax", page_icon="🎵")
st.title("vibeMax")
st.caption("Search music by vibe, not genre.")

mode = st.radio("Search by", ["Vibe phrase", "Song name", "Image"], horizontal=True)
as_song = mode == "Song name"

query = None
image_file = None
if mode == "Image":
    image_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png", "webp"])
else:
    query = st.text_input("Song name" if as_song else "What are you feeling?")

energy_choice = st.selectbox("Energy filter (optional)", ["Any", "low", "medium", "high"])
energy_filter = None if energy_choice == "Any" else energy_choice

ready = bool(query) or image_file is not None

if image_file is not None and st.session_state.get("image_used"):
    st.warning("You've already used your image upload for this session.")
    ready = False

if st.button("Search") and ready:
    spinner_text = "Building this song's vibe profile..." if as_song else "Searching..."
    with st.spinner(spinner_text):
        try:
            if image_file is not None:
                client_ip = get_client_ip()
                if client_ip != "unknown" and client_ip in get_used_ips():
                    raise ValueError("This IP has already used its image upload.")

                query = describe_image_vibe(image_file.getvalue(), mime_type=image_file.type)
                st.caption(f"Read from image: *{query}*")

                st.session_state["image_used"] = True
                get_used_ips().add(client_ip)

            results = search(query, as_song=as_song, top_k=5, energy=energy_filter)
        except Exception as e:
            st.error(f"Something went wrong: {e}")
            results = None

    if results is not None and not results:
        st.warning("No matches found.")
    elif results:
        for match in results:
            meta = match.get("metadata", {})
            with st.expander(f"🎵 **{meta.get('name')}** — {meta.get('artist')}"):
                if meta.get("album_art"):
                    st.image(meta["album_art"], width=150)
                st.caption(f"{meta.get('release_year')}")
                vibe_match = max(0, min(100, round(match["score"] * 100)))
                st.progress(vibe_match / 100, text=f"Vibe match: {vibe_match}%")
                st.write(meta.get("description"))
                st.markdown(
                    f"**Mood:** {meta.get('mood')} &nbsp;&nbsp; "
                    f"**Energy:** {meta.get('energy')} &nbsp;&nbsp; "
                    f"**Era feel:** {meta.get('era_feel')}"
                )
                st.markdown(f"**Best for:** {meta.get('best_for')}")
