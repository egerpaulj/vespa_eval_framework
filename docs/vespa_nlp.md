In Vespa, most of these features are achieved through a combination of **field indexing settings**, **linguistics configuration**, **query annotations**, and **query profiles**. There isn't a single "text template" that enables everything, but you can create a reusable pattern.

Here's what each feature maps to in Vespa:

| Feature       | Vespa approach                                                                        |
| ------------- | ------------------------------------------------------------------------------------- |
| Stemming      | `stemming: best` (or `shortest`, `multiple`) on indexed fields                        |
| Stopwords     | Custom linguistics component with stopword list (language-specific)                   |
| Synonyms      | Synonym file via linguistic processing or query rewriting                             |
| Fuzzy search  | `contains ({maxEditDistance:2}fuzzy("term"))` or `userInput()` with fuzzy annotations |
| Decompounding | `match { gram; }` or language-specific decompounder (German, Dutch, etc.)             |
| Fieldsets     | `fieldset default { fields: title, body, tags }`                                      |


Vespa's linguistics pipeline performs, depending on the configured language:

Tokenization
Lowercasing
Stemming
Stopword filtering


---

## Example schema

```vespa
schema document {

    document document {

        field id type string {
            indexing: attribute | summary
        }

        field title type string {
            indexing: index | summary

            match {
                text
            }

            stemming: best
            rank: filter
        }

        field body type string {
            indexing: index | summary

            match {
                text
            }

            stemming: best
        }

        field tags type array<string> {
            indexing: index | summary

            match {
                word
            }

            stemming: best
        }
    }

    fieldset default {
        fields: title, body, tags
    }

    fieldset semantic {
        fields: title, body
    }
}
```

---

# 1. Stemming

Simply enable

```vespa
stemming: best
```

Other options include

```vespa
stemming: shortest
stemming: multiple
stemming: none
```

`best` is almost always the recommended option.

Example

```
running
runs
ran
```

all normalize to

```
run
```

---

# 2. Stopwords

Vespa uses its linguistic processing during indexing and querying.

You typically configure:

```
services.xml
```

```xml
<container id="default" version="1.0">
    <search/>
    <document-api/>
</container>
```

Then provide a custom stopword file to the linguistic component.

Example stopword file

```
the
a
an
of
to
```

For domain-specific search you might add

```
document
page
item
```

if they occur everywhere.

---

# 3. Synonyms

Vespa supports synonym expansion through synonym files.

Example

```
fast,quick,rapid
cpu,processor
tv,television
```

A query for

```
fast cpu
```

becomes approximately

```
(fast OR quick OR rapid)
(cpu OR processor)
```

without changing the indexed documents.

Large synonym lists are usually managed separately from the schema.

---

# 4. Fuzzy search

Modern Vespa supports fuzzy matching.

Example YQL

```sql
select * from sources * where title contains ({maxEditDistance:2}fuzzy("iphnoe"));
```

returns

```
iphone
iphones
iPhone
```

with edit distance ≤ 2.

You can also expose this through `userInput()` by rewriting the query or by selectively applying fuzzy matching to specific fields.

Typical values:

```
maxEditDistance:1
```

for autocomplete

```
maxEditDistance:2
```

for general search.

---

# 5. Decompounding

Useful mainly for

* German
* Dutch
* Scandinavian languages

Example

```
Krankenhausversicherung
```

becomes

```
Krankenhaus
Versicherung
```

Enable an appropriate linguistic implementation (such as Lucene linguistic components) that supports decompounding for the language. English typically does not benefit from this.

---

# 6. Fieldsets

Instead of searching each field individually:

```sql
where title contains "vespa"
or body contains "vespa"
or tags contains "vespa"
```

define

```vespa
fieldset default {
    fields: title, body, tags
}
```

Then

```sql
where default contains "vespa"
```

searches all three fields.

You can define multiple fieldsets.

```vespa
fieldset semantic {
    fields: title, body
}

fieldset metadata {
    fields: tags, author
}
```

---

# Putting it together

A production-ready schema might look like this:

```vespa
schema docs {

    document docs {

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
            stemming: best
        }

        field language type string {
            indexing: attribute | summary
        }
    }

    fieldset default {
        fields: title, body, tags
    }

    fieldset semantic {
        fields: title, body
    }
}
```

and a corresponding query:

```sql
select * from docs where default contains (
    {
        grammar:"weakAnd",
        targetHits:20
    }userInput(@query)
);
```

If typo tolerance is desired for user-entered queries, you can instead use fuzzy matching on selected fields:

```sql
select * from docs where title contains (
    {maxEditDistance:2}fuzzy(@query)
)
or body contains (
    {maxEditDistance:2}fuzzy(@query)
);
```

## Notes on "openly available templates"

Unlike Elasticsearch, Vespa does not provide built-in "analysis templates" (e.g., an "english analyzer" or "standard analyzer" that bundles stemming, stopwords, synonyms, and decompounding together). The common pattern is to:

* Enable stemming (`stemming: best`) on all full-text fields.
* Configure language-specific linguistic processing (including stopwords and optional decompounding) at the application level.
* Manage synonyms separately through synonym resources or query rewriting.
* Apply fuzzy matching selectively in YQL rather than as an index-time property.
* Use fieldsets to define logical search scopes.

This separation gives more control but requires assembling these capabilities explicitly rather than selecting a predefined analyzer template.




