from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QVBoxLayout, QListWidget, QLabel, QGroupBox
import Modules.Function as Func


class StreamList(QGroupBox):
    def __init__(self):
        super(StreamList, self).__init__()

        self.setTitle("选择输出轨道（多选）")

        self.stream_list_label = QLabel("* MP4支持封装多音轨，但PR只能识别出一条音轨\n"
                                        "* MP4支持封装subrip字幕，但PR不能识别")
        self.stream_list = QListWidget()
        self.stream_list.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.MultiSelection)

        self.box = QVBoxLayout()
        self.box.addWidget(self.stream_list_label)
        self.box.addWidget(self.stream_list)
        self.setLayout(self.box)

    def read_video_stream(self, path):
        # print("read_video_stream", path)
        # self.out_folder_path.set(os.path.dirname(mkv_path))

        info = Func.read_stream_info(path)
        self.stream_list.clear()
        for item in info:
            self.stream_list.addItem(item)
