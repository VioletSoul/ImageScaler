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

# Worker thread for resizing image in the background
class ResizeWorker(QThread):
    # Signal to update progress bar
    progress_changed = pyqtSignal(int)
    # Signal emitted when resizing is finished, passes the resized PIL image
    finished = pyqtSignal(object)

    def __init__(self, pil_image, scale, interp_method):
        super().__init__()
        self.pil_image = pil_image        # Original PIL image
        self.scale = scale                # Scale factor
        self.interp_method = interp_method # Interpolation method

    def run(self):
        # Calculate new dimensions
        width = max(1, int(self.pil_image.width * self.scale))
        height = max(1, int(self.pil_image.height * self.scale))
        # Simulate progress in 10 steps for user feedback
        steps = 10
        base_sleep = 5
        sleep_time = max(5, int(base_sleep * self.scale))
        for i in range(steps):
            self.msleep(sleep_time)
            self.progress_changed.emit(int((i + 1) / steps * 100))
        # Perform the actual resizing operation
        resized = self.pil_image.resize((width, height), self.interp_method)
        # Emit the finished signal with the resized image
        self.finished.emit(resized)

# Main application window
class ImageScaler(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Resolution Scaler")

        # Set window icon if present
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Supported languages and UI texts
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

        # State variables for image and UI
        self.scale = 1.0                    # Current scale factor
        self.img_pil_original = None        # Original PIL image
        self.img_resized = None             # Resized PIL image
        self.worker = None                  # Worker thread for resizing
        self.cached_pixmap = None           # Cached QPixmap for display
        self.last_pixmap_scaled = None      # Last scaled QPixmap for display

        # Interpolation method selector (combo box)
        self.combo_interp = QComboBox()
        self.combo_interp.addItems(self.texts[self.lang]['interp_methods'])
        self.combo_interp.setCurrentIndex(2) # Default to Bicubic
        self.combo_interp.setMaximumWidth(180)
        self.combo_interp.currentIndexChanged.connect(self.on_interp_changed)

        # Language selector (combo box)
        self.combo_lang = QComboBox()
        self.combo_lang.addItems(['English', 'Русский'])
        self.combo_lang.setMaximumWidth(120)
        self.combo_lang.currentIndexChanged.connect(self.switch_language)

        # Control buttons for loading, scaling, and saving
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

        # Grid layout for displaying image parameters (scale, sizes)
        self.info_grid = QGridLayout()
        self.labels_values = []
        for i in range(4):
            lbl_title = QLabel()
            lbl_value = QLabel("-")
            self.info_grid.addWidget(lbl_title, i, 0)
            self.info_grid.addWidget(lbl_value, i, 1)
            self.labels_values.append(lbl_value)
        # Titles for each parameter row
        self.info_titles = [self.info_grid.itemAtPosition(i, 0).widget() for i in range(4)]
        self.info_container = QFrame()
        self.info_container.setLayout(self.info_grid)
        self.info_container.setMaximumWidth(220)

        # Label to show current interpolation method
        self.label_interpolation = QLabel("")
        self.label_interpolation.setStyleSheet(
            "color: #aa4444; font-weight: bold; border: 1px solid #aa4444; padding: 4px;"
        )
        self.label_interpolation.hide()

        # Progress bar for resizing operation
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.hide()

        # Label to display the image
        self.label_image = QLabel(self.texts[self.lang]['no_image'])
        self.label_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_image.setStyleSheet("border: 1px solid #444; background: #232323; color: #bbb;")
        self.label_image.setMinimumSize(400, 400)
        self.label_image.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Layout for controls (left side)
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

        # Layout for image display (right side)
        image_layout = QVBoxLayout()
        image_layout.addWidget(self.label_image)

        # Main horizontal layout
        main_layout = QHBoxLayout()
        control_widget = QFrame()
        control_widget.setLayout(control_layout)
        control_widget.setMaximumWidth(260)
        main_layout.addWidget(control_widget)
        main_layout.addLayout(image_layout, stretch=1)

        self.setLayout(main_layout)

        # Enable drag & drop for the window
        self.setAcceptDrops(True)

        # Initialize UI texts and button states
        self.update_ui_texts()
        self.update_buttons_state()

    # --- Drag & Drop Handlers ---
    def dragEnterEvent(self, event):
        # Accept only file drops with image extensions
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.toLocalFile().lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dropEvent(self, event):
        # Load the dropped image file
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                self.load_image_from_path(file_path)
                break

    def load_image_from_path(self, file_path):
        # Load image from file and reset scale
        t = self.texts[self.lang]
        try:
            self.img_pil_original = Image.open(file_path).convert("RGBA")
            self.scale = 1.0
            self.update_buttons_state()
            self.start_interpolation()
        except Exception as e:
            QMessageBox.warning(self, t['title'], t['load_error'].format(e))
    # --- End Drag & Drop Handlers ---

    def update_ui_texts(self):
        # Update all UI texts according to the selected language
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
        # If no image loaded, show placeholder text
        if self.img_resized is None:
            self.label_image.clear()
            self.label_image.setText(t['no_image'])
            self.cached_pixmap = None
            self.last_pixmap_scaled = None
            self.update_frame_size_label()
        else:
            self.show_cached_pixmap()

    def show_cached_pixmap(self):
        # Display the cached pixmap, scaled to fit the label
        if self.cached_pixmap:
            label_w = self.label_image.width()
            label_h = self.label_image.height()
            pixmap_scaled = self.cached_pixmap.scaled(
                label_w, label_h,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.label_image.setPixmap(pixmap_scaled)
            self.last_pixmap_scaled = pixmap_scaled
            self.update_frame_size_label()

    def update_frame_size_label(self):
        # Update the label showing the image size in the frame
        if self.img_resized and self.last_pixmap_scaled:
            self.labels_values[3].setText(
                f"{self.last_pixmap_scaled.width()}×{self.last_pixmap_scaled.height()} px"
            )
        else:
            self.labels_values[3].setText("-")

    def switch_language(self, idx):
        # Change the UI language and update all texts
        self.lang = self.languages[idx]
        self.update_ui_texts()
        self.update_buttons_state()
        # Update interpolation label if visible
        if self.label_interpolation.isVisible():
            interp_name = self.texts[self.lang]['interp_methods'][self.combo_interp.currentIndex()]
            self.label_interpolation.setText(self.texts[self.lang]['interp_shown'].format(interp_name))

    def update_buttons_state(self):
        # Enable or disable buttons depending on the state (busy, image loaded, etc.)
        busy = self.worker is not None and self.worker.isRunning()
        self.btn_downscale.setEnabled(self.img_pil_original is not None and self.scale > 0.05 and not busy)
        self.btn_upscale.setEnabled(self.img_pil_original is not None and self.scale < 3.0 and not busy)
        self.btn_save.setEnabled(self.img_resized is not None and not busy)
        self.btn_load.setEnabled(not busy)

    def on_interp_changed(self):
        # Called when interpolation method is changed
        if self.img_pil_original:
            self.start_interpolation()

    def load_image(self):
        # Open file dialog to select and load an image
        t = self.texts[self.lang]
        file_path, _ = QFileDialog.getOpenFileName(
            self, t['load_title'], "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*)"
        )
        if not file_path:
            return
        self.load_image_from_path(file_path)

    def start_interpolation(self):
        # Start resizing the image in a background thread
        self.update_buttons_state() # Block buttons immediately
        # Stop previous worker if running
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
        # Get selected interpolation method
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
        # Create and start the worker thread
        self.worker = ResizeWorker(self.img_pil_original, self.scale, interp_method)
        self.worker.progress_changed.connect(self.progress_bar.setValue)
        self.worker.finished.connect(self.on_interpolation_finished)
        self.worker.finished.connect(self.update_buttons_state)
        self.worker.start()
        # Block buttons right after starting the worker
        self.update_buttons_state()

    def on_interpolation_finished(self, pil_img):
        # Called when resizing is finished
        self.img_resized = pil_img
        # Convert PIL image to QPixmap for display
        data = pil_img.tobytes("raw", "RGBA")
        qimg = QImage(data, pil_img.width, pil_img.height, QImage.Format.Format_RGBA8888)
        self.cached_pixmap = QPixmap.fromImage(qimg)
        self.show_cached_pixmap()
        self.progress_bar.hide()
        # Update parameter labels
        values = [
            f"{self.scale:.2f}x",
            f"{self.img_pil_original.width}×{self.img_pil_original.height} px",
            f"{pil_img.width}×{pil_img.height} px",
            f"{self.last_pixmap_scaled.width()}×{self.last_pixmap_scaled.height()} px"
        ]
        for lbl_value, val in zip(self.labels_values, values):
            lbl_value.setText(val)
        self.update_buttons_state()

    def resizeEvent(self, event):
        # Repaint the image when the window is resized
        super().resizeEvent(event)
        if self.cached_pixmap:
            self.show_cached_pixmap()

    def downscale(self):
        # Decrease the image scale by 0.05, minimum 0.05
        if not self.img_pil_original:
            QMessageBox.information(self, self.texts[self.lang]['title'], self.texts[self.lang]['please_load'])
            return
        if self.scale <= 0.05:
            return
        self.scale = max(0.05, self.scale - 0.05)
        self.start_interpolation()

    def upscale(self):
        # Increase the image scale by 0.05, maximum 3.0
        if not self.img_pil_original:
            QMessageBox.information(self, self.texts[self.lang]['title'], self.texts[self.lang]['please_load'])
            return
        if self.scale >= 3.0:
            return
        self.scale = min(3.0, self.scale + 0.05)
        self.start_interpolation()

    def save_as(self):
        # Save the resized image to a file
        t = self.texts[self.lang]
        if not self.img_resized:
            QMessageBox.warning(self, t['title'], t['save_none'])
            return
        file_path, _ = QFileDialog.getSaveFileName(
            self, t['save_title'], "",
            "PNG (*.png);;JPEG (*.jpg *.jpeg);;BMP (*.bmp);;GIF (*.gif);;All Files (*)"
        )
        if not file_path:
            return
        try:
            ext = os.path.splitext(file_path)[1].lower()
            fmt = None
            if ext in ('.jpg', '.jpeg'):
                fmt = 'JPEG'
            elif ext == '.bmp':
                fmt = 'BMP'
            elif ext == '.gif':
                fmt = 'GIF'
            else:
                fmt = 'PNG'
            self.img_resized.save(file_path, fmt)
            QMessageBox.information(self, t['title'], t['save_success'].format(file_path))
        except Exception as e:
            QMessageBox.warning(self, t['title'], t['save_error'].format(e))

# Application entry point
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageScaler()
    window.show()
    sys.exit(app.exec())
