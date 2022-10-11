from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QGroupBox, QLabel, QPushButton, QGridLayout, QLineEdit, QFileDialog


class ChooseFileGroup(QGroupBox):  # 1
    selected_file_path = pyqtSignal(str)

    def __init__(self):
        super(ChooseFileGroup, self).__init__()

        self.setTitle("选择视频文件")
        self.setAcceptDrops(True)  # 2

        self.choose_file_label = QLabel("* 支持直接拖拽视频文件到此处")
        self.choose_file_btn = QPushButton('选择', self)
        self.choose_file_btn.clicked.connect(self.choose_file_event)
        self.choose_file_line = QLineEdit()
        self.choose_file_line.setReadOnly(True)
        # self.LineEdit.setPlaceholderText("拖拽文件到此处也可")

        self.grid = QGridLayout()
        self.grid.addWidget(self.choose_file_label, 0, 0, 1, 2)
        self.grid.addWidget(self.choose_file_btn, 1, 0)
        self.grid.addWidget(self.choose_file_line, 1, 1)
        self.setLayout(self.grid)

    def choose_file_event(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择视频文件", "/", "视频(*.mkv *.mov *.mp4);;其它视频(*.*)")
        # print(file_path)
        if len(file_path) < 3:
            return
        self.set_path(file_path)

    def dragEnterEvent(self, QDragEnterEvent):  # 3
        # print('Drag Enter')
        if QDragEnterEvent.mimeData().hasText():
            QDragEnterEvent.acceptProposedAction()

    def dropEvent(self, QDropEvent):  # 6
        # 多个文件只获取第一个
        file_list = str.split(QDropEvent.mimeData().text(), "\n")
        if len(file_list) < 1:
            return
        # print(file_list)
        file_path = file_list[0][8:].strip()  # 'file:///C:/Tools/mp4Remuxer/README.md'
        if len(file_path) < 3:
            return
        self.set_path(file_path)

    def set_path(self, file_path):
        if len(file_path) < 3:
            return
        self.choose_file_line.setText(file_path)
        self.selected_file_path.emit(file_path)
