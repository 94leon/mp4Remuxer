import os

from PyQt6.QtWidgets import QGroupBox, QRadioButton, QLabel, QButtonGroup, QPushButton, QGridLayout, QLineEdit, \
    QFileDialog


class ExportSetting(QGroupBox):
    def __init__(self):
        super(ExportSetting, self).__init__()

        self.setTitle("输出设置")

        self.direct_out_btn = QRadioButton('音轨直出', self)
        self.direct_out_label = QLabel("* 不做任何处理。部分编码MP4不支持，表现为导出文件大小为0，如TrueHD、FLAC等")
        self.default_recode_btn = QRadioButton('默认转码', self)
        self.default_recode_label = QLabel("* 将常见的MP4/PR不支持的音轨转码为AC3，如TrueHD、FLAC、DTS、OPUS等（有损）")
        self.all_recode_btn = QRadioButton('强制转码', self)
        self.all_recode_label = QLabel("* 碰到一些非主流编码，可以尝试一下（有损）")

        self.audio_radio = QButtonGroup(self)
        self.audio_radio.addButton(self.direct_out_btn, 0)
        self.audio_radio.addButton(self.default_recode_btn, 1)
        self.audio_radio.addButton(self.all_recode_btn, 2)
        self.default_recode_btn.setChecked(True)

        self.auto_aac_btn = QRadioButton('7.1声道转为AAC', self)
        self.auto_aac_label = QLabel("* AC3最多支持5.1声道；AAC支持7.1但转码速度较慢")
        self.auto_aac_btn.setChecked(True)

        self.export_batch_btn = QRadioButton('批量导出', self)
        self.export_batch_label = QLabel("* 将同目录下视频使用同样的参数导出，需每个视频的轨道一致；导出期间本工具无法操作")
        self.export_batch_btn.setChecked(False)

        self.choose_export_dir_btn = QPushButton('选择文件夹', self)
        self.choose_export_dir_btn.clicked.connect(self.choose_export_dir_btn_event)
        self.choose_export_dir_line = QLineEdit()

        self.grid = QGridLayout()

        self.grid.addWidget(self.direct_out_btn, 0, 0)
        self.grid.addWidget(self.direct_out_label, 0, 1)
        self.grid.addWidget(self.default_recode_btn, 1, 0)
        self.grid.addWidget(self.default_recode_label, 1, 1)
        self.grid.addWidget(self.all_recode_btn, 2, 0)
        self.grid.addWidget(self.all_recode_label, 2, 1)
        self.grid.addWidget(QLabel(" "), 3, 0)
        self.grid.addWidget(self.auto_aac_btn, 4, 0)
        self.grid.addWidget(self.auto_aac_label, 4, 1)
        self.grid.addWidget(QLabel(" "), 5, 0)
        self.grid.addWidget(self.export_batch_btn, 6, 0)
        self.grid.addWidget(self.export_batch_label, 6, 1)
        self.grid.addWidget(QLabel(" "), 7, 0)
        self.grid.addWidget(self.choose_export_dir_btn, 8, 0)
        self.grid.addWidget(self.choose_export_dir_line, 8, 1)
        self.setLayout(self.grid)

    def choose_export_dir_btn_event(self):
        export_dir = QFileDialog.getExistingDirectory(self)
        # print(export_dir)
        if len(export_dir) < 1:
            return
        self.choose_export_dir_line.setText(export_dir)

    def generate_default_export_dir(self, path):
        self.choose_export_dir_line.setText(os.path.dirname(path))
