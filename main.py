from PyQt6.QtWidgets import (
    QWidget, QApplication, QMenuBar, QTextEdit, QVBoxLayout, QMainWindow, 
    QFileDialog, QMessageBox, QDialog, QDialogButtonBox, QToolBar
    )
from PyQt6.QtGui import (
    QWindow, QFont, QColor, QPalette, QAction, QFontMetricsF, QFont
    )
from PyQt6.QtCore import (
    Qt, QEvent,
    )

import subprocess
import sys
import qdarktheme
from pathlib import Path
from functools import partial

settings = {
    "font_size": 14,
    "font_color": "white",
    "bg_font_color": "black",
    "font_weight": 500,
    "tab_width": 7,
}


class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.curFileName = "*"
        self.openedFiles = ["*"]
        self.saved = True

        app.setStyleSheet(qdarktheme.load_stylesheet())
        self.size = (700, 700)
        self.init_actions()
        self.init_ui()
        self.show()

    def init_ui(self):
        self.setGeometry(500, 500, self.size[0], self.size[1])
        self.setWindowTitle("Editor")
        self.init_menu()
        self.init_side_bar()
        self.init_editor()
        

    def init_editor(self):
        self.editor = QTextEdit(self)
        self.editor.setGeometry(self.sidebar.widthMM()-25, 30, self.size[0] - 10, self.size[1] - 40)
        self.editor.setFontPointSize(settings["font_size"])
        self.editor.setTextColor(QColor(settings["font_color"]))
        self.editor.setFontWeight(settings["font_weight"])
        self.editor.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.editor.setTabStopDistance(QFontMetricsF(self.editor.font()).horizontalAdvance(' ') * settings["tab_width"])
        self.editor.textChanged.connect(self.textChangedEvent)
        #self.font = self.editor.font()
        #self.font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing,3)
        #self.editor.setFont(self.font)

    def init_menu(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("Файл")

        file_menu.addAction(self.save_file)
        file_menu.addAction(self.save_file_as)
        file_menu.addAction(self.open_file)

        edit_menu = menu_bar.addMenu("Изменить")

        edit_menu.addAction(self.show_sidebar)

        settings_menu = menu_bar.addMenu("Настройки")

        run_menu = menu_bar.addMenu("Запустить")
        run_menu.addAction(self.run_as_python_code)

    def init_side_bar(self):
        self.sidebar_hidden = False
        self.sidebar_orientation = "Left"
        self.sidebar_last_orientation = ""
        self.sidebar = QToolBar("Sidebar")
        # self.sidebar.setMovable(False)
        self.sidebar.setFloatable(False)
        self.sidebar.setMaximumWidth(350)
        self.sidebar.setMinimumWidth(50)
        self.sidebar.setAllowedAreas(Qt.ToolBarArea.LeftToolBarArea | Qt.ToolBarArea.TopToolBarArea)
        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, self.sidebar)
        self.sidebar.installEventFilter(self)
        self.sidebar.addAction(self.hide_sidebar)
        self.sidebar.orientationChanged.connect(self.sidebarOrientationChangedEvent)
    
        self.sidebar.hide()
        self.sidebar_hidden = True

    def init_actions(self):
        self.save_file = QAction("Сохранить", self)
        self.save_file_as = QAction("Сохранить как", self)
        self.open_file = QAction("Открыть", self)

        self.show_sidebar = QAction("Показать боковую панель", self)

        self.save_file.triggered.connect(self.btn_save_act)
        self.save_file.setShortcut('Ctrl+S')
        self.save_file_as.triggered.connect(self.btn_save_as_act)
        self.save_file_as.setShortcut('Ctrl+Shift+S')
        self.open_file.triggered.connect(self.btn_open_act)
        self.open_file.setShortcut('Ctrl+O')

        self.show_sidebar.triggered.connect(self.btn_show_sidebar)

        # ======== vvv Sidebar
        self.hide_sidebar = QAction("Скрыть", self)
        self.hide_sidebar.triggered.connect(self.btn_hide_sidebar)

        # ======== vvv Run tab
        self.run_as_python_code = QAction("Запустить как Python код.")
        self.run_as_python_code.triggered.connect(self.btn_run_as_python_code)

    def btn_run_as_python_code(self):
        if self.saved and self.curFileName != "*":
            print(f"<- Running  {self.curFileName} ->")
            subprocess.Popen(f"cmd.exe /c start python {self.curFileName}")
            print(f"<- Finished {self.curFileName} ->")
        else:
            if self.btn_save_act():
                print(f"<- Running  {self.curFileName} ->")
                subprocess.Popen(f"cmd.exe /c start python {self.curFileName}")
                print(f"<- Finished {self.curFileName} ->")

    def btn_save_act(self):
        data = self.editor.toPlainText()
        print("Saving", self.curFileName)

        if self.curFileName == "*":
            home_dir = str(Path.home())
            fname = QFileDialog.getSaveFileName(self, 'Сохранить', home_dir)

            if fname[0]:
                with open(fname[0], 'w') as f:
                    f.write(data)
                self.curFileName = fname[0]
                self.saved = True
                self.setWindowTitle(f"Editor: {self.curFileName}")
                return True
            else:
                return False
        else:
            with open(self.curFileName, 'w') as f:
                f.write(data)
            self.saved = True
            self.setWindowTitle(f"Editor: {self.curFileName}")
            return True

    def btn_save_as_act(self):
        print("Saving as")
        data = self.editor.toPlainText()
        home_dir = str(Path.home())
        fname = QFileDialog.getSaveFileName(self, 'Сохранить как', home_dir)
        if fname[0]:
            with open(fname[0], 'w') as f:
                f.write(data)
            self.curFileName = fname[0]
            self.saved = True
            self.setWindowTitle(f"Editor: {self.curFileName}")

    def btn_open_act(self):
        home_dir = str(Path.home())
        fname = QFileDialog.getOpenFileName(self, 'Открыть', home_dir)

        if fname[0]:
            with open(fname[0], 'r') as f:
                data = f.read()
            self.editor.setText(data)
            self.curFileName = fname[0]
            self.saved = True
            if self.curFileName not in self.openedFiles:
                print("Uploaded to opened")
                self.openedFiles.append(self.curFileName)
                act = QAction(self.curFileName)
                act.triggered.connect(partial(self.btn_open_file_fromOpened, self.curFileName))
                print(act.text(), act.actionGroup())
                self.sidebar.addAction(act)
            else:
                print("Already uploaded")

            self.setWindowTitle(f"Editor: {self.curFileName}")

    def btn_open_file_fromOpened(self, filename: str):
        print("Activated", filename)


    def btn_hide_sidebar(self):
        self.sidebar.hide()
        self.sidebar_hidden = True
        self.resizeEditor()

    def btn_show_sidebar(self):
        self.sidebar.show()
        self.sidebar_hidden = False
        self.resizeEditor()

    def resizeEvent(self, event):
        self.size = (self.width(), self.height())
        self.resizeEditor()

    def resizeEditor(self):
        if not self.sidebar_hidden:
            if self.sidebar_orientation == "Left":
                self.editor.setGeometry(self.sidebar.widthMM()*4+10, 30,
                    self.width() - 20 - self.sidebar.widthMM()*4, self.height() - 40)
                self.sidebar.setMaximumWidth(350)
                self.sidebar.setMinimumWidth(50)
                self.sidebar.setMaximumHeight(4000)
                self.sidebar.setMinimumHeight(25)
            elif self.sidebar_orientation == "Up":
                self.editor.setGeometry(10, 30 + self.sidebar.heightMM()*4+10,
                    self.width() - 20, self.height() - 40 - self.sidebar.heightMM()*4 -10)
                self.sidebar.setMaximumWidth(4000)
                self.sidebar.setMinimumWidth(50)
                self.sidebar.setMaximumHeight(75)
                self.sidebar.setMinimumHeight(25)
        else:
            self.editor.setGeometry(10, 30, self.width() - 20, self.height() - 40)


    def textChangedEvent(self):
        if self.saved:
            self.saved = False
        else:
            self.setWindowTitle(f"Editor: {self.curFileName} *")

    def sidebarOrientationChangedEvent(self):
        orient =  self.sidebar.orientation()
        if orient == Qt.Orientation.Vertical:
            self.sidebar_orientation = "Left"
        elif orient == Qt.Orientation.Horizontal:
            self.sidebar_orientation = "Up"
        self.resizeEditor()

    def eventFilter(self, obj, event):
        if (obj is self.sidebar):
            if event.type() == QEvent.Type.MouseButtonRelease and self.sidebar_last_orientation != self.sidebar_orientation:
                self.sidebar_last_orientation = self.sidebar_orientation
                self.resizeEditor()
            return False
        return False

    def closeEvent(self, event):
        if not self.saved:
            reply = QMessageBox.question(self, "Сохранение", "У вас есть несохранённый файл. Вы хотите сохранить его?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel, QMessageBox.StandardButton.Yes)
            if reply == QMessageBox.StandardButton.Yes:
                if self.btn_save_act():
                    event.accept()
                else:
                	event.ignore()
            elif reply == QMessageBox.StandardButton.No:
            	event.accept()
            else:
                event.ignore()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec())
