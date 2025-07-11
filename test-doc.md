# Writ Markdown Editor Test Document

This document tests various markdown features supported by the enhanced preview panel using Rich's built-in markdown rendering. This document is intentionally long to test the scrolling functionality.

## Basic Formatting

**Bold text** and *italic text* can be combined like ***bold italic***.

You can also use `inline code` within text.

## Headings

### This is an H3
#### This is an H4
##### This is an H5
###### This is an H6

## Lists

### Unordered Lists
- Item 1
- Item 2
  - Nested item 2.1
  - Nested item 2.2
- Item 3

### Ordered Lists
1. First item
2. Second item
   1. Nested item 2.1
   2. Nested item 2.2
3. Third item

## Code Blocks

### Python Code
```python
def hello_world():
    print("Hello, World!")
    return True

class MarkdownEditor:
    def __init__(self, title="Writ"):
        self.title = title
        self.content = ""
    
    def update_content(self, text):
        self.content = text
        return self.render_preview()
    
    def render_preview(self):
        # This is a sample method
        return f"Preview: {self.content}"

if __name__ == "__main__":
    editor = MarkdownEditor()
    editor.update_content("# Hello World")
    hello_world()
```

### JavaScript Code
```javascript
function greet(name) {
    console.log(`Hello, ${name}!`);
    return true;
}

class MarkdownEditor {
    constructor(title = "Writ") {
        this.title = title;
        this.content = "";
    }
    
    updateContent(text) {
        this.content = text;
        return this.renderPreview();
    }
    
    renderPreview() {
        return `Preview: ${this.content}`;
    }
}

const editor = new MarkdownEditor();
editor.updateContent("# Hello World");
greet("World");
```

## Tables

| Feature | Status | Notes | Version |
|---------|--------|-------|---------|
| Headers | ✅ | Working | 1.0 |
| Lists | ✅ | Working | 1.0 |
| Code | ✅ | Working | 1.0 |
| Tables | ✅ | Working | 1.0 |
| Scrolling | ✅ | Testing | 1.1 |

## Links

[Visit GitHub](https://github.com)
[Visit Python.org](https://python.org)
[Visit Textual](https://textual.textualize.io)

## Blockquotes

> This is a blockquote.
> It can span multiple lines.
>
> You can also nest blockquotes.

> Here's another blockquote to add more content.
> This helps demonstrate the scrolling functionality.

## Horizontal Rules

---

## More Content for Scrolling

This section is added to make the document longer and test the scrolling functionality.

### Section 1
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.

### Section 2
Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

### Section 3
Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo.

### Section 4
Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt.

### Section 5
Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem.

### Section 6
Ut enim ad minima veniam, quis nostrum exercitationem ullam corporis suscipit laboriosam, nisi ut aliquid ex ea commodi consequatur? Quis autem vel eum iure reprehenderit qui in ea voluptate velit esse quam nihil molestiae consequatur.

### Section 7
At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores et quas molestias excepturi sint occaecati cupiditate non provident.

### Section 8
Similique sunt in culpa qui officia deserunt mollitia animi, id est laborum et dolorum fuga. Et harum quidem rerum facilis est et expedita distinctio. Nam libero tempore, cum soluta nobis est eligendi optio cumque nihil impedit quo minus id quod maxime placeat facere possimus.

## Images

![Alt text](https://via.placeholder.com/150x50/blue/white?text=Image)

## Final Section

This is the final section of the document. If you can see this in the preview panel, it means the scrolling functionality is working correctly!

---

*This document demonstrates the preview functionality of Writ with scrolling capabilities.*