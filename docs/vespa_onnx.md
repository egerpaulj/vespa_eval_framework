You can run **multiple embedding models inside the Vespa container** and eliminate the network hop to an embedding service. Queries and documents are embedded in-process using ONNX Runtime. 

Your setup could look like this:

* `title` → BGE-M3
* `body` → BGE-M3
* `summary` → SentenceTransformer
* query → choose either model (or both)

## Option 1: Two embedders (recommended)

Configure two embedders in `services.xml`.

```xml
<container version="1.0">

    <component id="bge"
               type="hugging-face-embedder">
        <transformer-model path="models/bge-m3/model.onnx"/>
        <tokenizer-model path="models/bge-m3/tokenizer.json"/>

        <pooling-strategy>cls</pooling-strategy>
        <normalize>true</normalize>
    </component>

    <component id="sbert"
               type="hugging-face-embedder">
        <transformer-model path="models/all-MiniLM/model.onnx"/>
        <tokenizer-model path="models/all-MiniLM/tokenizer.json"/>

        <pooling-strategy>mean</pooling-strategy>
        <normalize>true</normalize>
    </component>

</container>
```

Vespa loads both models into memory and exposes them by name. 

---

## Embed different fields

```vespa
field title type string {
    indexing: summary | index
}

field body type string {
    indexing: summary | index
}

field summary type string {
    indexing: summary | index
}

field bge_embedding type tensor<float>(x[1024]) {
    indexing:
        input title .
        " " .
        input body
        | embed bge
        | attribute | index
}

field summary_embedding type tensor<float>(x[384]) {
    indexing:
        input summary
        | embed sbert
        | attribute | index
}
```

Notice each field chooses a different embedder.

---

## Query embedding

At query time you can embed using exactly the same models.

```
input.query(bge_q)=embed(bge, @query)
```

or

```
input.query(summary_q)=embed(sbert, @query)
```

- No Python API.

- No FastAPI.

- No TEI server.

- No network hop.

The embedding is computed inside the Vespa container. 

---

## Search one embedding

```yql
select * from docs where

nearestNeighbor(
    bge_embedding,
    bge_q
)
```

---

## Search another

```yql
select * from docs where

nearestNeighbor(
    summary_embedding,
    summary_q
)
```

---

## Hybrid search

```yql
select * from docs where

(
    userInput(@query)
)

OR

nearestNeighbor(bge_embedding, bge_q)
```

---

## Search both embeddings

You can even search both vector spaces.

```yql
select * from docs where

nearestNeighbor(bge_embedding, bge_q)

OR

nearestNeighbor(summary_embedding, summary_q)
```

and combine them in a rank profile.

```vespa
rank-profile hybrid {

    first-phase {

        expression:

            closeness(field, bge_embedding)

            +

            0.4 * closeness(field, summary_embedding)

            +

            bm25(title)

    }

}
```

This is useful if one model captures semantic similarity while another captures paraphrase or domain-specific meaning.

---

# Exporting your models

Since you're already using:

```python
BGEM3Embedder("BAAI/bge-m3")
```

and

```python
SentenceTransformer(...)
```

you would export each to ONNX once.

For SentenceTransformers:

```bash
optimum-cli export onnx \
    --task feature-extraction \
    -m sentence-transformers/all-MiniLM-L6-v2 \
    models/all-MiniLM
```

For BGE:

```bash
optimum-cli export onnx \
    --task sentence-similarity \
    -m BAAI/bge-m3 \
    models/bge-m3
```

The exported `model.onnx` and `tokenizer.json` can be referenced directly by the `hugging-face-embedder`. Vespa's documentation also includes examples for exporting Sentence Transformers and BGE-family models to ONNX. ([Vespa Blog][3])

---

# One thing to watch for with BGE-M3

`BAAI/bge-m3` is more than a simple dense embedding model. It supports:

* dense embeddings
* sparse retrieval
* ColBERT-style multi-vector retrieval

The built-in `hugging-face-embedder` uses the **dense embedding** path. If you want to leverage BGE-M3's sparse or multi-vector capabilities, you'll need additional indexing and ranking logic beyond a standard dense embedding pipeline. 

## Recommended architecture

For your use case, a clean production design would be:

| Field     | Embedder            | Purpose                                      |
| --------- | ------------------- | -------------------------------------------- |
| `title`   | BGE-M3              | Semantic retrieval of titles                 |
| `body`    | BGE-M3              | Long-form document retrieval                 |
| `summary` | SentenceTransformer | Lightweight semantic matching                |
| Query     | BGE-M3              | Main semantic retrieval                      |
| Query     | SentenceTransformer | Optional second retrieval space or reranking |

This lets you perform all embedding inference **inside Vespa**, avoiding a separate embedding API and reducing latency, while still allowing different fields to use different embedding models.

[1]: https://learn.vespa.ai/application-package-deployment/app-package/?utm_source=chatgpt.com "Application Package and Deployment | Vespa Learn"
[2]: https://blog.vespa.ai/text-embedding-made-simple/?utm_source=chatgpt.com "Text embedding made simple | Vespa Blog"
[3]: https://blog.vespa.ai/leveraging-frozen-embeddings-in-vespa-with-sentence-transformers/?utm_source=chatgpt.com "Leveraging frozen embeddings in Vespa with SentenceTransformers | Vespa Blog"
[4]: https://arxiv.org/abs/2402.03216?utm_source=chatgpt.com "BGE M3-Embedding: Multi-Lingual, Multi-Functionality, Multi-Granularity Text Embeddings Through Self-Knowledge Distillation"
