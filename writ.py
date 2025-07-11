#!/usr/bin/env python3

import re
import os
from pathlib import Path
from typing import Optional, Tuple, List
from dataclasses import dataclass

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Header, Footer, TextArea, Static, Input, ListView, ListItem, Label, Button
from textual.binding import Binding
from textual.screen import Screen, ModalScreen
from textual.message import Message
from rich.console import Console
from rich.markdown import Markdown


@dataclass
class State:
    file: Optional[Path] = None
    modified: bool = False
    preview: bool = False
    currentDir: Path = Path.cwd()


class ConfirmModal(ModalScreen):
    def __init__(self, title: str, message: str):
        super().__init__()
        self.title = title
        self.message = message
        self.result = None
    
    def compose(self) -> ComposeResult:
        with Container(id="confirm-modal"):
            yield Static(self.title or "", id="title")
            yield Static(self.message or "", id="message")
            with Horizontal():
                yield Button("Yes", id="yes", variant="primary")
                yield Button("No", id="no", variant="default")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.result = event.button.id == "yes"
        self.dismiss(self.result)
    
    def on_key(self, event) -> None:
        if event.key == "escape":
            self.dismiss(False)


class FileBrowser(ModalScreen):
    def __init__(self, title: str, currentDir: Optional[Path] = None):
        super().__init__()
        self.title = title
        self.currentDir = currentDir or Path.cwd()
        self.result = None
        self.pathMap = {}
    
    def compose(self) -> ComposeResult:
        with Container(id="file-browser"):
            yield Static(self.title or "", id="title")
            yield Static(f"Current: {self.currentDir}", id="current-dir")
            self.fileList = ListView(id="file-list")
            yield self.fileList
            with Horizontal():
                yield Button("Select", id="select", variant="primary")
                yield Button("Cancel", id="cancel", variant="default")
    
    def on_mount(self) -> None:
        self.updateFileList()
    
    def updateFileList(self) -> None:
        self.fileList.clear()
        self.pathMap.clear()
        
        if self.currentDir.parent != self.currentDir:
            self.fileList.append(ListItem(Label(".."), id="parent"))
        
        try:
            items = sorted(self.currentDir.iterdir())
            for idx, item in enumerate(items):
                itemId = f"item_{idx}"
                self.pathMap[itemId] = item
                
                if item.is_dir():
                    self.fileList.append(ListItem(Label(f"📁 {item.name}"), id=itemId))
                elif item.suffix.lower() in ['.md', '.txt', '.markdown']:
                    self.fileList.append(ListItem(Label(f"📄 {item.name}"), id=itemId))
        except PermissionError:
            self.fileList.append(ListItem(Label("Permission denied"), id="error"))
    
    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.item.id == "parent":
            self.currentDir = self.currentDir.parent
        elif event.item.id == "error":
            return
        else:
            if event.item.id and event.item.id in self.pathMap:
                path = self.pathMap[event.item.id]
                if path.is_dir():
                    self.currentDir = path
                else:
                    self.result = path
                    self.dismiss(self.result)
                    return
        
        self.updateFileList()
        self.query_one("#current-dir", Static).update(f"Current: {self.currentDir}")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "select":
            selected = self.fileList.highlighted_child
            if selected and selected.id != "parent" and selected.id != "error" and selected.id in self.pathMap:
                path = self.pathMap[selected.id]
                if path.is_file():
                    self.result = path
                    self.dismiss(self.result)
        elif event.button.id == "cancel":
            self.dismiss(None)
    
    def on_key(self, event) -> None:
        if event.key == "escape":
            self.dismiss(None)


class InputModal(ModalScreen):
    def __init__(self, title: str, placeholder: str = ""):
        super().__init__()
        self.title = title
        self.placeholder = placeholder
        self.result = None
    
    def compose(self) -> ComposeResult:
        with Container(id="modal"):
            yield Static(self.title or "", id="title")
            self.input = Input(placeholder=self.placeholder, id="input")
            yield self.input
            if "Save As" in (self.title or ""):
                yield Static("(.md extension will be added automatically)", id="hint")
    
    def on_mount(self) -> None:
        self.input.focus()
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.result = event.value
        self.dismiss(self.result)
    
    def on_key(self, event) -> None:
        if event.key == "escape":
            self.dismiss(None)


class CustomTextArea(TextArea):
    BINDINGS = [
        Binding("up", "cursor_up", "Cursor up", show=False),
        Binding("down", "cursor_down", "Cursor down", show=False),
        Binding("left", "cursor_left", "Cursor left", show=False),
        Binding("right", "cursor_right", "Cursor right", show=False),
        Binding("ctrl+left", "cursor_word_left", "Cursor word left", show=False),
        Binding("ctrl+right", "cursor_word_right", "Cursor word right", show=False),
        Binding("home,ctrl+a", "cursor_line_start", "Cursor line start", show=False),
        Binding("end,ctrl+e", "cursor_line_end", "Cursor line end", show=False),
        Binding("pageup", "cursor_page_up", "Cursor page up", show=False),
        Binding("pagedown", "cursor_page_down", "Cursor page down", show=False),
        Binding("shift+up", "cursor_up(True)", "Cursor up select", show=False),
        Binding("shift+down", "cursor_down(True)", "Cursor down select", show=False),
        Binding("shift+left", "cursor_left(True)", "Cursor left select", show=False),
        Binding("shift+right", "cursor_right(True)", "Cursor right select", show=False),
        Binding("f6", "select_line", "Select line", show=False),
        Binding("f7", "select_all", "Select all", show=False),
        Binding("backspace", "delete_left", "Delete character left", show=False),
        Binding("delete,ctrl+d", "delete_right", "Delete character right", show=False),
        Binding("ctrl+x", "cut", "Cut", show=False),
        Binding("ctrl+c", "copy", "Copy", show=False),
        Binding("ctrl+v", "paste", "Paste", show=False),
        Binding("ctrl+z", "undo", "Undo", show=False),
        Binding("ctrl+y", "redo", "Redo", show=False),
        Binding("ctrl+j", "bold", "Bold", show=False, priority=True),
        Binding("ctrl+k", "italic", "Italic", show=False, priority=True),
        Binding("ctrl+u", "link", "Link", show=False, priority=True),
        Binding("f7", "code_block", "Code Block", show=False, priority=True),
        Binding("f8", "inline_code", "Inline Code", show=False, priority=True),
        Binding("f9", "list", "List", show=False, priority=True),
        Binding("f1", "h1", "H1", show=False, priority=True),
        Binding("f2", "h2", "H2", show=False, priority=True),
        Binding("f3", "h3", "H3", show=False, priority=True),
        Binding("f4", "h4", "H4", show=False, priority=True),
        Binding("f5", "h5", "H5", show=False, priority=True),
        Binding("f6", "h6", "H6", show=False, priority=True),
    ]

    def action_bold(self) -> None:
        getattr(self.app, 'action_bold', lambda: None)()
    
    def action_italic(self) -> None:
        getattr(self.app, 'action_italic', lambda: None)()
    
    def action_link(self) -> None:
        getattr(self.app, 'action_link', lambda: None)()
    
    def action_code_block(self) -> None:
        getattr(self.app, 'action_code_block', lambda: None)()
    
    def action_inline_code(self) -> None:
        getattr(self.app, 'action_inline_code', lambda: None)()
    
    def action_list(self) -> None:
        getattr(self.app, 'action_list', lambda: None)()
    
    def action_h1(self) -> None:
        getattr(self.app, 'action_h1', lambda: None)()
    
    def action_h2(self) -> None:
        getattr(self.app, 'action_h2', lambda: None)()
    
    def action_h3(self) -> None:
        getattr(self.app, 'action_h3', lambda: None)()
    
    def action_h4(self) -> None:
        getattr(self.app, 'action_h4', lambda: None)()
    
    def action_h5(self) -> None:
        getattr(self.app, 'action_h5', lambda: None)()
    
    def action_h6(self) -> None:
        getattr(self.app, 'action_h6', lambda: None)()


class Format:
    @staticmethod
    def bold(text: str, pos: int) -> Tuple[str, int]:
        return Format._wrap(text, pos, "**")
    
    @staticmethod
    def italic(text: str, pos: int) -> Tuple[str, int]:
        return Format._wrap(text, pos, "*")
    
    @staticmethod
    def inlineCode(text: str, pos: int) -> Tuple[str, int]:
        return Format._wrap(text, pos, "`")
    
    @staticmethod
    def _wrap(text: str, pos: int, wrapper: str) -> Tuple[str, int]:
        wlen = len(wrapper)
        
        left = max(0, pos - 20)
        right = min(len(text), pos + 20)
        search_text = text[left:right]
        search_pos = pos - left
        
        start_pattern = re.escape(wrapper)
        matches = list(re.finditer(start_pattern, search_text))
        
        for i in range(0, len(matches) - 1, 2):
            if i + 1 < len(matches):
                start_match = matches[i]
                end_match = matches[i + 1]
                
                if start_match.end() <= search_pos <= end_match.start():
                    actual_start = left + start_match.start()
                    actual_end = left + end_match.end()
                    content = text[actual_start + wlen:actual_end - wlen]
                    new_text = text[:actual_start] + content + text[actual_end:]
                    new_pos = actual_start + len(content)
                    return new_text, new_pos
        
        new_text = text[:pos] + wrapper + wrapper + text[pos:]
        new_pos = pos + wlen
        return new_text, new_pos
    
    @staticmethod
    def heading(text: str, pos: int, level: int) -> Tuple[str, int]:
        if not 1 <= level <= 6:
            return text, pos
        
        lines = text.split('\n')
        current_pos = 0
        target_line = 0
        
        for i, line in enumerate(lines):
            if current_pos + len(line) >= pos:
                target_line = i
                break
            current_pos += len(line) + 1
        
        line = lines[target_line]
        heading_match = re.match(r'^(#{1,6})\s*', line)
        
        if heading_match:
            new_line = '#' * level + ' ' + line[heading_match.end():]
        else:
            new_line = '#' * level + ' ' + line
        
        old_len = len(lines[target_line])
        lines[target_line] = new_line
        new_text = '\n'.join(lines)
        
        pos_in_line = pos - current_pos
        new_pos = current_pos + min(pos_in_line + (len(new_line) - old_len), len(new_line))
        
        return new_text, new_pos
    
    @staticmethod
    def link(text: str, pos: int) -> Tuple[str, int]:
        link_text = "[text](url)"
        new_text = text[:pos] + link_text + text[pos:]
        new_pos = pos + 1
        return new_text, new_pos
    
    @staticmethod
    def codeBlock(text: str, pos: int) -> Tuple[str, int]:
        lines = text.split('\n')
        current_pos = 0
        
        for i, line in enumerate(lines):
            if current_pos + len(line) >= pos:
                line_start = current_pos
                break
            current_pos += len(line) + 1
        else:
            line_start = len(text)
        
        if pos > 0 and text[pos - 1] != '\n':
            block = "\n```\n\n```\n"
            new_pos = pos + 5
        else:
            block = "```\n\n```\n"
            new_pos = pos + 4
        
        new_text = text[:pos] + block + text[pos:]
        return new_text, new_pos
    
    @staticmethod
    def listItem(text: str, pos: int) -> Tuple[str, int]:
        lines = text.split('\n')
        current_pos = 0
        target_line = 0
        
        for i, line in enumerate(lines):
            if current_pos + len(line) >= pos:
                target_line = i
                break
            current_pos += len(line) + 1
        
        line = lines[target_line]
        stripped = line.lstrip()
        
        if stripped.startswith('- '):
            indent = line[:len(line) - len(stripped)]
            new_line = indent + stripped[2:]
            pos_change = -2
        else:
            indent = line[:len(line) - len(stripped)]
            new_line = indent + '- ' + stripped
            pos_change = 2
        
        lines[target_line] = new_line
        new_text = '\n'.join(lines)
        new_pos = pos + pos_change
        
        return new_text, new_pos


class Preview(Static):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.content = ""
        self.can_focus = True
    
    def update_content(self, text: str) -> None:
        if not text.strip():
            self.update("")
            return
        
        self.content = text
        try:
            from rich.markdown import Markdown
            
            markdown = Markdown(text)
            self.update(markdown)
        except Exception as e:
            self.update(f"Preview Error: {str(e)}")
    



class Writ(App):
    CSS = """
    .editor {
        dock: left;
        width: 50%;
        height: 100%;
        overflow-y: auto;
    }
    
    .preview {
        dock: right;
        width: 50%;
        height: 100%;
        background: $surface;
        border-left: thick $primary;
        padding: 1;
        overflow-y: auto;
        scrollbar-gutter: stable;
        scrollbar-size: 1 1;
    }
    
    .hidden {
        display: none;
    }
    
    .editor-full {
        width: 100%;
        overflow-y: auto;
    }
    
    #editor {
        scrollbar-gutter: stable;
    }
    
    #preview-content {
        width: 100%;
        height: auto;
        padding: 1;
    }
    
    .status {
        dock: bottom;
        height: 1;
        background: $primary;
        color: $text;
        padding: 0 1;
    }
    
    #modal {
        align: center middle;
        background: $surface;
        border: thick $primary;
        width: 60;
        height: 10;
        padding: 1;
    }
    
    #confirm-modal {
        align: center middle;
        background: $surface;
        border: thick $primary;
        width: 50;
        height: 10;
        padding: 1;
    }
    
    #file-browser {
        align: center middle;
        background: $surface;
        border: thick $primary;
        width: 90;
        height: 30;
        padding: 1;
    }
    
    #title {
        text-align: center;
        margin-bottom: 1;
    }
    
    #file-list {
        height: 20;
        margin: 1 0;
    }
    
    #input {
        width: 100%;
        margin: 1 0;
    }
    
    #hint {
        text-align: center;
        color: $text-muted;
        margin-top: 1;
    }
    """
    
    BINDINGS = [
        Binding("ctrl+n", "new", "New"),
        Binding("ctrl+o", "open", "Open"),
        Binding("ctrl+s", "save", "Save"),
        Binding("ctrl+shift+s", "saveAs", "Save As"),
        Binding("ctrl+q", "quit", "Quit"),
        Binding("f12", "preview", "Preview"),
    ]
    
    def __init__(self):
        super().__init__()
        self.state = State()
        self.format = Format()
    
    def compose(self) -> ComposeResult:
        yield Header()
        
        with Container():
            with Horizontal():
                initial_text = self._get_initial_text()
                self.editor = CustomTextArea(
                    text=initial_text,
                    language="markdown",
                    show_line_numbers=True,
                    classes="editor-full",
                    id="editor"
                )
                yield self.editor
                
                with ScrollableContainer(classes="preview hidden", id="preview-container"):
                    self.preview = Preview(id="preview-content")
                    yield self.preview
        
        self.status = Static(self._status_text(), classes="status")
        yield self.status
        
        yield Footer()
    
    def on_mount(self) -> None:
        self._update_preview()
        self._update_status()
        self.editor.focus()
    
    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        self.state.modified = True
        self._update_preview()
        self._update_status()
    
    def on_resize(self, event) -> None:
        if self.state.preview:
            self.call_after_refresh(self._update_preview)
    
    def _update_preview(self) -> None:
        if hasattr(self, 'preview'):
            try:
                self.preview.update_content(self.editor.text)
            except Exception as e:
                self.preview.update(f"Preview Error: {str(e)}")
    
    def _update_status(self) -> None:
        if hasattr(self, 'status'):
            self.status.update(self._status_text())
    
    def _get_initial_text(self) -> str:
        try:
            test_doc = Path("test-doc.md")
            if test_doc.exists():
                return test_doc.read_text(encoding='utf-8')
        except Exception:
            pass
        return "# Welcome to Writ\n\nStart writing..."
    
    def _status_text(self) -> str:
        name = self.state.file.name if self.state.file else "untitled"
        mod = " •" if self.state.modified else ""
        prev = "ON" if self.state.preview else "OFF"
        return f"{name}{mod} | Preview: {prev}"
    
    def _format_text(self, func, *args):
        pos = self._get_cursor_position()
        text, new_pos = func(self.editor.text, pos, *args)
        self.editor.text = text
        self.call_after_refresh(self._set_cursor_position, new_pos)
    
    def _get_cursor_position(self) -> int:
        row, col = self.editor.cursor_location
        lines = self.editor.text.split('\n')
        pos = 0
        
        for i in range(row):
            if i < len(lines):
                pos += len(lines[i]) + 1
        
        if row < len(lines):
            pos += min(col, len(lines[row]))
        
        return pos
    
    def _set_cursor_position(self, pos: int) -> None:
        lines = self.editor.text.split('\n')
        current_pos = 0
        
        for row, line in enumerate(lines):
            if current_pos + len(line) >= pos:
                col = pos - current_pos
                self.editor.cursor_location = (row, col)
                return
            current_pos += len(line) + 1
        
        if lines:
            self.editor.cursor_location = (len(lines) - 1, len(lines[-1]))
    
    def action_new(self) -> None:
        self.run_worker(self._new_worker)
    
    def action_open(self) -> None:
        self.run_worker(self._open_worker)
    
    def action_save(self) -> None:
        self.run_worker(self._save_worker)
    
    def action_saveAs(self) -> None:
        self.run_worker(self._save_as_worker)
    
    def action_quit(self) -> None:
        self.run_worker(self._quit_worker)
    
    async def _new_worker(self) -> None:
        if self.state.modified:
            confirm = ConfirmModal("Unsaved Changes", "You have unsaved changes. Continue?")
            if not await self.push_screen_wait(confirm):
                return
        
        self.state.file = None
        self.state.modified = False
        self.editor.text = ""
        self._update_status()
        self._update_preview()
    
    async def _open_worker(self) -> None:
        if self.state.modified:
            confirm = ConfirmModal("Unsaved Changes", "You have unsaved changes. Continue?")
            if not await self.push_screen_wait(confirm):
                return
        
        browser = FileBrowser("Open File", self.state.currentDir)
        path = await self.push_screen_wait(browser)
        if path:
            try:
                if path.exists():
                    self.state.file = path
                    self.state.currentDir = path.parent
                    self.editor.text = path.read_text(encoding='utf-8')
                    self.state.modified = False
                    self._update_status()
                    self._update_preview()
                    self.notify(f"Opened: {path.name}")
                else:
                    self.notify(f"File not found: {path}")
            except Exception as e:
                self.notify(f"Error opening file: {e}")
    
    async def _save_worker(self) -> None:
        if self.state.file:
            try:
                self.state.file.write_text(self.editor.text, encoding='utf-8')
                self.state.modified = False
                self._update_status()
                self.notify(f"Saved: {self.state.file.name}")
            except Exception as e:
                self.notify(f"Error saving file: {e}")
        else:
            await self._save_as_worker()
    
    async def _save_as_worker(self) -> None:
        modal = InputModal("Save As (Markdown file):", "filename")
        path = await self.push_screen_wait(modal)
        if path:
            try:
                filePath = Path(path)
                
                if not filePath.suffix:
                    filePath = filePath.with_suffix('.md')
                
                if not filePath.is_absolute():
                    filePath = self.state.currentDir / filePath
                
                if filePath.exists():
                    confirm = ConfirmModal("File Exists", f"File {filePath.name} exists. Overwrite?")
                    if not await self.push_screen_wait(confirm):
                        return
                
                filePath.parent.mkdir(parents=True, exist_ok=True)
                filePath.write_text(self.editor.text, encoding='utf-8')
                self.state.file = filePath
                self.state.currentDir = filePath.parent
                self.state.modified = False
                self._update_status()
                self.notify(f"Saved: {filePath.name}")
            except Exception as e:
                self.notify(f"Error saving file: {e}")
    
    async def _quit_worker(self) -> None:
        if self.state.modified:
            confirm = ConfirmModal("Unsaved Changes", "You have unsaved changes. Exit anyway?")
            if not await self.push_screen_wait(confirm):
                return
        self.exit()
    
    def action_preview(self) -> None:
        self.state.preview = not self.state.preview
        preview_panel = self.query_one("#preview-container")
        editor = self.query_one("#editor")
        
        if self.state.preview:
            preview_panel.remove_class("hidden")
            editor.remove_class("editor-full")
            editor.add_class("editor")
            self._update_preview()
        else:
            preview_panel.add_class("hidden")
            editor.remove_class("editor")
            editor.add_class("editor-full")
        
        self._update_status()
    
    def action_bold(self) -> None:
        self._format_text(self.format.bold)
    
    def action_italic(self) -> None:
        self._format_text(self.format.italic)
    
    def action_inline_code(self) -> None:
        self._format_text(self.format.inlineCode)
    
    def action_link(self) -> None:
        self._format_text(self.format.link)
    
    def action_code_block(self) -> None:
        self._format_text(self.format.codeBlock)
    
    def action_list(self) -> None:
        self._format_text(self.format.listItem)
    
    def action_h1(self) -> None:
        self._format_text(self.format.heading, 1)
    
    def action_h2(self) -> None:
        self._format_text(self.format.heading, 2)
    
    def action_h3(self) -> None:
        self._format_text(self.format.heading, 3)
    
    def action_h4(self) -> None:
        self._format_text(self.format.heading, 4)
    
    def action_h5(self) -> None:
        self._format_text(self.format.heading, 5)
    
    def action_h6(self) -> None:
        self._format_text(self.format.heading, 6)


def main():
    app = Writ()
    app.run()


if __name__ == "__main__":
    main() 