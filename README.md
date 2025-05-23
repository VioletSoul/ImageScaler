# ImageScaler

## Brief Description
ImageScaler is a simple and user-friendly PyQt6 application for loading, viewing, scaling, and saving images using high-quality bicubic interpolation. The program allows easy adjustment of image resolution while preserving quality and displays detailed size information.

## Project Description
This application was created for users who need a fast and quality image resolution changer without complex graphic editors. Using PyQt6 provides a convenient and responsive interface, and Pillow ensures high-quality image processing. Future plans include expanding functionality, adding support for more formats, and improving the interface.

## Key Features
- Load images in popular formats (PNG, JPEG, BMP, GIF, etc.).
- Scale images with 0.05 step increments in the range from 0.05x to 3.0x.
- High-quality bicubic interpolation for smooth resizing.
- Display detailed size information: original size, current scaled size, and displayed size in the window.
- Indicate the interpolation method used when upscaling.
- Save the scaled image in various formats.
- Responsive interface with centered elements and visually clear buttons.

## Installation and Running
1. Make sure you have Python version 3.7 or higher installed.
2. Install required dependencies by running:  
   `pip install PyQt6 Pillow`
3. Run the application with:  
   `python scaling.py`

## Usage
- Click the **Load Image** button to select an image.
- Use the **Increase Resolution** and **Decrease Resolution** buttons to adjust the scale.
- Size information updates automatically.
- When scaling above 1.0x, a label with the interpolation method appears.
- To save the result, click **Save As...** and choose the destination.

## Project Goals
- Provide a simple and fast tool for image scaling while preserving quality.
- Ensure a clear and responsive user interface.
- Minimize dependencies for easy installation and use.

## Technologies
- PyQt6 for the graphical interface.
- Pillow (PIL) for image processing and scaling.
- Python 3.7+.

## Comparison with Alternatives
Unlike full-featured graphic editors, ImageScaler is a lightweight and fast application without unnecessary features. Compared to simple image viewers, it provides precise control over scale and quality.

## License
This project is licensed under the MIT License.

## Author
VioletSoul

## Contact
For questions and suggestions, please use the Issues section on GitHub or contact the author directly.

---

*Thank you for your interest and for using ImageScaler!*
