import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox,
    QSizePolicy, QGridLayout, QFrame, QComboBox
)
from PyQt6.QtGui import QPixmap, QImage, QIcon
from PyQt6.QtCore import Qt
from PIL import Image

class ImageScaler(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Resolution Scaler")

        # Set window icon if available
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Supported languages and default language
        self.languages = ['en', 'ru']
        self.lang = 'en'

        # Localized UI texts for English and Russian
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
            }
        }

        # Current scale factor
        self.scale = 1.0
        # Original loaded PIL image
        self.img_pil_original = None
        # Resized image after interpolation
        self.img_resized = None

        # Create UI elements

        # Combo box for interpolation methods
        self.combo_interp = QComboBox()
        self.combo_interp.addItems(self.texts[self.lang]['interp_methods'])
        self.combo_interp.setCurrentIndex(2)  # Default Bicubic
        self.combo_interp.setMaximumWidth(180)
        self.combo_interp.currentIndexChanged.connect(self.update_image)

        # Combo box for language selection
        self.combo_lang = QComboBox()
        self.combo_lang.addItems(['English', 'Русский'])
        self.combo_lang.setMaximumWidth(120)
        self.combo_lang.currentIndexChanged.connect(self.switch_language)

        # Buttons for load, scale down/up, save
        self.btn_load = QPushButton()
        self.btn_downscale = QPushButton()
        self.btn_upscale = QPushButton()
        self.btn_save = QPushButton()

        # Set fixed width and size policy for buttons
        for btn in (self.btn_load, self.btn_downscale, self.btn_upscale, self.btn_save):
            btn.setMaximumWidth(180)
            btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        # Connect buttons to their handlers
        self.btn_load.clicked.connect(self.load_image)
        self.btn_downscale.clicked.connect(self.downscale)
        self.btn_upscale.clicked.connect(self.upscale)
        self.btn_save.clicked.connect(self.save_as)

        # Grid layout to show image parameters (scale, sizes)
        self.info_grid = QGridLayout()
        self.labels_values = []
        # Create labels for titles and values
        for i in range(4):
            lbl_title = QLabel()
            lbl_value = QLabel("-")
            self.info_grid.addWidget(lbl_title, i, 0)
            self.info_grid.addWidget(lbl_value, i, 1)
            self.labels_values.append(lbl_value)
        self.info_titles = [self.info_grid.itemAtPosition(i, 0).widget() for i in range(4)]

        # Container frame for info grid
        self.info_container = QFrame()
        self.info_container.setLayout(self.info_grid)
        self.info_container.setMaximumWidth(220)

        # Label to show interpolation method when scaling up
        self.label_interpolation = QLabel("")
        self.label_interpolation.setStyleSheet("color: red; font-weight: bold;")
        self.label_interpolation.hide()

        # Label to display the image
        self.label_image = QLabel(self.texts[self.lang]['no_image'])
        self.label_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_image.setStyleSheet("border: 1px solid #444; background: #232323; color: #bbb;")
        self.label_image.setMinimumSize(400, 400)
        self.label_image.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Layout for controls: language selector, interpolation selector, buttons, info
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
        control_layout.addSpacing(10)
        control_layout.addWidget(self.label_interpolation)
        control_layout.addStretch(1)

        # Layout for image display
        image_layout = QVBoxLayout()
        image_layout.addWidget(self.label_image)

        # Main horizontal layout: controls on left, image on right
        main_layout = QHBoxLayout()
        control_widget = QFrame()
        control_widget.setLayout(control_layout)
        control_widget.setMaximumWidth(260)
        main_layout.addWidget(control_widget)
        main_layout.addLayout(image_layout, stretch=1)

        self.setLayout(main_layout)

        # Style for disabled buttons
        disabled_style = """
            QPushButton:disabled {
                color: #666666;
                background-color: #cccccc;
                border: 1px solid #999999;
            }
        """
        for btn in (self.btn_downscale, self.btn_upscale):
            btn.setStyleSheet(disabled_style)

        # Initialize UI texts and button states
        self.update_ui_texts()
        self.update_buttons_state()

    def update_ui_texts(self):
        """Update all UI texts according to the selected language."""
        t = self.texts[self.lang]
        self.setWindowTitle(t['title'])
        self.btn_load.setText(t['load'])
        self.btn_downscale.setText(t['downscale'])
        self.btn_upscale.setText(t['upscale'])
        self.btn_save.setText(t['save'])
        self.label_image.setText(t['no_image'])

        titles = [t['scale'], t['orig_size'], t['curr_size'], t['frame_size']]
        for lbl, title in zip(self.info_titles, titles):
            lbl.setText(title)

        # Update interpolation combo box without triggering signals
        self.combo_interp.blockSignals(True)
        self.combo_interp.clear()
        self.combo_interp.addItems(t['interp_methods'])
        self.combo_interp.setCurrentIndex(2)  # Default Bicubic
        self.combo_interp.blockSignals(False)

        # Update language combo box texts
        self.combo_lang.setItemText(0, "English")
        self.combo_lang.setItemText(1, "Русский")

    def switch_language(self, idx):
        """Switch UI language and update texts."""
        self.lang = self.languages[idx]
        self.update_ui_texts()
        self.update_image()

    def load_image(self):
        """Open file dialog to load an image, convert to RGBA PIL Image."""
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
            self.update_image()
            self.update_buttons_state()
        except Exception as e:
            QMessageBox.warning(self, t['title'], t['load_error'].format(e))

    def update_image(self):
        """Resize and display the image according to current scale and interpolation."""
        if self.img_pil_original is None:
            return

        label_w = self.label_image.width()
        label_h = self.label_image.height()
        new_img_w = max(1, int(self.img_pil_original.width * self.scale))
        new_img_h = max(1, int(self.img_pil_original.height * self.scale))

        # Map combo box index to Pillow interpolation method
        idx = self.combo_interp.currentIndex()
        methods = {
            0: Image.NEAREST,
            1: Image.BILINEAR,
            2: Image.BICUBIC,
            3: Image.LANCZOS,
        }
        method = methods.get(idx, Image.BICUBIC)
        self.img_resized = self.img_pil_original.resize((new_img_w, new_img_h), method)

        # Convert PIL image to QImage for display
        data = self.img_resized.tobytes("raw", "RGBA")
        qimg = QImage(data, new_img_w, new_img_h, QImage.Format.Format_RGBA8888)
        pixmap = QPixmap.fromImage(qimg)
        pixmap_scaled = pixmap.scaled(label_w, label_h,
                                      Qt.AspectRatioMode.KeepAspectRatio,
                                      Qt.TransformationMode.SmoothTransformation)
        self.label_image.setPixmap(pixmap_scaled)

        # Update info labels with current scale and sizes
        values = [
            f"{self.scale:.2f}x",
            f"{self.img_pil_original.width}×{self.img_pil_original.height} px",
            f"{new_img_w}×{new_img_h} px",
            f"{pixmap_scaled.width()}×{pixmap_scaled.height()} px"
        ]
        for lbl_value, val in zip(self.labels_values, values):
            lbl_value.setText(val)

        # Show interpolation method label only if scale > 1.0
        if self.scale > 1.0:
            interp_name = self.texts[self.lang]['interp_methods'][idx]
            self.label_interpolation.setText(self.texts[self.lang]['interp_shown'].format(interp_name))
            self.label_interpolation.show()
        else:
            self.label_interpolation.hide()

    def resizeEvent(self, event):
        """Update image display when window is resized."""
        super().resizeEvent(event)
        self.update_image()

    def downscale(self):
        """Decrease scale factor by 0.05, minimum 0.05."""
        if self.img_pil_original is None:
            return
        self.scale = max(0.05, self.scale - 0.05)
        self.update_image()
        self.update_buttons_state()

    def upscale(self):
        """Increase scale factor by 0.05, maximum 3.0."""
        if self.img_pil_original is None:
            return
        if self.scale < 3.0:
            self.scale = min(3.0, self.scale + 0.05)
            self.update_image()
        self.update_buttons_state()

    def update_buttons_state(self):
        """Enable or disable scale buttons depending on image load and scale limits."""
        if self.img_pil_original is None:
            self.btn_upscale.setEnabled(False)
            self.btn_downscale.setEnabled(False)
        else:
            self.btn_upscale.setEnabled(self.scale < 3.0)
            self.btn_downscale.setEnabled(self.scale > 0.05)

    def save_as(self):
        """Open file dialog to save the resized image."""
        t = self.texts[self.lang]
        if self.img_resized is None:
            QMessageBox.information(self, t['title'], t['save_none'])
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
