# Spec: `generate_response()`

**File:** `generator.py`
**Status:** Spec incomplete — fill in all blank fields before implementing

---

## Purpose

Given a user query and a list of retrieved rule chunks, generate a response that directly answers the question using only the retrieved text as context. The response must be grounded — it should not draw on the model's general knowledge of board games, only on what was retrieved.

---

## Input / Output Contract

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | `str` | The user's original question |
| `retrieved_chunks` | `list[dict]` | Ranked list of chunks from `retrieve()`, each with `"text"`, `"game"`, and `"distance"` |

**Output:** `str`

A plain string containing the response to show the user. The response should:
- Answer the question using only the retrieved rule text
- Identify which game the answer comes from
- Acknowledge clearly when the answer is not found in the loaded rules

Returns a fallback string (not an error) when `retrieved_chunks` is empty.

---

## Design Decisions

*Complete the fields below before writing any code. Use your AI tool in Plan or Ask mode to help you reason through what belongs here — but the decisions are yours.*

---

### Context formatting

*How will you format the retrieved chunks before passing them to the LLM? Describe the structure — not the code. Consider: will you label chunks by game? Include distance scores? Separate chunks with delimiters?*

```
Each chunk will be sepearated by a delimiter. In addition, an encapsulating wrapper will designate all of the chunks as rules. For each chunk, the title will be listed at a label. Distance scores will not be included to limit confusion or misinterpretation by the LLM. However, the chunks will be ordered by smallest distance score. 
```

---

### System prompt — grounding instruction

*Write the exact system prompt instruction you will use to prevent the model from answering beyond the retrieved text. This is the most important design decision in this function.*

```
Answer using only the rules between <rules> and </rules> provided below. If the answer is not contained in the provided rules, say so explicitly instead of citing a game. Do not draw outside knowledge or fill any gaps from what you know about board games.
```

---

### System prompt — citation instruction

*Write the exact instruction you will use to tell the model to identify which game its answer comes from.*

```
Each chunk is labeled with its game. After any statement drawn from a chunk, cite the game in brackets, e.g. '[Catan]'.
```

---

### Fallback behavior

*What should the response say when the answer isn't found in the loaded rule books? Write the exact fallback message.*

```
I couldn't find anything relevant in the loaded rulebooks. Try rephrasing your question.
```

---

### Handling low-relevance chunks

*`retrieved_chunks` may include chunks with high distance scores (weak relevance). Will you filter these out before building context, pass them all in, or handle them another way? What are the tradeoffs?*

```
Weak relevance chunks have been filtered out based on a distance threshold of 0.7. Despite this, some questions may correspond to a game. Responses should be constrained to correlated game chunks. 

"The chunks may come from different games. Identify which game the user is asking about, then answer using only chunks from that game. Ignore chunks from any other game. If no chunk matches the game in question, say the rules don't cover it."
```

---

### Message structure

*Describe how you will structure the messages list for the API call — what goes in the system message vs. the user message?*

```
The messages list has two entries. The system message holds the unchanging
policy: RulesBot's persona plus the grounding, citation, and fallback rules
that apply identically to every query. The user message holds the per-request
data: the retrieved chunks formatted as a delimited <rules> block, followed by
the user's question. Context goes in the user turn (not system) because it
changes each call and belongs next to the question it answers — the system
prompt governs behavior while the user turn supplies the material. Context
comes before the question so the question is the model's last instruction.
```

---

## Implementation Notes

*Fill this in after implementing and testing.*

**Test query and response:**

```
Query: How do you win?
Response: Returned three games with explanations on how to win, then asked for clarification about what specific game was being referred to. 
Correctly grounded? Yes
Cited the right game? Yes
```

**One thing you changed from your original spec after seeing the actual output:**

```
Added an exclusion to the citation if no relevant chunks returned. 
```
