from PyQt6.QtWidgets import QGroupBox, QPushButton, QLabel, QHBoxLayout


class ExportBtnGroup(QGroupBox):
    def __init__(self):
        super(ExportBtnGroup, self).__init__()

        self.export_mp4_btn = QPushButton('导出MP4', self)
        self.export_srt_btn = QPushButton('导出SRT', self)
        self.export_mp4_btn.setFixedHeight(40)
        self.export_srt_btn.setFixedHeight(40)
        self.export_srt_label = QLabel("* 单独导出srt字幕，方便导入PR中\n"
                                       "* 仅支持subrip(srt)字幕\n"
                                       "* 每次只能选中一个字幕轨道")

        self.grid = QHBoxLayout()
        self.grid.addWidget(self.export_mp4_btn)
        self.grid.addWidget(self.export_srt_btn)
        self.grid.addWidget(self.export_srt_label)
        self.setLayout(self.grid)
