# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
import json
import os
import cv2
import numpy as np
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMenu, QWidget
from PySide6.QtCore import QThread, Signal, QPoint, Qt
from PySide6.QtGui import QImage, QPixmap, QAction, QColor
from ui.CustomMessageBox import MessageBox
from ui.UIFunctions import *
from ui.home import Ui_MainWindow
from ui.rtsp_dialog import Ui_Form
from utils.capnums import Camera


# from run_test import get_args_parser, model_init, predict

# class Net():
#     def __init__(self):
#         self.parser = argparse.ArgumentParser('P2PNet evaluation script', parents=[get_args_parser()])
#         self.args = self.parser.parse_args()
#         self.model = model_init(self.args)
#
#     def predict(self, img):
#         return predict(self.model, img)

class RtspWindow(QWidget, Ui_Form):
    def __init__(self):
        super(RtspWindow, self).__init__()
        self.setupUi(self)





class VideoPlayerThread(QThread):
    video_progressbar = Signal(int)
    pre_frame_changed = Signal(np.ndarray)
    post_frame_changed = Signal(np.ndarray)
    play_finished = Signal()
    head_count_changed = Signal(int)
    detect_fps = Signal(int)

    def __init__(self):
        super(VideoPlayerThread, self).__init__()

        self.video = None
        self.video_src = None

        self.paused = False
        self.save_flag = False

        # 播放参数
        # self.net = Net()
        self.threshold = 0.5
        self.size = 2
        self.send_delay = 2  # 默认发送跳帧
        self.output_number = len(os.listdir('./output'))
        self.head_count = 0
        self.current_frames = 0

    def run(self):
        if self.video:
            total_frames = self.video.get(cv2.CAP_PROP_FRAME_COUNT) - 1
            fps = self.video.get(cv2.CAP_PROP_FPS)
            frame_size = (
                int(self.video.get(cv2.CAP_PROP_FRAME_WIDTH)), int(self.video.get(cv2.CAP_PROP_FRAME_HEIGHT)))

            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter(f'output/output_{self.output_number}.avi', fourcc, fps, frame_size)
            start_time = time.time()
            while True:
                if not self.paused:
                    _, frame = self.video.read()
                    self.current_frames += 1
                    if self.video_src == "file":
                        if self.current_frames >= total_frames:
                            self.paused = True
                            self.play_finished.emit()
                            current_frames = 0
                            self.video.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        progress = int(self.current_frames / total_frames * 100)
                        self.video_progressbar.emit(progress)
                    self.pre_frame_changed.emit(frame)
                    if self.current_frames % self.send_delay == 0:
                        # TODO: 预测,目前没有网络，模拟预测
                        # predict, self.head_count = self.net.run(frame, self.threshold, self.size)
                        predict = frame
                        if self.save_flag:
                            out.write(predict)
                        self.post_frame_changed.emit(frame)
                        self.head_count_changed.emit(self.head_count)
                        cv2.waitKey(int(60))
                        self.detect_fps.emit(int(self.send_delay / (time.time() - start_time)))
                        start_time = time.time()



class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setupUi(self)

        self.btn_start_flag = False

        self.rtsp_dialog = None

        # ui界面初始化
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint)
        UIFuncitons.uiDefinitions(self)
        UIFuncitons.shadow_style(self, self.Class_QF, QColor(162, 129, 247))
        UIFuncitons.shadow_style(self, self.Fps_QF, QColor(170, 128, 213))
        UIFuncitons.shadow_style(self, self.Model_QF, QColor(64, 186, 193))

        # label 初始显示--
        self.label_fpsshow.setText('--')
        self.label_estishow.setText('--')
        self.label_modelshow.setText('--')

        # 按钮功能实现
        self.btn_file.clicked.connect(self.choose_file)
        self.btn_start.clicked.connect(self.toggle_play_pause)
        self.btn_stop.clicked.connect(self.end_play)
        self.btn_cam.clicked.connect(self.choose_cam)
        self.btn_menu.clicked.connect(lambda: UIFuncitons.toggleMenu(self, True))
        self.btn_setting.clicked.connect(lambda: UIFuncitons.settingBox(self, True))
        self.btn_savevideo.toggled.connect(self.is_save)
        self.btn_rstp.clicked.connect(self.choose_rtsp)

        # 开启子线程
        self.video_thread = VideoPlayerThread()
        self.video_thread.pre_frame_changed.connect(lambda x: self.show_image(x, self.label_invideo))
        self.video_thread.post_frame_changed.connect(lambda x: self.show_image(x, self.label_outvideo))
        self.video_thread.video_progressbar.connect(lambda x: self.progressbar.setValue(x))
        self.video_thread.play_finished.connect(self.play_finished)
        self.video_thread.head_count_changed.connect(lambda x: self.label_estishow.setText(str(x)))
        self.video_thread.detect_fps.connect(lambda x: self.label_fpsshow.setText(str(x)))

        # 设置滑条
        self.slider_thresh.valueChanged.connect(lambda x: self.change_val(x, 'slider_thresh'))
        self.spinbox_thresh.valueChanged.connect(lambda x: self.change_val(x, 'spinbox_thresh'))
        self.slider_playspeed.valueChanged.connect(lambda x: self.change_val(x, 'slider_speed'))
        self.spinbox_playspeed.valueChanged.connect(lambda x: self.change_val(x, 'spinbox_speed'))
        self.slider_pointsize.valueChanged.connect(lambda x: self.change_val(x, 'slider_size'))
        self.spinbox_pointsize.valueChanged.connect(lambda x: self.change_val(x, 'spinbox_size'))

    def choose_file(self):
        '''打开文件夹选择视频文件'''
        if self.video_thread.video is not None:
            self.end_play()
        config = json.load(open('config/fold_cfg.json', 'r', encoding='utf-8'))
        open_fold = config['fold']
        if not os.path.exists(open_fold):
            open_fold = os.getcwd()
        file_name, _ = QFileDialog.getOpenFileName(self, "选择视频文件", open_fold,
                                                   "video file (*.mp4 *.avi *.wmv *.mkv);;All Files (*)")
        if file_name:
            self.video_thread.video_src = "file"
            self.video_thread.video = cv2.VideoCapture(file_name)
            # 获取视频第一帧
            ret, frame = self.video_thread.video.read()
            if ret:
                self.show_image(frame, self.label_invideo)

    def choose_cam(self):
        try:
            self.end_play()
            MessageBox(
                self.btn_close, title='Note', text='loading camera...', time=2000, auto=True).exec()
            # get the number of local cameras
            _, cams = Camera().get_cam_num()
            popMenu = QMenu()
            popMenu.setFixedWidth(self.btn_menu.width())

            # TODO: 测试。。。待修改回原功能
            for cam in range(5):
                exec("action_%s = QAction('%s')" % (cam, cam))
                exec("popMenu.addAction(action_%s)" % cam)

            x = self.btn_cam.mapToGlobal(self.btn_cam.pos()).x()
            y = self.btn_cam.mapToGlobal(self.btn_cam.pos()).y() - self.btn_cam.geometry().height()
            x = x + self.LeftMenuBg.geometry().width()
            pos = QPoint(x, y)
            action = popMenu.exec(pos)
            if action:
                self.video_thread.video_src = "camera"
                self.video_thread.video = cv2.VideoCapture(int(action.text()))
                self.label_status.setText('Loading camera：{}'.format(action.text()))

        except Exception as e:
            self.label_status.setText('%s' % e)

    def choose_rtsp(self):
        self.end_play()
        self.rtsp_dialog = RtspWindow()
        self.rtsp_dialog.show()
        ip_cfg = json.load(open('config/ip_cfg.json', 'r', encoding='utf-8'))
        ip = ip_cfg['ip']
        self.rtsp_dialog.lineEdit_inaddress.setText(ip)
        self.rtsp_dialog.pushButton.clicked.connect(lambda: self.load_rtsp(self.rtsp_dialog.lineEdit_inaddress.text()))

    def load_rtsp(self, ip):
        try:
            self.video_thread.video_src = "rtsp"
            MessageBox(
                self.btn_close, title='提示', text='加载 rtsp...', time=1000, auto=True).exec()
            self.rtsp_dialog.close()
            self.video_thread.video = cv2.VideoCapture(ip)
            new_config = {"ip": ip}
            new_json = json.dumps(new_config, ensure_ascii=False, indent=2)
            with open('config/ip_cfg.json', 'w', encoding='utf-8') as f:
                f.write(new_json)
            self.label_status.setText('Loading rtsp：{}'.format(ip))
        except Exception as e:
            self.label_status.setText('%s' % e)

    @staticmethod
    def show_image(img_src, label):
        if img_src is not None:
            ih, iw, _ = img_src.shape
            w = label.geometry().width()
            h = label.geometry().height()
            if iw / w > ih / h:
                scal = w / iw
                nw = w
                nh = int(scal * ih)
                img_src_ = cv2.resize(img_src, (nw, nh))
            else:
                scal = h / ih
                nw = int(scal * iw)
                nh = h
                img_src_ = cv2.resize(img_src, (nw, nh))

            frame = cv2.cvtColor(img_src_, cv2.COLOR_BGR2RGB)
            img = QImage(frame.data, frame.shape[1], frame.shape[0], frame.shape[2] * frame.shape[1], QImage.Format_RGB888)
            label.setPixmap(QPixmap.fromImage(img))

    def change_val(self, x, flag):
        if flag == 'spinbox_speed':
            self.slider_playspeed.setValue(int(x * 10))  # The box value changes, changing the slider
        elif flag == 'slider_speed':
            self.spinbox_playspeed.setValue(x / 10)  # The slider value changes, changing the box
            self.label_status.setText('play speed: %s' % str(x))
            self.video_thread.send_delay = x
        elif flag == 'spinbox_thresh':
            self.slider_thresh.setValue(int(x * 100))
        elif flag == 'slider_thresh':
            self.spinbox_thresh.setValue(x / 100)
            self.label_status.setText(' Threshold: %s' % str(x/100))
            self.video_thread.threshold = x/100
        elif flag == 'spinbox_size':
            self.slider_pointsize.setValue(x*5)
        elif flag == 'slider_size':
            self.spinbox_pointsize.setValue(x/5)
            self.label_status.setText('point size: %s ' % str(x))
            self.video_thread.size = x

    def is_save(self):
        if self.btn_savevideo.checkState() == Qt.CheckState.Checked:
            self.video_thread.save_flag = True
        elif self.btn_savevideo.checkState() == Qt.CheckState.Unchecked:
            self.video_thread.save_flag = False

    def toggle_play_pause(self):
        if self.video_thread.video is None:
            self.label_status.setText("Please choose a video source...")
            self.btn_start.setChecked(False)
        else:
            self.btn_start_flag = not self.btn_start_flag
            if self.btn_start_flag:
                self.video_thread.paused = False
                self.video_thread.start()
                self.label_status.setText("Detecting...")
            else:
                self.video_thread.paused = True
                self.label_status.setText("Pause...")

    def play_finished(self):
        self.btn_start.setChecked(False)
        self.toggle_play_pause()

    def end_play(self):
        '''结束播放'''
        if self.video_thread.video:
            self.video_thread.video.release()
        elif self.video_thread.isRunning():
            self.video_thread.quit()
        self.btn_start_flag = False
        self.video_thread.paused = True
        self.btn_start.setChecked(False)
        self.label_status.setText("Welcome")
        cv2.waitKey(60)
        self.label_invideo.clear()
        self.label_outvideo.clear()
        self.video_thread.current_frames = 0
        self.progressbar.setValue(0)


if __name__ == "__main__":
    app = QApplication()
    window = MainWindow()
    window.show()
    app.exec()
