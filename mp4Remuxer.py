# -*- coding:utf-8 -*-

import os
import re
import subprocess
from tkinter import ttk, filedialog
from tkinter import *
# import windnd
# from functools import partial
from tkinter.ttk import *
import ctypes


class Application(Frame):

    def __init__(self, master=None):
        super().__init__(master)  # super()代表的是父类的定义 ，而不是父类的对像
        self.master = master
        self.pack(fill=BOTH, expand=True)

        self.mkv_path = None
        self.out_folder_path = None
        self.stream_info_listbox = None
        self.ac3_switch = None

        self.create_widget()

    def create_widget(self):
        # global photo  # 定义为全局变量

        frame_read = Frame(self, relief=SUNKEN, padding=10)
        frame_read.pack(padx=30, pady=30, fill=X)
        # Label(frame_read, text="拖拽文件到此处也可以").pack(ipady=10)
        # windnd.hook_dropfiles(frame_read, func=self.dropfiles)
        # 选择按钮
        read_button = ttk.Button(frame_read, text='选择视频文件', command=self.handle_read_mkv)
        read_button.pack(side=LEFT, ipadx=20, ipady=10)
        # 文件路径
        self.mkv_path = StringVar()  # 数据绑定
        mkv_path_entry = Entry(frame_read, textvariable=self.mkv_path)
        mkv_path_entry.pack(fill=BOTH, padx=30, ipady=12)

        # 视频流选择
        frame_track = Frame(self)
        frame_track.pack(padx=30, pady=30, fill=BOTH, expand=True)
        Label(frame_track, text="选择输出轨道（多选）").pack(pady=10)
        Label(frame_track, text="【MP4支持切换音轨，PR不支持；TrueHD音轨封装到MP4有兼容问题，默认转码为AC3（有损）；PR无法识别字幕】").pack(pady=10)

        sb = Scrollbar(frame_track)  # 垂直滚动条组件
        sb.pack(side=RIGHT, fill=Y)  # 设置垂直滚动条显示的位置
        self.stream_info_listbox = Listbox(frame_track, selectmode=MULTIPLE,
                                           yscrollcommand=sb.set)  # Listbox组件添加Scrollbar组件的set()方法
        sb.config(command=self.stream_info_listbox.yview)  # 设置Scrollbar组件的command选项为该组件的yview()方法
        self.stream_info_listbox.pack(fill=BOTH, expand=True)

        # 输出选项
        frame_check = Frame(self, padding=10)
        frame_check.pack(padx=30, fill=X)

        self.ac3_switch = IntVar()
        Checkbutton(frame_check, text="DTS转码为AC3 - 【MP4支持DTS音频，但PR不支持，默认开启（有损）】",
                    variable=self.ac3_switch).pack(side=LEFT)
        self.ac3_switch.set(1)

        frame_output = Frame(self, relief=SUNKEN, padding=10)
        frame_output.pack(padx=30, pady=30, fill=X)

        save_button = ttk.Button(frame_output, text='确定导出', command=self.export_mp4)
        save_button.pack(side=RIGHT, ipadx=20, ipady=10)

        # 选择输出文件夹路径
        folder_button = ttk.Button(frame_output, text='选择目标文件夹', command=self.set_out_folder_path)
        folder_button.pack(side=LEFT, ipadx=20, ipady=10)
        self.out_folder_path = StringVar()  # 数据绑定
        save_path_entry = Entry(frame_output, textvariable=self.out_folder_path)
        save_path_entry.pack(fill=BOTH, padx=30, ipady=12)

    def handle_read_mkv(self):
        mkv_path = filedialog.askopenfilename(title="请选择视频文件",
                                              filetypes=[('视频', '*.mkv'), ('视频', '*.mov'), ('视频', '*.mp4'),
                                                         ('其它视频', '*.*')])
        if len(mkv_path) < 6:
            return
        self.mkv_path.set(mkv_path)
        self.out_folder_path.set(os.path.dirname(mkv_path))

        info = read_stream_info(mkv_path)
        self.stream_info_listbox.delete(0, END)
        for item in info:
            self.stream_info_listbox.insert(END, item)  # END表示每插入一个都是在最后一个位置

    # 拖拽文件有BUG无法解决
    # def dropfiles(self, files): # print(files) for item in files: file_path = item.decode('gbk') #
    # 多个文件只取第一个 if    #         str(file_path).endswith("mkv"): self.read_mkv(file_path) # self.read_mkv(
    # os.path.normpath(file_path))    #             return

    def export_mp4(self):
        # print(self.ac3_switch.get())
        choose_stream = [(self.stream_info_listbox.get(i)) for i in self.stream_info_listbox.curselection()]
        export_confing = ""
        audio_config = ""
        audio_index = 0
        for item in choose_stream:
            # print(item)
            # Stream #0:0: Video: hevc (Main 10)
            # Stream #0:1(eng): Audio: truehd
            export_confing += " -map " + re.findall(r"Stream #(\d+:\d+)[:([]", item)[0]
            if ": Audio:" in item:
                if ": Audio: truehd" in item:
                    audio_config += " -c:a:" + str(audio_index) + " ac3"
                elif self.ac3_switch.get() & (": Audio: dts" in item):
                    audio_config += " -c:a:" + str(audio_index) + " ac3"
                audio_index += 1
        # print(export_confing, audio_config)

        if len(export_confing) < 6:
            return
        if len(self.out_folder_path.get()) < 3:
            return
        mp4_name = get_mp4_name(self.mkv_path.get())
        if len(mp4_name) < 3:
            return

        exe_cmd(".\\bin\\ffmpeg.exe -i " + "\"{}\"".format(self.mkv_path.get())
                + export_confing + " -c:v copy -c:a copy -c:s mov_text" + audio_config + " " +
                "\"{}\"".format(self.out_folder_path.get() + os.sep + mp4_name))

    def set_out_folder_path(self):
        folder_path = filedialog.askdirectory()
        # print(root_path)
        self.out_folder_path.set(folder_path)


#
# def mkdir(path):
#     # makedirs 创建文件时如果路径不存在会创建这个路径
#     if not os.path.exists(path):
#         os.mkdir(path)


def get_mp4_name(path):
    base_name = os.path.split(path)[1] if path else ""
    base_name = os.path.splitext(base_name)[0] if base_name else ""
    # print(base_name)
    return (base_name + "_remux.mp4") if base_name else ""


def get_cmd_result(cmd):
    # print("cmd: ", cmd)
    # 标准输出和错误输出合并，只需要将stderr参数设置为subprocess.STDOUT：
    # 需设置encoding，默认为byte数组
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8")
    res = proc.stdout.read()
    proc.stdout.close()
    return res


def exe_cmd(cmd):
    # 标准输出和错误输出合并，只需要将stderr参数设置为subprocess.STDOUT：
    # 需设置encoding，默认为byte数组
    # print(cmd)
    subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)


def read_stream_info(path):
    # 文件路径可能有空格需加引号
    res = get_cmd_result(".\\bin\\ffmpeg.exe -i " + "\"{}\"".format(path))
    res_arr = res.split("\n")
    stream_info = []
    for line in res_arr:
        print(line)
        if line.startswith("  Stream #"):
            stream_info.append(line.strip())
        if line.startswith("      title           :"):
            # 如果有title信息添加到最后一行
            stream_info[-1] += line.strip().replace("title           :", "  --  ")
    return stream_info


if __name__ == '__main__':
    self = Tk()
    self.title("mp4Remuxer - bilibili@李昂的4K视界")
    self.geometry("1366x1000")
    # # 告诉操作系统使用程序自身的dpi适配
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
    # 获取屏幕的缩放因子
    scale_factor = ctypes.windll.shcore.GetScaleFactorForDevice(0)
    # print(scale_factor)
    # 设置程序缩放
    self.tk.call('tk', 'scaling', scale_factor / 75)

    app = Application(master=self)

    self.mainloop()
