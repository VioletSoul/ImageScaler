"""
ImageScaler - PyQt6 Image Resolution Scaler Application

This module provides a GUI application for loading, displaying, scaling,
and saving images with high-quality bicubic interpolation. It supports
dynamic resizing of the window and updates the displayed image accordingly.

Features:
- Load images of various formats.
- Scale images between 0.05x and 3.0x with fine step increments.
- Display detailed image size information in a neatly formatted table.
- Show the interpolation method used only when image is upscaled (>1.0x).
- Save the currently displayed scaled image to disk.
- Responsive GUI with buttons centered and disabled states visually distinct.
- Custom window icon displayed in the title bar and taskbar.

Author: VioletSoul
Date: 2025-05-23
"""

import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox,
    QSizePolicy, QGridLayout, QFrame
)
from PyQt6.QtGui import QPixmap, QImage, QIcon
from PyQt6.QtCore import Qt
from PIL import Image
import os


class ImageScaler(QWidget):
    """
    Main application window class for image scaling.

    Attributes:
        scale (float): Current scaling factor for the image.
        img_pil_original (PIL.Image.Image): Original loaded image.
        img_resized (PIL.Image.Image): Currently scaled image.
        label_image (QLabel): Widget displaying the image.
        label_interpolation (QLabel): Label showing interpolation method when upscaled.
        labels_values (list): List of QLabel widgets holding size info values.
        btn_downscale (QPushButton): Button to decrease scale.
        btn_upscale (QPushButton): Button to increase scale.
    """

    def __init__(self):
        """
        Initialize the GUI components, layout, and set window icon.
        """
        super().__init__()
        self.setWindowTitle("Image Resolution Scaler with Bicubic Interpolation")

        # Set window icon (make sure 'icon.png' is in the same folder as this script)
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            # If icon not found, no icon will be set
            print(f"Warning: Icon file not found at {icon_path}")

        # Initialize scale and image placeholders
        self.scale = 1.0
        self.img_pil_original = None
        self.img_resized = None

        # QLabel to display the image; styled and minimum size set
        self.label_image = QLabel("Load an image")
        self.label_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_image.setStyleSheet("border: 1px solid gray;")
        self.label_image.setMinimumSize(300, 300)
        self.label_image.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Grid layout for displaying image info in a table format
        self.info_grid = QGridLayout()
        self.info_grid.setContentsMargins(0, 0, 0, 0)
        self.info_grid.setHorizontalSpacing(10)
        self.info_grid.setVerticalSpacing(5)

        # Titles for the info table rows
        titles = [
            "Scale:",
            "Original size:",
            "Current size (with scale):",
            "Size in frame:"
        ]

        # Create QLabel widgets for titles and corresponding values
        self.labels_values = []
        for i, title in enumerate(titles):
            lbl_title = QLabel(title)
            lbl_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            lbl_value = QLabel("-")
            lbl_value.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.info_grid.addWidget(lbl_title, i, 0)
            self.info_grid.addWidget(lbl_value, i, 1)
            self.labels_values.append(lbl_value)

        # Container frame for the info grid with fixed max height (~2 rows)
        self.info_container = QFrame()
        self.info_container.setLayout(self.info_grid)
        self.info_container.setMaximumHeight(60)  # Adjust height to fit two rows comfortably
        self.info_container.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        # Horizontal layout to center the info container
        info_hbox = QHBoxLayout()
        info_hbox.addStretch(1)
        info_hbox.addWidget(self.info_container)
        info_hbox.addStretch(1)

        # Label for interpolation method, shown only when scale > 1.0
        self.label_interpolation = QLabel("")
        self.label_interpolation.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.label_interpolation.setStyleSheet("color: red; font-weight: bold;")
        self.label_interpolation.hide()  # Hidden by default

        # Control buttons with fixed max width and fixed size policy
        btn_load = QPushButton("Load Image")
        self.btn_downscale = QPushButton("Decrease Resolution")
        self.btn_upscale = QPushButton("Increase Resolution")
        btn_save = QPushButton("Save As...")

        for btn in (btn_load, self.btn_downscale, self.btn_upscale, btn_save):
            btn.setMaximumWidth(150)
            btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        # Connect buttons to their respective methods
        btn_load.clicked.connect(self.load_image)
        self.btn_downscale.clicked.connect(self.downscale)
        self.btn_upscale.clicked.connect(self.upscale)
        btn_save.clicked.connect(self.save_as)

        # Layout for buttons centered horizontally
        btn_layout = QHBoxLayout()
        btn_layout.addStretch(1)
        btn_layout.addWidget(btn_load)
        btn_layout.addWidget(self.btn_downscale)
        btn_layout.addWidget(self.btn_upscale)
        btn_layout.addWidget(btn_save)
        btn_layout.addStretch(1)

        # Vertical layout for image and interpolation label
        image_layout = QVBoxLayout()
        image_layout.addWidget(self.label_image)
        image_layout.addWidget(self.label_interpolation)
        image_layout.setAlignment(self.label_interpolation, Qt.AlignmentFlag.AlignLeft)

        # Main vertical layout combining all parts
        main_layout = QVBoxLayout()
        main_layout.addLayout(image_layout)
        main_layout.addLayout(info_hbox)
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

        # Style disabled buttons with readable gray text and background
        disabled_style = """
            QPushButton:disabled {
                color: #666666;
                background-color: #cccccc;
                border: 1px solid #999999;
            }
        """
        for btn in (self.btn_downscale, self.btn_upscale):
            btn.setStyleSheet(disabled_style)

        # Initialize button states
        self.update_buttons_state()

    def load_image(self):
        """
        Open a file dialog to load an image and reset scale.
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "",
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
            QMessageBox.warning(self, "Error", f"Failed to load image:\n{e}")

    def update_image(self):
        """
        Resize the original image according to current scale using bicubic interpolation,
        update the displayed pixmap, and refresh info labels.
        """
        if self.img_pil_original is None:
            return

        label_w = self.label_image.width()
        label_h = self.label_image.height()

        # Calculate new image size based on scale
        new_img_w = max(1, int(self.img_pil_original.width * self.scale))
        new_img_h = max(1, int(self.img_pil_original.height * self.scale))

        # Resize image with bicubic interpolation for quality
        self.img_resized = self.img_pil_original.resize((new_img_w, new_img_h), Image.BICUBIC)

        # Convert PIL image to QPixmap for display
        data = self.img_resized.tobytes("raw", "RGBA")
        qimg = QImage(data, new_img_w, new_img_h, QImage.Format.Format_RGBA8888)
        pixmap = QPixmap.fromImage(qimg)

        # Scale pixmap to fit label while keeping aspect ratio
        pixmap_scaled = pixmap.scaled(label_w, label_h, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.FastTransformation)

        self.label_image.setPixmap(pixmap_scaled)

        # Update info labels with current data
        values = [
            f"{self.scale:.2f}x",
            f"{self.img_pil_original.width}×{self.img_pil_original.height} px",
            f"{new_img_w}×{new_img_h} px",
            f"{pixmap_scaled.width()}×{pixmap_scaled.height()} px"
        ]
        for lbl_value, val in zip(self.labels_values, values):
            lbl_value.setText(val)

        # Show interpolation method label only when image is upscaled
        if self.scale > 1.0:
            self.label_interpolation.setText("Interpolation method: Bicubic")
            self.label_interpolation.show()
        else:
            self.label_interpolation.hide()

    def resizeEvent(self, event):
        """
        Override resize event to update image display on window resize.
        """
        super().resizeEvent(event)
        self.update_image()

    def downscale(self):
        """
        Decrease scale by 0.05 down to minimum 0.05 and update UI.
        """
        if self.img_pil_original is None:
            return
        self.scale = max(0.05, self.scale - 0.05)
        self.update_image()
        self.update_buttons_state()

    def upscale(self):
        """
        Increase scale by 0.05 up to maximum 3.0 and update UI.
        """
        if self.img_pil_original is None:
            return
        if self.scale < 3.0:
            self.scale = min(3.0, self.scale + 0.05)
            self.update_image()
        self.update_buttons_state()

    def update_buttons_state(self):
        """
        Enable or disable scale buttons based on current scale limits.
        """
        self.btn_upscale.setEnabled(self.scale < 3.0)
        self.btn_downscale.setEnabled(self.scale > 0.05)

    def save_as(self):
        """
        Open a file dialog to save the currently displayed scaled image.
        """
        if self.img_resized is None:
            QMessageBox.information(self, "Save", "No image to save.")
            return
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Image As", "",
            "PNG (*.png);;JPEG (*.jpg *.jpeg);;BMP (*.bmp);;All Files (*)"
        )
        if not file_path:
            return
        try:
            self.img_resized.save(file_path)
            QMessageBox.information(self, "Save", f"Image saved: {file_path}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save image:\n{e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageScaler()
    window.resize(900, 700)
    window.show()
    sys.exit(app.exec())
