import sys
import os
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtCore import Qt

# Стили
APP_STYLE = """
QMainWindow {
    background-color: #1a1a1a;
    border: 1px solid #343434;
    border-radius: 10px;
}

QPlainTextEdit {
    background-color: #1e1e1e;
    color: #d4d4d4;
    selection-background-color: #264F78;
    border: none;
    font-family: 'Consolas';
    font-size: 18px;
    padding: 8px;
    border-radius: 6px;
}

QTabWidget::pane {
    border: 0;
    background: #252526;
    border-radius: 8px;
}

QTabBar::tab {
    background: #2d2d2d;
    color: #cccccc;
    padding: 8px 16px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    font-family: 'Segoe UI';
    font-size: 14px;
    margin-right: 2px;
    transition: all 0.3s ease-in-out;
}

QTabBar::tab:selected {
    background: #1e1e1e;
    border-bottom: 2px solid #569cd6;
    font-weight: bold;
}

QTabBar::tab:hover {
    background: #323232;
}

QMenuBar {
    background-color: #252526;
    color: #cccccc;
    padding: 6px;
    border-bottom: 1px solid #353535;
    border-radius: 6px;
}

QMenuBar::item:selected {
    background-color: #3a3a3a;
    border-radius: 6px;
}

QMenu {
    background-color: #252526;
    color: #cccccc;
    border: 1px solid #454545;
    padding: 8px;
    border-radius: 8px;
}

QMenu::item {
    padding: 6px 24px;
    margin: 2px;
    border-radius: 6px;
    font-size: 14px;
    transition: all 0.2s ease-in-out;
}

QMenu::item:selected {
    background-color: #094771;
}

QToolBar {
    background: #333333;
    border: none;
    border-bottom: 1px solid #404040;
    padding: 4px;
    border-radius: 8px;
}

QToolButton {
    padding: 6px;
    border-radius: 6px;
    transition: background 0.3s ease-in-out;
}

QToolButton:hover {
    background: #404040;
}

QStatusBar {
    background: #252526;
    color: #909090;
    border-top: 1px solid #353535;
    font-family: 'Segoe UI';
    font-size: 12px;
    padding: 6px;
    border-radius: 6px;
}

QPushButton {
    background: #2b79c2;
    color: #ffffff;
    border: none;
    padding: 10px 20px;
    border-radius: 6px;
    font-family: 'Segoe UI';
    font-size: 14px;
    min-width: 100px;
    transition: all 0.3s ease-in-out;
}

QPushButton:hover {
    background: #3a8ad4;
}
"""

class CodeMap(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self.setFont(QFont("Consolas", 6))
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.setStyleSheet("background: #1a1a1a; color: #666666;")
        self.main_editor = None
        self.setCursor(Qt.CursorShape.OpenHandCursor)

    def set_main_editor(self, editor):
        self.main_editor = editor
        self.main_editor.verticalScrollBar().valueChanged.connect(self.update)
        self.main_editor.textChanged.connect(self.update_map)
        self.update_map()

    def update_map(self):
        if self.main_editor:
            self.setPlainText(self.main_editor.toPlainText())

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.main_editor:
            painter = QPainter(self.viewport())
            visible_rect = self.main_editor.viewport().rect()
            y1 = self.main_editor.verticalScrollBar().value()
            total = self.main_editor.verticalScrollBar().maximum() + visible_rect.height()
            ratio = self.height() / total if total > 0 else 0
            viewport_height = visible_rect.height() * ratio
            viewport_y = y1 * ratio
            painter.setPen(QColor(100, 100, 100, 150))
            painter.setBrush(QColor(80, 80, 80, 50))
            painter.drawRect(0, viewport_y, self.width(), viewport_height)
            cursor = self.main_editor.textCursor()
            line_pos = cursor.blockNumber() * self.fontMetrics().height()
            painter.setPen(QColor(66, 165, 245, 200))
            painter.drawLine(0, line_pos * ratio, self.width(), line_pos * ratio)

class SyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, parent, file_extension):
        super().__init__(parent)
        self.file_extension = file_extension.lower()
        self.highlighting_rules = []
        self.setup_rules()

    def setup_rules(self):
        # Общие правила
        string_format = QTextCharFormat()
        string_format.setForeground(QColor('#CE9178'))
        self.highlighting_rules.append((QRegularExpression(r'".*?"'), string_format))

        number_format = QTextCharFormat()
        number_format.setForeground(QColor('#B5CEA8'))
        self.highlighting_rules.append((QRegularExpression(r'\b\d+\b'), number_format))

        # Python правила
        if self.file_extension == '.py':
            keyword_format = QTextCharFormat()
            keyword_format.setForeground(QColor('#c92aff'))
            keyword_format.setFontWeight(QFont.Weight.Bold)
            keywords = {
                'and', 'as', 'assert', 'break', 'class', 'continue', 'def', 'del',
                'elif', 'else', 'except', 'False', 'finally', 'for', 'from', 'global',
                'if', 'import', 'in', 'is', 'lambda', 'None', 'nonlocal', 'not', 'or',
                'pass', 'raise', 'return', 'True', 'try', 'while', 'with', 'yield'
            }
            for word in keywords:
                self.highlighting_rules.append((QRegularExpression(r'\b' + word + r'\b'), keyword_format))

            function_format = QTextCharFormat()
            function_format.setForeground(QColor('#DCDCAA'))
            self.highlighting_rules.append((QRegularExpression(r'\bdef\s+(\w+)'), function_format))
            self.highlighting_rules.append((QRegularExpression(r'\bclass\s+(\w+)'), function_format))

            comment_format = QTextCharFormat()
            comment_format.setForeground(QColor('#6A9955'))
            comment_format.setFontItalic(True)
            self.highlighting_rules.append((QRegularExpression(r'#.*'), comment_format))

        # Batch правила
        elif self.file_extension in ('.bat', '.cmd'):
            batch_format = QTextCharFormat()
            batch_format.setForeground(QColor('#4EC9B0'))
            commands = {
                'call', 'cd', 'chdir', 'cls', 'copy', 'del', 'dir', 'echo', 'exit',
                'for', 'goto', 'if', 'pause', 'rem', 'ren', 'set', 'start', 'time',
                'title', 'type', 'ver', 'vol', 'reg', 'ping', 'net', 'taskkill'
            }
            for word in commands:
                pattern = QRegularExpression(r'\b' + word + r'\b', QRegularExpression.PatternOption.CaseInsensitiveOption)
                self.highlighting_rules.append((pattern, batch_format))

            comment_format = QTextCharFormat()
            comment_format.setForeground(QColor('#6A9955'))
            comment_format.setFontItalic(True)
            self.highlighting_rules.append((QRegularExpression(r'::.*'), comment_format))

        # Java правила
        elif self.file_extension == '.java':
            keyword_format = QTextCharFormat()
            keyword_format.setForeground(QColor('#569CD6'))
            keyword_format.setFontWeight(QFont.Weight.Bold)
            keywords = {
                'abstract', 'assert', 'boolean', 'break', 'byte', 'case', 'catch', 'char',
                'class', 'const', 'continue', 'default', 'do', 'double', 'else', 'enum',
                'exports', 'extends', 'final', 'finally', 'float', 'for', 'goto', 'if',
                'implements', 'import', 'instanceof', 'int', 'interface', 'long', 'native',
                'new', 'package', 'private', 'protected', 'public', 'return', 'short', 'static',
                'strictfp', 'super', 'switch', 'synchronized', 'this', 'throw', 'throws', 'transient',
                'try', 'void', 'volatile', 'while'
            }
            for word in keywords:
                self.highlighting_rules.append((QRegularExpression(r'\b' + word + r'\b'), keyword_format))

            comment_format = QTextCharFormat()
            comment_format.setForeground(QColor('#6A9955'))
            comment_format.setFontItalic(True)
            self.highlighting_rules.append((QRegularExpression(r'//.*'), comment_format))
            self.highlighting_rules.append((QRegularExpression(r'/\*.*?\*/', QRegularExpression.PatternOption.DotMatchesEverythingOption), comment_format))

        # C++ правила
        elif self.file_extension in ('.cpp', '.hpp'):
            keyword_format = QTextCharFormat()
            keyword_format.setForeground(QColor('#569CD6'))
            keyword_format.setFontWeight(QFont.Weight.Bold)
            keywords = {
                'alignas', 'alignof', 'and', 'and_eq', 'asm', 'auto', 'bool', 'break', 'case',
                'catch', 'char', 'char16_t', 'char32_t', 'class', 'compl', 'const', 'const_cast',
                'constexpr', 'continue', 'decltype', 'default', 'delete', 'do', 'double', 'dynamic_cast',
                'else', 'enum', 'export', 'extern', 'false', 'float', 'for', 'friend', 'goto', 'if',
                'inline', 'int', 'long', 'mutable', 'namespace', 'new', 'noexcept', 'not', 'not_eq',
                'nullptr', 'operator', 'or', 'or_eq', 'private', 'protected', 'public', 'register',
                'reinterpret_cast', 'return', 'short', 'signed', 'sizeof', 'static', 'static_assert',
                'static_cast', 'struct', 'switch', 'template', 'this', 'throw', 'true', 'try', 'typedef',
                'typeid', 'typename', 'union', 'unsigned', 'using', 'virtual', 'void', 'volatile', 'wchar_t',
                'while'
            }
            for word in keywords:
                self.highlighting_rules.append((QRegularExpression(r'\b' + word + r'\b'), keyword_format))

            comment_format = QTextCharFormat()
            comment_format.setForeground(QColor('#6A9955'))
            comment_format.setFontItalic(True)
            self.highlighting_rules.append((QRegularExpression(r'//.*'), comment_format))
            self.highlighting_rules.append((QRegularExpression(r'/\*.*?\*/', QRegularExpression.PatternOption.DotMatchesEverythingOption), comment_format))

    def highlightBlock(self, text):
        for pattern, format in self.highlighting_rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)

class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.code_editor = editor

    def sizeHint(self):
        return QSize(self.code_editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(event.rect(), QColor(30, 30, 30))
        block = self.code_editor.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.code_editor.blockBoundingGeometry(block).translated(self.code_editor.contentOffset()).top()
        bottom = top + self.code_editor.blockBoundingRect(block).height()
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                painter.setPen(QColor(139, 148, 158))
                painter.drawText(0, int(top), self.width() - 10, self.code_editor.fontMetrics().height(), Qt.AlignmentFlag.AlignRight, str(block_number + 1))
            block = block.next()
            top = bottom
            bottom = top + self.code_editor.blockBoundingRect(block).height()
            block_number += 1

class CodeEditor(QPlainTextEdit):
    cursor_position_changed = pyqtSignal(int, int)

    def __init__(self, file_extension=''):
        super().__init__()
        self.file_extension = file_extension
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.setTabStopDistance(QFontMetricsF(self.font()).horizontalAdvance(' ') * 4)
        self.cursorPositionChanged.connect(self.update_cursor_position)
        self.highlighter = SyntaxHighlighter(self.document(), self.file_extension)
        self.init_line_numbers()
        self.highlight_current_line()

    def init_line_numbers(self):
        self.line_number_area = LineNumberArea(self)
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.update_line_number_area_width(0)

    def line_number_area_width(self):
        digits = len(str(max(1, self.blockCount())))
        return 25 + self.fontMetrics().horizontalAdvance('9') * digits

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))

    def update_cursor_position(self):
        cursor = self.textCursor()
        line = cursor.blockNumber() + 1
        col = cursor.columnNumber() + 1
        self.cursor_position_changed.emit(line, col)

    def highlight_current_line(self):
        extra_selections = []
        selection = QTextEdit.ExtraSelection()
        line_color = QColor(35, 35, 35)
        selection.format.setBackground(line_color)
        selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
        selection.cursor = self.textCursor()
        selection.cursor.clearSelection()
        extra_selections.append(selection)
        self.setExtraSelections(extra_selections)

class ModernTabWidget(QTabWidget):
    def __init__(self):
        super().__init__()
        self.setTabsClosable(True)
        self.setMovable(True)
        self.tabCloseRequested.connect(self.close_tab)
        self.setDocumentMode(False)
        self.setDocumentMode(False)  # Отключаем documentMode
        self.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: #252526; /* или любой другой цвет фона */
            }
            QTabBar::tab {
                background: #2d2d2d;
                color: #cccccc;
                padding: 8px 16px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-family: 'Segoe UI';
                font-size: 14px;
                margin-right: 2px;
                transition: all 0.3s ease-in-out;
            }
            QTabBar::tab:selected {
                background: #1e1e1e;
                border-bottom: 2px solid #569cd6;
                font-weight: bold;
            }
            QTabBar::tab:hover {
                background: #323232;
            }
        """)

    def add_new_tab(self, content='', title='Untitled'):
        file_extension = os.path.splitext(title)[1]
        editor = CodeEditor(file_extension)
        editor.setPlainText(content)
        self.addTab(editor, title)
        self.setCurrentIndex(self.count()-1)
        return editor

    def close_tab(self, index):
        if self.count() > 1:
            self.removeTab(index)

class FileExplorer(QTreeView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.setModel(QFileSystemModel())
        self.model().setRootPath(QDir.currentPath())
        self.setRootIndex(self.model().index(QDir.currentPath()))
        self.doubleClicked.connect(self.open_file)
        self.setHeaderHidden(True)
        self.setIndentation(20)
        self.setFrameShape(QFrame.Shape.NoFrame)
        for i in range(1, 4):
            self.hideColumn(i)

    def open_file(self, index):
        path = self.model().filePath(index)
        if os.path.isfile(path):
            try:
                with open(path, 'r') as f:
                    content = f.read()
                filename = os.path.basename(path)
                self.main_window.add_new_tab(content, filename)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open file:\n{str(e)}")

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        layout = QVBoxLayout()
        self.font_size = QSpinBox()
        self.font_size.setRange(12, 24)
        self.font_size.setValue(15)
        save_btn = QPushButton("Apply Settings")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(QLabel("Font Size:"))
        layout.addWidget(self.font_size)
        layout.addWidget(save_btn)
        self.setLayout(layout)

    def save_settings(self):
        font_size = self.font_size.value()
        font = QFont("Consolas", font_size)
        QApplication.instance().setFont(font)
        self.accept()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(APP_STYLE)
        self.settings = QSettings("CodeEditorPro", "Settings")
        self.init_ui()
        self.init_advanced_ui()
        

    def init_ui(self):
        self.setWindowTitle("Code Editor Pro")
        self.resize(self.settings.value("window_size", QSize(800, 600)))
        self.move(self.settings.value("window_pos", QPoint(100, 100)))
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.tabs = ModernTabWidget()
        self.splitter.addWidget(self.tabs)
        self.splitter.setSizes([800, 200])
        self.setCentralWidget(self.splitter)
        
        self.create_actions()
        self.create_main_menu()
        self.create_toolbars()
        self.create_statusbar()
        
        self.add_new_tab()

    def init_advanced_ui(self):
        self.file_explorer = FileExplorer(self)
        dock = QDockWidget("Explorer", self)
        dock.setWidget(self.file_explorer)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)

        self.settings_dialog = SettingsDialog(self)
        self.actions['settings'] = QAction("Settings", self)
        self.actions['settings'].triggered.connect(self.settings_dialog.exec)
        
        view_menu = self.menuBar().addMenu("View")
        view_menu.addAction(dock.toggleViewAction())

    def add_new_tab(self, content='', title='Untitled'):
        editor = self.tabs.add_new_tab(content, title)
        editor.cursor_position_changed.connect(self.update_status_bar)
        return editor

    def update_status_bar(self, line, col):
        self.status_bar.showMessage(f"Line: {line}, Column: {col}")

    def create_actions(self):
        self.actions = {
            'new': QAction("New", self),
            'open': QAction("Open", self),
            'save': QAction("Save", self),
            'save_as': QAction("Save As", self),
            'exit': QAction("Exit", self),
            'undo': QAction("Undo", self),
            'redo': QAction("Redo", self),
            'find': QAction("Find", self),
            'replace': QAction("Replace", self),
        }

        shortcuts = {
            'new': "Ctrl+N",
            'open': "Ctrl+O",
            'save': "Ctrl+S",
            'save_as': "Ctrl+Shift+S",
            'exit': "Ctrl+Q",
            'undo': "Ctrl+Z",
            'redo': "Ctrl+Shift+Z",
            'find': "Ctrl+F",
            'replace': "Ctrl+H"
        }

        for name, action in self.actions.items():
            action.setShortcut(shortcuts.get(name, ""))
        
        self.actions['new'].triggered.connect(self.new_file)
        self.actions['open'].triggered.connect(self.open_file)
        self.actions['save'].triggered.connect(self.save_file)
        self.actions['save_as'].triggered.connect(self.save_file_as)
        self.actions['exit'].triggered.connect(self.close)
        self.actions['undo'].triggered.connect(lambda: self.tabs.currentWidget().undo())
        self.actions['redo'].triggered.connect(lambda: self.tabs.currentWidget().redo())
        self.actions['find'].triggered.connect(self.show_find_dialog)
        self.actions['replace'].triggered.connect(self.show_replace_dialog)

    def create_main_menu(self):
        menu_bar = self.menuBar()
        
        file_menu = menu_bar.addMenu("File")
        file_menu.addAction(self.actions['new'])
        file_menu.addAction(self.actions['open'])
        file_menu.addAction(self.actions['save'])
        file_menu.addAction(self.actions['save_as'])
        file_menu.addSeparator()
        file_menu.addAction(self.actions['exit'])

        edit_menu = menu_bar.addMenu("Edit")
        edit_menu.addAction(self.actions['undo'])
        edit_menu.addAction(self.actions['redo'])
        edit_menu.addSeparator()
        edit_menu.addAction(self.actions['find'])
        edit_menu.addAction(self.actions['replace'])

    def create_toolbars(self):
        main_toolbar = QToolBar("Main Toolbar")
        main_toolbar.setMovable(False)
        
        main_toolbar.addAction(self.actions['new'])
        main_toolbar.addAction(self.actions['open'])
        main_toolbar.addAction(self.actions['save'])
        main_toolbar.addSeparator()
        main_toolbar.addAction(self.actions['undo'])
        main_toolbar.addAction(self.actions['redo'])
        main_toolbar.addSeparator()
        main_toolbar.addAction(self.actions['find'])
        main_toolbar.addAction(self.actions['replace'])
        
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, main_toolbar)

    def create_statusbar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def new_file(self):
        self.add_new_tab()

    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            "",
            "All Files (*);;Text Files (*.txt);;Python Files (*.py)"
        )
        if filename:
            try:
                with open(filename, 'r') as f:
                    content = f.read()
                self.add_new_tab(content, os.path.basename(filename))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open file:\n{str(e)}")

    def save_file(self):
        current_editor = self.tabs.currentWidget()
        if current_editor:
            filename = self.tabs.tabText(self.tabs.currentIndex())
            if filename == 'Untitled':
                self.save_file_as()
            else:
                try:
                    with open(filename, 'w') as f:
                        f.write(current_editor.toPlainText())
                    self.status_bar.showMessage(f"Saved: {filename}")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to save file:\n{str(e)}")

    def save_file_as(self):
        current_editor = self.tabs.currentWidget()
        if current_editor:
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Save File",
                "",
                "All Files (*);;Text Files (*.txt);;Python Files (*.py)"
            )
            if filename:
                try:
                    with open(filename, 'w') as f:
                        f.write(current_editor.toPlainText())
                    self.tabs.setTabText(self.tabs.currentIndex(), filename)
                    self.status_bar.showMessage(f"Saved: {filename}")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to save file:\n{str(e)}")

    def show_find_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Find")
        dialog.setStyleSheet("""
            QDialog { background: #252526; }
            QLabel { color: #cccccc; }
            QLineEdit { 
                background: #333333; 
                color: white; 
                border: 1px solid #454545;
                padding: 6px;
            }
            QPushButton { 
                background: #2b79c2; 
                color: white;
                padding: 8px;
                min-width: 80px;
            }
        """)
        layout = QVBoxLayout()
        
        self.find_field = QLineEdit()
        find_button = QPushButton("Find Next")
        find_button.clicked.connect(lambda: self.find_text(self.find_field.text()))
        
        layout.addWidget(QLabel("Find:"))
        layout.addWidget(self.find_field)
        layout.addWidget(find_button)
        dialog.setLayout(layout)
        dialog.exec()

    def show_replace_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Replace")
        dialog.setStyleSheet("""
            QDialog { background: #252526; }
            QLabel { color: #cccccc; }
            QLineEdit { 
                background: #333333; 
                color: white; 
                border: 1px solid #454545;
                padding: 6px;
            }
            QPushButton { 
                background: #2b79c2; 
                color: white;
                padding: 8px;
                min-width: 80px;
            }
        """)
        layout = QVBoxLayout()
        
        self.find_replace_field = QLineEdit()
        self.replace_field = QLineEdit()
        replace_button = QPushButton("Replace")
        replace_all_button = QPushButton("Replace All")
        
        replace_button.clicked.connect(self.replace_text)
        replace_all_button.clicked.connect(self.replace_all_text)
        
        layout.addWidget(QLabel("Find:"))
        layout.addWidget(self.find_replace_field)
        layout.addWidget(QLabel("Replace with:"))
        layout.addWidget(self.replace_field)
        layout.addWidget(replace_button)
        layout.addWidget(replace_all_button)
        dialog.setLayout(layout)
        dialog.exec()

    def find_text(self, text):
        current_editor = self.tabs.currentWidget()
        if current_editor and text:
            cursor = current_editor.textCursor()
            document = current_editor.document()
            found_cursor = document.find(text, cursor)
            if not found_cursor.isNull():
                current_editor.setTextCursor(found_cursor)
            else:
                QMessageBox.information(self, "Find", "Text not found.")

    def replace_text(self):
        current_editor = self.tabs.currentWidget()
        if current_editor:
            find_text = self.find_replace_field.text()
            replace_text = self.replace_field.text()
            cursor = current_editor.textCursor()
            if cursor.hasSelection() and cursor.selectedText() == find_text:
                cursor.insertText(replace_text)
            self.find_text(find_text)

    def replace_all_text(self):
        current_editor = self.tabs.currentWidget()
        if current_editor:
            find_text = self.find_replace_field.text()
            replace_text = self.replace_field.text()
            document = current_editor.document()
            cursor = document.rootFrame().firstCursorPosition()
            count = 0
            
            while True:
                cursor = document.find(find_text, cursor)
                if cursor.isNull():
                    break
                cursor.insertText(replace_text)
                count += 1
            
            QMessageBox.information(self, "Replace All", f"Replaced {count} occurrences.")

    def closeEvent(self, event):
        self.settings.setValue("window_size", self.size())
        self.settings.setValue("window_pos", self.pos())
        reply = QMessageBox.question(
            self,
            "Exit",
            "Are you sure you want to exit?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Установка темной палитры
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.ColorRole.Window, QColor(37, 37, 38))
    dark_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.Base, QColor(30, 30, 30))
    dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(37, 37, 38))
    dark_palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.Button, QColor(43, 43, 43))
    dark_palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
    app.setPalette(dark_palette)
    
    font = QFont("Consolas", 12)  # Изменено
    app.setFont(font)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())