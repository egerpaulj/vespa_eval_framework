Decompounding in Vespa is **language-dependent** and is provided by the **linguistics implementation**, not by the schema itself. There is no schema option like:

```vespa
decompound: true    ❌
```

Instead, Vespa relies on the configured linguistic analyzer for languages where compound words are common (German, Dutch, Norwegian, Swedish, Danish, etc.).

## 1. Default decompounding

If the document language is German:

```json
{
    "fields": {
        "title": "Krankenhausversicherung"
    },
    "language": "de"
}
```

the analyzer may produce terms similar to

```
krankenhausversicherung
krankenhaus
versicherung
```

depending on the configured linguistics implementation.

---

## 2. Lucene Linguistics

When using Lucene Linguistics, you can choose an analyzer that performs decompounding.

For example, the Lucene `GermanAnalyzer` includes:

* tokenization
* lowercasing
* stopwords
* German stemming

It **does not** perform full dictionary-based decompounding by itself. If you need aggressive decompounding (e.g., splitting `Donaudampfschifffahrtsgesellschaft`), you typically configure additional Lucene token filters such as:

* `DictionaryCompoundWordTokenFilter`
* `HyphenationCompoundWordTokenFilter`

within your analysis profile.

A simplified configuration looks like:

```xml
<analysis>
  <item key="profile=german;language=de">
    <tokenizer>
      <name>standard</name>
    </tokenizer>

    <tokenFilters>
      <item>
        <name>lowercase</name>
      </item>

      <item>
        <name>dictionaryCompoundWord</name>
        <conf>
          <item key="dictionary">de/words.txt</item>
        </conf>
      </item>

      <item>
        <name>germanStem</name>
      </item>
    </tokenFilters>
  </item>
</analysis>
```

---

## 3. Gram matching

If your goal is simply to match parts of long compound words without linguistic decompounding, you can use character n-grams:

```vespa
field title type string {
    indexing: index

    match {
        gram
        gram-size: 3
    }
}
```

This is not true decompounding but can improve recall for partial matches.

---

## 4. Query-time alternatives

Some applications avoid linguistic decompounding and instead expand the query:

```
Krankenhausversicherung

↓

Krankenhaus Versicherung Krankenhausversicherung
```

This can be done in a custom query searcher.

---

## Summary

| Approach                    | Best for                          | Notes                                     |
| --------------------------- | --------------------------------- | ----------------------------------------- |
| Language-specific analyzer  | Normal German search              | Built-in stemming and language processing |
| Dictionary compound filter  | High-quality German decompounding | Requires a compound dictionary            |
| Hyphenation compound filter | Better linguistic splitting       | Requires hyphenation patterns             |
| `match { gram }`            | Partial matching/autocomplete     | Not linguistic decompounding              |
| Query rewriting             | Domain-specific compounds         | Fully customizable                        |

For **German production search**, a common setup is:

* `match { text }`
* `stemming: best`
* German language (`language: de`)
* `GermanAnalyzer`
* `DictionaryCompoundWordTokenFilter` (or `HyphenationCompoundWordTokenFilter`) if you need explicit compound splitting beyond what the standard analyzer provides.
