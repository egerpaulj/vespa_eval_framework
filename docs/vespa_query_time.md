At query time, Vespa generally applies **the same linguistic processing** to the query terms that it applied to the indexed text. This symmetry is important so that `"running"` in a query matches `"run"` in the index, for example.

For a field with:

```vespa
field body type string {
    indexing: index

    match { text }

    stemming: best
}
```

a query like:

```
Running quickly to the hospitals
```

typically goes through:

1. **Tokenization**
2. **Case folding** (lowercasing)
3. **Language detection or specified language**
4. **Stopword removal** (if configured)
5. **Stemming**
6. **Decompounding** (if the analyzer supports it)

The resulting terms are then looked up in the inverted index.

### What is applied where?

| Feature           |          Index time          | Query time |
| ----------------- | :--------------------------: | :--------: |
| Tokenization      |               ✓              |      ✓     |
| Lowercasing       |               ✓              |      ✓     |
| Stopword removal  |               ✓              |      ✓     |
| Stemming          |               ✓              |      ✓     |
| Decompounding     |               ✓              |      ✓     |
| Synonym expansion | Usually query time (or both) |            |
| Fuzzy matching    |        Query time only       |            |

### Stemming example

Document:

```
The foxes were running
```

Indexed terms:

```
fox
run
```

Query:

```
running fox
```

Processed query:

```
run
fox
```

which matches the indexed terms.

### Stopwords

Document:

```
The quick brown fox
```

Indexed:

```
quick
brown
fox
```

Query:

```
the fox
```

Processed:

```
fox
```

### Decompounding

Suppose the document contains:

```
Krankenhausversicherung
```

If the analyzer performs decompounding, the index might contain:

```
krankenhausversicherung
krankenhaus
versicherung
```

A query for:

```
Krankenhaus
```

is also analyzed and matches the decompounded token.

### Fuzzy matching

This is **not** part of the linguistic pipeline. Instead, it's a query operator:

```sql
where title contains ({maxEditDistance:2}fuzzy("iphnoe"))
```

The query term `"iphnoe"` is analyzed (e.g., lowercased) first, and then the fuzzy operator performs edit-distance matching against indexed terms. No fuzzy terms are stored in the index.

### Synonyms

Synonyms are different because they are **not automatically applied** as part of the standard linguistic processing. You typically implement them by:

* expanding the query (preferred), or
* expanding documents at indexing time, or
* doing both.

For example:

```
fast
```

might be rewritten to

```
(fast OR quick OR rapid)
```

before execution.

## Summary

The standard `match { text }` pipeline is intentionally symmetric:

| Processing                      | Applied symmetrically? |
| ------------------------------- | :--------------------: |
| Tokenization                    |            ✓           |
| Lowercasing                     |            ✓           |
| Language-specific normalization |            ✓           |
| Stopwords                       |            ✓           |
| Stemming                        |            ✓           |
| Decompounding (if configured)   |            ✓           |

The main exceptions are:

* **Fuzzy matching**: query-time only.
* **Synonym expansion**: usually query-time (unless you explicitly choose index-time expansion).
* **Ranking and retrieval operators** (e.g., `weakAnd`, `nearestNeighbor`): query-time only.
