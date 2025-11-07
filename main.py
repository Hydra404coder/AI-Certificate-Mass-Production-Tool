newyguy

import sys
import os
import string
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional

import numpy as np
import cv2
import pandas as pd

from PyQt6.QtCore import (
    Qt, QRect, QPoint, QSize, pyqtSignal, QEvent
)
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QPixmap, QImage, QFont, QFontMetrics, QAction
)
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QSplitter, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QScrollArea, QFileDialog, QMessageBox,
    QGroupBox, QFrame, QToolButton, QSizePolicy, QColorDialog
)

# -------------------------
# Data structures
# -------------------------

@dataclass
class TextStyle:
    bold: bool = False
    italic: bool = False
    underline: bool = False
    color: QColor = field(default_factory=lambda: QColor(20, 20, 20))

@dataclass
class MaskRegion:
    letter: str
    rect: QRect                 # in IMAGE coordinates (original size)
    label_text: str = ""        # user-assigned string (e.g., NAME)
    style: TextStyle = field(default_factory=TextStyle)
    rotation: float = 0.0       # NEW: rotation in degrees

# -------------------------
# Utility functions
# -------------------------

def load_qimage(path: str) -> Optional[QImage]:
    img = QImage(path)
    if img.isNull():
        return None
    # Convert to a paintable format
    return img.convertToFormat(QImage.Format.Format_RGBA8888)

def cv_rect_to_qrect(x, y, w, h) -> QRect:
    return QRect(int(x), int(y), int(w), int(h))

def qrect_to_tuple(r: QRect) -> Tuple[int, int, int, int]:
    return r.x(), r.y(), r.width(), r.height()

def sort_rects_reading_order(rects: List[QRect]) -> List[QRect]:
    # Sort top-to-bottom, then left-to-right
    return sorted(rects, key=lambda r: (r.y(), r.x()))

def detect_blank_regions_cv(image_path: str, max_regions: int = 8) -> List[QRect]:
    """
    Enhanced auto-detection of empty regions suitable for text placement.
    Uses multiple techniques including OCR and contour analysis.
    """
    img = cv2.imread(image_path)
    if img is None:
        return []
    h, w = img.shape[:2]
    
    # Convert to grayscale and enhance contrast
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)
    
    # 1. Text Detection via Edge Analysis
    edges = cv2.Canny(enhanced, 50, 150)
    kernel = np.ones((5, 5), np.uint8)
    edges_dil = cv2.dilate(edges, kernel, iterations=2)
    
    # Create a text presence mask
    text_mask = edges_dil.copy()
    text_mask = cv2.dilate(text_mask, np.ones((15,15), np.uint8), iterations=1)
    
    # 2. Potential Text Area Detection
    # Threshold to find dark regions (potential text)
    _, dark_mask = cv2.threshold(enhanced, 180, 255, cv2.THRESH_BINARY_INV)
    dark_mask = cv2.dilate(dark_mask, np.ones((7,7), np.uint8), iterations=1)
    
    # Combine masks to get refined empty regions
    empty_mask = cv2.bitwise_not(cv2.bitwise_or(text_mask, dark_mask))
    
    # Clean up noise
    empty_mask = cv2.erode(empty_mask, np.ones((5,5), np.uint8), iterations=1)
    empty_mask = cv2.dilate(empty_mask, np.ones((7,7), np.uint8), iterations=1)
    
    # Find contours of empty regions
    contours, _ = cv2.findContours(empty_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Process contours to get rectangles
    rects = []
    total_area = w * h
    min_area = total_area * 0.003  # Minimum area threshold
    max_area = total_area * 0.15   # Maximum area threshold
    
    for cnt in contours:
        # Get bounding rectangle
        x, y, ww, hh = cv2.boundingRect(cnt)
        area = ww * hh
        
        # Filter based on size and aspect ratio
        if area < min_area or area > max_area:
            continue
            
        aspect_ratio = ww / hh if hh != 0 else 0
        if aspect_ratio < 0.2 or aspect_ratio > 5:  # Filter extreme aspect ratios
            continue
            
        # Check if rectangle is suitable for text
        roi = enhanced[y:y+hh, x:x+ww]
        if roi.size == 0:
            continue
            
        # Calculate text-free percentage in ROI
        text_free_ratio = np.sum(roi > 200) / roi.size
        if text_free_ratio < 0.4:  # Must be at least 40% free of dark pixels
            continue
        
        # Add rectangle with some padding
        padding = int(min(ww, hh) * 0.1)
        x = max(0, x - padding)
        y = max(0, y - padding)
        ww = min(w - x, ww + padding * 2)
        hh = min(h - y, hh + padding * 2)
        
        rects.append(cv_rect_to_qrect(x, y, ww, hh))
    
    # Merge overlapping and nearby rectangles
    merged = []
    for r in sort_rects_reading_order(rects):
        merged_flag = False
        for j, m in enumerate(merged):
            # Check for overlap or proximity
            expanded = QRect(m)
            expanded.adjust(-10, -10, 10, 10)
            if r.intersects(expanded):
                merged[j] = m.united(r)
                merged_flag = True
                break
        if not merged_flag:
            merged.append(r)
    
    # Final filtering and limiting
    final_rects = []
    for r in sort_rects_reading_order(merged):
        # Ensure minimum dimensions for text
        if r.width() >= 60 and r.height() >= 25:
            final_rects.append(r)
    
    if len(final_rects) > max_regions:
        final_rects = final_rects[:max_regions]
    
    return final_rects

def ensure_dir(path: str):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

# -------------------------
# Drag & Drop widgets
# -------------------------

class DropArea(QFrame):
    fileDropped = pyqtSignal(str)

    def __init__(self, title: str, exts: List[str]):
        super().__init__()
        self.setAcceptDrops(True)
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setStyleSheet("""
            QFrame {
                border: 2px dashed #444;
                border-radius: 10px;
                background-color: #181818;
            }
            QFrame:hover {
                background-color: #222;
                border-color: #888;
            }
        """)
        self.setMinimumHeight(140)
        self.exts = set([e.lower() for e in exts])
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(self)
        
        # Main label
        self.label = QLabel(title)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("color: #eee; font-size: 16px;")
        # Click instruction
        self.click_label = QLabel("Drop files here or click to browse")
        self.click_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.click_label.setStyleSheet("color: #bbb; font-size: 12px;")
        # Extensions info
        ext_list = ", ".join(self.exts)
        self.ext_label = QLabel(f"Supported: {ext_list}")
        self.ext_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ext_label.setStyleSheet("color: #666; font-size: 11px;")

        layout.addWidget(self.label)
        layout.addWidget(self.click_label)
        layout.addWidget(self.ext_label)
        layout.setContentsMargins(12, 12, 12, 12)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._browse_files()

    def _browse_files(self):
        ext_filter = f"Files ({' '.join(f'*{ext}' for ext in self.exts)})"
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select File",
            "",
            ext_filter
        )
        if file_path and os.path.isfile(file_path):
            if os.path.splitext(file_path)[-1].lower() in self.exts:
                self.fileDropped.emit(file_path)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    if os.path.splitext(url.toLocalFile())[-1].lower() in self.exts:
                        self.setStyleSheet("""
                            QFrame {
                                border: 2px solid #4a90e2;
                                border-radius: 10px;
                                background-color: #222;
                            }
                        """)
                        event.acceptProposedAction()
                        return
        event.ignore()

    def dragLeaveEvent(self, event):
        self.setStyleSheet("""
            QFrame {
                border: 2px dashed #444;
                border-radius: 10px;
                background-color: #181818;
            }
            QFrame:hover {
                background-color: #222;
                border-color: #888;
            }
        """)
        super().dragLeaveEvent(event)

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            if url.isLocalFile():
                p = url.toLocalFile()
                if os.path.splitext(p)[-1].lower() in self.exts:
                    self.setStyleSheet("""
                        QFrame {
                            border: 2px dashed #444;
                            border-radius: 10px;
                            background-color: #181818;
                        }
                        QFrame:hover {
                            background-color: #222;
                            border-color: #888;
                        }
                    """)
                    self.fileDropped.emit(p)
                    break

# -------------------------
# Variable Assignment Panel
# -------------------------

class VarAssignPanel(QGroupBox):
    assignmentChanged = pyqtSignal(str, str)      # letter, label_text
    styleChanged = pyqtSignal(str, TextStyle)     # letter, style
    deleteRequested = pyqtSignal(str)             # NEW: letter

    def __init__(self):
        super().__init__("VarAssign")
        self.setMinimumHeight(280)
        self.letter_rows: Dict[str, Tuple[QLineEdit, QToolButton, QToolButton, QToolButton, QToolButton]] = {}
        self.outer = QVBoxLayout(self)
        self.outer.setContentsMargins(10, 8, 10, 8)
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setSpacing(8)
        self.outer.addWidget(self.container)
        self.note = QLabel("Set strings for each variable. Formatting applies per-variable.")
        self.note.setStyleSheet("color:#666; font-size:12px;")
        self.outer.addWidget(self.note)

    def clear_rows(self):
        for i in reversed(range(self.container_layout.count())):
            w = self.container_layout.itemAt(i).widget()
            if w:
                w.setParent(None)
        self.letter_rows.clear()

    def set_variables(self, masks: List[MaskRegion]):
        self.clear_rows()
        for m in masks:
            row = QWidget()
            hl = QHBoxLayout(row)
            hl.setContentsMargins(0, 0, 0, 0)
            hl.setSpacing(6)

            label = QLabel(f"{m.letter} =")
            label.setFixedWidth(22)
            label.setStyleSheet("font-weight:600;")

            edit = QLineEdit()
            edit.setPlaceholderText("Enter string (e.g., NAME)")
            edit.setText(m.label_text)

            # Formatting buttons
            btn_b = QToolButton()
            btn_b.setText("B")
            btn_b.setCheckable(True)
            btn_b.setChecked(m.style.bold)
            btn_b.setToolTip("Bold")
            btn_b.setStyleSheet("font-weight:bold;")

            btn_i = QToolButton()
            btn_i.setText("I")
            btn_i.setCheckable(True)
            btn_i.setChecked(m.style.italic)
            btn_i.setToolTip("Italic")
            btn_i.setStyleSheet("font-style:italic;")

            btn_u = QToolButton()
            btn_u.setText("U")
            btn_u.setCheckable(True)
            btn_u.setChecked(m.style.underline)
            btn_u.setToolTip("Underline")
            btn_u.setStyleSheet("text-decoration: underline;")

            # Color picker button
            btn_color = QToolButton()
            btn_color.setText("◙")
            btn_color.setToolTip("Pick color")
            # set background to current color
            c = m.style.color
            btn_color.setStyleSheet(f"background: rgb({c.red()},{c.green()},{c.blue()}); color: white; font-weight:600;")
            def make_color_picker(letter, button):
                def _pick():
                    # Use the mask's current style color (m is captured from outer loop)
                    cur = m.style.color if hasattr(m.style, 'color') else QColor(20, 20, 20)
                    col = QColorDialog.getColor(cur, self, "Choose text color")
                    if col.isValid():
                        # update button background
                        button.setStyleSheet(f"background: rgb({col.red()},{col.green()},{col.blue()}); color: white; font-weight:600;")
                        st = TextStyle(bold=btn_b.isChecked(), italic=btn_i.isChecked(), underline=btn_u.isChecked(), color=col)
                        self.styleChanged.emit(letter, st)
                return _pick

            btn_color.clicked.connect(make_color_picker(m.letter, btn_color))

            # NEW delete button
            btn_del = QToolButton()
            btn_del.setText("✕")
            btn_del.setToolTip("Delete this variable")
            btn_del.setStyleSheet("color: red; font-weight: bold;")
            def make_delete(letter):
                def _do_delete():
                    self.deleteRequested.emit(letter)
                return _do_delete
            btn_del.clicked.connect(make_delete(m.letter))

            def make_edit_changed(letter):
                def _on_changed(text):
                    self.assignmentChanged.emit(letter, text)
                return _on_changed

            edit.textChanged.connect(make_edit_changed(m.letter))

            def make_style_toggled(letter):
                def _update_style():
                    st = TextStyle(
                        bold=btn_b.isChecked(),
                        italic=btn_i.isChecked(),
                        underline=btn_u.isChecked()
                    )
                    self.styleChanged.emit(letter, st)
                return _update_style

            updater = make_style_toggled(m.letter)
            btn_b.toggled.connect(lambda _: updater())
            btn_i.toggled.connect(lambda _: updater())
            btn_u.toggled.connect(lambda _: updater())

            hl.addWidget(label)
            hl.addWidget(edit, 1)
            hl.addWidget(btn_b)
            hl.addWidget(btn_i)
            hl.addWidget(btn_u)
            hl.addWidget(btn_color)
            hl.addWidget(btn_del)  # NEW
            self.container_layout.addWidget(row)

            self.letter_rows[m.letter] = (edit, btn_b, btn_i, btn_u, btn_color, btn_del)  # NEW

        if not masks:
            info = QLabel("No masks detected. Add manually on the Preview → Manual Masking.")
            info.setStyleSheet("color:#a33;")
            self.container_layout.addWidget(info)

# -------------------------
# Template Preview Canvas
# -------------------------

class TemplateCanvas(QWidget):
    maskAdded = pyqtSignal(QRect)  # in IMAGE coordinates
    requestRepaint = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setMinimumSize(400, 300)
        self.image: Optional[QImage] = None
        self.display_pixmap: Optional[QPixmap] = None
        self.masks: List[MaskRegion] = []
        self.assignments: Dict[str, str] = {}    # letter -> label text
        self.styles: Dict[str, TextStyle] = {}   # letter -> style
        self.manual_mode = False

        # For drawing rectangles in manual mode
        self.dragging = False
        self.drag_start: Optional[QPoint] = None
        self.drag_current: Optional[QPoint] = None

        # --- Interactive mask editing additions ---
        self.selected_mask_idx: Optional[int] = None  # index in self.masks
        self.edit_mode = None  # 'move', 'resize', 'rotate', None
        self.handle_type = None  # which handle is being dragged
        self.edit_start_pos: Optional[QPoint] = None
        self.edit_start_rect: Optional[QRect] = None
        self.edit_start_rotation: Optional[float] = None
        self.handle_radius = 4  # Reduced size of handles
        self.rotate_handle_offset = 20  # Adjusted offset for rotation handle
        self._last_cursor_pos: Optional[QPoint] = None

    def set_image(self, img: Optional[QImage]):
        self.image = img
        self._update_display_pixmap()
        self.update()

    def set_masks(self, masks: List[MaskRegion]):
        self.masks = masks
        self.update()

    def set_assignments(self, assignments: Dict[str, str]):
        self.assignments = assignments
        self.update()

    def set_styles(self, styles: Dict[str, TextStyle]):
        self.styles = styles
        self.update()

    def set_manual_mode(self, enabled: bool):
        self.manual_mode = enabled
        self.update()

    def _update_display_pixmap(self):
        if self.image is None:
            self.display_pixmap = None
            return
        # Fit to widget with aspect ratio
        avail = self.size()
        iw, ih = self.image.width(), self.image.height()
        if iw <= 0 or ih <= 0 or avail.width() <= 0 or avail.height() <= 0:
            self.display_pixmap = QPixmap.fromImage(self.image)
            return
        scale = min(avail.width() / iw, avail.height() / ih)
        new_w = int(iw * scale)
        new_h = int(ih * scale)
        scaled = self.image.scaled(new_w, new_h, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.display_pixmap = QPixmap.fromImage(scaled)

    def resizeEvent(self, event):
        self._update_display_pixmap()
        super().resizeEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(245, 245, 245))
        if self.display_pixmap is None:
            # No image yet
            painter.setPen(QPen(QColor(160, 160, 160), 1, Qt.PenStyle.DashLine))
            painter.drawRect(self.rect().adjusted(5, 5, -5, -5))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Drop a certificate template on the left")
            return

        # Draw scaled image centered
        canvas_rect = self._canvas_rect()
        painter.drawPixmap(canvas_rect.topLeft(), self.display_pixmap)

        # Scaling factors: image -> display
        iw, ih = self.image.width(), self.image.height()
        disp_w, disp_h = self.display_pixmap.width(), self.display_pixmap.height()
        sx = disp_w / iw
        sy = disp_h / ih

        # Draw masks (rectangles + letters)
        pen = QPen(QColor(220, 50, 50), 2, Qt.PenStyle.SolidLine)
        painter.setPen(pen)
        for idx, m in enumerate(self.masks):
            x, y, w, h = qrect_to_tuple(m.rect)
            rx = int(canvas_rect.x() + x * sx)
            ry = int(canvas_rect.y() + y * sy)
            rw = int(w * sx)
            rh = int(h * sy)

            # --- Rotation support ---
            painter.save()
            cx = rx + rw // 2
            cy = ry + rh // 2
            painter.translate(cx, cy)
            painter.rotate(m.rotation)
            painter.translate(-cx, -cy)

            painter.drawRect(QRect(rx, ry, rw, rh))

            # Letter tag at top-left
            font = QFont()
            font.setBold(True)
            painter.setFont(font)
            tag_color = self.styles.get(m.letter, TextStyle()).color if m.letter in self.styles else QColor(220, 50, 50)
            painter.setPen(tag_color)
            painter.drawText(QRect(rx + 4, ry + 2, 40, 22), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, m.letter)

            # Draw assignment text live
            text = self.assignments.get(m.letter, "")
            if text:
                f = QFont()
                st = self.styles.get(m.letter, TextStyle())
                f.setBold(st.bold)
                f.setItalic(st.italic)
                f.setUnderline(st.underline)
                px = max(10, min(48, int(h * sy * 0.5)))
                f.setPointSize(px)
                painter.setFont(f)
                st = self.styles.get(m.letter, TextStyle())
                painter.setPen(st.color)
                painter.drawText(QRect(rx + 6, ry + 4, rw - 12, rh - 8),
                                 Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                                 text)

            # --- Interactive controls overlay (draw for all masks; highlight selected) ---
            # Draw handles: 4 corners, 4 edges, rotate button, drag handle
            if self.selected_mask_idx == idx:
                handle_color = QColor(50, 120, 230)
                handle_fill = QColor(220, 240, 255)
            else:
                handle_color = QColor(160, 160, 160)
                handle_fill = QColor(250, 250, 250)
            painter.setPen(QPen(handle_color, 2))
            painter.setBrush(handle_fill)
            # Get 8 handle positions (corners + edges)
            pts = [
                (rx, ry),
                (rx + rw // 2, ry),
                (rx + rw, ry),
                (rx + rw, ry + rh // 2),
                (rx + rw, ry + rh),
                (rx + rw // 2, ry + rh),
                (rx, ry + rh),
                (rx, ry + rh // 2)
            ]
            for i, (px, py) in enumerate(pts):
                painter.drawEllipse(QPoint(px, py), self.handle_radius, self.handle_radius)
            # Rotate handle (above top center)
            rot_px = rx + rw // 2
            rot_py = ry - self.rotate_handle_offset
            painter.setBrush(handle_fill.darker(110))
            painter.drawEllipse(QPoint(rot_px, rot_py), self.handle_radius + 2, self.handle_radius + 2)
            painter.drawText(QRect(rot_px - 10, rot_py - 10, 20, 20), Qt.AlignmentFlag.AlignCenter, "⟳")
            # Drag handle (center)
            painter.setBrush(handle_fill)
            painter.drawEllipse(QPoint(rx + rw // 2, ry + rh // 2), self.handle_radius + 1, self.handle_radius + 1)

            painter.restore()

        # Draw manual selection rectangle while dragging
        if self.manual_mode and self.dragging and self.drag_start and self.drag_current:
            painter.setPen(QPen(QColor(50, 120, 230), 2, Qt.PenStyle.DashLine))
            painter.drawRect(QRect(self.drag_start, self.drag_current))

    # --- Helper: hit test for handles and mask selection ---
    def _mask_hit_test(self, pos: QPoint) -> Optional[int]:
        # Returns index of mask under pos (in display coords)
        if self.image is None or self.display_pixmap is None:
            return None
        canvas_rect = self._canvas_rect()
        iw, ih = self.image.width(), self.image.height()
        disp_w, disp_h = self.display_pixmap.width(), self.display_pixmap.height()
        sx = disp_w / iw
        sy = disp_h / ih
        for idx, m in enumerate(self.masks):
            x, y, w, h = qrect_to_tuple(m.rect)
            rx = int(canvas_rect.x() + x * sx)
            ry = int(canvas_rect.y() + y * sy)
            rw = int(w * sx)
            rh = int(h * sy)
            # Apply rotation for hit test (approximate by bounding box)
            box = QRect(rx, ry, rw, rh)
            if box.contains(pos):
                return idx
        return None

    def _handle_hit_test(self, pos: QPoint, mask_idx: int) -> Optional[str]:
        # Returns which handle is under pos, or None
        if self.image is None or self.display_pixmap is None or mask_idx is None:
            return None
        canvas_rect = self._canvas_rect()
        iw, ih = self.image.width(), self.image.height()
        disp_w, disp_h = self.display_pixmap.width(), self.display_pixmap.height()
        sx = disp_w / iw
        sy = disp_h / ih
        m = self.masks[mask_idx]
        x, y, w, h = qrect_to_tuple(m.rect)
        rx = int(canvas_rect.x() + x * sx)
        ry = int(canvas_rect.y() + y * sy)
        rw = int(w * sx)
        rh = int(h * sy)
        pts = [
            (rx, ry, 'nw'),
            (rx + rw // 2, ry, 'n'),
            (rx + rw, ry, 'ne'),
            (rx + rw, ry + rh // 2, 'e'),
            (rx + rw, ry + rh, 'se'),
            (rx + rw // 2, ry + rh, 's'),
            (rx, ry + rh, 'sw'),
            (rx, ry + rh // 2, 'w')
        ]
        for px, py, name in pts:
            if abs(px - pos.x()) <= self.handle_radius + 4 and abs(py - pos.y()) <= self.handle_radius + 4:
                return name
        # Rotate handle
        rot_px = rx + rw // 2
        rot_py = ry - self.rotate_handle_offset
        if abs(rot_px - pos.x()) <= self.handle_radius + 6 and abs(rot_py - pos.y()) <= self.handle_radius + 6:
            return 'rotate'
        # Drag handle (center)
        if abs((rx + rw // 2) - pos.x()) <= self.handle_radius + 4 and abs((ry + rh // 2) - pos.y()) <= self.handle_radius + 4:
            return 'move'
        return None

    # --- Mouse events for selection and editing ---
    def mousePressEvent(self, event):
        if self.manual_mode and self.image is not None:
            if event.button() == Qt.MouseButton.LeftButton:
                self.dragging = True
                self.drag_start = event.position().toPoint()
                self.drag_current = self.drag_start
                self.update()
            return

        pos = event.position().toPoint()
        mask_idx = self._mask_hit_test(pos)
        if mask_idx is not None:
            self.selected_mask_idx = mask_idx
            handle = self._handle_hit_test(pos, mask_idx)
            self.edit_mode = handle
            self.handle_type = handle
            self.edit_start_pos = pos
            self.edit_start_rect = QRect(self.masks[mask_idx].rect)
            self.edit_start_rotation = self.masks[mask_idx].rotation
            self._last_cursor_pos = pos
            self.update()
        else:
            self.selected_mask_idx = None
            self.edit_mode = None
            self.handle_type = None
            self.update()

    def mouseMoveEvent(self, event):
        if self.manual_mode:
            if self.dragging:
                self.drag_current = event.position().toPoint()
                self.update()
            return

        if self.selected_mask_idx is not None and self.edit_mode is not None:
            pos = event.position().toPoint()
            dx = pos.x() - self.edit_start_pos.x()
            dy = pos.y() - self.edit_start_pos.y()
            m = self.masks[self.selected_mask_idx]
            r = QRect(self.edit_start_rect)
            # --- Resize ---
            if self.edit_mode in ['nw', 'ne', 'sw', 'se', 'n', 's', 'e', 'w']:
                # Convert display delta to image delta
                iw, ih = self.image.width(), self.image.height()
                disp_w, disp_h = self.display_pixmap.width(), self.display_pixmap.height()
                sx = iw / disp_w
                sy = ih / disp_h
                ddx = int(dx * sx)
                ddy = int(dy * sy)
                if self.edit_mode == 'nw':
                    r.setTopLeft(r.topLeft() + QPoint(ddx, ddy))
                elif self.edit_mode == 'ne':
                    r.setTopRight(r.topRight() + QPoint(ddx, ddy))
                elif self.edit_mode == 'sw':
                    r.setBottomLeft(r.bottomLeft() + QPoint(ddx, ddy))
                elif self.edit_mode == 'se':
                    r.setBottomRight(r.bottomRight() + QPoint(ddx, ddy))
                elif self.edit_mode == 'n':
                    r.setTop(r.top() + ddy)
                elif self.edit_mode == 's':
                    r.setBottom(r.bottom() + ddy)
                elif self.edit_mode == 'e':
                    r.setRight(r.right() + ddx)
                elif self.edit_mode == 'w':
                    r.setLeft(r.left() + ddx)
                # Minimum size
                if r.width() < 20: r.setWidth(20)
                if r.height() < 12: r.setHeight(12)
                m.rect = r.normalized()
                self.update()
            # --- Move ---
            elif self.edit_mode == 'move':
                iw, ih = self.image.width(), self.image.height()
                disp_w, disp_h = self.display_pixmap.width(), self.display_pixmap.height()
                sx = iw / disp_w
                sy = ih / disp_h
                ddx = int(dx * sx)
                ddy = int(dy * sy)
                m.rect = QRect(r.x() + ddx, r.y() + ddy, r.width(), r.height())
                self.update()
            # --- Rotate ---
            elif self.edit_mode == 'rotate':
                # Calculate angle from center to mouse
                x, y, w, h = qrect_to_tuple(r)
                cx = x + w // 2
                cy = y + h // 2
                canvas_rect = self._canvas_rect()
                disp_w, disp_h = self.display_pixmap.width(), self.display_pixmap.height()
                sx = disp_w / self.image.width()
                sy = disp_h / self.image.height()
                center_disp = QPoint(int(canvas_rect.x() + cx * sx), int(canvas_rect.y() + cy * sy))
                start_angle = self.edit_start_rotation
                angle1 = np.arctan2(self.edit_start_pos.y() - center_disp.y(), self.edit_start_pos.x() - center_disp.x())
                angle2 = np.arctan2(event.position().toPoint().y() - center_disp.y(), event.position().toPoint().x() - center_disp.x())
                delta_deg = np.degrees(angle2 - angle1)
                m.rotation = (start_angle + delta_deg) % 360
                self.update()
        self._last_cursor_pos = event.position().toPoint()

    def mouseReleaseEvent(self, event):
        if self.manual_mode:
            if self.dragging:
                end_pt = event.position().toPoint()
                self.dragging = False
                if self.drag_start and end_pt:
                    r = QRect(self.drag_start, end_pt).normalized()
                    p1 = self._to_image_coords(r.topLeft())
                    p2 = self._to_image_coords(r.bottomRight())
                    if p1 and p2:
                        ir = QRect(p1, p2).normalized()
                        if ir.width() >= 20 and ir.height() >= 12:
                            self.maskAdded.emit(ir)
                            # Select the newly added mask after manual masking
                            if hasattr(self, 'masks') and self.masks:
                                self.selected_mask_idx = len(self.masks) - 1
                                self.update()
                self.drag_start = None
                self.drag_current = None
                self.update()
            return

        # End interactive edit
        self.edit_mode = None
        self.handle_type = None
        self.edit_start_pos = None
        self.edit_start_rect = None
        self.edit_start_rotation = None
        self.update()

    def _canvas_rect(self) -> QRect:
        # Center the pixmap
        if self.display_pixmap is None:
            return QRect(0, 0, 0, 0)
        pw, ph = self.display_pixmap.width(), self.display_pixmap.height()
        x = (self.width() - pw) // 2
        y = (self.height() - ph) // 2
        return QRect(x, y, pw, ph)

    def _to_image_coords(self, p: QPoint) -> Optional[QPoint]:
        if self.image is None or self.display_pixmap is None:
            return None
        canvas = self._canvas_rect()
        if not canvas.contains(p):
            return None
        iw, ih = self.image.width(), self.image.height()
        disp_w, disp_h = self.display_pixmap.width(), self.display_pixmap.height()
        sx = iw / disp_w
        sy = ih / disp_h
        ix = int((p.x() - canvas.x()) * sx)
        iy = int((p.y() - canvas.y()) * sy)
        return QPoint(ix, iy)

    # Note: mouse event handlers for both manual masking and interactive editing
    # are implemented earlier in this class. The older duplicate handlers
    # were removed so they don't override the interactive behavior.

# -------------------------
# Generated certificates list (unchanged)
# -------------------------

class GeneratedItem(QWidget):
    downloadClicked = pyqtSignal(int)  # index in list

    def __init__(self, index: int, pixmap: QPixmap):
        super().__init__()
        self.index = index
        lay = QHBoxLayout(self)
        lay.setContentsMargins(8, 8, 8, 8)
        img_label = QLabel()
        # Scale preview to a reasonable width, keep aspect ratio
        target_w = 480
        scaled = pixmap.scaledToWidth(target_w, Qt.TransformationMode.SmoothTransformation)
        img_label.setPixmap(scaled)
        btn = QPushButton("Download JPG")
        btn.clicked.connect(self._dl)
        lay.addWidget(img_label, 1)
        lay.addWidget(btn)

    def _dl(self):
        self.downloadClicked.emit(self.index)

class GeneratedList(QWidget):
    downloadOne = pyqtSignal(int)
    downloadAll = pyqtSignal()

    def __init__(self):
        super().__init__()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        controls = QHBoxLayout()
        title = QLabel("Generated Certificates")
        title.setStyleSheet("font-weight:600;")
        controls.addWidget(title)
        controls.addStretch(1)
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search by value...")
        self.search_box.setFixedWidth(200)
        self.search_box.returnPressed.connect(self._on_search)
        controls.addWidget(self.search_box)
        btn_all = QPushButton("Download All")
        btn_all.clicked.connect(lambda: self.downloadAll.emit())
        controls.addWidget(btn_all)
        outer.addLayout(controls)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.inner = QWidget()
        self.inner_layout = QVBoxLayout(self.inner)
        self.inner_layout.setContentsMargins(8, 8, 8, 8)
        self.scroll.setWidget(self.inner)
        outer.addWidget(self.scroll, 1)
        self._search_data = []

    def populate(self, pixmaps: List[QPixmap], search_data: list = None):
        # Clear
        for i in reversed(range(self.inner_layout.count())):
            w = self.inner_layout.itemAt(i).widget()
            if w:
                w.setParent(None)
        # Add items
        for idx, pm in enumerate(pixmaps):
            item = GeneratedItem(idx, pm)
            item.downloadClicked.connect(self.downloadOne.emit)
            self.inner_layout.addWidget(item)
        self.inner_layout.addStretch(1)
        self._search_data = search_data if search_data else []

    def _on_search(self):
        value = self.search_box.text().strip().lower()
        if not value or not self._search_data:
            return
        for idx, row in enumerate(self._search_data):
            if any(value in str(cell).lower() for cell in row):
                # Scroll to the matching certificate
                item_widget = self.inner_layout.itemAt(idx).widget()
                if item_widget:
                    self.scroll.ensureWidgetVisible(item_widget)
                break

# -------------------------
# Main Window
# -------------------------

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Certificate Mass Production Tool")
        self.showMaximized()

        # State
        self.template_path: Optional[str] = None
        self.template_img: Optional[QImage] = None
        self.masks: List[MaskRegion] = []
        self.assignments: Dict[str, str] = {}  # letter -> label string
        self.styles: Dict[str, TextStyle] = {}
        self.generated_images: List[QImage] = []  # original-size images
        self.generated_pixmaps: List[QPixmap] = []

        self._letters_iter = iter(string.ascii_lowercase)

        # Layout: Split left (30%) and right (70%)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(8, 8, 8, 8)
        left_layout.setSpacing(8)

        # Container 1: TempDrop
        gb1 = QGroupBox("TempDrop")
        gb1_layout = QVBoxLayout(gb1)
        self.drop_template = DropArea("Drop Certificate Template", [".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"])
        self.drop_template.fileDropped.connect(self.on_template_dropped)
        gb1_layout.addWidget(self.drop_template)

        # Container 2: VarAssign
        self.var_panel = VarAssignPanel()
        self.var_panel.assignmentChanged.connect(self.on_assignment_changed)
        self.var_panel.styleChanged.connect(self.on_style_changed)
        self.var_panel.deleteRequested.connect(self.on_delete_variable)  # NEW LINE

        # Container 3: XLDrop
        gb3 = QGroupBox("XLDrop")
        gb3_layout = QVBoxLayout(gb3)
        self.drop_excel = DropArea("Drop XL Sheet", [".xls", ".xlsx"])
        self.drop_excel.fileDropped.connect(self.on_excel_dropped)
        gb3_layout.addWidget(self.drop_excel)

        left_layout.addWidget(gb1)
        left_layout.addWidget(self.var_panel, 1)
        left_layout.addWidget(gb3)

        splitter.addWidget(left_panel)

        # Right: Preview
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(8, 8, 8, 8)
        right_layout.setSpacing(8)

        # Manual masking toggle (as required)
        controls = QHBoxLayout()
        self.btn_manual = QPushButton("Manual Masking")
        self.btn_manual.setCheckable(True)
        self.btn_manual.setEnabled(False)
        self.btn_manual.toggled.connect(self.on_manual_toggled)
        controls.addWidget(self.btn_manual)
        controls.addStretch(1)
        right_layout.addLayout(controls)

        # Stacked-ish views: we'll swap between template preview and generated list
        self.template_canvas = TemplateCanvas()
        self.template_canvas.maskAdded.connect(self.on_mask_added)
        right_layout.addWidget(self.template_canvas, 1)

        self.generated_list = GeneratedList()
        self.generated_list.setVisible(False)
        self.generated_list.downloadOne.connect(self.on_download_one)
        self.generated_list.downloadAll.connect(self.on_download_all)
        right_layout.addWidget(self.generated_list, 1)

        splitter.addWidget(right_panel)

        # Set initial sizes to favor the preview (like your image2): ~5% / 95%
        self.setCentralWidget(splitter)
        # Force left panel to a fixed small width for consistent wide preview
        splitter.setSizes([120, 2000])
        # If you want to keep stretch factors, uncomment below:
        # splitter.setStretchFactor(0, 1)
        # splitter.setStretchFactor(1, 4)


    # ----------------- Template handling -----------------
    def on_template_dropped(self, path: str):
        img = load_qimage(path)
        if img is None:
            QMessageBox.critical(self, "Error", "Failed to load image.")
            return
        self.reset_generated_outputs()
        self.template_path = path
        self.template_img = img
        self.template_canvas.set_image(self.template_img)
        self.btn_manual.setEnabled(True)

        # Auto-detect empty spaces / gaps
        rects = detect_blank_regions_cv(path)
        self.masks = []
        self._letters_iter = iter(string.ascii_lowercase)
        for r in rects:
            letter = next(self._letters_iter, None)
            if letter is None:
                break
            self.masks.append(MaskRegion(letter=letter, rect=r))

        self.assignments = {m.letter: m.label_text for m in self.masks}
        self.styles = {m.letter: m.style for m in self.masks}

        self.var_panel.set_variables(self.masks)
        self.template_canvas.set_masks(self.masks)
        self.template_canvas.set_assignments(self.assignments)
        self.template_canvas.set_styles(self.styles)
        self.show_template_preview()

    def on_mask_added(self, rect_in_image: QRect):
        # Add a new variable letter
        letter = next(self._letters_iter, None)
        if letter is None:
            QMessageBox.warning(self, "Limit", "Maximum variable letters (a-z) reached.")
            return
        m = MaskRegion(letter=letter, rect=rect_in_image)
        self.masks.append(m)
        self.assignments[m.letter] = ""
        self.styles[m.letter] = TextStyle()
        self.var_panel.set_variables(self.masks)
        self.template_canvas.set_masks(self.masks)
        self.template_canvas.set_assignments(self.assignments)
        self.template_canvas.set_styles(self.styles)
        # Select the newly added mask
        self.template_canvas.selected_mask_idx = len(self.masks) - 1
        # Exit manual masking so handles/buttons work immediately
        if self.btn_manual.isChecked():
            self.btn_manual.setChecked(False)  # triggers on_manual_toggled(False)
        else:
            # Ensure canvas is not in manual mode even if button was already off
            self.template_canvas.set_manual_mode(False)
        self.template_canvas.update()  # Ensure the canvas updates with new handles and buttons

    def on_manual_toggled(self, checked: bool):
        self.template_canvas.set_manual_mode(checked)

    def on_assignment_changed(self, letter: str, text: str):
        for m in self.masks:
            if m.letter == letter:
                m.label_text = text
                break
        self.assignments[letter] = text
        self.template_canvas.set_assignments(self.assignments)

    def on_style_changed(self, letter: str, style: TextStyle):
        for m in self.masks:
            if m.letter == letter:
                m.style = style
                break
        self.styles[letter] = style
        self.template_canvas.set_styles(self.styles)

    def on_delete_variable(self, letter: str):   # NEW METHOD
        # Remove from masks, assignments, and styles
        self.masks = [m for m in self.masks if m.letter != letter]
        if letter in self.assignments:
            del self.assignments[letter]
        if letter in self.styles:
            del self.styles[letter]

        # Refresh UI
        self.var_panel.set_variables(self.masks)
        self.template_canvas.set_masks(self.masks)
        self.template_canvas.set_assignments(self.assignments)
        self.template_canvas.set_styles(self.styles)
        # Clear selection or select last mask if any remain
        if self.masks:
            self.template_canvas.selected_mask_idx = len(self.masks) - 1
        else:
            self.template_canvas.selected_mask_idx = None
        self.template_canvas.update()  # Ensure the canvas updates after deletion

    # ----------------- Excel handling -----------------
    def on_excel_dropped(self, path: str):
        if not self.template_img or not self.masks:
            QMessageBox.warning(self, "Info", "Please drop a certificate template and set masks first.")
            return
        try:
            df = self._read_excel(path)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to read Excel: {e}")
            return

        # Validation 1: number of columns equals number of masked variables
        masked_vars_count = len(self.masks)
        if df.shape[1] != masked_vars_count:
            QMessageBox.critical(self, "Error", "Column and mask variable number mismatch error")
            return

        # Validation 2: column names equal the variable assigned strings
        assigned_strings = [m.label_text for m in self.masks]
        if any(s.strip() == "" for s in assigned_strings):
            # If user didn't type labels, this will never match Excel headers
            QMessageBox.critical(self, "Error", "Mask variable corresponding string and column name error")
            return
        excel_cols = list(df.columns.astype(str))
        if excel_cols != assigned_strings:
            QMessageBox.critical(self, "Error", "Mask variable corresponding string and column name error")
            return

        # Passed validation: Create (row_count - 1) certificate copies (i.e., one per data row)
        try:
            self.generate_certificates(df)
            self.show_generated_list()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate certificates: {e}")

    def _read_excel(self, path: str) -> pd.DataFrame:
        ext = os.path.splitext(path)[-1].lower()
        if ext == ".xlsx":
            return pd.read_excel(path, engine="openpyxl")
        elif ext == ".xls":
            return pd.read_excel(path, engine="xlrd")
        else:
            raise ValueError("Unsupported Excel format")

    # ----------------- Generation & Export -----------------

    def _draw_text_on_image(self, base: QImage, values_by_letter: Dict[str, str]) -> QImage:
        """
        Draws per-mask text with per-variable styles on a copy of the original-size image.
        Ensures text auto-scales to fit inside the mask (both width and height).
        """
        out = QImage(base)  # copy
        painter = QPainter(out)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)

        for m in self.masks:
            text = values_by_letter.get(m.letter, "")
            if not text:
                continue
            r = m.rect

            # If name has 3 or more words, use only the first two (e.g., "Ambati Venkata Prasad" -> "Ambati Venkata")
            # This keeps long multi-part names from overflowing small masked regions.
            words = text.strip().split()
            if len(words) >= 3:
                text = " ".join(words[:2]).strip()  # ensure clean trimming
                
            # Start with a conservative initial font size based on region size
            f = QFont()
            f.setBold(m.style.bold)
            f.setItalic(m.style.italic)
            f.setUnderline(m.style.underline)
            # Start with a size that's likely to fit but might need reduction
            initial_size = min(int(r.height() * 0.7), int(r.width() / (len(text) * 0.7)))

            # --- Auto font scaling (robust) ---
            # Use horizontalAdvance for width and QFontMetrics.height() for height checks.
            # Determine padding dynamically so small boxes get smaller padding.
            padding = max(8, int(min(r.width(), r.height()) * 0.06))
            avail_w = max(4, r.width() - (padding * 2))
            avail_h = max(4, r.height() - (padding * 2))

            test_font = QFont(f)
            max_size = int(avail_h)  # don't exceed available height
            min_size = 8
            fitted_size = min_size

            # Find the largest point size that fits both width and height
            for size in range(max_size, min_size - 1, -1):
                test_font.setPointSize(size)
                fm = QFontMetrics(test_font)
                text_w = fm.horizontalAdvance(text)
                text_h = fm.height()
                if text_w <= avail_w and text_h <= avail_h:
                    fitted_size = size
                    break

            f.setPointSize(fitted_size)

            # Extra shrink loop in case font metrics behave differently when applied by the painter
            fm_check = QFontMetrics(f)
            text_w = fm_check.horizontalAdvance(text)
            text_h = fm_check.height()
            while (text_w > avail_w or text_h > avail_h) and f.pointSize() > min_size:
                new_size = max(min_size, int(f.pointSize() * 0.9))
                if new_size == f.pointSize():
                    new_size = f.pointSize() - 1
                f.setPointSize(new_size)
                fm_check = QFontMetrics(f)
                text_w = fm_check.horizontalAdvance(text)
                text_h = fm_check.height()

            # Final fallback: if text still doesn't fit horizontally, elide with an ellipsis
            if text_w > avail_w:
                try:
                    elided = fm_check.elidedText(text, Qt.TextElideMode.ElideRight, avail_w)
                    text = elided
                    # update measurements
                    fm_check = QFontMetrics(f)
                    text_w = fm_check.horizontalAdvance(text)
                    text_h = fm_check.height()
                except Exception:
                    # crude truncation as last resort
                    if text_w > 0:
                        approx_chars = max(1, int(len(text) * (avail_w / text_w)))
                        text = text[:approx_chars]
                        fm_check = QFontMetrics(f)
                        text_w = fm_check.horizontalAdvance(text)
                        text_h = fm_check.height()

            painter.setFont(f)
            # Use variable style color if provided
            pen_color = m.style.color if hasattr(m.style, 'color') else QColor(10, 10, 10)
            painter.setPen(pen_color)

            # Draw text centered in the rectangle with proper padding
            painter.drawText(r.adjusted(padding, padding, -padding, -padding),
                             Qt.AlignmentFlag.AlignCenter,
                             text)

        painter.end()  # End painter after all text has been drawn
        return out

    def generate_certificates(self, df: pd.DataFrame):
        # Map label_text (column names) -> letter
        label_to_letter = {m.label_text: m.letter for m in self.masks}
        self.generated_images.clear()
        self.generated_pixmaps.clear()
        self.excel_data_rows = df.values.tolist()  # Save for search
        for idx, row in df.iterrows():
            values_by_letter = {}
            for col_name, value in row.items():
                letter = label_to_letter.get(str(col_name))
                if letter:
                    values_by_letter[letter] = "" if pd.isna(value) else str(value)
            final = self._draw_text_on_image(self.template_img, values_by_letter)
            self.generated_images.append(final)
            self.generated_pixmaps.append(QPixmap.fromImage(final))

    def on_download_one(self, index: int):
        if index < 0 or index >= len(self.generated_images):
            return
        default_name = f"certificate_{index+1:03d}.jpg"
        path, _ = QFileDialog.getSaveFileName(self, "Save Certificate", default_name, "JPEG Image (*.jpg)")
        if path:
            self._save_qimage_jpg(self.generated_images[index], path)

    def on_download_all(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Folder to Save All")
        if not directory:
            return
        for i, img in enumerate(self.generated_images, start=1):
            fname = os.path.join(directory, f"certificate_{i:03d}.jpg")
            self._save_qimage_jpg(img, fname)
        QMessageBox.information(self, "Done", "All certificates saved.")

    def _save_qimage_jpg(self, img: QImage, path: str):
        # Maintain original size; QImage.save with JPEG keeps dimensions
        if not img.save(path, "JPG", quality=95):
            QMessageBox.critical(self, "Error", f"Failed to save: {path}")

    def reset_generated_outputs(self):
        self.generated_images.clear()
        self.generated_pixmaps.clear()
        self.generated_list.setVisible(False)
        self.template_canvas.setVisible(True)

    def reset_all(self):
        self.template_path = None
        self.template_img = None
        self.masks.clear()
        self.assignments.clear()
        self.styles.clear()
        self.reset_generated_outputs()
        self.var_panel.clear_rows()
        self.template_canvas.set_image(None)
        self.btn_manual.setEnabled(False)
        self._letters_iter = iter(string.ascii_lowercase)

    def show_generated_list(self):
        # Switch the right panel to show generated results
        self.template_canvas.setVisible(False)
        self.generated_list.setVisible(True)
        # Pass Excel data rows for search
        if hasattr(self, 'excel_data_rows'):
            self.generated_list.populate(self.generated_pixmaps, self.excel_data_rows)
        else:
            self.generated_list.populate(self.generated_pixmaps)

    def show_template_preview(self):
        self.generated_list.setVisible(False)
        self.template_canvas.setVisible(True)


# -------------------------
# App entry
# -------------------------

def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.showFullScreen()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()