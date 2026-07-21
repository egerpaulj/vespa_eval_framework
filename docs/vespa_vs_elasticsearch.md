## Text analysis comparison: Vespa vs. Elasticsearch

| Feature                            | Vespa                                                              | Elasticsearch                                                                         |
| ---------------------------------- | ------------------------------------------------------------------ | ------------------------------------------------------------------------------------- |
| **Tokenization**                   | Language-aware linguistics (`match { text }`)                      | Configurable tokenizer in an analyzer (`standard`, `whitespace`, `icu`, etc.)         |
| **Lowercasing**                    | Applied by linguistics                                             | `lowercase` token filter                                                              |
| **Stemming**                       | `stemming: best`, `shortest`, `multiple`, `none`                   | `stemmer`, `porter_stem`, `kstem`, Snowball, language analyzers                       |
| **Stopwords**                      | Language-specific linguistics or custom Lucene Linguistics profile | `stop` token filter with built-in or custom lists                                     |
| **Synonyms**                       | Typically query rewriting or Lucene Linguistics synonym filter     | `synonym` / `synonym_graph` token filters                                             |
| **Decompounding**                  | Via language-specific linguistics or Lucene compound word filters  | `dictionary_decompounder`, `hyphenation_decompounder`                                 |
| **Fuzzy search**                   | Query operator (`fuzzy()`, `maxEditDistance`)                      | `fuzziness: AUTO`, `1`, `2` on `match` queries                                        |
| **Autocomplete**                   | `match { gram }`, prefix search, custom searchers                  | `edge_ngram`, `search_as_you_type`, completion suggester                              |
| **Language analyzers**             | Built-in linguistics or Lucene Linguistics                         | Rich set of built-in language analyzers                                               |
| **Custom analysis pipeline**       | Via Lucene Linguistics configuration                               | First-class analyzers with tokenizer + char filters + token filters                   |
| **Per-field analyzer**             | Via linguistics profile                                            | `analyzer` / `search_analyzer` mapping                                                |
| **Different index/query analyzer** | Limited (requires custom searchers/profiles)                       | Native support (`analyzer` vs. `search_analyzer`)                                     |
| **Field grouping**                 | `fieldset`                                                         | `copy_to`, `multi_match`, field aliases                                               |
| **Ranking integration**            | Native hybrid lexical + vector ranking                             | Hybrid supported, but ranking logic is less integrated than Vespa's ranking framework |

---

## Mapping common Elasticsearch analyzers to Vespa

| Elasticsearch       | Vespa equivalent                                       |
| ------------------- | ------------------------------------------------------ |
| `standard` analyzer | `match { text }` + default linguistics                 |
| `english` analyzer  | `match { text }` + `stemming: best` + English language |
| `german` analyzer   | German language + Lucene Linguistics                   |
| `stop` filter       | Linguistics stopword list                              |
| `stemmer`           | `stemming: best`                                       |
| `synonym_graph`     | Query rewriting or Lucene synonym filter               |
| `edge_ngram`        | `match { gram }` or prefix search                      |
| `fuzziness: AUTO`   | `fuzzy()` with `maxEditDistance`                       |

---

## When to use which feature in Vespa

| Requirement                          | Recommended Vespa feature                              | Notes                                            |
| ------------------------------------ | ------------------------------------------------------ | ------------------------------------------------ |
| General full-text search             | `match { text }` + `stemming: best`                    | Default choice                                   |
| Exact identifiers (SKU, UUID, email) | `match { exact }`                                      | No linguistic processing                         |
| Tags and categories                  | `match { word }`                                       | Preserves word boundaries                        |
| Autocomplete                         | `match { gram }` or prefix search                      | Character n-grams for infix matching             |
| Multi-field search                   | `fieldset`                                             | Simplifies querying multiple fields              |
| Typo tolerance                       | `fuzzy()`                                              | Query-time feature                               |
| English documents                    | English language + stemming                            | Built-in linguistics                             |
| German/Dutch documents               | Language-specific linguistics + optional decompounding | Improves compound-word matching                  |
| Domain synonyms                      | Query rewriting or Lucene synonym filter               | Prefer query-time expansion                      |
| Domain stopwords                     | Custom Lucene Linguistics profile                      | Applied consistently at indexing and query time  |
| Semantic search                      | Dense tensor field + `nearestNeighbor()`               | Combine with lexical retrieval for hybrid search |
| Hybrid search                        | `userInput()` + `nearestNeighbor()` + rank profile     | One of Vespa's strengths                         |

### Rule of thumb

| If you need...                   | Vespa recommendation                                                     |
| -------------------------------- | ------------------------------------------------------------------------ |
| Standard keyword search          | `match { text }`                                                         |
| Production document search       | `text` + `stemming: best` + `fieldset`                                   |
| Product/catalog search           | `word` for facets, `text` for descriptions, `exact` for IDs              |
| Search with typos                | Add `fuzzy()` to selected query terms                                    |
| German legal/technical documents | Enable German linguistics and decompounding                              |
| Hybrid BM25 + vector retrieval   | Use Vespa's lexical indexing with tensor fields and custom rank profiles |
| Fine-grained ML ranking          | Use Vespa's ranking expressions or ONNX models in rank profiles          |

The biggest conceptual difference is that **Elasticsearch emphasizes configurable analyzers** (tokenizer + filters defined per field), whereas **Vespa emphasizes language-aware linguistics and separates text analysis from ranking**. In Vespa, sophisticated retrieval and ranking (including hybrid lexical/vector search and ML models) are first-class features, while text analysis is intentionally simpler and more language-centric.


Neither is universally "better"—they were designed with different priorities. Elasticsearch excels as a **search and analytics engine** with a rich text-analysis ecosystem, while Vespa is a **retrieval and ranking engine** optimized for large-scale, low-latency search and recommendation.

| Capability                               | Elasticsearch              | Vespa                                         | Better choice               |
| ---------------------------------------- | -------------------------- | --------------------------------------------- | --------------------------- |
| Full-text search                         | Excellent                  | Excellent                                     | Tie                         |
| Text analysis (analyzers, token filters) | ⭐⭐⭐⭐⭐                      | ⭐⭐⭐                                           | Elasticsearch               |
| Language analyzers                       | Extensive built-in support | Good, fewer built-in options                  | Elasticsearch               |
| Synonyms                                 | Native support             | Usually query rewriting or Lucene Linguistics | Elasticsearch               |
| Custom analyzers                         | First-class feature        | Possible with Lucene Linguistics              | Elasticsearch               |
| Fuzzy search                             | Simple (`fuzziness: AUTO`) | Powerful but more explicit                    | Elasticsearch (ease of use) |
| Aggregations & analytics                 | Industry-leading           | Limited                                       | Elasticsearch               |
| Faceted search                           | Excellent                  | Good                                          | Elasticsearch               |
| BM25 search                              | Excellent                  | Excellent                                     | Tie                         |
| Vector search                            | Good (HNSW)                | Excellent                                     | Vespa                       |
| Hybrid lexical + vector                  | Good                       | ⭐⭐⭐⭐⭐ Native                                  | Vespa                       |
| Learning-to-rank / ML                    | Plugin-based or external   | Built into ranking framework                  | Vespa                       |
| ONNX model serving                       | Basic                      | Native                                        | Vespa                       |
| Multi-stage ranking                      | Limited                    | Native                                        | Vespa                       |
| Personalization                          | Possible                   | Designed for it                               | Vespa                       |
| Latency at scale                         | Good                       | Excellent                                     | Vespa                       |
| Streaming updates                        | Good                       | Excellent                                     | Vespa                       |
| Billion-document retrieval               | Good                       | Excellent                                     | Vespa                       |
| Operational simplicity                   | Easier                     | More complex                                  | Elasticsearch               |
| Ecosystem                                | Huge                       | Smaller                                       | Elasticsearch               |

## Text analysis

Elasticsearch has a much richer analysis pipeline.

Example:

```text
Tokenizer
    ↓
Character filters
    ↓
Token filters
    ↓
Analyzer
```

You can easily combine:

* ICU tokenizer
* lowercase
* stopwords
* synonyms
* stemmer
* decompounder
* shingles
* edge n-grams

on a per-field basis.

In Vespa, text analysis is intentionally simpler:

```text
Language
    ↓
Linguistics
    ↓
Index
```

You typically configure:

* language
* stemming
* stopwords
* optional Lucene Linguistics profile

This simplicity works well for many applications but offers less flexibility than Elasticsearch's analyzer framework.

**Winner:** Elasticsearch

---

## Ranking

This is where Vespa stands out.

Elasticsearch generally follows:

```
Retrieve
    ↓
BM25
    ↓
Optional rescoring
```

Vespa supports:

```
Retrieve
    ↓
BM25
    ↓
Vector similarity
    ↓
Business features
    ↓
Tensor features
    ↓
ONNX models
    ↓
Custom ranking expressions
```

Everything is part of a single ranking pipeline.

**Winner:** Vespa

---

## Hybrid search

Elasticsearch supports hybrid search, but Vespa was designed around it.

Example in Vespa:

```
nearestNeighbor(embedding, query_embedding)
OR
userInput(@query)
```

Then rank using:

* BM25
* cosine similarity
* popularity
* freshness
* click-through rate
* ONNX model

all within one rank profile.

**Winner:** Vespa

---

## Recommendations

Recommendation systems often need:

* user embeddings
* item embeddings
* freshness
* popularity
* personalization
* business rules

These are natural fits for Vespa's ranking framework.

**Winner:** Vespa

---

## Analytics

Need queries like:

* average price
* top brands
* histograms
* date buckets
* percentiles

Elasticsearch's aggregation framework is far more mature.

**Winner:** Elasticsearch

---

## Ease of use

Elasticsearch is generally easier to get started with.

Create an index:

```json
{
  "mappings": {
    "properties": {
      "body": {
        "type": "text"
      }
    }
  }
}
```

Vespa requires:

* application package
* schema
* services.xml
* deployment
* rank profiles

There's more upfront configuration, but also more control.

**Winner:** Elasticsearch

## Which should you choose?

| Use case                             | Recommendation                                                                                   |
| ------------------------------------ | ------------------------------------------------------------------------------------------------ |
| Website search                       | Elasticsearch                                                                                    |
| Documentation search                 | Elasticsearch                                                                                    |
| Log analytics                        | Elasticsearch                                                                                    |
| E-commerce search                    | Vespa if ranking quality matters; Elasticsearch if text search and aggregations are the priority |
| AI-powered search                    | Vespa                                                                                            |
| Semantic search                      | Vespa                                                                                            |
| RAG retrieval                        | Vespa                                                                                            |
| Personalized search                  | Vespa                                                                                            |
| Recommendation engine                | Vespa                                                                                            |
| News feed ranking                    | Vespa                                                                                            |
| Ad ranking                           | Vespa                                                                                            |
| Real-time ML inference during search | Vespa                                                                                            |

## Overall

| If your priority is...                         | Choose        |
| ---------------------------------------------- | ------------- |
| Powerful text analysis and search ecosystem    | Elasticsearch |
| Dashboards, logs, and analytics                | Elasticsearch |
| Fast setup and broad community support         | Elasticsearch |
| Hybrid lexical + vector retrieval              | Vespa         |
| Large-scale personalized search                | Vespa         |
| Sophisticated ranking with ML models           | Vespa         |
| Low-latency retrieval over very large datasets | Vespa         |

A practical rule of thumb is:

* **Choose Elasticsearch** when search is primarily about **finding the right documents** and you need rich text analysis, aggregations, and a mature ecosystem.
* **Choose Vespa** when search is about **ranking the best results** using multiple signals—text relevance, vectors, business features, personalization, and machine learning—in a single, low-latency serving system. This is why Vespa is commonly used for applications like recommendation systems, feeds, and AI-powered search rather than as a general-purpose search and analytics platform.
