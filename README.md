# ImageScaler

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![PyQt6](https://img.shields.io/badge/PyQt6-41CD52?style=flat&logo=qt&logoColor=white)
![Pillow](https://img.shields.io/badge/Pillow-FFD43B?style=flat&logo=python&logoColor=blue)
![Image Processing](https://img.shields.io/badge/Image%20Processing-✓-orange)
![Cross-Platform](https://img.shields.io/badge/Cross--Platform-✓-blueviolet)
![Multilingual](https://img.shields.io/badge/Multilingual-✓-lightgrey)
![License](https://img.shields.io/badge/License-MIT-blue)

## Brief Description
ImageScaler is a simple and user-friendly PyQt6 application for loading, viewing, scaling, and saving images using high-quality interpolation methods (Nearest, Bilinear, Bicubic, Lanczos). The program allows easy resolution changes while preserving quality and displays detailed size information.

## Project Description
This application was created for users who need quick and quality image resolution changes without complex graphic editors. PyQt6 provides a convenient and responsive interface, while Pillow ensures high-quality image processing. Future plans include expanding functionality, adding support for more formats, and improving the interface.

## Main Features
- Load images in popular formats (PNG, JPEG, BMP, GIF, etc.).
- Scale images with a step of 0.05 within the range from 0.05x to 3.0x.
- Four interpolation methods: Nearest Neighbor, Bilinear, Bicubic, Lanczos.
- Display detailed size information: original, current with scale, and displayed in the window.
- Indication of the interpolation method used when scaling up.
- Save scaled images in various formats.
- Adaptive interface with centered elements and visually clear buttons.
- Increase and decrease buttons are disabled until an image is loaded.
- Support for English and Russian languages with interface switching.

## Installation and Launch
1. Make sure you have Python version 3.7 or higher installed.
2. Install required dependencies with:  
   `pip install PyQt6 pillow`
3. Run the application with:  
   `python scaling.py`

## Usage
- Click **Load Image** to select an image.
- Use **Increase** and **Decrease** buttons to adjust the scale.
- Size information updates automatically.
- When scaling above 1.0x, the interpolation method name appears.
- To save the result, click **Save As...** and choose the destination.
- Switch interface language via the dropdown in the top-left corner.

## Project Goals
- Provide a simple and fast tool for image scaling with quality preservation.
- Ensure a clear and responsive user interface.
- Minimize dependencies for easy installation and use.

## Technologies
- PyQt6 — for graphical user interface.
- Pillow (PIL) — for image processing and scaling.
- Python 3.7+.

## Comparison with Alternatives
Unlike full-featured graphic editors, ImageScaler is a lightweight and fast application without unnecessary features. Compared to simple image viewers, it offers precise control over scale and quality.

## License
The project is licensed under the MIT License.

## Author
VioletSoul

## Contacts
For questions and suggestions, please use the Issues section on GitHub or contact the author directly.

---

*Thank you for your interest and for using ImageScaler!*
