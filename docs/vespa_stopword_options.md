If you're using **Lucene Linguistics** (the recommended approach when you need custom analyzers), you can configure a stopword filter in `services.xml` like this:

```xml
<services version="1.0">
    <container id="default" version="1.0">
        <search/>

        <component id="linguistics"
                   class="com.yahoo.language.lucene.LuceneLinguistics"
                   bundle="my-vespa-app">
            <config name="com.yahoo.language.lucene.lucene-analysis">
                <configDir>lucene-linguistics</configDir>

                <analysis>
                    <item key="profile=standardStopStem;language=en">
                        <tokenizer>
                            <name>standard</name>
                        </tokenizer>

                        <tokenFilters>

                            <!-- Custom stopword list -->
                            <item>
                                <name>stop</name>
                                <conf>
                                    <item key="words">en/stopwords.txt</item>
                                    <item key="ignoreCase">true</item>
                                </conf>
                            </item>

                            <!-- Optional stemming -->
                            <item>
                                <name>englishMinimalStem</name>
                            </item>

                        </tokenFilters>
                    </item>
                </analysis>

            </config>
        </component>
    </container>

    <content id="content" version="1.0">
        ...
    </content>
</services>
```

Your application package would then contain:

```text
application/
├── services.xml
├── schemas/
│   └── document.sd
└── lucene-linguistics/
    └── en/
        └── stopwords.txt
```

Example `stopwords.txt`:

```text
a
an
the
and
or
of
to
for
with
in
on
```

Or for a domain-specific search engine:

```text
document
page
chapter
section
figure
table
```

Finally, reference the profile from your schema:

```vespa
field body type string {
    indexing: index | summary

    match {
        text
    }

    linguistics {
        profile: standardStopStem
    }

    stemming: best
}
```

### Notes

* `ignoreCase=true` makes stopword matching case-insensitive.
* The stopword list is applied **both at indexing and query time**, ensuring consistent analysis. ([Vespa. Big data. Real time. Open source.][1])
* This configuration is specific to the **Lucene Linguistics** component. Vespa's default OpenNLP linguistics does not provide a `services.xml` option for supplying a custom stopword file. ([Vespa. Big data. Real time. Open source.][2])

[1]: https://docs.vespa.ai/en/linguistics/lucene-linguistics.html?utm_source=chatgpt.com "Lucene Linguistics | Vespa. Big data. Real time. Open source."
[2]: https://docs.vespa.ai/en/linguistics/linguistics.html?utm_source=chatgpt.com "Linguistics in Vespa | Vespa. Big data. Real time. Open source."
