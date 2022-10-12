# !/usr/bin/python
import sys
import requests
import os
from PyQt6 import QtGui
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QMessageBox

from Modules.ChooseFileGroup import ChooseFileGroup
from Modules.ExportBtnGroup import ExportBtnGroup
from Modules.ExportSetting import ExportSetting
from Modules.StreamList import StreamList
import Modules.Function as Func

version = "v2.3.1"


class Application(QWidget):
    def __init__(self):
        super(Application, self).__init__()

        self.choose_file = ChooseFileGroup()
        self.stream_list = StreamList()
        self.export_setting = ExportSetting()
        self.export_btn_group = ExportBtnGroup()

        self.box = QVBoxLayout()
        self.box.addWidget(self.choose_file)
        self.box.addWidget(self.stream_list)
        self.box.addWidget(self.export_setting)
        self.box.addWidget(self.export_btn_group)
        self.setLayout(self.box)

        # 选择文件后触发
        self.choose_file.selected_file_path.connect(self.stream_list.read_video_stream)
        self.choose_file.selected_file_path.connect(self.export_setting.generate_default_export_dir)
        # 导出按钮
        self.export_btn_group.export_mp4_btn.clicked.connect(self.confirm_export_event)
        self.export_btn_group.export_srt_btn.clicked.connect(self.export_srt_event)

    def confirm_export_event(self):
        mkv_path = self.choose_file.choose_file_line.text()
        mp4_name = Func.get_mp4_name(mkv_path)
        # print(mkv_path, mp4_name)
        if len(mkv_path) < 3:
            return
        if len(mp4_name) < 3:
            return

        export_dir = self.export_setting.choose_export_dir_line.text()
        # print(export_dir)
        if len(export_dir) < 3:
            return

        stream_config, audio_config = Func.parse_export_confing(self.stream_list.stream_list,
                                                                self.export_setting.audio_radio.checkedId(),
                                                                self.export_setting.auto_aac_btn.isChecked())

        if len(stream_config) < 6:
            return

        Func.mkdir(export_dir)

        if self.export_setting.export_batch_btn.isChecked():
            Func.export_batch(mkv_path, export_dir, stream_config, audio_config)
        else:
            Func.exe_cmd(Func.ffmpeg + Func.format_path_quotes(mkv_path)
                         + stream_config + " -c:v copy -c:a copy -c:s mov_text" + audio_config + " " +
                         Func.format_path_quotes(export_dir + os.sep + mp4_name))

    def export_srt_event(self):
        mkv_path = self.choose_file.choose_file_line.text()
        srt_name = Func.get_srt_name(mkv_path)
        # print(mkv_path, srt_name)
        if len(mkv_path) < 3:
            return
        if len(srt_name) < 3:
            return

        export_dir = self.export_setting.choose_export_dir_line.text()
        # print(export_dir)
        if len(export_dir) < 3:
            return

        stream_config = Func.parse_export_srt_confing(self.stream_list.stream_list)
        # print(stream_config)

        if len(stream_config) < 6:
            return

        Func.mkdir(export_dir)

        if self.export_setting.export_batch_btn.isChecked():
            Func.export_srt_batch(mkv_path, export_dir, stream_config)
        else:
            Func.exe_cmd(Func.ffmpeg + Func.format_path_quotes(mkv_path) + stream_config
                         + " " + Func.format_path_quotes(export_dir + os.sep + srt_name))

    def check_update(self):
        try:
            a = requests.get('https://api.github.com/repos/94leon/mp4Remuxer/releases/latest', timeout=2)
            res = a.json()
        except requests.exceptions.RequestException:
            return
        released_version = res['tag_name'] if 'tag_name' in res else ""
        released_description = res['body'] if 'body' in res else ""
        # print(released_version, released_version > version)
        if released_version > version:
            check_update_message_box = QMessageBox.information(self, '提示',
                                                               '发现新版本' + released_version + '\n' + released_description,
                                                               QMessageBox.StandardButton.Yes |
                                                               QMessageBox.StandardButton.Ignore)
            if check_update_message_box == QMessageBox.StandardButton.Yes:
                QDesktopServices.openUrl(QUrl("https://www.bilibili.com/video/BV1N3411H72Z/"))


def main():
    app = QApplication(sys.argv)
    w = Application()
    w.setWindowTitle('mp4Remuxer ' + version + ' - bilibili@李昂不是Leon')
    w.resize(888, 888)
    # 窗口居中
    qr = w.frameGeometry()
    cp = QtGui.QGuiApplication.primaryScreen().availableGeometry().center()
    qr.moveCenter(cp)
    w.move(qr.topLeft())
    w.show()
    # 检查更新
    w.check_update()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
