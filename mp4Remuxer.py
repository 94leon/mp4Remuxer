# !/usr/bin/python
import sys
import requests
import os
import re
import subprocess
from PyQt6 import QtGui, QtWidgets
from PyQt6.QtCore import pyqtSignal, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit, QVBoxLayout, QGroupBox, QFileDialog, \
    QListWidget, QLabel, QGridLayout, QRadioButton, QHBoxLayout, QButtonGroup, QMessageBox

ffmpeg = ".\\bin\\ffmpeg.exe -i "
version = "v2.2"


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

        info = read_stream_info(path)
        self.stream_list.clear()
        for item in info:
            self.stream_list.addItem(item)


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
        self.grid.addWidget(self.choose_export_dir_btn, 6, 0)
        self.grid.addWidget(self.choose_export_dir_line, 6, 1)
        self.setLayout(self.grid)

    def choose_export_dir_btn_event(self):
        export_dir = QFileDialog.getExistingDirectory(self)
        # print(export_dir)
        if len(export_dir) < 1:
            return
        self.choose_export_dir_line.setText(export_dir)

    def generate_default_export_dir(self, path):
        self.choose_export_dir_line.setText(os.path.dirname(path))


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
        mp4_name = get_mp4_name(mkv_path)
        # print(mkv_path, mp4_name)
        if len(mkv_path) < 3:
            return
        if len(mp4_name) < 3:
            return

        export_dir = self.export_setting.choose_export_dir_line.text()
        # print(export_dir)
        if len(export_dir) < 3:
            return

        stream_config, audio_config = parse_export_confing(self.stream_list.stream_list,
                                                           self.export_setting.audio_radio.checkedId(),
                                                           self.export_setting.auto_aac_btn.isChecked())

        if len(stream_config) < 6:
            return

        mkdir(export_dir)
        exe_cmd(ffmpeg + format_path_quotes(mkv_path)
                + stream_config + " -c:v copy -c:a copy -c:s mov_text" + audio_config + " " +
                format_path_quotes(export_dir + os.sep + mp4_name))

    def export_srt_event(self):
        mkv_path = self.choose_file.choose_file_line.text()
        srt_name = get_srt_name(mkv_path)
        # print(mkv_path, srt_name)
        if len(mkv_path) < 3:
            return
        if len(srt_name) < 3:
            return

        export_dir = self.export_setting.choose_export_dir_line.text()
        # print(export_dir)
        if len(export_dir) < 3:
            return

        stream_config = parse_export_srt_confing(self.stream_list.stream_list)
        # print(stream_config)

        if len(stream_config) < 6:
            return

        mkdir(export_dir)
        exe_cmd(ffmpeg + format_path_quotes(mkv_path) + stream_config
                + " " + format_path_quotes(export_dir + os.sep + srt_name))

    def check_update(self):
        a = requests.get('https://api.github.com/repos/94leon/mp4Remuxer/releases/latest')
        res = a.json()
        released_version = res['tag_name'] if res['tag_name'] else ""
        # print(released_version, released_version > version)
        if released_version > version:
            check_update_message_box = QMessageBox.information(self, '提示', '发现新版本' + released_version,
                                                               QMessageBox.StandardButton.Yes |
                                                               QMessageBox.StandardButton.Ignore)
            if check_update_message_box == QMessageBox.StandardButton.Yes:
                QDesktopServices.openUrl(QUrl("https://www.bilibili.com/video/BV1N3411H72Z/"))


def mkdir(path):
    # mkdir 路径不存在会创建最低级路径
    # makedirs 路径不存在会创建多级完整路径
    if not os.path.exists(path):
        os.makedirs(path)


def parse_export_confing(stream_list, audio_radio, auto_aac):
    if stream_list is None:
        return "", ""
    selected_streams = [(item.data()) for item in stream_list.selectedIndexes()]
    if len(selected_streams) < 1:
        return "", ""
    default_recode_list = [': Audio: truehd', ': Audio: dts', ': Audio: flac', ': Audio: opus']
    stream_confing = ""
    audio_config = ""
    audio_index = 0
    hdmv_pgs_subtitle = False
    for item in selected_streams:
        # print(item)
        # Stream #0:0: Video: hevc (Main 10)
        # Stream #0:1(eng): Audio: truehd
        stream_confing += " -map " + re.findall(r"Stream #(\d+:\d+)[:([]", item)[0]
        if ": Audio:" in item:
            if audio_radio == 0:
                continue
            elif audio_radio == 1 and any(key in item for key in default_recode_list):
                if auto_aac and ", 7.1," in item:
                    audio_config += " -c:a:" + str(audio_index) + " aac"
                else:
                    audio_config += " -c:a:" + str(audio_index) + " ac3"
            elif audio_radio == 2:
                if auto_aac and ", 7.1," in item:
                    audio_config += " -c:a:" + str(audio_index) + " aac"
                else:
                    audio_config += " -c:a:" + str(audio_index) + " ac3"
            audio_index += 1
        elif ": Subtitle: hdmv_pgs_subtitle" in item:
            hdmv_pgs_subtitle = True

    print(stream_confing, audio_config)

    if hdmv_pgs_subtitle:
        return "", ""
    return stream_confing, audio_config


def parse_export_srt_confing(stream_list):
    if stream_list is None:
        return ""
    selected_streams = [(item.data()) for item in stream_list.selectedIndexes()]
    if len(selected_streams) != 1:
        return ""

    stream_confing = ""
    # Stream #0:2(eng): Subtitle: subrip (default)
    if ": Subtitle: subrip" in selected_streams[0]:
        stream_confing = " -map " + re.findall(r"Stream #(\d+:\d+)[:([]", selected_streams[0])[0]
    return stream_confing


def get_mp4_name(path):
    base_name = os.path.split(path)[1] if path else ""
    base_name = os.path.splitext(base_name)[0] if base_name else ""
    # print(base_name)
    return (base_name + "_remux.mp4") if base_name else ""


def get_srt_name(path):
    base_name = os.path.split(path)[1] if path else ""
    base_name = os.path.splitext(base_name)[0] if base_name else ""
    # print(base_name)
    return (base_name + "_remux.srt") if base_name else ""


def exe_cmd(cmd):
    print("cmd:", cmd)
    subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)


def get_cmd_result(cmd):
    print("cmd:", cmd)
    # 标准输出和错误输出合并，只需要将stderr参数设置为subprocess.STDOUT：
    # 需设置encoding，默认为byte数组
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8")
    res = proc.stdout.readlines()
    proc.stdout.close()
    return res


def read_stream_info(path):
    res_arr = get_cmd_result(ffmpeg + format_path_quotes(path))
    stream_info = []
    for line in res_arr:
        line = line.replace('\n', '')
        print(line)
        if line.startswith("  Stream #"):
            stream_info.append(line.strip())
        if line.startswith("      title           :"):
            # 如果有title信息添加到该行末尾
            stream_info[-1] += line.strip().replace("title           :", "  --  ")
    return stream_info


def format_path_quotes(path):
    # 文件路径可能有空格需加引号
    return "\"{}\"".format(path)


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
