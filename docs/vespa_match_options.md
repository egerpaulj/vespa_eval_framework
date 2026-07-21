In Vespa, the `match` block controls **how terms are tokenized and matched** for a field. The available options are relatively small compared to systems like Elasticsearch, but they're important.

## `match` modes

### `text` (most common)

Use for natural language.

```vespa
field body type string {
    indexing: index | summary

    match {
        text
    }
}
```

Characteristics:

* Linguistic tokenization
* Lowercasing
* Stemming (if enabled)
* Stopword removal (depending on linguistics)
* Phrase queries supported
* Best choice for documents, articles, descriptions

Example

```
"The Quick Brown Foxes"
```

becomes approximately

```
quick
brown
fox
```

---

### `word`

Matches complete words without linguistic normalization.

```vespa
field sku type string {
    indexing: index | attribute

    match {
        word
    }
}
```

Useful for:

* Tags
* Categories
* Product IDs
* Usernames
* Country codes

Example

```
USB-C
```

remains

```
USB-C
```

rather than being linguistically processed.

---

### `exact`

Entire field is treated as one token.

```vespa
field isbn type string {
    indexing: attribute | summary

    match {
        exact
    }
}
```

Only matches the full value.

Example

```
9780134685991
```

must be queried exactly.

Common uses:

* IDs
* UUIDs
* Email addresses
* Hashes

---

### `gram`

Indexes character n-grams.

```vespa
field name type string {
    indexing: index

    match {
        gram
    }
}
```

Used for:

* Partial matching
* Prefix search
* Infix search
* Languages with compound words
* Some autocomplete scenarios

Instead of indexing

```
banana
```

it indexes character grams (size depends on configuration), allowing queries like

```
nan
```

to match.

---

## Match modifiers

Within `match { ... }`, there are additional options.

### `max-length`

Limit indexed token length.

```vespa
match {
    text
    max-length: 256
}
```

Useful to prevent indexing extremely long tokens.

---

### `gram-size`

Only for `gram`.

```vespa
match {
    gram
    gram-size: 3
}
```

Indexes trigrams.

Example

```
banana
```

→

```
ban
ana
nan
ana
```

---

## Stemming

Configured outside the `match` block.

```vespa
field body type string {
    indexing: index

    match {
        text
    }

    stemming: best
}
```

---

## Complete examples

Natural language

```vespa
field description type string {
    indexing: index | summary

    match {
        text
    }

    stemming: best
}
```

Tags

```vespa
field tags type array<string> {
    indexing: index | summary

    match {
        word
    }
}
```

SKU

```vespa
field sku type string {
    indexing: attribute

    match {
        exact
    }
}
```

Autocomplete

```vespa
field product_name type string {
    indexing: index

    match {
        gram
        gram-size: 3
    }
}
```

## Which should you use?

| Field              | Match             |
| ------------------ | ----------------- |
| Title              | `text`            |
| Body               | `text`            |
| Description        | `text`            |
| Tags               | `word`            |
| Categories         | `word`            |
| Username           | `exact` or `word` |
| UUID               | `exact`           |
| SKU                | `exact`           |
| Email              | `exact`           |
| Autocomplete field | `gram`            |

For most full-text search applications, a common pattern is:

```vespa
field title type string {
    indexing: index | summary
    match { text }
    stemming: best
}

field body type string {
    indexing: index | summary
    match { text }
    stemming: best
}

field tags type array<string> {
    indexing: index | summary
    match { word }
}
```

This combination provides robust full-text search for titles and bodies while preserving exact tag values for filtering and matching.
