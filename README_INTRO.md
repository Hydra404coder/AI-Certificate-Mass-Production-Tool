# Certificate Mass Production Tool - Intro Website

This is a professional intro website for the Certificate Mass Production Tool, featuring:

- **Parallax scrolling effects** - Smooth, immersive scrolling experience
- **Modern design** - Inspired by techfolio template with dark theme and gradient accents
- **Interactive illustrations** - Visual guides for each step of the certificate creation process
- **Responsive layout** - Works seamlessly on desktop, tablet, and mobile devices

## 🚀 Getting Started

### Prerequisites
- Node.js (v14 or higher)
- Python 3.x
- npm or yarn

### Installation & Running

#### 1. Start the React Frontend

```powershell
cd my-app
npm install
npm start
```

The React app will open at `http://localhost:3000`

#### 2. Start the Flask Backend (Optional - for "Start It" button)

```powershell
# In the root directory (certfi)
pip install -r requirements_server.txt
python server.py
```

The Flask server will run at `http://localhost:5000`

### Alternative: Direct Execution

If you don't want to use the Flask backend, the "Start It" button can be modified to:

1. **Direct Python execution** (if running locally):
   ```javascript
   const { spawn } = require('child_process');
   spawn('python', ['main.py']);
   ```

2. **Open file dialog** to select main.py

3. **Desktop shortcut** that runs main.py

## 📋 Features

### Step-by-Step Visualization

1. **Drag/Drop** - Upload certificate template with visual drag-drop indicator
2. **Setup Masked Area** - Manual mask selection and variable assignment illustration
3. **Mapping** - Variable to column header mapping visualization
4. **Format** - Text styling options (Bold, Italic, Underline, Color)
5. **Upload XL Sheet** - Excel file upload with validation warnings
6. **Output** - Bulk certificate generation preview

### Design Features

- Dark theme with purple/indigo gradient accents
- Container shadows with glow effects
- Smooth parallax scrolling animations
- Hover effects and transitions
- Custom scrollbar styling
- Responsive grid layouts
- Mobile-friendly navigation

## 🎨 Color Theme

Primary colors match the techfolio template aesthetic:
- Background: `#0f172a`, `#1e293b`
- Accents: Purple (`#8b5cf6`), Indigo (`#6366f1`), Pink (`#ec4899`)
- Text: Light gray shades for hierarchy

## 🔧 Customization

### Modify Colors
Edit the CSS variables in `src/App.css`:
```css
:root {
  --accent-purple: #8b5cf6;
  --accent-indigo: #6366f1;
  /* ... */
}
```

### Adjust Parallax Speed
Modify the scroll multipliers in `src/App.js`:
```javascript
style={{ transform: `translateY(${scrollY * 0.5}px)` }}
```

### Change Illustrations
The SVG illustrations are inline in `App.js` - customize colors, shapes, and animations directly.

## 📦 Build for Production

```powershell
cd my-app
npm run build
```

The optimized build will be in the `my-app/build` directory.

## 🤝 Integration with main.py

The "Start It" button triggers the main.py certificate tool. Three integration methods:

1. **Flask Backend** (Recommended): Uses server.py to execute main.py
2. **Electron**: Package as desktop app with direct Python execution
3. **Manual**: Button opens instructions to run main.py

## 📝 Notes

- Ensure main.py is in the root `certfi` directory
- Flask server must be running for the "Start It" button to work
- All illustrations are SVG-based for crisp display on any screen
- Parallax effects are performance-optimized with CSS transforms

## 🎯 Future Enhancements

- Add video tutorials in each section
- Include interactive demos
- Multi-language support
- Dark/light theme toggle
- Progress tracking animation

---

**Created with ❤️ for seamless certificate generation**
