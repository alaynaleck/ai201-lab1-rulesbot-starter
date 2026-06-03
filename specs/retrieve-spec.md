# Spec: `retrieve()`

**File:** `retriever.py`
**Status:** Spec incomplete — fill in all blank fields before implementing

---

## Purpose

Given a user's natural language query, find the most relevant chunks from the vector store using semantic similarity search. Return them ranked by relevance so that `generate_response()` can use them as context.

---

## Input / Output Contract

**Inputs:**

| Parameter   | Type  | Description                                                                |
| ----------- | ----- | -------------------------------------------------------------------------- |
| `query`     | `str` | The user's natural language question                                       |
| `n_results` | `int` | Maximum number of chunks to return (default: `N_RESULTS` from `config.py`) |

**Output:** `list[dict]`

Each dict in the returned list must contain exactly these keys:

| Key          | Type    | Description                                                   |
| ------------ | ------- | ------------------------------------------------------------- |
| `"text"`     | `str`   | The chunk text                                                |
| `"game"`     | `str`   | The game name this chunk came from                            |
| `"distance"` | `float` | Cosine distance score — lower means more similar to the query |

Results should be ordered from most to least relevant (lowest to highest distance). Returns an empty list `[]` if the collection contains no documents.

---

## Design Decisions

_Complete the fields below before writing any code. Use your AI tool in Plan or Ask mode to help you reason through what belongs here — but the decisions are yours._

---

### Query approach

_Describe how you will use `_collection.query()` to find relevant chunks. What arguments will you pass, and why?_

```
`_collection.query()` returns a dict of keys, each corresponding to a list of lists of relevant data.

Since we are passing a query in natural language to the database, we must pass our query to the formal parameter query_texts. Because this expects a list of user queries, we will convert our singular query into a list.

We then include the maximum number of chunks to return by matching the formal and actual parameters.

Finally, we use include to constrain the response to the doc specs of documents, metadatas, and distances.

```

```python
results = _collection.query(
    query_texts=[query],
    n_results=n_results,
    include=["documents", "metadatas", "distances"],
)
```

---

### Return structure

*Sketch out what one item in your return list looks like as a concrete example. Where does each field come from in the query results?*

```
The result will return as a list of dicts, each dict with the keys "text", "game", and "distance". 

Text can be retrieved from the documents field by accessing the first index and iterating through. Game corresponds to metadatas and distance corresponds to distances.
```

```json
{
  "ids":       [ ["catan_0", "catan_3"] ],
  "documents": [ ["CATAN — OFFICIAL RULES SUMMARY\n\nOVERVIEW...", "e the number tokens..."] ],
  "metadatas": [ [ {"game": "Catan"}, {"game": "Catan"} ] ],
  "distances": [ [ 0.3798600435256958, 0.5805382132530212 ] ],
  "embeddings": None,   # not requested
  "uris": None, "data": None,
  "included": ["documents", "metadatas", "distances"],
}
```

---

### Handling the nested result structure

*`_collection.query()` returns nested lists. Describe what index you need to access to get the actual list of results for a single query, and why the nesting exists.*

```
To access the actual list of results for a single query, you need to access the key name, then the 0 index for the first result. This is because `_colleciton.query()` returns a nested list corresponding to a list of queries. Rules bot only passes one query, resulting in the 0 index. 

```

---

### Relevance threshold

*Will you filter out results above a certain distance score, or return all `n_results` regardless of how relevant they are? What are the tradeoffs of each approach?*

```

Apply a lenient threshold (drop distance > .7) to filter out irrevelant queries, returning []. This allows the bot to say "not in the rules". Tradeoffs accepted: potentially relevant data can be filtered out; however, most relevant data will generally have a closer distance. More testing required to find the best T. 

```

---

### Edge cases

*How does your implementation behave when: (a) the collection is empty, (b) the query matches no chunks well, (c) the query matches chunks from multiple games?*

```
When the collection is empty, the query will return no results; the same for when the query matches no chunks below the threshold. If the query matches chunks from multiple games, it will return results from all games. 

```

---

## Implementation Notes

*Fill this in after implementing, before moving to Milestone 3.*

**Test query and top result returned:**

```

Query: How do you win?
Top result game: Catan
Distance score: .42
Does it make sense? Yes-- while the results span multiple games, all excerpts contain references to winning, and the question lacks designation of a specific game.

```

**One thing about the query results that surprised you:**

```

Query results can return different games when the question is too vague, which isn't a database issue since the results return semantically similar results. 

```

```
