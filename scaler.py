import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox,
    QSizePolicy, QGridLayout, QFrame, QComboBox, QProgressBar
)
from PyQt6.QtGui import QPixmap, QImage, QIcon
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PIL import Image

class ResizeWorker(QThread):
    progress_changed = pyqtSignal(int)
    finished = pyqtSignal(object)

    def __init__(self, pil_image, scale, interp_method):
        super().__init__()
        self.pil_image = pil_image
        self.scale = scale
        self.interp_method = interp_method

    def run(self):
        width = max(1, int(self.pil_image.width * self.scale))
        height = max(1, int(self.pil_image.height * self.scale))

        # Simulate progress proportional to scale and image size
        steps = 10
        # Adjust sleep time to be shorter when scaling down (fast) and longer when scaling up
        base_sleep = 50  # base ms per step
        sleep_time = max(5, int(base_sleep * self.scale))  # faster for small scale

        for i in range(steps):
            self.msleep(sleep_time)
            self.progress_changed.emit(int((i + 1) / steps * 100))

        resized = self.pil_image.resize((width, height), self.interp_method)
        self.finished.emit(resized)

class ImageScaler(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Resolution Scaler")

        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.languages = ['en', 'ru']
        self.lang = 'en'

        self.texts = {
            'en': {
                'title': "Image Resolution Scaler",
                'interp_label': "Interpolation method:",
                'interp_methods': [
                    "Nearest (Nearest Neighbor)",
                    "Bilinear",
                    "Bicubic",
                    "Lanczos"
                ],
                'load': "Load Image",
                'downscale': "Decrease",
                'upscale': "Increase",
                'save': "Save As...",
                'params': "Image Parameters:",
                'scale': "Scale:",
                'orig_size': "Original size:",
                'curr_size': "Current size:",
                'frame_size': "Size in frame:",
                'no_image': "Load an image",
                'interp_shown': "Method: {}",
                'save_title': "Save Image As",
                'save_success': "Image saved: {}",
                'save_error': "Failed to save image:\n{}",
                'save_none': "No image to save.",
                'load_title': "Select Image",
                'load_error': "Failed to load image:\n{}",
                'lang_switch': "Language:",
                'please_load': "Please load an image first.",
            },
            'ru': {
                'title': "Масштабирование изображения",
                'interp_label': "Метод интерполяции:",
                'interp_methods': [
                    "Ближайший сосед (Nearest)",
                    "Билинейная",
                    "Бикубическая",
                    "Ланцош"
                ],
                'load': "Загрузить",
                'downscale': "Уменьшить",
                'upscale': "Увеличить",
                'save': "Сохранить как",
                'params': "Параметры изображения:",
                'scale': "Масштаб:",
                'orig_size': "Исходный размер:",
                'curr_size': "Текущий размер:",
                'frame_size': "Размер в окне:",
                'no_image': "Загрузите изображение",
                'interp_shown': "Метод: {}",
                'save_title': "Сохранить изображение как",
                'save_success': "Изображение сохранено: {}",
                'save_error': "Не удалось сохранить изображение:\n{}",
                'save_none': "Нет изображения для сохранения.",
                'load_title': "Выберите изображение",
                'load_error': "Не удалось загрузить изображение:\n{}",
                'lang_switch': "Язык:",
                'please_load': "Пожалуйста, сначала загрузите изображение.",
            }
        }

        self.scale = 1.0
        self.img_pil_original = None
        self.img_resized = None
        self.worker = None

        self.combo_interp = QComboBox()
        self.combo_interp.addItems(self.texts[self.lang]['interp_methods'])
        self.combo_interp.setCurrentIndex(2)
        self.combo_interp.setMaximumWidth(180)
        self.combo_interp.currentIndexChanged.connect(self.on_interp_changed)

        self.combo_lang = QComboBox()
        self.combo_lang.addItems(['English', 'Русский'])
        self.combo_lang.setMaximumWidth(120)
        self.combo_lang.currentIndexChanged.connect(self.switch_language)

        self.btn_load = QPushButton()
        self.btn_downscale = QPushButton()
        self.btn_upscale = QPushButton()
        self.btn_save = QPushButton()

        for btn in (self.btn_load, self.btn_downscale, self.btn_upscale, self.btn_save):
            btn.setMaximumWidth(180)
            btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        self.btn_load.clicked.connect(self.load_image)
        self.btn_downscale.clicked.connect(self.downscale)
        self.btn_upscale.clicked.connect(self.upscale)
        self.btn_save.clicked.connect(self.save_as)

        self.info_grid = QGridLayout()
        self.labels_values = []
        for i in range(4):
            lbl_title = QLabel()
            lbl_value = QLabel("-")
            self.info_grid.addWidget(lbl_title, i, 0)
            self.info_grid.addWidget(lbl_value, i, 1)
            self.labels_values.append(lbl_value)
        self.info_titles = [self.info_grid.itemAtPosition(i, 0).widget() for i in range(4)]

        self.info_container = QFrame()
        self.info_container.setLayout(self.info_grid)
        self.info_container.setMaximumWidth(220)

        self.label_interpolation = QLabel("")
        self.label_interpolation.setStyleSheet(
            "color: #aa4444; font-weight: bold; border: 1px solid #aa4444; padding: 4px;"
        )
        self.label_interpolation.hide()

        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.hide()

        self.label_image = QLabel(self.texts[self.lang]['no_image'])
        self.label_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_image.setStyleSheet("border: 1px solid #444; background: #232323; color: #bbb;")
        self.label_image.setMinimumSize(400, 400)
        self.label_image.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        control_layout = QVBoxLayout()
        lang_hbox = QHBoxLayout()
        lang_hbox.addWidget(QLabel(self.texts[self.lang]['lang_switch']))
        lang_hbox.addWidget(self.combo_lang)
        lang_hbox.addStretch(1)
        control_layout.addLayout(lang_hbox)
        control_layout.addSpacing(8)
        control_layout.addWidget(QLabel(self.texts[self.lang]['interp_label']))
        control_layout.addWidget(self.combo_interp)
        control_layout.addSpacing(10)
        control_layout.addWidget(self.btn_load)
        control_layout.addWidget(self.btn_downscale)
        control_layout.addWidget(self.btn_upscale)
        control_layout.addWidget(self.btn_save)
        control_layout.addSpacing(20)
        control_layout.addWidget(QLabel(self.texts[self.lang]['params']))
        control_layout.addWidget(self.info_container)
        control_layout.addWidget(self.label_interpolation)
        control_layout.addWidget(self.progress_bar)
        control_layout.addSpacing(10)
        control_layout.addStretch(1)

        image_layout = QVBoxLayout()
        image_layout.addWidget(self.label_image)

        main_layout = QHBoxLayout()
        control_widget = QFrame()
        control_widget.setLayout(control_layout)
        control_widget.setMaximumWidth(260)
        main_layout.addWidget(control_widget)
        main_layout.addLayout(image_layout, stretch=1)

        self.setLayout(main_layout)

        self.update_ui_texts()
        self.update_buttons_state()

    def update_ui_texts(self):
        t = self.texts[self.lang]
        self.setWindowTitle(t['title'])
        self.btn_load.setText(t['load'])
        self.btn_downscale.setText(t['downscale'])
        self.btn_upscale.setText(t['upscale'])
        self.btn_save.setText(t['save'])

        titles = [t['scale'], t['orig_size'], t['curr_size'], t['frame_size']]
        for lbl, title in zip(self.info_titles, titles):
            lbl.setText(title)

        self.combo_interp.blockSignals(True)
        self.combo_interp.clear()
        self.combo_interp.addItems(t['interp_methods'])
        self.combo_interp.setCurrentIndex(2)
        self.combo_interp.blockSignals(False)

        self.combo_lang.setItemText(0, "English")
        self.combo_lang.setItemText(1, "Русский")

        # Show image or placeholder text without clearing pixmap unnecessarily
        if self.img_resized is None:
            self.label_image.clear()
            self.label_image.setText(t['no_image'])
        else:
            label_w = self.label_image.width()
            label_h = self.label_image.height()
            pixmap = self.label_image.pixmap()
            if pixmap:
                pixmap_scaled = pixmap.scaled(
                    label_w, label_h,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.label_image.setPixmap(pixmap_scaled)

    def switch_language(self, idx):
        self.lang = self.languages[idx]
        self.update_ui_texts()
        self.update_buttons_state()
        if self.label_interpolation.isVisible():
            interp_name = self.texts[self.lang]['interp_methods'][self.combo_interp.currentIndex()]
            self.label_interpolation.setText(self.texts[self.lang]['interp_shown'].format(interp_name))

    def update_buttons_state(self):
        self.btn_downscale.setEnabled(self.img_pil_original is not None and self.scale > 0.05)
        self.btn_upscale.setEnabled(self.img_pil_original is not None and self.scale < 3.0)

    def on_interp_changed(self):
        if self.img_pil_original:
            self.start_interpolation()

    def load_image(self):
        t = self.texts[self.lang]
        file_path, _ = QFileDialog.getOpenFileName(
            self, t['load_title'], "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*)"
        )
        if not file_path:
            return
        try:
            self.img_pil_original = Image.open(file_path).convert("RGBA")
            self.scale = 1.0
            self.update_buttons_state()
            self.start_interpolation()
        except Exception as e:
            QMessageBox.warning(self, t['title'], t['load_error'].format(e))

    def start_interpolation(self):
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()

        idx = self.combo_interp.currentIndex()
        methods = {
            0: Image.NEAREST,
            1: Image.BILINEAR,
            2: Image.BICUBIC,
            3: Image.LANCZOS,
        }
        interp_method = methods.get(idx, Image.BICUBIC)

        self.progress_bar.setValue(0)
        self.progress_bar.show()
        interp_name = self.texts[self.lang]['interp_methods'][idx]
        self.label_interpolation.setText(self.texts[self.lang]['interp_shown'].format(interp_name))
        self.label_interpolation.show()

        self.worker = ResizeWorker(self.img_pil_original, self.scale, interp_method)
        self.worker.progress_changed.connect(self.progress_bar.setValue)
        self.worker.finished.connect(self.on_interpolation_finished)
        self.worker.start()

    def on_interpolation_finished(self, pil_img):
        self.img_resized = pil_img

        label_w = self.label_image.width()
        label_h = self.label_image.height()

        data = pil_img.tobytes("raw", "RGBA")
        qimg = QImage(data, pil_img.width, pil_img.height, QImage.Format.Format_RGBA8888)
        pixmap = QPixmap.fromImage(qimg)
        pixmap_scaled = pixmap.scaled(label_w, label_h, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.label_image.setPixmap(pixmap_scaled)

        self.progress_bar.hide()

        values = [
            f"{self.scale:.2f}x",
            f"{self.img_pil_original.width}×{self.img_pil_original.height} px",
            f"{pil_img.width}×{pil_img.height} px",
            f"{pixmap_scaled.width()}×{pixmap_scaled.height()} px"
        ]
        for lbl_value, val in zip(self.labels_values, values):
            lbl_value.setText(val)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.img_resized:
            self.on_interpolation_finished(self.img_resized)

    def downscale(self):
        if not self.img_pil_original:
            QMessageBox.information(self, self.texts[self.lang]['title'], self.texts[self.lang]['please_load'])
            return
        if self.scale <= 0.05:
            return
        self.scale = max(0.05, self.scale - 0.05)
        self.update_buttons_state()
        self.start_interpolation()

    def upscale(self):
        if not self.img_pil_original:
            QMessageBox.information(self, self.texts[self.lang]['title'], self.texts[self.lang]['please_load'])
            return
        if self.scale >= 3.0:
            return
        self.scale = min(3.0, self.scale + 0.05)
        self.update_buttons_state()
        self.start_interpolation()

    def save_as(self):
        t = self.texts[self.lang]
        if self.img_resized is None:
            QMessageBox.information(self, t['title'], t['please_load'])
            return
        file_path, _ = QFileDialog.getSaveFileName(
            self, t['save_title'], "",
            "PNG (*.png);;JPEG (*.jpg *.jpeg);;BMP (*.bmp);;All Files (*)"
        )
        if not file_path:
            return
        try:
            self.img_resized.save(file_path)
            QMessageBox.information(self, t['title'], t['save_success'].format(file_path))
        except Exception as e:
            QMessageBox.warning(self, t['title'], t['save_error'].format(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageScaler()
    window.resize(1000, 700)
    window.show()
    sys.exit(app.exec())
