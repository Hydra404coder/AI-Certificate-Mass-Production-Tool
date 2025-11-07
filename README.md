# 🎓 Certificate Mass Production Tool

> **Automate the creation of personalized certificates with ease and precision**

A comprehensive desktop application that streamlines the process of generating bulk certificates by automatically detecting text regions on certificate templates and mapping them to Excel data for mass production.

![Certificate Tool Demo](https://img.shields.io/badge/Python-PyQt6-blue) ![React](https://img.shields.io/badge/React-18.2.0-blue) ![Node.js](https://img.shields.io/badge/Node.js-Express-green) ![OpenCV](https://img.shields.io/badge/OpenCV-4.10.0-orange)

## ✨ Features

### 🎯 Core Functionality
- **Intelligent Text Detection**: Automatically detects empty regions suitable for text placement using advanced OpenCV algorithms
- **Interactive Mask Editor**: Click-and-drag interface to create, resize, rotate, and position text regions
- **Excel Integration**: Seamless mapping between certificate variables and Excel column data
- **Bulk Generation**: Generate hundreds of personalized certificates in seconds
- **High-Quality Output**: Export certificates in high-resolution JPG format

### 🎨 Advanced Styling
- **Rich Text Formatting**: Bold, italic, underline, and custom color options for each variable
- **Smart Font Scaling**: Automatic font size adjustment to fit text perfectly within masked regions
- **Multi-word Handling**: Intelligent truncation for names with 3+ words (keeps first two)
- **Visual Feedback**: Real-time preview of text placement and formatting

### 🖥️ User Interface
- **Modern Dark Theme**: Professional dark-themed interface with purple accent colors
- **Click-to-Browse**: Enhanced drag-and-drop zones with file browser integration
- **Full-Screen Mode**: Immersive full-screen experience for better workflow
- **Responsive Layout**: Optimized 5%/95% split for maximum preview area

### 🌐 Web Integration
- **React Frontend**: Beautiful parallax landing page with step-by-step guide
- **Auto-scroll Feature**: Animated "scroll down" hint with smooth auto-scrolling
- **Express/Flask Backend**: Dual backend support for launching the desktop application
- **One-Click Launch**: Start the certificate tool directly from the web interface

## 📋 Prerequisites

Before installing, ensure you have the following installed on your system:

- **Python 3.8+** ([Download Python](https://www.python.org/downloads/))
- **Node.js 14+** ([Download Node.js](https://nodejs.org/))
- **npm** (comes with Node.js)

### System Requirements
- **Operating System**: Windows 10/11, macOS 10.14+, or Linux Ubuntu 18.04+
- **RAM**: Minimum 4GB (8GB recommended for large batch processing)
- **Storage**: 500MB free space
- **Display**: 1920x1080 or higher resolution recommended

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone <your-repository-url>
cd certfi
```

### 2. Install Python Dependencies
```bash
# Install required Python packages
pip install -r requirements.txt
```

**Required Python packages:**
- `PyQt6==6.7.1` - Modern GUI framework
- `opencv-python==4.10.0.84` - Computer vision for text detection
- `numpy==2.2.2` - Numerical operations
- `pandas==2.2.3` - Excel data processing
- `openpyxl==3.1.5` - Excel file handling
- `Pillow==10.4.0` - Image processing

### 3. Install Node.js Dependencies
```bash
# Install backend dependencies
npm install

# Install React frontend dependencies
cd my-app
npm install
cd ..
```

### 4. Verify Installation
```bash
# Test Python dependencies
python -c "import PyQt6, cv2, pandas; print('Python dependencies OK')"

# Test Node.js backend
node server.js
# Should output: "Node backend listening on http://localhost:5000"
```

## 🎮 How to Run

You have multiple options to launch the Certificate Mass Production Tool:

### Option 1: Web Interface (Recommended)
1. **Start the Backend Server:**
   ```bash
   # Terminal 1: Start Node.js backend
   node server.js
   ```

2. **Start the React Frontend:**
   ```bash
   # Terminal 2: Start React development server
   cd my-app
   npm start
   ```

3. **Access the Application:**
   - Open your browser and go to `http://localhost:3000`
   - Click the **"Start It"** button to launch the desktop application
   - Enjoy the full-screen certificate tool experience!

### Option 2: Direct Python Launch
```bash
# Run the desktop application directly
python main.py
```

### Option 3: Flask Backend Alternative
```bash
# Alternative backend using Flask
python server.py
```

## 📖 Step-by-Step Usage Guide

### 1. 📁 **Drag/Drop Template**
- **Supported Formats**: PNG, JPG, JPEG, BMP, TIF, TIFF
- Drag your certificate template into the **TempDrop** area
- Or click the drop zone to browse and select files
- The system automatically detects potential text regions

### 2. 🎯 **Setup Masked Areas**
- **Auto-Detection**: The tool automatically identifies empty spaces suitable for text
- **Manual Adjustment**: Click and drag to create custom masked regions
- **Interactive Controls**: 
  - **Resize**: Drag corner/edge handles
  - **Move**: Drag the center handle
  - **Rotate**: Use the rotation handle above each mask
  - **Delete**: Click the ✕ button in the variable panel

### 3. 🔗 **Variable Mapping**
- Assign labels to each masked area (a, b, c...)
- Enter meaningful names like "NAME", "DATE", "SCORE"
- These labels must **exactly match** your Excel column headers
- Example mapping:
  - Mask A → "NAME"
  - Mask B → "DATE" 
  - Mask C → "CERTIFICATE_ID"

### 4. 🎨 **Text Formatting**
- **Bold (B)**: Make text bold
- **Italic (I)**: Apply italic styling
- **Underline (U)**: Add underline decoration
- **Color Picker (◙)**: Choose custom text colors
- **Real-time Preview**: See changes instantly on the template

### 5. 📊 **Upload Excel Data**
- **Supported Formats**: .xlsx, .xls
- **Header Requirement**: First row must contain column names matching your variable labels
- **Validation**: The tool automatically validates column count and names
- **Example Excel Structure**:
  ```
  | NAME         | DATE       | CERTIFICATE_ID |
  |--------------|------------|----------------|
  | John Doe     | 2024-11-08 | CERT001        |
  | Jane Smith   | 2024-11-08 | CERT002        |
  | Bob Johnson  | 2024-11-08 | CERT003        |
  ```

### 6. 📥 **Generate & Download**
- **Bulk Generation**: Creates one certificate per Excel row
- **Download Options**: 
  - **Individual**: Save single certificates as needed
  - **Batch Export**: Download all certificates to a folder
- **High Quality**: Maintains original template resolution
- **Format**: Exports as high-quality JPG files (95% quality)

## 🛠️ Advanced Features

### Text Fitting Algorithm
- **Smart Scaling**: Automatically adjusts font size to fit within masked regions
- **Long Name Handling**: Intelligently handles names with 3+ words (keeps first two)
- **Precise Positioning**: Uses advanced font metrics for pixel-perfect text placement
- **Border Padding**: Adds 6px internal padding to prevent text from touching mask edges

### File Management
- **Auto-numbering**: Generated files are named `certificate_001.jpg`, `certificate_002.jpg`, etc.
- **Organized Output**: Batch exports create organized folder structures
- **Search Functionality**: Built-in search to quickly find specific certificates

### Quality Control
- **Preview Mode**: Real-time preview before generation
- **Error Validation**: Comprehensive checks for data consistency
- **Font Optimization**: Binary search algorithm finds optimal font sizes
- **Memory Efficient**: Handles large datasets without memory issues

## 🎨 Customization

### Theme Customization
The application uses a modern dark theme with purple accents. Key colors:
- **Background**: `#181818` (dark gray)
- **Accent**: `#8b5cf6` (purple)
- **Text**: `#eee` (light gray)

### Layout Preferences
- **Default Split**: 5% left panel, 95% preview area
- **Full-Screen**: Launches in full-screen mode for immersive experience
- **Responsive**: Adapts to different screen sizes

## ❗ Troubleshooting

### Common Issues

**1. Python Dependencies Not Found**
```bash
# Solution: Reinstall dependencies
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

**2. React App Won't Start**
```bash
# Solution: Clear node modules and reinstall
cd my-app
rm -rf node_modules package-lock.json
npm install
npm start
```

**3. Backend Connection Failed**
- Ensure backend is running on port 5000
- Check firewall settings
- Verify CORS configuration

**4. Certificate Generation Errors**
- Verify Excel column headers match variable names exactly
- Check template image format compatibility
- Ensure sufficient disk space for output

**5. Text Appears Cut Off**
- Increase mask size using resize handles
- Reduce text content if too long
- Check font scaling settings

### Performance Tips
- **Large Datasets**: Process in batches of 100-500 certificates
- **Memory**: Close other applications when processing large batches
- **Storage**: Ensure 2-3x dataset size in available disk space

## 🤝 Contributing

We welcome contributions! Please feel free to submit issues, feature requests, or pull requests.

### Development Setup
1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Submit a pull request with detailed description

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Author

**Made by Akhil Shibu** ✌️😊

## 🙏 Acknowledgments

- **PyQt6** - Modern cross-platform GUI toolkit
- **OpenCV** - Computer vision library for text detection
- **React** - Frontend user interface framework
- **Express.js** - Web application framework for Node.js

---

### 📞 Support

If you encounter any issues or have questions:
1. Check the troubleshooting section above
2. Search existing issues in the repository
3. Create a new issue with detailed description and error logs

**Happy Certificate Generating! 🎓✨**