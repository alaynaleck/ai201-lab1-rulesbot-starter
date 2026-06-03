from groq import Groq
from config import GROQ_API_KEY, LLM_MODEL

_client = Groq(api_key=GROQ_API_KEY)


# Unchanging policy: persona + grounding, cross-game, and citation rules.
# This is identical for every query, so it lives in the system message.
SYSTEM_PROMPT = (
    "You are RulesBot, a board-game rules assistant.\n\n"
    "Answer using only the rules between <rules> and </rules> provided below. "
    "If the answer is not contained in the provided rules, say so explicitly "
    "instead of citing a game. Do not draw outside knowledge or fill any gaps "
    "from what you know about board games.\n\n"
    "The chunks may come from different games. Identify which game the user is "
    "asking about, then answer using only chunks from that game. Ignore chunks "
    "from any other game. If no chunk matches the game in question, say the "
    "rules don't cover it and exclude the citation.\n\n"
    "Each chunk is labeled with its game. After any statement drawn from a "
    "chunk, cite the game in brackets, e.g. '[Catan]'."
)


def generate_response(query, retrieved_chunks):
    """
    Generate a grounded answer from retrieved rule chunks.

    `retrieved_chunks` is the list returned by retrieve(). Each item is a dict
    with "text", "game", and "distance" (already filtered by relevance and
    ordered most- to least-relevant).

    The answer is grounded: the model is instructed to use only the retrieved
    text, name the game it cites, and admit when the rules don't cover the
    question. Returns a plain string.
    """
    if not retrieved_chunks:
        return (
            "I couldn't find anything relevant in the loaded rulebooks. "
            "Try rephrasing your question."
        )

    # Context block: one labeled, delimited entry per chunk, kept in the order
    # retrieve() returned them (most relevant first). Distance scores are
    # deliberately omitted so the model can't misread them as confidence.
    context = "\n\n".join(
        f'<chunk game="{chunk["game"]}">\n{chunk["text"]}\n</chunk>'
        for chunk in retrieved_chunks
    )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"<rules>\n{context}\n</rules>\n\nQuestion: {query}",
        },
    ]

    # Low temperature keeps the answer close to the source text — grounding
    # matters more here than creative phrasing.
    response = _client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        temperature=0.2,
    )
    return response.choices[0].message.content
