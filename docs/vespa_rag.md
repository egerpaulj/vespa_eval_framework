## 1. RAG Retrieval in Vespa

Vespa is well suited for Retrieval-Augmented Generation (RAG) because it can combine **keyword search**, **semantic search**, and **metadata filtering** in a single query.

### Document schema

```vespa
schema docs {

    document docs {

        field id type string {
            indexing: attribute | summary
        }

        field text type string {
            indexing: index | summary

            match { text }

            stemming: best
        }

        field embedding type tensor<float>(x[768]) {
            indexing: attribute | index
            attribute {
                distance-metric: angular
            }
        }

        field source type string {
            indexing: attribute | summary
        }
    }

    fieldset default {
        fields: text
    }

    rank-profile hybrid inherits default {

        first-phase {
            expression:
                bm25(text)
                +
                closeness(field, embedding)
        }
    }
}
```

---

### Query

```yql
select * from docs where
(
    userInput(@query)
)
OR
(
    nearestNeighbor(embedding, query_embedding)
);
```

Parameters

```json
{
    "query": "What is vector search?",
    "input.query(query_embedding)": [0.12, 0.44, ...],
    "hits": 10
}
```

This retrieves documents using

* BM25
* semantic similarity
* hybrid ranking

all in one request.

---

### Filtering

You can combine retrieval with metadata.

```yql
select * from docs where

source contains "documentation"

AND

(
    userInput(@query)
    OR
    nearestNeighbor(embedding, query_embedding)
);
```

Typical RAG filters include

* document type
* tenant
* language
* access control
* publication date

---

### Multi-stage ranking

Retrieve 500 candidates

```text
BM25 + ANN
```

then rerank

```text
Cross Encoder
```

using ONNX.

---

# 2. ONNX inference in Vespa

One of Vespa's strongest features is running ONNX models directly during ranking.

Example architecture

```text
User Query
      │
      ▼
Retrieve 500 docs
      │
      ▼
ONNX Cross Encoder
      │
      ▼
Top 10
```

No external inference server is required.

---

## Deploy the model

```
application/

    models/
        crossencoder.onnx
```

---

## Rank profile

```vespa
rank-profile rerank inherits default {

    onnx-model crossencoder {
        file: models/crossencoder.onnx
    }

    second-phase {

        expression:
            onnx(crossencoder).score

        rerank-count: 100
    }
}
```

The top 100 first-phase hits are reranked using the model.

---

## Passing tensors

Suppose the ONNX model expects

```
query_embedding
document_embedding
```

Inputs

```vespa
inputs {

    query(q) tensor<float>(x[768])

}
```

Then

```vespa
onnx-model semantic {

    file: models/model.onnx

    input query: query(q)

    input document: attribute(embedding)

}
```

Now every candidate document is scored by the neural model.

---

# Example: Dense retrieval

Rank profile

```vespa
rank-profile semantic {

    first-phase {

        expression:
            closeness(field, embedding)

    }
}
```

Query

```json
{
    "input.query(query_embedding)": [...],
    "ranking.profile": "semantic"
}
```

---

# Example: Hybrid RAG

```vespa
rank-profile hybrid {

    first-phase {

        expression:

            bm25(text)

            +

            5 * closeness(field, embedding)

    }
}
```

Now keyword and semantic signals contribute together.

---

# Example: Cross Encoder reranking

Retrieve

```
500 docs
```

First phase

```
BM25
+
ANN
```

Second phase

```vespa
second-phase {

    expression:
        onnx(crossencoder).score

    rerank-count: 50
}
```

Result

```
500 candidates

↓

50 reranked by BERT

↓

Top 10 returned
```

This pattern is common in production RAG systems because it balances latency and ranking quality.

---

# Typical production RAG pipeline

```text
User question
      │
      ▼
Embed query
      │
      ▼
Vespa
 ├── BM25
 ├── ANN
 ├── Filters
 ├── Business rules
 └── Hybrid ranking
      │
      ▼
Top 100 passages
      │
      ▼
ONNX Cross Encoder
      │
      ▼
Top 10 passages
      │
      ▼
LLM
```

## When to use ONNX in Vespa

| Use case                | Example model                          | Benefit                                                                                 |
| ----------------------- | -------------------------------------- | --------------------------------------------------------------------------------------- |
| Cross-encoder reranking | BERT, MiniLM, bge-reranker             | Improves RAG retrieval quality by jointly scoring the query and each candidate passage. |
| Learning-to-rank        | Gradient-boosted trees, neural rankers | Combines text relevance, popularity, freshness, and other features into a single score. |
| Classification          | Spam, intent, content moderation       | Classify documents or queries during search without an external inference service.      |
| Recommendation          | Two-tower or ranking models            | Personalize search results or recommendations using learned models.                     |
| Semantic scoring        | Sentence transformers exported to ONNX | Compute neural relevance scores as part of the ranking pipeline.                        |

The key advantage is that **retrieval, ranking, and model inference all happen within Vespa's serving layer**, avoiding extra network hops to separate model-serving infrastructure and making it practical to use ML models in latency-sensitive search applications.
