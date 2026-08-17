from langchain_huggingface import HuggingFaceEmbeddings

_encoder = None


def get_encoder() -> HuggingFaceEmbeddings:
    global _encoder
    if _encoder is None:
        _encoder = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-mpnet-base-v2",
            encode_kwargs={"normalize_embeddings": True},
        )
    return _encoder


def embed_text(text: str) -> list:
    return get_encoder().embed_query(text)
