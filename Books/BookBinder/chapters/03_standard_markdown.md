<!-- @chapter: Standard Markdown Syntax -->

<!-- @index-term: markdown -->
<!-- @index-term: syntax -->

# Standard Markdown Syntax

BookBinder supports the full CommonMark Markdown specification plus several extensions. This chapter covers all standard formatting that works in any Markdown renderer — and in BookBinder's PDF output.

## Headings

Use `#` characters for headings. BookBinder supports six levels:

```markdown
# Heading 1
## Heading 2
### Heading 3
#### Heading 4
##### Heading 5
###### Heading 6
```

<!-- @note: In a BookBinder book, `# Heading 1` is typically used only for chapter titles. Use `##` through `####` for section structure within chapters. -->

## Paragraphs and Line Breaks

Paragraphs are separated by blank lines. A single newline within text does not create a line break — it continues the same paragraph.

```markdown
This is the first paragraph. It can span
multiple lines in the source file.

This is the second paragraph.
```

To force a line break within a paragraph, end the line with two spaces or use `<br>`:

```markdown
Line one  
Line two (forced break with trailing spaces)

Line one<br>
Line two (forced break with HTML)
```

## Emphasis

```markdown
*italic text* or _italic text_
**bold text** or __bold text__
***bold italic*** or ___bold italic___
~~strikethrough~~
```

Renders as: *italic*, **bold**, ***bold italic***, ~~strikethrough~~.

## Lists

### Unordered Lists

```markdown
- Item one
- Item two
  - Nested item
  - Another nested item
- Item three
```

You can also use `*` or `+` as bullet markers.

### Ordered Lists

```markdown
1. First item
2. Second item
   1. Nested numbered item
   2. Another nested item
3. Third item
```

<!-- @tip: Markdown auto-numbers ordered lists. You can use `1.` for every item and the renderer will number them correctly. This makes reordering easier. -->

### Task Lists

```markdown
- [x] Completed task
- [ ] Incomplete task
- [ ] Another pending task
```

## Links

```markdown
[Link text](https://example.com)
[Link with title](https://example.com "Hover title")
<https://example.com>
```

Reference-style links keep your text readable:

```markdown
Read the [BookBinder docs][docs] for more information.

[docs]: https://github.com/yazici/BookBinder
```

## Images

```markdown
![Alt text](path/to/image.png)
![Alt text](path/to/image.png "Optional title")
```

Images are resolved relative to the Markdown file containing them. For more control over figures (captions, numbering, cross-references), use BookBinder's `@figure` marker described in the Extended Syntax chapter.

## Blockquotes

```markdown
> This is a blockquote.
> It can span multiple lines.
>
> > Nested blockquotes are supported.
```

Renders as:

> This is a blockquote.
> It can span multiple lines.
>
> > Nested blockquotes are supported.

## Code

### Inline Code

```markdown
Use the `make_a_book.py` script to build your PDF.
```

### Fenced Code Blocks

Use triple backticks with an optional language identifier for syntax highlighting:

````markdown
```python
def hello():
    print("Hello, BookBinder!")
```
````

<!-- @index-term: syntax highlighting -->

BookBinder uses Pygments for syntax highlighting. Supported languages include:

| Language | Identifier |
|----------|-----------|
| Python | `python` |
| JavaScript | `javascript` or `js` |
| TypeScript | `typescript` or `ts` |
| Bash/Shell | `bash` or `shell` |
| C++ | `cpp` or `c++` |
| C | `c` |
| Java | `java` |
| Rust | `rust` |
| Go | `go` |
| YAML | `yaml` |
| JSON | `json` |
| HTML | `html` |
| CSS | `css` |
| SQL | `sql` |
| Markdown | `markdown` or `md` |

And many more — any language Pygments supports will work.

### Indented Code Blocks

Four spaces of indentation also creates a code block (though fenced blocks are preferred):

```markdown
    def indented_code():
        return "This is a code block"
```

## Tables

Tables use pipes and hyphens:

```markdown
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Cell 1   | Cell 2   | Cell 3   |
| Cell 4   | Cell 5   | Cell 6   |
```

### Column Alignment

Use colons in the separator row:

```markdown
| Left | Center | Right |
|:-----|:------:|------:|
| L    |   C    |     R |
| L    |   C    |     R |
```

| Left | Center | Right |
|:-----|:------:|------:|
| L    |   C    |     R |
| L    |   C    |     R |

<!-- @note: Tables in BookBinder PDFs are styled by the active template. The `technical` template uses compact tables with alternating row colors. -->

## Horizontal Rules

Three or more hyphens, asterisks, or underscores on a line:

```markdown
---
***
___
```

All produce a horizontal rule. In BookBinder PDFs, these render as subtle dividers styled by the active theme.

## HTML in Markdown

BookBinder passes through inline HTML. This is useful for advanced formatting:

```markdown
<div style="text-align: center;">
  <em>Centered italic text</em>
</div>
```

<!-- @warning: Inline HTML works but may not style consistently across templates. Prefer Markdown syntax and BookBinder's semantic markers when possible. -->

## Escaping Special Characters

Use backslashes to escape Markdown syntax characters:

```markdown
\*not italic\*
\# not a heading
\[not a link\]
\`not code\`
```

Characters that can be escaped: `\` `` ` `` `*` `_` `{}` `[]` `()` `#` `+` `-` `.` `!` `|`

## Footnotes

```markdown
Here is a statement that needs a citation[^1].

[^1]: This is the footnote content.
```

Footnotes are collected and rendered at the bottom of the page (or section, depending on the template).

## Definition Lists

```markdown
Term 1
:   Definition of term 1

Term 2
:   Definition of term 2
:   Alternative definition
```

## Abbreviations

```markdown
The HTML specification is maintained by the W3C.

*[HTML]: Hyper Text Markup Language
*[W3C]: World Wide Web Consortium
```

When rendered, hovering over "HTML" or "W3C" shows the full expansion.

## Summary

BookBinder's standard Markdown support covers everything you need for technical writing:

| Feature | Syntax |
|---------|--------|
| Headings | `# H1` through `###### H6` |
| Bold | `**text**` |
| Italic | `*text*` |
| Code (inline) | `` `code` `` |
| Code (block) | ` ``` ` fences |
| Links | `[text](url)` |
| Images | `![alt](path)` |
| Lists | `- item` or `1. item` |
| Tables | Pipe syntax |
| Blockquotes | `> text` |
| Horizontal rule | `---` |

For BookBinder-specific features like includes, figures with captions, callouts, and more, see the next chapter on Extended Syntax.