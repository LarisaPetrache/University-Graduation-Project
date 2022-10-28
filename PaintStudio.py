import colorsys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPixmap, QColor, QIcon, QIntValidator
from PyQt5.QtWidgets import QToolButton, QGraphicsView, QFrame, QLineEdit, QPushButton, QLabel, QWidget, QVBoxLayout, \
    QSlider, QGridLayout, QApplication
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from qtpy import uic
import sys

"""================================
> MainWindow Class
    1. ColorPicker Functions
    2. Tools Functions
    3. Toolbar Functions
    4. Layer Functions
    5. Menu - New Canvas Functions
    6. Menu - Open Functions
    7. Menu - Save Function
    8. Menu - Close Function
    9. Menu - Quit Function
    10. Menu - Undo, Redo Functions
    11. Menu - Copy, Paste, 
            Select All Functions
    12. Menu - Disable/Enable
            Action Buttons
    13. Navigator Functions
    14. Event filter - Painting and
            View Navigation Functions
    
> Layer Class
> LayerNameWindow Class
> NewCanvasWindow Class
> CloseWindow Class
> Main()
================================"""

SELECTED_LAYER = None
LAYERS = []
UNDO = []
REDO = []


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        uic.loadUi('./ui_files/MainWindow_UI.ui', self)
        self.setWindowTitle("Paint Studio")
        self.setWindowIcon(QIcon("icons/app_icon.ico"))

        # ---- Default variables ----
        self.canvas_name = "NewCanvas"
        self.canvas_width = 0
        self.canvas_height = 0
        self.save_path = ""
        self.selected_image = None  # Copy of selected image from "Open" Menu
        self.saved_state = False

        self.layer_count = 0
        self.layer_number = 0
        self.max_layers = 50

        self.layout = self.findChild(QVBoxLayout, "verticalLayout_9")  # QScrollArea layout to add layers
        self.layout.setAlignment(Qt.AlignTop)

        self.zoomOut = 0.9
        self.zoomIn = 1.1

        self.BRUSH_SIZE = 1
        self.SHAPE_SIZE = 1
        self.DENSITY_VALUE = 100
        self.CANVAS = False

        self.start_point = QPoint()
        self.end_point = QPoint()

        # ---- Stacked Widgets ----
        self.stackedWidget_settings = self.findChild(QtWidgets.QStackedWidget, "stackedWidget")
        self.stackedWidget_size = self.findChild(QtWidgets.QStackedWidget, "stackedWidget_2")

        # Disable stacked widgets at start
        self.stackedWidget_settings.setDisabled(True)
        self.stackedWidget_size.setDisabled(True)

        # ---- Brush Slider ----
        self.brushSize_slider = self.findChild(QSlider, "brushSize_slider")
        self.brushSize_value = self.findChild(QLineEdit, "brushSize_value")
        self.brushSize_value.setValidator(QIntValidator())

        self.brushSize_slider.valueChanged.connect(self.setBrushSize_Slider)
        self.brushSize_value.textChanged.connect(self.setBrushSize_Text)

        self.label_density = self.findChild(QLabel, "label_density")
        self.density_slider = self.findChild(QSlider, "density_slider")
        self.density_value = self.findChild(QLineEdit, "density_value")
        self.density_value.setValidator(QIntValidator())

        self.hide_densitySettings()

        self.density_slider.valueChanged.connect(self.setDensity_Slider)
        self.density_value.textChanged.connect(self.setDensity_Text)

        # Brush Size Buttons and Layout
        self.brushSize_layout = self.findChild(QGridLayout, "gridLayout_8")
        self.shapeSize_layout = self.findChild(QGridLayout, "gridLayout_9")

        self.bsize_active = False
        self.size_button = None
        self.s_size_active = False
        self.size_button2 = None

        # Connect brush size buttons to function
        for i in range(self.brushSize_layout.count()):
            self.brushSize_layout.itemAt(i).widget().released.connect(self.bsize_state)

        for i in range(self.shapeSize_layout.count()):
            self.shapeSize_layout.itemAt(i).widget().released.connect(self.s_size_state)

        # ---- Shape Slider ----
        self.shapeSize_slider = self.findChild(QSlider, "shapeSize_slider")
        self.shapeSize_value = self.findChild(QLineEdit, "shapeSize_value")
        self.shapeFill_comboBox = self.findChild(QtWidgets.QComboBox, "shapeFill_comboBox")

        self.shapeSize_slider.valueChanged.connect(self.setShapeSize_Slider)
        self.shapeSize_value.textChanged.connect(self.setShapeSize_Text)

        # ---- Text Settings ----
        self.bold = False
        self.italic = False
        self.underline = False
        self.text = ""
        self.text_pos = None

        self.fontName_comboBox = self.findChild(QtWidgets.QComboBox, "fontName_comboBox")
        self.text_boldBtn = self.findChild(QToolButton, "text_boldBtn")
        self.text_italicBtn = self.findChild(QToolButton, "text_italicBtn")
        self.text_underlineBtn = self.findChild(QToolButton, "text_underlineBtn")
        self.fontSize_comboBox = self.findChild(QtWidgets.QComboBox, "fontSize_comboBox")
        self.textValue = self.findChild(QLineEdit, "textValue")

        self.text_boldBtn.clicked.connect(self.textBold_state)
        self.text_italicBtn.clicked.connect(self.textItalic_state)
        self.text_underlineBtn.clicked.connect(self.textUnderline_state)
        self.textValue.textChanged.connect(self.setTextValue)

        # ---- ColorPicker ----

        self.color = (0, 0, 0)
        self.firstColor = QColor(0, 0, 0)
        self.secondColor = QColor(255, 255, 255)

        # Color
        self.firstColor_label = self.findChild(QLabel, "firstColor")
        self.secondColor_label = self.findChild(QLabel, "secondColor")
        self.switchColor = self.findChild(QToolButton, "switchColor")
        self.colorView = self.findChild(QFrame, "colorView")

        self.redValue = self.findChild(QLineEdit, "redValue")
        self.redValue.setValidator(QRegExpValidator(QRegExp("[0-9]{3}")))

        self.greenValue = self.findChild(QLineEdit, "greenValue")
        self.greenValue.setValidator(QRegExpValidator(QRegExp("[0-9]{3}")))

        self.blueValue = self.findChild(QLineEdit, "blueValue")
        self.blueValue.setValidator(QRegExpValidator(QRegExp("[0-9]{3}")))

        self.hexValue = self.findChild(QLineEdit, "hexValue")
        self.hexValue.setValidator(QRegExpValidator(QRegExp("^[a-fA-F0-9]{6}$")))

        self.hue = self.findChild(QFrame, "hue")
        self.blackOverlay = self.findChild(QFrame, "blackOverlay")
        self.hueSelector = self.findChild(QLabel, "hueSelector")
        self.svSelector = self.findChild(QFrame, "svSelector")

        # Connect Mouse Events
        self.hue.mouseMoveEvent = self.move_hueSelector
        self.blackOverlay.mouseMoveEvent = self.move_svSelector
        self.blackOverlay.mousePressEvent = self.move_svSelector

        # Connect functions
        self.redValue.textEdited.connect(self.RGB_changed)
        self.greenValue.textEdited.connect(self.RGB_changed)
        self.blueValue.textEdited.connect(self.RGB_changed)
        self.hexValue.textEdited.connect(self.HEX_changed)
        self.switchColor.clicked.connect(self.switchColors)

        # ---- Painting Tools ----
        self.tools_layout = self.findChild(QGridLayout, "gridLayout_4")

        self.penBtn = self.findChild(QToolButton, "penBtn")
        self.penBtn.clicked.connect(self.penBtn_state)
        self.pen_active = False

        self.brushBtn = self.findChild(QToolButton, "brushBtn")
        self.brushBtn.clicked.connect(self.brushBtn_state)
        self.brush_active = False

        self.eraserBtn = self.findChild(QToolButton, "eraserBtn")
        self.eraserBtn.clicked.connect(self.eraserBtn_state)
        self.eraser_active = False

        self.bucketBtn = self.findChild(QToolButton, "bucketBtn")
        self.bucketBtn.clicked.connect(self.bucketBtn_state)
        self.bucket_active = False

        self.textBtn = self.findChild(QToolButton, "textBtn")
        self.textBtn.clicked.connect(self.textBtn_state)
        self.text_active = False

        self.pickerBtn = self.findChild(QToolButton, "pickerBtn")
        self.pickerBtn.clicked.connect(self.pickerBtn_state)
        self.picker_active = False

        self.lineBtn = self.findChild(QToolButton, "lineBtn")
        self.lineBtn.clicked.connect(self.lineBtn_state)
        self.line_active = False

        self.squareBtn = self.findChild(QToolButton, "squareBtn")
        self.squareBtn.clicked.connect(self.squareBtn_state)
        self.square_active = False

        self.ellipseBtn = self.findChild(QToolButton, "ellipseBtn")
        self.ellipseBtn.clicked.connect(self.ellipseBtn_state)
        self.ellipse_active = False

        # ---- Canvas View Settings ----
        self.canvasFrame = self.findChild(QFrame, "CanvasFrame")
        self.view = self.findChild(QGraphicsView, "canvasView")
        self.view.setRenderHints(QPainter.HighQualityAntialiasing | QPainter.SmoothPixmapTransform)
        self.view.setAlignment(QtCore.Qt.AlignCenter)
        self.view.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

        # Navigator View
        self.view2 = self.findChild(QGraphicsView, "canvasView2")
        self.view2.setRenderHint(QtGui.QPainter.HighQualityAntialiasing)
        self.view2.setAlignment(QtCore.Qt.AlignCenter)

        # ---- Scene Settings ----
        self.scene = QtWidgets.QGraphicsScene(self.view)
        self.view.setScene(self.scene)
        self.view2.setScene(self.scene)

        # ---- Layers Buttons ----
        self.lockLayerBtn = self.findChild(QToolButton, "lockLayerBtn")
        self.lockLayerBtn.clicked.connect(self.lockLayer)

        self.addLayerBtn = self.findChild(QToolButton, "addLayerBtn")
        self.addLayerBtn.clicked.connect(self.addLayer)

        self.deleteLayerBtn = self.findChild(QToolButton, "deleteLayerBtn")
        self.deleteLayerBtn.clicked.connect(self.deleteLayer)

        self.eraseLayerBtn = self.findChild(QToolButton, "eraseLayerBtn")
        self.eraseLayerBtn.clicked.connect(self.eraseLayer)

        self.moveLayerAboveBtn = self.findChild(QToolButton, "moveLayerAboveBtn")
        self.moveLayerAboveBtn.clicked.connect(self.moveLayerAbove)

        self.moveLayerBelowBtn = self.findChild(QToolButton, "moveLayerBelowBtn")
        self.moveLayerBelowBtn.clicked.connect(self.moveLayerBelow)

        # ---- Menu ----

        # File
        self.actionNew_Canvas = self.findChild(QtWidgets.QAction, "actionNew_Canvas")
        self.actionNew_Canvas.triggered.connect(self.newCanvas)

        self.actionOpen = self.findChild(QtWidgets.QAction, "actionOpen")
        self.actionOpen.triggered.connect(self.setImageOnCanvas)

        self.actionSave = self.findChild(QtWidgets.QAction, "actionSave")
        self.actionSave.triggered.connect(self.file_save)
        self.actionSave.setDisabled(True)

        self.actionSave_as = self.findChild(QtWidgets.QAction, "actionSave_as")
        self.actionSave_as.triggered.connect(self.file_saveAs)
        self.actionSave_as.setDisabled(True)

        self.actionClose = self.findChild(QtWidgets.QAction, "actionClose")
        self.actionClose.triggered.connect(self.open_closeCanvasWindow)
        self.actionClose.setDisabled(True)

        self.actionQuit = self.findChild(QtWidgets.QAction, "actionQuit")
        self.actionQuit.triggered.connect(self.quitApp)

        # Edit
        self.actionUndo = self.findChild(QtWidgets.QAction, "actionUndo")
        self.actionUndo.triggered.connect(self.undoActions)

        self.actionRedo = self.findChild(QtWidgets.QAction, "actionRedo")
        self.actionRedo.triggered.connect(self.redoActions)

        self.actionCopy = self.findChild(QtWidgets.QAction, "actionCopy")
        self.actionCopy.triggered.connect(self.copySelection)

        self.actionPaste = self.findChild(QtWidgets.QAction, "actionPaste")
        self.actionPaste.triggered.connect(self.pasteSelection)

        self.actionSelect_All = self.findChild(QtWidgets.QAction, "actionSelect_All")
        self.actionSelect_All.triggered.connect(self.select_all)

        # Selection
        self.actionDeselect = self.findChild(QtWidgets.QAction, "actionDeselect")
        self.actionDeselect.triggered.connect(self.deselectBtn_state)

        self.actionDelete_selectedArea = self.findChild(QtWidgets.QAction, "actionDelete_selectedArea")
        self.actionDelete_selectedArea.triggered.connect(self.delete_selectedArea)

        self.actionFill_Selected_Area = self.findChild(QtWidgets.QAction, "actionFill_Selected_Area")
        self.actionFill_Selected_Area.triggered.connect(self.fill_selectedArea)

        # Layer
        self.actionAdd_Layer = self.findChild(QtWidgets.QAction, "actionAdd_Layer")
        self.actionAdd_Layer.triggered.connect(self.addLayer)

        self.actionDelete_Layer = self.findChild(QtWidgets.QAction, "actionDelete_Layer")
        self.actionDelete_Layer.triggered.connect(self.deleteLayer)

        self.actionErase_Layer = self.findChild(QtWidgets.QAction, "actionErase_Layer")
        self.actionErase_Layer.triggered.connect(self.eraseLayer)

        # View
        self.actionZoom_In = self.findChild(QtWidgets.QAction, "actionZoom_In")
        self.actionZoom_In.triggered.connect(self.canvas_zoomIn)

        self.actionZoom_Out = self.findChild(QtWidgets.QAction, "actionZoom_Out")
        self.actionZoom_Out.triggered.connect(self.canvas_zoomOut)

        self.actionRotate_View_CW = self.findChild(QtWidgets.QAction, "actionRotate_View_CW")
        self.actionRotate_View_CW.triggered.connect(self.canvas_rotateRight)

        self.actionRotate_View_CCW = self.findChild(QtWidgets.QAction, "actionRotate_View_CCW")
        self.actionRotate_View_CCW.triggered.connect(self.canvas_rotateLeft)

        self.actionFlip_Horizontally = self.findChild(QtWidgets.QAction, "actionFlip_Horizontally")
        self.actionFlip_Horizontally.triggered.connect(self.canvas_flipHorizontally)

        self.actionFlip_Vertically = self.findChild(QtWidgets.QAction, "actionFlip_Vertically")
        self.actionFlip_Vertically.triggered.connect(self.canvas_flipVertically)

        self.actionFit_In_View = self.findChild(QtWidgets.QAction, "actionFit_In_View")
        self.actionFit_In_View.triggered.connect(self.canvas_fitInView)

        self.actionReset_View = self.findChild(QtWidgets.QAction, "actionReset_View")
        self.actionReset_View.triggered.connect(self.canvas_resetView)

        # ---- Navigator Buttons ----
        self.rotateLeftBtn = self.findChild(QToolButton, "rotateLeftBtn")
        self.rotateLeftBtn.clicked.connect(self.canvas_rotateLeft)

        self.rotateRightBtn = self.findChild(QToolButton, "rotateRightBtn")
        self.rotateRightBtn.clicked.connect(self.canvas_rotateRight)

        self.zoomInBtn = self.findChild(QToolButton, "zoomInBtn")
        self.zoomInBtn.clicked.connect(self.canvas_zoomIn)

        self.zoomOutBtn = self.findChild(QToolButton, "zoomOutBtn")
        self.zoomOutBtn.clicked.connect(self.canvas_zoomOut)

        self.flipVerticallyBtn = self.findChild(QToolButton, "flipVerticallyBtn")
        self.flipVerticallyBtn.clicked.connect(self.canvas_flipVertically)

        self.flipHorizontallyBtn = self.findChild(QToolButton, "flipHorizontallyBtn")
        self.flipHorizontallyBtn.clicked.connect(self.canvas_flipHorizontally)

        self.fitInViewBtn = self.findChild(QToolButton, "fitInViewBtn")
        self.fitInViewBtn.clicked.connect(self.canvas_fitInView)

        self.resetViewBtn = self.findChild(QToolButton, "resetViewBtn")
        self.resetViewBtn.clicked.connect(self.canvas_resetView)

        self.rotateValue_comboBox = self.findChild(QtWidgets.QComboBox, "rotateValue_comboBox")

        # ---- Disable Buttons ----
        self.navigator_disableButtons()
        self.layers_disableButtons()
        self.toolbar_disableButtons()
        self.tools_disableButtons()

        # ---- Disable Canvas Menu Actions ----
        self.disableActions_afterCanvasClose()

        # ---- View Event Filter ----
        self.view.viewport().installEventFilter(self)
        self.draw = False

        # ---- Toolbar Buttons ----
        self.undoBtn = self.findChild(QToolButton, "undoBtn")
        self.undoBtn.clicked.connect(self.undoActions)

        self.redoBtn = self.findChild(QToolButton, "redoBtn")
        self.redoBtn.clicked.connect(self.redoActions)

        self.undoBtn.setDisabled(True)
        self.redoBtn.setDisabled(True)

        self.move_active = False
        self.move = False
        self.moveSelection_start = False
        self.move_selectionSet = False
        self.selection_flipped = False

        self.flipHBtn = self.findChild(QPushButton, "flipHBtn")
        self.flipHBtn.clicked.connect(self.selection_flipHorizontally)

        self.flipVBtn = self.findChild(QPushButton, "flipVBtn")
        self.flipVBtn.clicked.connect(self.selection_flipVertically)

        self.dragBtn = self.findChild(QToolButton, "dragBtn")
        self.dragBtn.clicked.connect(self.dragBtn_state)
        self.drag_active = False

        self.selectBtn = self.findChild(QToolButton, "selectBtn")
        self.selectBtn.clicked.connect(self.selectBtn_state)
        self.free_selectionBtn = self.findChild(QToolButton, "free_selectionBtn")
        self.free_selectionBtn.clicked.connect(self.free_selectionBtn_state)
        self.deselectBtn = self.findChild(QToolButton, "deselectBtn")
        self.deselectBtn.clicked.connect(self.deselectBtn_state)

        self.select_active = False
        self.freeSelect_active = False
        self.area_selected = False
        self.area_freeSelected = False

        self.before_select_pixmap = None
        self.before_moveSelection_pixmap = None
        self.selectionRect_CanvasPixmap = None
        self.selectionRect_Pixmap = None
        self.selectionRect = None
        self.selectionPath = None

        # Default brush/shape cursor
        self.cursor_pix = QPixmap(self.BRUSH_SIZE + 5, self.BRUSH_SIZE + 5)
        self.cursor_pix.fill(Qt.transparent)

        painter = QPainter(self.cursor_pix)
        painter.setPen(QPen(Qt.black, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.drawEllipse(1, 1, self.BRUSH_SIZE, self.BRUSH_SIZE)

        # Adjust cursor size based on canvas size
        self.cursor_size = 0

    """================================
            ColorPicker Functions
    ================================"""

    def switchColors(self):
        # Get color as hex
        color1 = self.firstColor_label.palette().window().color().name()
        color2 = self.secondColor_label.palette().window().color().name()

        # Switch color of labels
        self.firstColor_label.setStyleSheet(f"background-color: {color2}")
        self.secondColor_label.setStyleSheet(f"background-color: {color1}")

        aux = self.firstColor
        self.firstColor = self.secondColor
        self.secondColor = aux

        self.setHex(color2[1:])
        self.setRGB(self.hex_to_rgb(color2[1:]))
        self.setHSV(self.hex_to_hsv(color2[1:]))

    def move_hueSelector(self, event):
        if event.buttons() == Qt.LeftButton:
            pos = event.pos().y() - 7
            if pos < 0:
                pos = 0
            if pos > 185:
                pos = 185
            self.hueSelector.move(QPoint(7, pos))
            self.HSV_changed()

    def move_svSelector(self, event):
        if event.buttons() == Qt.LeftButton:
            pos = event.pos()
            if pos.x() < 0:
                pos.setX(0)
            if pos.y() < 0:
                pos.setY(0)
            if pos.x() > 200:
                pos.setX(200)
            if pos.y() > 200:
                pos.setY(200)
            self.svSelector.move(pos - QPoint(6, 6))
            self.HSV_changed()

    def RGB_changed(self):
        if self.redValue.text() == "":
            self.redValue.setText("0")
        if self.greenValue.text() == "":
            self.greenValue.setText("0")
        if self.blueValue.text() == "":
            self.blueValue.setText("0")

        r, g, b = int(self.redValue.text()), int(self.greenValue.text()), int(self.blueValue.text())

        if r > 255:
            r = 255
            self.redValue.setText("255")
        if g > 255:
            g = 255
            self.greenValue.setText("255")
        if b > 255:
            b = 255
            self.blueValue.setText("255")

        if r == 0 and self.redValue.hasFocus():
            self.setRGB((r, g, b))
            self.redValue.selectAll()

        if g == 0 and self.greenValue.hasFocus():
            self.setRGB((r, g, b))
            self.greenValue.selectAll()

        if b == 0 and self.blueValue.hasFocus():
            self.setRGB((r, g, b))
            self.blueValue.selectAll()

        self.color = self.rgb_to_hsv(r, g, b)
        self.setHSV(self.color)
        self.setHex(self.rgb_to_hex((r, g, b)))
        self.firstColor_label.setStyleSheet(f"background-color: rgb({r},{g},{b})")
        self.firstColor = QColor(r, g, b)

    def HEX_changed(self):
        hex = self.hexValue.text()

        r, g, b = self.hex_to_rgb(hex)
        self.color = self.hex_to_hsv(hex)
        self.setHSV(self.color)
        self.setRGB((r, g, b))
        self.firstColor_label.setStyleSheet(f"background-color: rgb({r},{g},{b})")

    def HSV_changed(self):
        h, s, v = (100 - self.hueSelector.y() / 1.85,
                   (self.svSelector.x() + 6) / 2.0,
                   (194 - self.svSelector.y()) / 2.0)

        r, g, b = self.hsv_to_rgb(h, s, v)

        self.color = (h, s, v)

        self.setRGB((r, g, b))
        self.setHex(self.hsv_to_hex(self.color))

        self.firstColor_label.setStyleSheet(f"background-color: rgb({r},{g},{b})")
        self.colorView.setStyleSheet(f"border-radius: 5px; background-color: "
                                     f"qlineargradient(x1:1, x2:0, stop:0 hsl({h}%,100%,50%), stop:1 #fff);")

    # Set Values
    def setRGB(self, rgb_value):
        r, g, b = rgb_value
        r, g, b = int(r), int(g), int(b)
        self.firstColor = QColor(r, g, b)

        self.redValue.setText(str(r))
        self.greenValue.setText(str(g))
        self.blueValue.setText(str(b))

    def setHex(self, hex_value):
        self.hexValue.setText(hex_value)

    def setHSV(self, c):
        self.hueSelector.move(7, int((100 - c[0]) * 1.85))
        self.colorView.setStyleSheet(f"border-radius: 5px; background-color: "
                                     f"qlineargradient(x1:1, x2:0, stop:0 hsl({int(c[0])}%,100%,50%), stop:1 #fff);")
        self.svSelector.move(int(c[1] * 2 - 6), int((200 - c[2] * 2) - 6))

    # Color Conversion
    def hsv_to_rgb(self, h_or_color, s=0, v=0):
        if type(h_or_color).__name__ == "tuple":
            h, s, v = h_or_color
        else:
            h = h_or_color

        r, g, b = colorsys.hsv_to_rgb(h / 100.0, s / 100.0, v / 100.0)
        return r * 255, g * 255, b * 255

    def hsv_to_hex(self, h_or_color, s=0, v=0):
        if type(h_or_color).__name__ == "tuple":
            h, s, v = h_or_color
        else:
            h = h_or_color
        return self.rgb_to_hex(self.hsv_to_rgb(h, s, v))

    def rgb_to_hex(self, r_or_color, g=0, b=0):
        if type(r_or_color).__name__ == "tuple":
            r, g, b = r_or_color
        else:
            r = r_or_color

        hex = '%02x%02x%02x' % (int(r), int(g), int(b))
        return hex

    def rgb_to_hsv(self, r_or_color, g=0, b=0):
        if type(r_or_color).__name__ == "tuple":
            r, g, b = r_or_color
        else:
            r = r_or_color

        h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
        return (h * 100, s * 100, v * 100)

    def hex_to_rgb(self, hex):
        if len(hex) < 6:
            hex += "0" * (6 - len(hex))
        elif len(hex) > 6:
            hex = hex[0:6]
        rgb = tuple(int(hex[i:i + 2], 16) for i in (0, 2, 4))

        return rgb

    def hex_to_hsv(self, hex):
        return self.rgb_to_hsv(self.hex_to_rgb(hex))

    """================================
            Tools Functions
    ================================"""

    # Brush size Slider
    def setBrushSize_Slider(self, value):
        self.brushSize_value.setText(str(value))
        self.BRUSH_SIZE = value
        self.change_to_brushCursor()

    def setBrushSize_Text(self):
        if self.bsize_active:
            self.size_button.setChecked(False)

        size = self.brushSize_value.text()

        if size != "":
            self.BRUSH_SIZE = size
            self.brushSize_slider.setValue(int(size))

        if size == "":
            self.BRUSH_SIZE = 1
            self.brushSize_slider.setValue(self.BRUSH_SIZE)

    # Density Slider
    def setDensity_Slider(self, value):
        self.density_value.setText(str(value))
        self.DENSITY_VALUE = value

    def setDensity_Text(self):
        density = self.density_value.text()

        if density != "":
            self.DENSITY_VALUE = density
            self.density_slider.setValue(int(density))

        if density == "":
            self.DENSITY_VALUE = 0
            self.density_slider.setValue(self.DENSITY_VALUE)

    def hide_densitySettings(self):
        self.label_density.hide()
        self.density_slider.hide()
        self.density_value.hide()

    def show_densitySettings(self):
        self.label_density.show()
        self.density_slider.show()
        self.density_value.show()

    # Brush Size Buttons
    def bsize_state(self):
        self.brushSize_uncheckButtons()
        self.drag_active = False
        self.toolbar_setDefaultBackground()

        # Get clicked button and activate it
        self.size_button = self.brushSize_layout.sender()
        self.bsize_active = True

        # Change brush size and slider value
        self.BRUSH_SIZE = int(self.size_button.text())
        self.brushSize_value.setText(str(self.BRUSH_SIZE))
        self.brushSize_slider.setValue(self.BRUSH_SIZE)

        self.size_button.setChecked(Qt.Checked)

    def setShapeSize_Slider(self, value):
        self.shapeSize_value.setText(str(value))
        self.SHAPE_SIZE = value
        self.change_to_shapeCursor()

    def setShapeSize_Text(self):
        if self.s_size_active:
            self.size_button2.setChecked(False)

        size = self.shapeSize_value.text()

        if size != "":
            self.SHAPE_SIZE = size
            self.shapeSize_slider.setValue(int(size))

        if size == "":
            self.SHAPE_SIZE = 1
            self.shapeSize_slider.setValue(self.SHAPE_SIZE)

    def s_size_state(self):
        self.shapeSize_uncheckButtons()
        self.drag_active = False
        self.toolbar_setDefaultBackground()

        # Get clicked button and activate it
        self.size_button2 = self.shapeSize_layout.sender()
        self.s_size_active = True

        # Change brush size and slider value
        self.SHAPE_SIZE = int(self.size_button2.text())
        self.shapeSize_value.setText(str(self.SHAPE_SIZE))
        self.shapeSize_slider.setValue(self.SHAPE_SIZE)

        self.size_button2.setChecked(Qt.Checked)

    def change_to_shapeCursor(self):
        # Change the size of the shape cursor
        self.cursor_pix = QPixmap(self.SHAPE_SIZE + 5, self.SHAPE_SIZE + 5)
        self.cursor_pix.fill(Qt.transparent)

        painter = QPainter(self.cursor_pix)
        painter.setRenderHint(QPainter.HighQualityAntialiasing)

        painter.setPen(QPen(Qt.black, self.cursor_size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.drawEllipse(1, 1, self.SHAPE_SIZE, self.SHAPE_SIZE)

        painter.setPen(QPen(Qt.white, self.cursor_size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.drawEllipse(2, 2, self.SHAPE_SIZE - 2, self.SHAPE_SIZE - 2)

        self.cursor_item.setPixmap(self.cursor_pix)

    def change_to_brushCursor(self):
        # Change the size of the brush cursor
        self.cursor_pix = QPixmap(self.BRUSH_SIZE + 5, self.BRUSH_SIZE + 5)
        self.cursor_pix.fill(Qt.transparent)

        painter = QPainter(self.cursor_pix)
        painter.setRenderHint(QPainter.HighQualityAntialiasing)

        painter.setPen(QPen(Qt.black, self.cursor_size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.drawEllipse(1, 1, self.BRUSH_SIZE, self.BRUSH_SIZE)

        painter.setPen(QPen(Qt.white, self.cursor_size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.drawEllipse(2, 2, self.BRUSH_SIZE - 2, self.BRUSH_SIZE - 2)

        self.cursor_item.setPixmap(self.cursor_pix)

    def penBtn_state(self):
        if not self.pen_active:
            self.tools_uncheckButtons()
            self.disable_activeState()

            # Disable toolbar Buttons
            self.deselectBtn_state()
            self.toolbar_disable_activeState()
            self.toolbar_setDefaultBackground()

            self.penBtn.setChecked(Qt.Checked)
            self.pen_active = True
            self.hide_densitySettings()

            # Show Shape Settings Frame
            self.stackedWidget_settings.setCurrentIndex(0)
            self.stackedWidget_size.setCurrentIndex(0)

            # Change cursor
            self.change_to_brushCursor()
        else:
            self.pen_active = False

    def brushBtn_state(self):
        if not self.brush_active:
            self.tools_uncheckButtons()
            self.disable_activeState()

            # Disable toolbar Buttons
            self.deselectBtn_state()
            self.toolbar_disable_activeState()
            self.toolbar_setDefaultBackground()

            self.brushBtn.setChecked(Qt.Checked)
            self.brush_active = True
            self.show_densitySettings()

            # Show Shape Settings Frame
            self.stackedWidget_settings.setCurrentIndex(0)
            self.stackedWidget_size.setCurrentIndex(0)

            # Change cursor
            self.change_to_brushCursor()
        else:
            self.brush_active = False

    def eraserBtn_state(self):
        if not self.eraser_active:
            self.tools_uncheckButtons()
            self.disable_activeState()

            # Disable toolbar Buttons
            self.deselectBtn_state()
            self.toolbar_disable_activeState()
            self.toolbar_setDefaultBackground()

            self.eraserBtn.setChecked(Qt.Checked)
            self.eraser_active = True

            # Show Shape Settings Frame
            self.stackedWidget_settings.setCurrentIndex(0)
            self.stackedWidget_size.setCurrentIndex(0)

            # Change cursor
            self.change_to_brushCursor()
        else:
            self.eraser_active = False

    def bucketBtn_state(self):
        if not self.bucket_active:
            self.tools_uncheckButtons()
            self.disable_activeState()

            # Disable toolbar Buttons
            self.deselectBtn_state()
            self.toolbar_disable_activeState()
            self.toolbar_setDefaultBackground()

            self.bucketBtn.setChecked(Qt.Checked)
            self.bucket_active = True

            # Show Shape Settings Frame
            self.stackedWidget_settings.setCurrentIndex(0)
            self.stackedWidget_size.setCurrentIndex(0)
        else:
            self.bucket_active = False

    def textBtn_state(self):
        if not self.text_active:
            self.tools_uncheckButtons()
            self.disable_activeState()

            # Disable toolbar Buttons
            self.deselectBtn_state()
            self.toolbar_disable_activeState()
            self.toolbar_setDefaultBackground()

            self.textBtn.setChecked(Qt.Checked)
            self.text_active = True

            # Show Shape Settings Frame
            self.stackedWidget_settings.setCurrentIndex(2)
            self.stackedWidget_size.setCurrentIndex(2)
        else:
            self.text_active = False

    def pickerBtn_state(self):
        if not self.picker_active:
            self.tools_uncheckButtons()
            self.disable_activeState()

            # Disable toolbar Buttons
            self.deselectBtn_state()
            self.toolbar_disable_activeState()
            self.toolbar_setDefaultBackground()

            self.pickerBtn.setChecked(Qt.Checked)
            self.picker_active = True
            self.stackedWidget_settings.setCurrentIndex(0)
            self.stackedWidget_size.setCurrentIndex(0)
        else:
            self.picker_active = False

    def lineBtn_state(self):
        if not self.line_active:
            self.tools_uncheckButtons()
            self.disable_activeState()

            # Disable toolbar Buttons
            self.deselectBtn_state()
            self.toolbar_disable_activeState()
            self.toolbar_setDefaultBackground()

            self.lineBtn.setChecked(Qt.Checked)
            self.line_active = True

            # Show Shape Settings Frame
            self.stackedWidget_settings.setCurrentIndex(1)
            self.stackedWidget_size.setCurrentIndex(1)

            # Change cursor
            self.change_to_shapeCursor()
        else:
            self.line_active = False

    def squareBtn_state(self):
        if not self.square_active:
            self.tools_uncheckButtons()
            self.disable_activeState()

            # Disable toolbar Buttons
            self.deselectBtn_state()
            self.toolbar_disable_activeState()
            self.toolbar_setDefaultBackground()

            self.squareBtn.setChecked(Qt.Checked)
            self.square_active = True

            # Show Shape Settings Frame
            self.stackedWidget_settings.setCurrentIndex(1)
            self.stackedWidget_size.setCurrentIndex(1)

            # Change cursor
            self.change_to_shapeCursor()
        else:
            self.square_active = False

    def ellipseBtn_state(self):
        if not self.ellipse_active:
            self.tools_uncheckButtons()
            self.disable_activeState()

            # Disable toolbar Buttons
            self.deselectBtn_state()
            self.toolbar_disable_activeState()
            self.toolbar_setDefaultBackground()

            self.ellipseBtn.setChecked(Qt.Checked)
            self.ellipse_active = True

            # Show Shape Settings Frame
            self.stackedWidget_settings.setCurrentIndex(1)
            self.stackedWidget_size.setCurrentIndex(1)

            # Change cursor
            self.change_to_shapeCursor()
        else:
            self.ellipse_active = False

    # Text Settings
    def setTextValue(self):
        self.text = self.textValue.text()

    def textBold_state(self):
        if self.bold:
            self.bold = False
            self.text_boldBtn.setChecked(Qt.Unchecked)
        else:
            self.bold = True
            self.text_boldBtn.setChecked(Qt.Checked)

    def textItalic_state(self):
        if self.italic:
            self.italic = False
            self.text_italicBtn.setChecked(Qt.Unchecked)
        else:
            self.italic = True
            self.text_italicBtn.setChecked(Qt.Checked)

    def textUnderline_state(self):
        if self.underline:
            self.underline = False
            self.text_underlineBtn.setChecked(Qt.Unchecked)
        else:
            self.underline = True
            self.text_underlineBtn.setChecked(Qt.Checked)

    def disable_activeState(self):
        self.pen_active = False
        self.brush_active = False
        self.eraser_active = False
        self.line_active = False
        self.square_active = False
        self.ellipse_active = False
        self.picker_active = False
        self.text_active = False
        self.bucket_active = False

    def tools_disableButtons(self):
        self.penBtn.setDisabled(True)
        self.brushBtn.setDisabled(True)
        self.eraserBtn.setDisabled(True)
        self.bucketBtn.setDisabled(True)
        self.textBtn.setDisabled(True)
        self.lineBtn.setDisabled(True)
        self.squareBtn.setDisabled(True)
        self.ellipseBtn.setDisabled(True)
        self.pickerBtn.setDisabled(True)

    def tools_enableButtons(self):
        self.penBtn.setEnabled(True)
        self.brushBtn.setEnabled(True)
        self.eraserBtn.setEnabled(True)
        self.bucketBtn.setEnabled(True)
        self.textBtn.setEnabled(True)
        self.lineBtn.setEnabled(True)
        self.squareBtn.setEnabled(True)
        self.ellipseBtn.setEnabled(True)
        self.pickerBtn.setEnabled(True)

    def tools_uncheckButtons(self):
        for i in range(self.tools_layout.count()):
            self.tools_layout.itemAt(i).widget().setChecked(Qt.Unchecked)

    def brushSize_uncheckButtons(self):
        for i in range(self.brushSize_layout.count()):
            self.brushSize_layout.itemAt(i).widget().setChecked(Qt.Unchecked)

    def brushSize_disableButtons(self):
        for i in range(self.brushSize_layout.count()):
            self.brushSize_layout.itemAt(i).widget().setDisabled(True)

    def brushSize_enableButtons(self):
        for i in range(self.brushSize_layout.count()):
            self.brushSize_layout.itemAt(i).widget().setEnabled(True)

    def shapeSize_uncheckButtons(self):
        for i in range(self.shapeSize_layout.count()):
            self.shapeSize_layout.itemAt(i).widget().setChecked(Qt.Unchecked)

    def shapeSize_disableButtons(self):
        for i in range(self.brushSize_layout.count()):
            self.brushSize_layout.itemAt(i).widget().setDisabled(True)

    def shapeSize_enableButtons(self):
        for i in range(self.brushSize_layout.count()):
            self.brushSize_layout.itemAt(i).widget().setEnabled(True)

    """================================
            Toolbar Functions
    ================================"""

    def dragBtn_state(self):
        self.tools_uncheckButtons()
        self.disable_activeState()
        self.select_active = False
        self.freeSelect_active = False
        self.move_active = False
        self.toolbar_setDefaultBackground()

        if not self.drag_active:
            # If a selection is made, clear it
            self.deselectBtn_state()

            self.drag_active = True
            self.dragBtn.setStyleSheet("QToolButton{ background-color: rgb(99, 101, 135);}"
                                       "QToolButton:hover{background-color: rgb(82, 82, 124);}")

            self.stackedWidget_settings.setCurrentIndex(0)
            self.stackedWidget_size.setCurrentIndex(0)

        else:
            self.drag_active = False
            self.dragBtn.setStyleSheet("QToolButton{ background-color: rgb(57, 58, 65);}"
                                       "QToolButton:hover{background-color: rgb(82, 82, 124);}")

    def selectBtn_state(self):
        self.tools_uncheckButtons()
        self.disable_activeState()
        self.drag_active = False
        self.freeSelect_active = False
        self.move_active = False
        self.toolbar_setDefaultBackground()

        if not self.select_active:
            self.select_active = True
            self.selectBtn.setStyleSheet("QToolButton{ background-color: rgb(99, 101, 135);}"
                                         "QToolButton:hover{background-color: rgb(82, 82, 124);}")

            self.stackedWidget_settings.setCurrentIndex(3)
            self.stackedWidget_size.setCurrentIndex(3)

            # Deselect the "select all selection"
            self.selectionRect = None
            self.item_selection.setPixmap(self.pixmap_selection)
        else:
            self.select_active = False
            self.selectBtn.setStyleSheet("QToolButton{ background-color: rgb(57, 58, 65);}"
                                         "QToolButton:hover{background-color: rgb(82, 82, 124);}")
            self.selectionMenu_disable()
            self.actionCopy.setDisabled(True)

    def free_selectionBtn_state(self):
        self.tools_uncheckButtons()
        self.disable_activeState()
        self.drag_active = False
        self.select_active = False
        self.move_active = False
        self.toolbar_setDefaultBackground()

        if not self.freeSelect_active:
            self.freeSelect_active = True
            self.free_selectionBtn.setStyleSheet("QToolButton{ background-color: rgb(99, 101, 135);}"
                                                 "QToolButton:hover{background-color: rgb(82, 82, 124);}")
            self.selectionMenu_disable()

            self.stackedWidget_settings.setCurrentIndex(0)
            self.stackedWidget_size.setCurrentIndex(0)

            # Deselect the "select all selection"
            self.selectionRect = None
            self.item_selection.setPixmap(self.pixmap_selection)
        else:
            self.freeSelect_active = False
            self.free_selectionBtn.setStyleSheet("QToolButton{ background-color: rgb(57, 58, 65);}"
                                                 "QToolButton:hover{background-color: rgb(82, 82, 124);}")
            self.selectionMenu_disable()

    def deselectBtn_state(self):
        self.select_active = False
        self.freeSelect_active = False
        self.selectionRect = None
        self.selectionPath = None
        self.toolbar_setDefaultBackground()
        self.item_selection.setPixmap(self.pixmap_selection)

        self.selectionMenu_disable()
        self.actionCopy.setDisabled(True)

    def delete_selectedArea(self):
        if (self.select_active or self.area_selected) and self.selectionRect is not None:
            x, y, w, h = self.selectionRect.getRect()

            pixmap = SELECTED_LAYER.pixmap
            painter = QPainter(pixmap)
            painter.setCompositionMode(QPainter.CompositionMode_Clear)
            painter.setRenderHint(QPainter.HighQualityAntialiasing)
            painter.setPen(QPen(Qt.black))
            painter.setBrush(QBrush(Qt.black))

            painter.drawRect(x, y, w, h)

            SELECTED_LAYER.setPixmapItem(pixmap)
            self.add_to_undoList(SELECTED_LAYER, SELECTED_LAYER.pixmap)
            self.saved_state = False
            self.view.viewport().update()

        elif self.freeSelect_active and self.selectionPath is not None:
            pixmap = SELECTED_LAYER.pixmap
            painter = QPainter(pixmap)
            painter.setCompositionMode(QPainter.CompositionMode_Clear)
            painter.setRenderHint(QPainter.HighQualityAntialiasing)

            painter.fillPath(self.selectionPath, QBrush(Qt.black))

            SELECTED_LAYER.setPixmapItem(pixmap)
            self.add_to_undoList(SELECTED_LAYER, SELECTED_LAYER.pixmap)
            self.saved_state = False
            self.view.viewport().update()

    def fill_selectedArea(self):
        if (self.select_active or self.area_selected) and self.selectionRect is not None:
            x, y, w, h = self.selectionRect.getRect()

            pixmap = SELECTED_LAYER.pixmap
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.HighQualityAntialiasing)

            painter.setPen(QPen(self.firstColor))
            painter.setBrush(QBrush(self.firstColor))

            painter.drawRect(x, y, w, h)

            SELECTED_LAYER.setPixmapItem(pixmap)
            self.add_to_undoList(SELECTED_LAYER, SELECTED_LAYER.pixmap)
            self.saved_state = False
            self.view.viewport().update()

        elif self.freeSelect_active and self.selectionPath is not None:
            pixmap = SELECTED_LAYER.pixmap
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.HighQualityAntialiasing)

            painter.fillPath(self.selectionPath, QBrush(self.firstColor))

            SELECTED_LAYER.setPixmapItem(pixmap)
            self.add_to_undoList(SELECTED_LAYER, SELECTED_LAYER.pixmap)
            self.saved_state = False
            self.view.viewport().update()

    def selection_setPixmapAfterMove_or_Flip(self):
        if self.selectionRect is not None:
            painter = QPainter(SELECTED_LAYER.pixmap)
            # Draw the moved selection on the layer
            painter.drawPixmap(self.selectionRect.x(), self.selectionRect.y(), self.selectionRect_CanvasPixmap)
            self.add_to_undoList(SELECTED_LAYER, SELECTED_LAYER.pixmap)
            self.saved_state = False
            SELECTED_LAYER.setPixmapItem(SELECTED_LAYER.pixmap)

    def selection_flipHorizontally(self):
        if self.selectionRect is not None:
            pixmap_flipped = self.selectionRect_CanvasPixmap.transformed(QTransform().scale(-1, 1))

            x, y, w, h = self.selectionRect.getRect()

            preview_pixmap = SELECTED_LAYER.pixmap
            painter = QPainter(preview_pixmap)
            painter.setCompositionMode(QPainter.CompositionMode_Clear)
            painter.setRenderHint(QPainter.HighQualityAntialiasing)
            painter.setPen(QPen(Qt.black))
            painter.setBrush(QBrush(Qt.black))

            painter.drawRect(x, y, w, h)

            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
            painter.drawPixmap(x, y, pixmap_flipped)

            self.selectionRect_CanvasPixmap = pixmap_flipped
            SELECTED_LAYER.setPixmapItem(preview_pixmap)
            self.selection_flipped = True

    def selection_flipVertically(self):
        if self.selectionRect is not None:
            pixmap_flipped = self.selectionRect_CanvasPixmap.transformed(QTransform().scale(1, -1))

            x, y, w, h = self.selectionRect.getRect()

            preview_pixmap = SELECTED_LAYER.pixmap
            painter = QPainter(preview_pixmap)
            painter.setCompositionMode(QPainter.CompositionMode_Clear)
            painter.setRenderHint(QPainter.HighQualityAntialiasing)
            painter.setPen(QPen(Qt.black))
            painter.setBrush(QBrush(Qt.black))

            painter.drawRect(x, y, w, h)

            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
            painter.drawPixmap(x, y, pixmap_flipped)

            self.selectionRect_CanvasPixmap = pixmap_flipped
            SELECTED_LAYER.setPixmapItem(preview_pixmap)
            self.selection_flipped = True

    def toolbar_disableButtons(self):
        self.undoBtn.setDisabled(True)
        self.actionUndo.setDisabled(True)
        self.redoBtn.setDisabled(True)
        self.actionRedo.setDisabled(True)

        self.dragBtn.setDisabled(True)
        self.selectBtn.setDisabled(True)
        self.free_selectionBtn.setDisabled(True)
        self.deselectBtn.setDisabled(True)

    def toolbar_enableButtons(self):
        self.dragBtn.setEnabled(True)
        self.selectBtn.setEnabled(True)
        self.free_selectionBtn.setEnabled(True)
        self.deselectBtn.setEnabled(True)

    def toolbar_setDefaultBackground(self):
        self.dragBtn.setStyleSheet("QToolButton{ background-color: rgb(57, 58, 65);} "
                                   "QToolButton:hover{background-color: rgb(82, 82, 124);}")
        self.selectBtn.setStyleSheet("QToolButton{ background-color: rgb(57, 58, 65);}"
                                     "QToolButton:hover{background-color: rgb(82, 82, 124);}")
        self.free_selectionBtn.setStyleSheet("QToolButton{ background-color: rgb(57, 58, 65);}"
                                             "QToolButton:hover{background-color: rgb(82, 82, 124);}")

    def toolbar_disable_activeState(self):
        self.move_active = False
        self.drag_active = False
        self.select_active = False
        self.freeSelect_active = False

    def selectionMenu_disable(self):
        self.actionDeselect.setDisabled(True)
        self.actionDelete_selectedArea.setDisabled(True)
        self.actionFill_Selected_Area.setDisabled(True)

    def selectionMenu_enable(self):
        self.actionDeselect.setEnabled(True)
        self.actionDelete_selectedArea.setEnabled(True)
        self.actionFill_Selected_Area.setEnabled(True)

    """================================
            Layer Functions
    ================================"""

    def lockLayer(self):
        if SELECTED_LAYER.locked:
            SELECTED_LAYER.locked = False
            SELECTED_LAYER.removeLockIcon()
        else:
            SELECTED_LAYER.locked = True
            SELECTED_LAYER.setLockIcon()
            SELECTED_LAYER.updateLayerMask()

    def addLayer(self):
        global SELECTED_LAYER, LAYERS
        if self.layer_count != self.max_layers:
            self.layer_count += 1
            self.layer_number += 1

            LAYERS.append(Layer(self.layer_number, self.canvas_width, self.canvas_height, self.scene))
            self.layout.insertWidget(0, LAYERS[self.layer_count - 1])

            SELECTED_LAYER.set_defaultBg()
            SELECTED_LAYER = LAYERS[self.layer_count - 1]
            SELECTED_LAYER.set_activeBg()

    def addLayer_with_PastedSelection(self):
        global SELECTED_LAYER, LAYERS
        self.layer_count += 1
        self.layer_number += 1

        LAYERS.append(Layer(self.layer_number, self.canvas_width, self.canvas_height, self.scene))
        self.layout.insertWidget(0, LAYERS[self.layer_count - 1])

        SELECTED_LAYER.set_defaultBg()
        SELECTED_LAYER = LAYERS[self.layer_count - 1]
        SELECTED_LAYER.set_activeBg()

    def deleteLayer(self):
        global SELECTED_LAYER, UNDO

        # Get position in "LAYERS" list for the current selected layer
        layer_position = SELECTED_LAYER.findLayerPosition(SELECTED_LAYER.getLayerNumber())

        # Remove selected layer from "LAYERS" list
        if len(LAYERS) != 1:
            LAYERS.pop(layer_position)
            self.layer_count -= 1

            # Remove selected layer from view's scene
            self.scene.removeItem(SELECTED_LAYER.item)

            # Update UNDO and REDO list after the layer is deleted
            REDO.clear()
            self.actionRedo.setDisabled(True)
            self.redoBtn.setDisabled(True)
            self.redoBtn.setStyleSheet("QToolButton{ background-color: rgb(57, 58, 65);}"
                                       "QToolButton:hover{background-color: rgb(82, 82, 124);}")

            # Delete all the references for this layer in UNDO list
            if UNDO:
                UNDO = [element for element in UNDO if element[0] != SELECTED_LAYER]

            # Remove selected layer from layout
            index = self.layout.indexOf(SELECTED_LAYER)
            item = self.layout.takeAt(index)
            item.widget().deleteLater()

            # Set current selected layer to previous layer
            SELECTED_LAYER = LAYERS[layer_position - 1]
            SELECTED_LAYER.set_activeBg()

    def eraseLayer(self):
        SELECTED_LAYER.eraseLayer()
        self.add_to_undoList(SELECTED_LAYER, SELECTED_LAYER.pixmap)
        self.saved_state = False

    def moveLayerAbove(self):
        if self.layout.count() > 1:
            i = self.layout.indexOf(SELECTED_LAYER)
            if i != 0:
                current_layer = self.layout.itemAt(i).widget()
                layer_above = self.layout.itemAt(i - 1).widget()

                # Switch position (zValue) on canvas view
                layer_above_ZValue = layer_above.getZValue()
                current_layer_ZValue = current_layer.getZValue()

                layer_above.changeZValue(current_layer_ZValue)
                current_layer.changeZValue(layer_above_ZValue)

                # Switch position in Layers Frame layout
                self.layout.insertWidget(i - 1, current_layer)
                self.view.viewport().update()

    def moveLayerBelow(self):
        if self.layout.count() > 1:
            i = self.layout.indexOf(SELECTED_LAYER)
            if i != self.layout.count() - 1:
                current_layer = self.layout.itemAt(i).widget()
                layer_below = self.layout.itemAt(i + 1).widget()

                # Switch position (zValue) on canvas view
                layer_below_ZValue = layer_below.getZValue()
                current_layer_ZValue = current_layer.getZValue()

                layer_below.changeZValue(current_layer_ZValue)
                current_layer.changeZValue(layer_below_ZValue)

                # Switch position in Layers Frame layout
                self.layout.insertWidget(i + 1, current_layer)
                self.view.viewport().update()

    def layers_disableButtons(self):
        self.lockLayerBtn.setDisabled(True)
        self.addLayerBtn.setDisabled(True)
        self.deleteLayerBtn.setDisabled(True)
        self.eraseLayerBtn.setDisabled(True)
        self.moveLayerAboveBtn.setDisabled(True)
        self.moveLayerBelowBtn.setDisabled(True)

    def layers_enableButtons(self):
        self.lockLayerBtn.setEnabled(True)
        self.addLayerBtn.setEnabled(True)
        self.deleteLayerBtn.setEnabled(True)
        self.eraseLayerBtn.setEnabled(True)
        self.moveLayerAboveBtn.setEnabled(True)
        self.moveLayerBelowBtn.setEnabled(True)

    def layers_disable(self):
        for i in range(self.layout.count()):
            self.layout.itemAt(i).widget().setDisabled(True)

    def layers_enable(self):
        for i in range(self.layout.count()):
            self.layout.itemAt(i).widget().setEnabled(True)

    """================================
        Menu - New Canvas Functions
    ================================"""

    def newCanvas(self):
        self.newCanvas_window = NewCanvasWindow()
        self.newCanvas_window.show()
        self.newCanvas_window.okBtn.clicked.connect(self.setCanvas)
        self.newCanvas_window.cancelBtn.clicked.connect(self.closeWindow)

    def setCanvas(self):
        global SELECTED_LAYER, UNDO

        if self.newCanvas_window.getName() != "":
            self.canvas_name = self.newCanvas_window.getName()

        if self.newCanvas_window.getWidth() != "":
            if int(self.newCanvas_window.getWidth()) < 1:
                return
            else:
                self.canvas_width = int(self.newCanvas_window.getWidth())

        if self.newCanvas_window.getHeight() != "":
            if int(self.newCanvas_window.getHeight()) < 1:
                return
            else:
                self.canvas_height = int(self.newCanvas_window.getHeight())

        self.newCanvas_window.close()

        # Background Layer
        self.scene.setSceneRect(0, 0, self.canvas_width, self.canvas_height)
        self.canvas_bg = QtGui.QImage(self.canvas_width, self.canvas_height, QtGui.QImage.Format_ARGB32_Premultiplied)
        self.canvas_bg.fill(Qt.white)

        self.pixmap_bg = QPixmap(self.canvas_bg)
        self.item_bg = self.scene.addPixmap(self.pixmap_bg)
        self.item_bg.setPixmap(self.pixmap_bg)
        self.item_bg.setZValue(0)

        # Add brush cursor to scene
        self.cursor_item = self.scene.addPixmap(self.cursor_pix)
        self.cursor_item.setPixmap(self.cursor_pix)
        self.cursor_item.setZValue(500)
        self.cursor_item.hide()

        # Set cursor size based on canvas size
        if self.canvas_height >= 2000 or self.canvas_width >= 2000:
            self.cursor_size = 3
        elif self.canvas_height <= 1200 or self.canvas_width <= 1200:
            self.cursor_size = 1

        # Selection Layer
        self.selection_image = QtGui.QImage(self.canvas_width, self.canvas_height,
                                            QtGui.QImage.Format_ARGB32_Premultiplied)
        self.selection_image.fill(Qt.transparent)

        self.pixmap_selection = QPixmap(self.selection_image)
        self.item_selection = self.scene.addPixmap(self.pixmap_selection)
        self.item_selection.setPixmap(self.pixmap_selection)
        self.item_selection.setZValue(200)

        # Disable "New canvas" and "Open" Menu Option until "Close" Menu Option is selected
        # Enable "Save as" option
        self.actionNew_Canvas.setDisabled(True)
        self.actionOpen.setDisabled(True)

        # Enable Canvas Menu Actions
        self.enableActions_afterCanvasSet()

        # Enable Canvas Settings
        self.stackedWidget_settings.setEnabled(True)
        self.stackedWidget_size.setEnabled(True)

        # Create first layer and add it to QScrollArea
        self.layer_count += 1
        self.layer_number += 1

        LAYERS.append(Layer(self.layer_number, self.canvas_width, self.canvas_height, self.scene))
        self.layout.insertWidget(0, LAYERS[0])
        SELECTED_LAYER = LAYERS[0]
        SELECTED_LAYER.set_activeBg()

        self.navigator_fitInView()
        self.canvas_resetView()
        self.navigator_enableButtons()
        self.layers_enableButtons()
        self.toolbar_enableButtons()
        self.tools_enableButtons()
        self.CANVAS = True
        self.saved_state = True

    def closeWindow(self):
        self.newCanvas_window.close()

    """================================
            Menu - Open Functions
    ================================"""

    def openImage(self):
        file = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Open File",
            QtCore.QDir.currentPath(),
            filter="Images (*.png *.jpg *jpeg)",
        )

        if not file[0] == "":
            self.save_path = file[0]
            file_name = str(file[0]).split('/')
            name = file_name[len(file_name) - 1]
            name = name[0:name.index(".")]
            self.canvas_name = name

            return QPixmap(file[0])

        return 0

    def setImageOnCanvas(self):
        global SELECTED_LAYER, UNDO
        self.selected_image = self.openImage()

        if self.selected_image != 0:
            self.canvas_width = self.selected_image.width()
            self.canvas_height = self.selected_image.height()

            # Background Layer
            self.scene.setSceneRect(0, 0, self.canvas_width, self.canvas_height)
            self.canvas_bg = QtGui.QImage(self.canvas_width, self.canvas_height,
                                          QtGui.QImage.Format_ARGB32_Premultiplied)
            self.canvas_bg.fill(Qt.white)

            self.pixmap_bg = QPixmap(self.canvas_bg)
            self.item_bg = self.scene.addPixmap(self.pixmap_bg)
            self.item_bg.setPixmap(self.pixmap_bg)
            self.item_bg.setZValue(0)

            # Add brush cursor to scene
            self.cursor_item = self.scene.addPixmap(self.cursor_pix)
            self.cursor_item.setPixmap(self.cursor_pix)
            self.cursor_item.setZValue(500)
            self.cursor_item.hide()

            # Set cursor size based on canvas size
            if self.canvas_height >= 2000 or self.canvas_width >= 2000:
                self.cursor_size = 3
            elif self.canvas_height <= 1500 or self.canvas_width <= 1500:
                self.cursor_size = 1

            # Selection Layer
            self.selection_image = QtGui.QImage(self.canvas_width, self.canvas_height,
                                                QtGui.QImage.Format_ARGB32_Premultiplied)
            self.selection_image.fill(Qt.transparent)

            self.pixmap_selection = QPixmap(self.selection_image)
            self.item_selection = self.scene.addPixmap(self.pixmap_selection)
            self.item_selection.setPixmap(self.pixmap_selection)
            self.item_selection.setZValue(200)

            # Disable "Open" and "New Canvas" Menu Option until "Close" Menu Option is selected
            # Enable "Save as" option
            self.actionOpen.setDisabled(True)
            self.actionNew_Canvas.setDisabled(True)

            # Enable Canvas Menu Actions
            self.enableActions_afterCanvasSet()

            # Enable Canvas Settings
            self.stackedWidget_settings.setEnabled(True)
            self.stackedWidget_size.setEnabled(True)

            # Create first layer and add it to QScrollArea
            self.layer_count += 1
            self.layer_number += 1

            LAYERS.append(
                Layer(self.layer_number, self.canvas_width, self.canvas_height, self.scene, self.selected_image))
            self.layout.insertWidget(0, LAYERS[0])
            SELECTED_LAYER = LAYERS[0]
            SELECTED_LAYER.set_activeBg()

            self.navigator_fitInView()
            self.canvas_resetView()
            self.navigator_enableButtons()
            self.layers_enableButtons()
            self.toolbar_enableButtons()
            self.tools_enableButtons()
            self.CANVAS = True
            self.saved_state = True

    """================================
            Menu - Save Function
    ================================"""

    def file_save(self):
        if self.save_path == "":
            self.file_saveAs()
        else:
            # If a selection is made on the canvas, clear it
            self.deselectBtn_state()

            # Grab image from view and save it
            imageToSave = QtGui.QImage(self.canvas_width, self.canvas_height,
                                       QtGui.QImage.Format_ARGB32_Premultiplied)

            painter = QPainter(imageToSave)
            self.scene.render(painter, QRectF(), QRectF(imageToSave.rect()))
            painter.end()

            imageToSave.save(self.save_path)
            self.saved_state = True

    def file_saveAs(self):
        file, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save file",
            self.canvas_name,
            "JPEG (*.JPEG); PNG (*.png)")

        if file == "":
            return

        if not file == "":
            self.save_path = file

            # If a selection is made on the canvas, clear it
            self.deselectBtn_state()

            # Grab image from view and save it
            imageToSave = QtGui.QImage(self.canvas_width, self.canvas_height,
                                       QtGui.QImage.Format_ARGB32_Premultiplied)

            painter = QPainter(imageToSave)
            self.scene.render(painter, QRectF(), QRectF(imageToSave.rect()))
            painter.end()

            imageToSave.save(self.save_path)
            self.saved_state = True

    """================================
            Menu - Close Function
    ================================"""

    def open_closeCanvasWindow(self):
        if self.saved_state:
            self.closeCanvas()
        else:
            self.close_window = CloseWindow()
            self.close_window.show()
            self.close_window.yesBtn.clicked.connect(self.yesButton_closeCanvasWindow)
            self.close_window.noBtn.clicked.connect(self.noBtn_closeCanvasWindow)
            self.close_window.cancelBtn.clicked.connect(lambda: self.close_window.close())

    def yesButton_closeCanvasWindow(self):
        self.close_window.close()
        self.file_save()
        self.closeCanvas()

    def noBtn_closeCanvasWindow(self):
        self.closeCanvas()
        self.close_window.close()

    def closeCanvas(self):
        global SELECTED_LAYER

        SELECTED_LAYER = None
        self.layer_count = 0
        self.layer_number = 0
        LAYERS.clear()
        self.scene.clear()
        self.canvas_resetView()

        # Remove from layout
        for i in reversed(range(self.layout.count())):
            layerToRemove = self.layout.itemAt(i).widget()
            self.layout.removeWidget(layerToRemove)
            layerToRemove.deleteLater()

        # Clear UNDO and REDO lists
        UNDO.clear()
        REDO.clear()
        self.undoBtn.setDisabled(True)
        self.undoBtn.setStyleSheet("QToolButton{ background-color: rgb(57, 58, 65);}"
                                   "QToolButton:hover{background-color: rgb(82, 82, 124);}")
        self.redoBtn.setDisabled(True)
        self.redoBtn.setStyleSheet("QToolButton{ background-color: rgb(57, 58, 65);}"
                                   "QToolButton:hover{background-color: rgb(82, 82, 124);}")
        self.selected_image = None

        self.actionNew_Canvas.setEnabled(True)
        self.actionOpen.setEnabled(True)
        self.disableActions_afterCanvasClose()

        self.save_path = ""
        self.navigator_disableButtons()
        self.layers_disableButtons()
        self.toolbar_disableButtons()

        self.tools_disableButtons()
        self.tools_uncheckButtons()
        self.disable_activeState()
        self.CANVAS = False

        self.toolbar_disable_activeState()
        self.toolbar_setDefaultBackground()

        self.stackedWidget_settings.setCurrentIndex(0)
        self.stackedWidget_size.setCurrentIndex(0)

        # Disable Canvas Settings
        self.stackedWidget_settings.setDisabled(True)
        self.stackedWidget_size.setDisabled(True)
        self.brushSize_uncheckButtons()
        self.shapeSize_uncheckButtons()

    """================================
            Menu - Quit Function
    ================================"""

    def quitApp(self):
        if not self.CANVAS or self.saved_state:
            sys.exit(0)
        else:
            self.quit_window = CloseWindow()
            self.quit_window.show()
            self.quit_window.yesBtn.clicked.connect(self.yesButton_quitCanvasWindow)
            self.quit_window.noBtn.clicked.connect(self.noBtn_quitCanvasWindow)
            self.quit_window.cancelBtn.clicked.connect(lambda: self.quit_window.close())

    def yesButton_quitCanvasWindow(self):
        self.quit_window.close()
        self.file_save()

        # Close application
        sys.exit(0)

    def noBtn_quitCanvasWindow(self):
        self.quit_window.close()
        sys.exit(0)

    def closeEvent(self, event):
        if not self.CANVAS or self.saved_state:
            event.accept()
        else:
            self.quitApp()
            event.ignore()

    """====================================
          Menu - Undo, Redo Functions
    ===================================="""

    def undoActions(self):
        global SELECTED_LAYER, UNDO, REDO
        # Enable Redo
        self.actionRedo.setEnabled(True)
        self.redoBtn.setEnabled(True)
        self.redoBtn.setStyleSheet("QToolButton{ background-color: rgb(99, 101, 135);}"
                                   "QToolButton:hover{background-color: rgb(82, 82, 124);}")

        if UNDO:
            # Delete last element from UNDO list and append it to REDO list
            removed_element = UNDO.pop()
            REDO.append(removed_element)

            # If SELECTED_LAYER is not the same as the removed_element's layer
            # Change SELECTED_LAYER to removed_element's layer
            if SELECTED_LAYER != removed_element[0]:
                SELECTED_LAYER.set_defaultBg()
                SELECTED_LAYER = removed_element[0]
                SELECTED_LAYER.set_activeBg()

            # If UNDO list is empty
            if not UNDO:
                self.actionUndo.setDisabled(True)
                self.undoBtn.setDisabled(True)
                self.undoBtn.setStyleSheet("QToolButton{ background-color: rgb(57, 58, 65);}"
                                           "QToolButton:hover{background-color: rgb(82, 82, 124);}")

                if self.selected_image is None:
                    image = QtGui.QImage(self.canvas_width, self.canvas_height,
                                         QtGui.QImage.Format_ARGB32_Premultiplied)
                    image.fill(Qt.transparent)
                else:
                    image = self.selected_image

                SELECTED_LAYER.pixmap = QPixmap(image)
                SELECTED_LAYER.setPixmapItem(SELECTED_LAYER.pixmap)
            else:
                # Get layer and pixmap from the las element of UNDO list
                undo_layer = UNDO[-1][0]
                undo_pixmap = UNDO[-1][1]

                # Check if the SELECTED_LAYER is the same as the last element's layer from the UNDO list
                # If they are not the same, we have to change the SELECTED_LAYER to the layer of the
                # last element in the UNDO list
                # If they are the same, we continue and change the current pixmap of the layer to the previous one
                if SELECTED_LAYER == undo_layer:
                    SELECTED_LAYER.pixmap = QPixmap(undo_pixmap)
                    SELECTED_LAYER.setPixmapItem(SELECTED_LAYER.pixmap)
                else:
                    # In UNDO list, search the last element who has the same layer as removed_element's layer
                    # If it exists, change layer's pixmap with the found element's pixmap and mark
                    # the variable element_found as 1
                    element_found = False
                    for element in reversed(UNDO):
                        if element[0] == removed_element[0]:
                            element[0].setPixmapItem(QPixmap(element[1]))
                            element_found = True
                            break

                    # If element was not found, change the layer's pixmap with a transparent pixmap
                    if not element_found:
                        image = QtGui.QImage(self.canvas_width, self.canvas_height,
                                             QtGui.QImage.Format_ARGB32_Premultiplied)
                        image.fill(Qt.transparent)
                        SELECTED_LAYER.pixmap = QPixmap(image)
                        SELECTED_LAYER.setPixmapItem(SELECTED_LAYER.pixmap)

    def add_to_undoList(self, layer, pixmap):
        global UNDO, REDO
        if not UNDO:
            self.actionUndo.setEnabled(True)
            self.undoBtn.setEnabled(True)
            self.undoBtn.setStyleSheet("QToolButton{ background-color: rgb(99, 101, 135);}"
                                       "QToolButton:hover{background-color: rgb(82, 82, 124);}")

        UNDO.append([layer, QPixmap(pixmap)])

        REDO.clear()
        self.actionRedo.setDisabled(True)
        self.redoBtn.setDisabled(True)
        self.redoBtn.setStyleSheet("QToolButton{ background-color: rgb(57, 58, 65);}"
                                   "QToolButton:hover{background-color: rgb(82, 82, 124);}")
        self.actionUndo.setEnabled(True)
        self.undoBtn.setEnabled(True)
        self.undoBtn.setStyleSheet("QToolButton{ background-color: rgb(99, 101, 135);}"
                                   "QToolButton:hover{background-color: rgb(82, 82, 124);}")

    def redoActions(self):
        global REDO, UNDO, SELECTED_LAYER
        self.actionUndo.setEnabled(True)
        self.undoBtn.setEnabled(True)
        self.undoBtn.setStyleSheet("QToolButton{ background-color: rgb(99, 101, 135);}"
                                   "QToolButton:hover{background-color: rgb(82, 82, 124);}")

        if REDO:
            removed_element = REDO.pop()
            removed_element[1] = QPixmap(removed_element[1])
            UNDO.append(removed_element)

            redo_layer = removed_element[0]
            redo_pixmap = removed_element[1]

            if SELECTED_LAYER != redo_layer:
                SELECTED_LAYER.set_defaultBg()
                SELECTED_LAYER = redo_layer
                SELECTED_LAYER.set_activeBg()

            redo_layer.setPixmapItem(redo_pixmap)
            SELECTED_LAYER.pixmap = QPixmap(redo_pixmap)

            if not REDO:
                self.actionRedo.setDisabled(True)
                self.redoBtn.setDisabled(True)
                self.redoBtn.setStyleSheet("QToolButton{ background-color: rgb(57, 58, 65);}"
                                           "QToolButton:hover{background-color: rgb(82, 82, 124);}")

    """========================================
            Menu - Copy, Paste, Select All
                    Functions
    ========================================"""

    def copySelection(self):
        if self.select_active or self.area_selected:
            selection = SELECTED_LAYER.getPixmap().copy(self.selectionRect)

            # Add selection to clipboard
            clipboard = QApplication.clipboard()
            clipboard.setPixmap(selection)

    def pasteSelection(self):
        if self.CANVAS:
            self.addLayer_with_PastedSelection()

            clipboard = QApplication.clipboard()
            painter = QPainter(SELECTED_LAYER.pixmap)
            painter.drawPixmap(0, 0, clipboard.pixmap())

            SELECTED_LAYER.setPixmapItem(SELECTED_LAYER.pixmap)
            self.add_to_undoList(SELECTED_LAYER, SELECTED_LAYER.pixmap)
            self.deselectBtn_state()

            self.stackedWidget_settings.setCurrentIndex(0)
            self.stackedWidget_size.setCurrentIndex(0)

            self.view.viewport().setCursor(Qt.ArrowCursor)

    def select_all(self):
        if self.CANVAS:
            self.select_all_pixmap = QPixmap(QtGui.QImage(self.canvas_width, self.canvas_height,
                                                          QtGui.QImage.Format_ARGB32_Premultiplied))

            preview_pixmap = self.select_all_pixmap
            painter = QPainter(preview_pixmap)
            painter.drawPixmap(QPoint(), self.pixmap_selection)

            painter.setPen(QPen(Qt.black, 5, Qt.DashLine, Qt.RoundCap, Qt.RoundJoin))

            rect = QRectF(QPoint(0, 0), QPoint(self.canvas_width, self.canvas_height))
            self.selectionRect = rect.toRect()
            painter.drawRect(rect)

            self.item_selection.setPixmap(preview_pixmap)

            self.area_selected = True
            self.selectionMenu_enable()
            self.actionCopy.setEnabled(True)

            self.selectionRect_CanvasPixmap = SELECTED_LAYER.pixmap.copy(self.selectionRect)
            self.stackedWidget_settings.setCurrentIndex(3)
            self.stackedWidget_size.setCurrentIndex(3)

            self.toolbar_disable_activeState()
            self.toolbar_setDefaultBackground()

    """================================
            Menu - Disable/Enable
                Action Buttons
    ================================"""

    def enableActions_afterCanvasSet(self):
        # File Menu
        self.actionClose.setEnabled(True)
        self.actionSave.setEnabled(True)
        self.actionSave_as.setEnabled(True)
        # Edit Menu
        self.actionPaste.setEnabled(True)
        self.actionSelect_All.setEnabled(True)
        # Layer Menu
        self.actionAdd_Layer.setEnabled(True)
        self.actionDelete_Layer.setEnabled(True)
        self.actionErase_Layer.setEnabled(True)
        # View Menu
        self.actionZoom_In.setEnabled(True)
        self.actionZoom_Out.setEnabled(True)
        self.actionRotate_View_CW.setEnabled(True)
        self.actionRotate_View_CCW.setEnabled(True)
        self.actionFlip_Horizontally.setEnabled(True)
        self.actionFlip_Vertically.setEnabled(True)
        self.actionFit_In_View.setEnabled(True)
        self.actionReset_View.setEnabled(True)

    def disableActions_afterCanvasClose(self):
        # File Menu
        self.actionClose.setDisabled(True)
        self.actionSave.setDisabled(True)
        self.actionSave_as.setDisabled(True)
        # Edit Menu
        self.actionUndo.setDisabled(True)
        self.actionRedo.setDisabled(True)
        self.actionCopy.setDisabled(True)
        self.actionPaste.setDisabled(True)
        self.actionSelect_All.setDisabled(True)
        # Selection Menu
        self.actionDeselect.setDisabled(True)
        self.actionDelete_selectedArea.setDisabled(True)
        self.actionFill_Selected_Area.setDisabled(True)
        # Layer Menu
        self.actionAdd_Layer.setDisabled(True)
        self.actionDelete_Layer.setDisabled(True)
        self.actionErase_Layer.setDisabled(True)
        # View Menu
        self.actionZoom_In.setDisabled(True)
        self.actionZoom_Out.setDisabled(True)
        self.actionRotate_View_CW.setDisabled(True)
        self.actionRotate_View_CCW.setDisabled(True)
        self.actionFlip_Horizontally.setDisabled(True)
        self.actionFlip_Vertically.setDisabled(True)
        self.actionFit_In_View.setDisabled(True)
        self.actionReset_View.setDisabled(True)

    def enableActions_on_MoveSelection(self):
        # File Menu
        self.actionClose.setEnabled(True)
        self.actionSave.setEnabled(True)
        self.actionSave_as.setEnabled(True)
        # Edit Menu
        self.actionUndo.setEnabled(True)
        self.actionRedo.setEnabled(True)
        self.actionCopy.setEnabled(True)
        self.actionPaste.setEnabled(True)
        self.actionSelect_All.setEnabled(True)
        # Selection Menu
        self.actionDeselect.setEnabled(True)
        self.actionDelete_selectedArea.setEnabled(True)
        self.actionFill_Selected_Area.setEnabled(True)
        # Layer Menu
        self.actionAdd_Layer.setEnabled(True)
        self.actionDelete_Layer.setEnabled(True)
        self.actionErase_Layer.setEnabled(True)

    def disableActions_on_MoveSelection(self):
        # File Menu
        self.actionClose.setDisabled(True)
        self.actionSave.setDisabled(True)
        self.actionSave_as.setDisabled(True)
        # Edit Menu
        self.actionUndo.setDisabled(True)
        self.actionRedo.setDisabled(True)
        self.actionCopy.setDisabled(True)
        self.actionPaste.setDisabled(True)
        self.actionSelect_All.setDisabled(True)
        # Selection Menu
        self.actionDeselect.setDisabled(True)
        self.actionDelete_selectedArea.setDisabled(True)
        self.actionFill_Selected_Area.setDisabled(True)
        # Layer Menu
        self.actionAdd_Layer.setDisabled(True)
        self.actionDelete_Layer.setDisabled(True)
        self.actionErase_Layer.setDisabled(True)

    """================================
            Navigator Functions
    ================================"""

    def canvas_rotateLeft(self):
        value = int(self.rotateValue_comboBox.currentText()[:-1])
        self.view.rotate(-value)

    def canvas_rotateRight(self):
        value = int(self.rotateValue_comboBox.currentText()[:-1])
        self.view.rotate(value)

    def canvas_zoomIn(self):
        self.view.scale(self.zoomIn, self.zoomIn)

    def canvas_zoomOut(self):
        self.view.scale(self.zoomOut, self.zoomOut)

    def canvas_flipVertically(self):
        self.view.scale(1, -1)

    def canvas_flipHorizontally(self):
        self.view.scale(-1, 1)

    def canvas_fitInView(self):
        self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    def canvas_resetView(self):
        self.view.resetTransform()

        if self.scene.height() > self.view.height() or self.scene.width() > self.view.width():
            self.canvas_fitInView()

    def navigator_fitInView(self):
        self.view2.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    def navigator_disableButtons(self):
        self.rotateLeftBtn.setDisabled(True)
        self.rotateRightBtn.setDisabled(True)
        self.zoomInBtn.setDisabled(True)
        self.zoomOutBtn.setDisabled(True)
        self.flipVerticallyBtn.setDisabled(True)
        self.flipHorizontallyBtn.setDisabled(True)
        self.fitInViewBtn.setDisabled(True)
        self.resetViewBtn.setDisabled(True)

    def navigator_enableButtons(self):
        self.rotateLeftBtn.setDisabled(False)
        self.rotateRightBtn.setDisabled(False)
        self.zoomInBtn.setDisabled(False)
        self.zoomOutBtn.setDisabled(False)
        self.flipVerticallyBtn.setDisabled(False)
        self.flipHorizontallyBtn.setDisabled(False)
        self.fitInViewBtn.setDisabled(False)
        self.resetViewBtn.setDisabled(False)

    """================================
        Event filter - Painting and
        View Navigation Functions
    ================================"""

    def eventFilter(self, object, event):
        global SELECTED_LAYER
        if self.CANVAS:
            if object == self.view.viewport():
                # Blank image for shape tools
                self.layer_image = QtGui.QImage(self.canvas_width, self.canvas_height,
                                                QtGui.QImage.Format_ARGB32_Premultiplied)
                self.layer_image.fill(Qt.transparent)

                # Set cursor for brush and shape tools
                if self.pen_active or self.brush_active or self.eraser_active:
                    if event.type() == QtCore.QEvent.MouseMove:
                        position = SELECTED_LAYER.item.mapFromScene(self.view.mapToScene(event.pos()))
                        self.cursor_item.show()
                        self.cursor_item.setPos(position.x() - self.BRUSH_SIZE / 2, position.y() - self.BRUSH_SIZE / 2)
                    if event.type() == QtCore.QEvent.Leave:
                        self.cursor_item.hide()

                if self.line_active or self.square_active or self.ellipse_active:
                    if event.type() == QtCore.QEvent.MouseMove:
                        position = SELECTED_LAYER.item.mapFromScene(self.view.mapToScene(event.pos()))
                        self.cursor_item.show()
                        self.cursor_item.setPos(position.x() - self.SHAPE_SIZE / 2, position.y() - self.SHAPE_SIZE / 2)
                    if event.type() == QtCore.QEvent.Leave:
                        self.cursor_item.hide()

                # ---- Pen -----
                if self.pen_active:
                    if event.type() == QtCore.QEvent.MouseButtonPress:
                        position = SELECTED_LAYER.item.mapFromScene(self.view.mapToScene(event.pos()))
                        self.lastPoint = position
                        self.draw = True
                        return True

                    if event.type() == QtCore.QEvent.MouseMove and self.draw:
                        position = SELECTED_LAYER.item.mapFromScene(self.view.mapToScene(event.pos()))

                        pixmap = SELECTED_LAYER.getPixmap()
                        painter = QPainter(pixmap)
                        painter.setRenderHint(QPainter.HighQualityAntialiasing)
                        painter.setPen(QPen(self.firstColor, self.BRUSH_SIZE, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

                        # If the locked state is active, set the layer mask to the painter
                        if SELECTED_LAYER.locked:
                            painter.setClipRegion(QRegion(QBitmap(SELECTED_LAYER.mask)))

                        painter.drawLine(self.lastPoint, position)
                        painter.end()

                        self.lastPoint = position
                        self.update()

                        SELECTED_LAYER.setPixmapItem(pixmap)
                        return True

                    if event.type() == QtCore.QEvent.MouseButtonRelease:
                        self.draw = False

                        self.add_to_undoList(SELECTED_LAYER, SELECTED_LAYER.pixmap)
                        self.saved_state = False
                        return True

                # ---- Brush -----
                if self.brush_active:
                    if event.type() == QtCore.QEvent.MouseButtonPress:
                        position = SELECTED_LAYER.item.mapFromScene(self.view.mapToScene(event.pos()))
                        self.lastPoint = position
                        self.draw = True

                        # Reset Path
                        self.path = None
                        self.path = QPainterPath()
                        self.path.moveTo(position)
                        return True

                    if event.type() == QtCore.QEvent.MouseMove and self.draw:
                        position = SELECTED_LAYER.item.mapFromScene(self.view.mapToScene(event.pos()))

                        preview_pixmap = QPixmap(SELECTED_LAYER.pixmap)
                        painter = QPainter(preview_pixmap)
                        painter.setRenderHint(QPainter.HighQualityAntialiasing)
                        painter.setOpacity(self.DENSITY_VALUE * 0.01)

                        # If the locked state is active, set the layer mask to the painter
                        if SELECTED_LAYER.locked:
                            painter.setClipRegion(QRegion(QBitmap(SELECTED_LAYER.mask)))

                        painter.setPen(QPen(self.firstColor, self.BRUSH_SIZE, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                        self.path.lineTo(position)
                        painter.drawPath(self.path)
                        painter.end()

                        self.lastPoint = position
                        self.update()

                        SELECTED_LAYER.setPixmapItem(preview_pixmap)
                        return True

                    if event.type() == QtCore.QEvent.MouseButtonRelease:
                        self.draw = False

                        pixmap = SELECTED_LAYER.getPixmap()
                        painter = QPainter(pixmap)
                        painter.setRenderHint(QPainter.HighQualityAntialiasing)
                        painter.setOpacity(self.DENSITY_VALUE * 0.01)
                        painter.setPen(QPen(self.firstColor, self.BRUSH_SIZE, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

                        # If the locked state is active, set the layer mask to the painter
                        if SELECTED_LAYER.locked:
                            painter.setClipRegion(QRegion(QBitmap(SELECTED_LAYER.mask)))

                        painter.drawPath(self.path)
                        painter.end()

                        SELECTED_LAYER.setPixmapItem(pixmap)
                        self.add_to_undoList(SELECTED_LAYER, SELECTED_LAYER.pixmap)
                        self.saved_state = False
                        self.update()
                        return True

                # ---- Eraser -----
                if self.eraser_active:
                    if event.type() == QtCore.QEvent.MouseButtonPress:
                        position = SELECTED_LAYER.item.mapFromScene(self.view.mapToScene(event.pos()))
                        self.lastPoint = position
                        self.draw = True
                        return True

                    if event.type() == QtCore.QEvent.MouseMove and self.draw:
                        position = SELECTED_LAYER.item.mapFromScene(self.view.mapToScene(event.pos()))

                        pixmap = SELECTED_LAYER.getPixmap()
                        painter = QPainter(pixmap)
                        painter.setRenderHint(QPainter.HighQualityAntialiasing)
                        painter.setCompositionMode(QPainter.CompositionMode_Clear)

                        # If the locket state is active, set the layer mask to the painter
                        if SELECTED_LAYER.locked:
                            painter.setClipRegion(QRegion(QBitmap(SELECTED_LAYER.mask)))

                        painter.setPen(QPen(Qt.black, self.BRUSH_SIZE, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                        painter.drawLine(self.lastPoint, position)
                        painter.end()

                        self.lastPoint = position
                        self.update()

                        SELECTED_LAYER.setPixmapItem(pixmap)

                        return True

                    if event.type() == QtCore.QEvent.MouseButtonRelease:
                        self.draw = False
                        self.add_to_undoList(SELECTED_LAYER, SELECTED_LAYER.pixmap)
                        self.saved_state = False
                        return True

                # ---- Bucket ----
                if self.bucket_active:
                    if event.type() == QtCore.QEvent.MouseButtonPress:
                        mouse_position = SELECTED_LAYER.item.mapFromScene(self.view.mapToScene(event.pos()))

                        image = QtGui.QImage(self.canvas_width, self.canvas_height,
                                             QtGui.QImage.Format_ARGB32_Premultiplied)

                        painter = QPainter(image)
                        self.scene.render(painter, QRectF(), QRectF(image.rect()))
                        painter.end()

                        w, h = image.width(), image.height()
                        x, y = int(mouse_position.x()), int(mouse_position.y())

                        color = image.pixel(x, y)

                        pixels_visited = set()
                        queue = [(x, y)]

                        # Get neighbours coords
                        def get_neighbours(pixels_visited, pixel_pos):
                            neighbours = []
                            current_X, current_Y = pixel_pos
                            for x, y in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
                                neighbour_X = current_X + x
                                neighbour_Y = current_Y + y
                                if 0 <= neighbour_X < w and \
                                        0 <= neighbour_Y < h and \
                                        (neighbour_X, neighbour_Y) not in pixels_visited:
                                    neighbours.append((neighbour_X, neighbour_Y))
                                    pixels_visited.add((neighbour_X, neighbour_Y))

                            return neighbours

                        # Search and fill the pixels
                        painter = QPainter(SELECTED_LAYER.pixmap)
                        painter.setRenderHint(QPainter.HighQualityAntialiasing)
                        painter.setPen(QPen(self.firstColor))

                        # If the locked state is active, set the layer mask to the painter
                        if SELECTED_LAYER.locked:
                            region = QRegion(QBitmap(SELECTED_LAYER.mask))
                            painter.setClipRegion(region)

                            # Fill selection only if the mouse coords are in the bounds of clipped mask
                            if region.contains(QPoint(x,y)):
                                while queue:
                                    x, y = queue.pop()
                                    if image.pixel(x, y) == color:
                                        painter.drawPoint(QPoint(x, y))
                                        queue.extend(get_neighbours(pixels_visited, (x, y)))

                                painter.end()
                                SELECTED_LAYER.setPixmapItem(SELECTED_LAYER.pixmap)
                                self.add_to_undoList(SELECTED_LAYER, SELECTED_LAYER.pixmap)
                                self.saved_state = False
                                self.view.viewport().update()
                        else:
                            while queue:
                                x, y = queue.pop()
                                if image.pixel(x, y) == color:
                                    painter.drawPoint(QPoint(x, y))
                                    queue.extend(get_neighbours(pixels_visited, (x, y)))

                            painter.end()
                            SELECTED_LAYER.setPixmapItem(SELECTED_LAYER.pixmap)
                            self.add_to_undoList(SELECTED_LAYER, SELECTED_LAYER.pixmap)
                            self.saved_state = False
                            self.view.viewport().update()

                # ---- Text ----
                if self.text_active:
                    if event.type() == QtCore.QEvent.MouseButtonPress:
                        self.text_pos = SELECTED_LAYER.item.mapFromScene(self.view.mapToScene(event.pos()))

                        painter = QPainter(SELECTED_LAYER.pixmap)
                        painter.setRenderHint(QPainter.HighQualityAntialiasing)

                        size = int(self.fontSize_comboBox.currentText())
                        font_name = self.fontName_comboBox.currentText()
                        font = QFont(font_name, size)

                        if self.bold:
                            font.setBold(True)
                        if self.italic:
                            font.setItalic(True)
                        if self.underline:
                            font.setUnderline(True)

                        painter.setFont(font)
                        painter.setPen(QColor(self.firstColor))
                        painter.drawText(self.text_pos, self.text)
                        painter.end()

                        SELECTED_LAYER.setPixmapItem(SELECTED_LAYER.pixmap)
                        self.add_to_undoList(SELECTED_LAYER, SELECTED_LAYER.pixmap)
                        self.saved_state = False
                        self.view.viewport().update()

                    if event.type() == QtCore.QEvent.MouseMove and self.text != "":
                        self.text_pos = SELECTED_LAYER.item.mapFromScene(self.view.mapToScene(event.pos()))

                        preview_pixmap = QPixmap(self.layer_image)
                        painter = QPainter(preview_pixmap)
                        painter.drawPixmap(QPoint(), SELECTED_LAYER.pixmap)

                        size = int(self.fontSize_comboBox.currentText())
                        font_name = self.fontName_comboBox.currentText()
                        font = QFont(font_name, size)

                        if self.bold:
                            font.setBold(True)
                        if self.italic:
                            font.setItalic(True)
                        if self.underline:
                            font.setUnderline(True)

                        painter.setFont(font)
                        painter.setPen(QColor(self.firstColor))
                        painter.drawText(self.text_pos, self.text)
                        painter.end()

                        SELECTED_LAYER.setPixmapItem(preview_pixmap)

                    if event.type() == QtCore.QEvent.Leave:
                        SELECTED_LAYER.setPixmapItem(SELECTED_LAYER.pixmap)

                # ---- Picker ----
                if self.picker_active:
                    if event.type() == QtCore.QEvent.MouseButtonPress:
                        view_pixmap = self.view.grab(self.view.sceneRect().toRect())
                        color = view_pixmap.toImage().pixel(event.pos())
                        hex = QColor(color).name()

                        if event.button() == Qt.LeftButton:
                            self.firstColor_label.setStyleSheet(f"background-color: {hex}")
                            self.firstColor = self.hex_to_rgb(hex[1:])
                            self.setHex(hex[1:])
                            self.setRGB(self.hex_to_rgb(hex[1:]))
                            self.setHSV(self.hex_to_hsv(hex[1:]))

                # ---- Square ----
                if self.square_active:
                    if event.type() == QtCore.QEvent.MouseButtonPress:
                        position = SELECTED_LAYER.item.mapFromScene(self.view.mapToScene(event.pos()))
                        self.start_point = position
                        self.end_point = self.start_point
                        self.draw = True
                        return True

                    if event.type() == QtCore.QEvent.MouseMove and self.draw:
                        position = SELECTED_LAYER.item.mapFromScene(self.view.mapToScene(event.pos()))
                        self.end_point = position

                        # Set the painter to draw on a copy of the layer’s pixmap
                        preview_pixmap = QPixmap(self.layer_image)
                        painter = QPainter(preview_pixmap)
                        painter.setRenderHint(QPainter.HighQualityAntialiasing)
                        painter.drawPixmap(QPoint(), SELECTED_LAYER.pixmap)

                        # If the locked state is active, set the layer mask to the painter
                        if SELECTED_LAYER.locked:
                            painter.setClipRegion(QRegion(QBitmap(SELECTED_LAYER.mask)))

                        if self.shapeFill_comboBox.currentText() == "Solid":
                            painter.setBrush(QBrush(QColor(self.secondColor), Qt.SolidPattern))

                        painter.setPen(
                            QPen(QColor(self.firstColor), self.SHAPE_SIZE, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                        rect = QRectF(self.start_point, self.end_point)
                        painter.drawRect(rect)
                        painter.end()

                        SELECTED_LAYER.setPixmapItem(preview_pixmap)
                        return True

                    if event.type() == QtCore.QEvent.MouseButtonRelease:
                        painter = QPainter(SELECTED_LAYER.pixmap)
                        painter.setRenderHint(QPainter.HighQualityAntialiasing)
                        painter.setPen(
                            QPen(QColor(self.firstColor), self.SHAPE_SIZE, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

                        if self.shapeFill_comboBox.currentText() == "Solid":
                            painter.setBrush(QBrush(QColor(self.secondColor), Qt.SolidPattern))

                        # If the locked state is active, set the layer mask to the painter
                        if SELECTED_LAYER.locked:
                            painter.setClipRegion(QRegion(QBitmap(SELECTED_LAYER.mask)))

                        rect = QRectF(self.start_point, self.end_point)
                        painter.drawRect(rect)
                        painter.end()

                        SELECTED_LAYER.setPixmapItem(SELECTED_LAYER.pixmap)
                        self.add_to_undoList(SELECTED_LAYER, SELECTED_LAYER.pixmap)
                        self.saved_state = False
                        self.view.viewport().update()
                        self.draw = False
                        return True

                # ---- Ellipse ----
                if self.ellipse_active:
                    if event.type() == QtCore.QEvent.MouseButtonPress:
                        position = SELECTED_LAYER.item.mapFromScene(self.view.mapToScene(event.pos()))
                        self.start_point = position
                        self.end_point = self.start_point
                        self.draw = True
                        return True

                    if event.type() == QtCore.QEvent.MouseMove and self.draw:
                        position = SELECTED_LAYER.item.mapFromScene(self.view.mapToScene(event.pos()))
                        self.end_point = position

                        # Set the painter to draw on a copy of the layer’s pixmap
                        preview_pixmap = QPixmap(self.layer_image)
                        painter = QPainter(preview_pixmap)
                        painter.setRenderHint(QPainter.HighQualityAntialiasing)
                        painter.drawPixmap(QPoint(), SELECTED_LAYER.pixmap)

                        # If the locked state is active, set the layer mask to the painter
                        if SELECTED_LAYER.locked:
                            painter.setClipRegion(QRegion(QBitmap(SELECTED_LAYER.mask)))

                        if self.shapeFill_comboBox.currentText() == "Solid":
                            painter.setBrush(QBrush(QColor(self.secondColor), Qt.SolidPattern))

                        painter.setPen(
                            QPen(QColor(self.firstColor), self.SHAPE_SIZE, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                        rect = QRectF(self.start_point, self.end_point)
                        painter.drawEllipse(rect)
                        painter.end()

                        SELECTED_LAYER.setPixmapItem(preview_pixmap)
                        return True

                    if event.type() == QtCore.QEvent.MouseButtonRelease:
                        painter = QPainter(SELECTED_LAYER.pixmap)
                        painter.setRenderHint(QPainter.HighQualityAntialiasing)
                        painter.setPen(
                            QPen(QColor(self.firstColor), self.SHAPE_SIZE, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

                        # If the locked state is active, set the layer mask to the painter
                        if SELECTED_LAYER.locked:
                            painter.setClipRegion(QRegion(QBitmap(SELECTED_LAYER.mask)))

                        if self.shapeFill_comboBox.currentText() == "Solid":
                            painter.setBrush(QBrush(QColor(self.secondColor), Qt.SolidPattern))

                        rect = QRectF(self.start_point, self.end_point)
                        painter.drawEllipse(rect)
                        painter.end()

                        SELECTED_LAYER.setPixmapItem(SELECTED_LAYER.pixmap)
                        self.add_to_undoList(SELECTED_LAYER, SELECTED_LAYER.pixmap)
                        self.saved_state = False
                        self.view.viewport().update()
                        self.draw = False
                        return True

                # ---- Line ----
                if self.line_active:
                    if event.type() == QtCore.QEvent.MouseButtonPress:
                        position = SELECTED_LAYER.item.mapFromScene(self.view.mapToScene(event.pos()))
                        self.start_point = position
                        self.end_point = self.start_point
                        self.draw = True
                        return True

                    # Set the painter to draw on a copy of the layer’s pixmap
                    if event.type() == QtCore.QEvent.MouseMove and self.draw:
                        position = SELECTED_LAYER.item.mapFromScene(self.view.mapToScene(event.pos()))
                        self.end_point = position

                        preview_pixmap = QPixmap(self.layer_image)
                        painter = QPainter(preview_pixmap)
                        painter.setRenderHint(QPainter.HighQualityAntialiasing)
                        painter.drawPixmap(QPoint(), SELECTED_LAYER.pixmap)

                        # If the locked state is active, set the layer mask to the painter
                        if SELECTED_LAYER.locked:
                            painter.setClipRegion(QRegion(QBitmap(SELECTED_LAYER.mask)))

                        painter.setPen(
                            QPen(QColor(self.firstColor), self.SHAPE_SIZE, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                        painter.drawLine(self.start_point, self.end_point)
                        painter.end()

                        SELECTED_LAYER.setPixmapItem(preview_pixmap)
                        return True

                    if event.type() == QtCore.QEvent.MouseButtonRelease:
                        painter = QPainter(SELECTED_LAYER.pixmap)
                        painter.setRenderHint(QPainter.HighQualityAntialiasing)
                        painter.setPen(
                            QPen(QColor(self.firstColor), self.SHAPE_SIZE, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

                        # If the locked state is active, set the layer mask to the painter
                        if SELECTED_LAYER.locked:
                            painter.setClipRegion(QRegion(QBitmap(SELECTED_LAYER.mask)))

                        painter.drawLine(self.start_point, self.end_point)
                        painter.end()

                        SELECTED_LAYER.setPixmapItem(SELECTED_LAYER.pixmap)
                        self.add_to_undoList(SELECTED_LAYER, SELECTED_LAYER.pixmap)
                        self.saved_state = False
                        self.view.viewport().update()
                        self.draw = False
                        return True

                # ---- Select and Move Selection ----
                if self.select_active:
                    if event.type() == QtCore.QEvent.MouseButtonPress:

                        """ Select - ButtonPress """
                        if not self.move_active:
                            position = SELECTED_LAYER.item.mapFromScene(self.view.mapToScene(event.pos()))
                            self.start_point = position
                            self.end_point = self.start_point
                            self.draw = True
                            self.area_selected = False

                            # Clear selection on right click
                            self.before_select_pixmap = self.pixmap_selection
                            self.item_selection.setPixmap(self.before_select_pixmap)

                            self.moveSelection_start = False

                            if self.selection_flipped and not self.move_selectionSet:
                                self.selection_setPixmapAfterMove_or_Flip()
                                self.selection_flipped = False

                            # If the user moved the selection then clicked out of it
                            # update the layer's pixmap with the pixmap after selection move action
                            if self.move_selectionSet:
                                self.selection_setPixmapAfterMove_or_Flip()
                                self.move_selectionSet = False

                            # Enable flip functions
                            self.flipVBtn.setEnabled(True)
                            self.flipHBtn.setEnabled(True)

                            self.tools_enableButtons()
                            self.toolbar_enableButtons()
                            self.layers_enableButtons()
                            self.layers_enable()

                            self.enableActions_on_MoveSelection()

                            self.undoBtn.setEnabled(True)
                            self.redoBtn.setEnabled(True)
                            return True
                        else:
                            """ Move Selection - ButtonPress """
                            position = SELECTED_LAYER.item.mapFromScene(self.view.mapToScene(event.pos()))
                            self.start_point = position

                            # No flip while moving selection
                            self.flipVBtn.setDisabled(True)
                            self.flipHBtn.setDisabled(True)

                            if not self.moveSelection_start:
                                # Delete selected area
                                x, y, w, h = self.selectionRect.getRect()

                                pixmap = SELECTED_LAYER.pixmap
                                painter = QPainter(pixmap)
                                painter.setCompositionMode(QPainter.CompositionMode_Clear)
                                painter.setRenderHint(QPainter.HighQualityAntialiasing)
                                painter.setPen(QPen(Qt.black))
                                painter.setBrush(QBrush(Qt.black))
                                painter.drawRect(x, y, w, h)

                                self.moveSelection_start = True

                            self.move = True

                            # Disable tools
                            self.tools_disableButtons()
                            self.layers_disableButtons()
                            self.layers_disable()
                            self.toolbar_disableButtons()

                            self.disableActions_on_MoveSelection()

                            self.undoBtn.setDisabled(True)
                            self.redoBtn.setDisabled(True)
                            return True

                    if event.type() == QtCore.QEvent.MouseMove:

                        """ Select - MouseMove """
                        if not self.move_active and self.draw:
                            position = SELECTED_LAYER.item.mapFromScene(self.view.mapToScene(event.pos()))
                            self.end_point = position

                            preview_pixmap = QPixmap(self.layer_image)
                            painter = QPainter(preview_pixmap)
                            painter.setRenderHint(QPainter.HighQualityAntialiasing, True)

                            # Set Pen size depending on the Canvas size
                            if self.canvas_height >= 2000 or self.canvas_width >= 2000:
                                painter.setPen(QPen(Qt.black, 5, Qt.DashLine, Qt.RoundCap, Qt.RoundJoin))
                            elif self.canvas_height <= 500 or self.canvas_width <= 500:
                                painter.setPen(QPen(Qt.black, 1, Qt.DashLine, Qt.RoundCap, Qt.RoundJoin))
                            else:
                                painter.setPen(QPen(Qt.black, 2, Qt.DashLine, Qt.RoundCap, Qt.RoundJoin))

                            rect = QRectF(self.start_point, self.end_point)
                            self.selectionRect = rect.toRect()
                            painter.drawRect(rect)

                            self.item_selection.setPixmap(preview_pixmap)
                            self.area_selected = False
                            return True

                        elif self.move_active and self.move:
                            """ Move Selection - MouseMove """
                            # Get mouse position
                            position = SELECTED_LAYER.item.mapFromScene(self.view.mapToScene(event.pos()))
                            x = int(position.x())
                            y = int(position.y())
                            selection_width = int(self.selectionRect_CanvasPixmap.width())
                            selection_height = int(self.selectionRect_CanvasPixmap.height())

                            # Draw selection on mouse position
                            preview_pixmap = QPixmap(self.layer_image)
                            painter = QPainter(preview_pixmap)
                            painter.drawPixmap(QPoint(), SELECTED_LAYER.pixmap)
                            painter.setRenderHint(QPainter.HighQualityAntialiasing, True)

                            # Draw center of pixmap at mouse position
                            painter.drawPixmap(x - int(selection_width / 2), y - int(selection_height / 2),
                                               self.selectionRect_CanvasPixmap)

                            # Change selection rectangle position
                            preview_pixmap2 = QPixmap(self.layer_image)
                            painter = QPainter(preview_pixmap2)
                            painter.drawPixmap(QPoint(), preview_pixmap2)

                            painter.drawPixmap(x - int(selection_width / 2), y - int(selection_height / 2),
                                               self.selectionRect_Pixmap)

                            SELECTED_LAYER.setPixmapItem(preview_pixmap)
                            self.item_selection.setPixmap(preview_pixmap2)
                            return True

                        """ Default - MouseMove """
                        if self.selectionRect is not None:
                            position = SELECTED_LAYER.item.mapFromScene(self.view.mapToScene(event.pos()))
                            x = int(position.x())
                            y = int(position.y())

                            # If mouse in selection, enable move selection option
                            if self.selectionRect.contains(x, y):
                                self.view.viewport().setCursor(QCursor(Qt.SizeAllCursor))
                                self.move_active = True
                            else:
                                self.view.viewport().setCursor(QCursor(Qt.ArrowCursor))
                                self.move_active = False

                    if event.type() == QtCore.QEvent.MouseButtonRelease:

                        """ Select - Mouse Release """
                        if not self.move_active:
                            self.before_select_pixmap = self.item_selection.pixmap()

                            if self.start_point != self.end_point:
                                # Selection is made and can be copied
                                self.actionCopy.setEnabled(True)
                                self.area_selected = True
                                self.actionDeselect.setEnabled(True)
                                self.actionFill_Selected_Area.setEnabled(True)
                                self.actionDelete_selectedArea.setEnabled(True)

                                # If current selectionRect has negative values for width and height
                                # make them positive
                                if self.selectionRect.width() < 0 and self.selectionRect.height() < 0:
                                    x = int(self.end_point.x())
                                    y = int(self.end_point.y())
                                    self.selectionRect = QRect(x, y, -self.selectionRect.width(),
                                                               -self.selectionRect.height())

                                if self.selectionRect.width() < 0:
                                    self.selectionRect = QRect(int(self.end_point.x()), int(self.start_point.y()),
                                                               -self.selectionRect.width(), self.selectionRect.height())

                                if self.selectionRect.height() < 0:
                                    self.selectionRect = QRect(int(self.start_point.x()), int(self.end_point.y()),
                                                               self.selectionRect.width(), -self.selectionRect.height())

                                # Save canvas selection
                                self.selectionRect_Pixmap = self.item_selection.pixmap().copy(self.selectionRect)
                                self.selectionRect_CanvasPixmap = SELECTED_LAYER.pixmap.copy(self.selectionRect)
                            else:
                                # No slection made, disable copy action from menu
                                self.actionCopy.setDisabled(True)
                                self.actionDeselect.setDisabled(True)
                                self.actionFill_Selected_Area.setDisabled(True)
                                self.actionDelete_selectedArea.setDisabled(True)
                                self.selectionRect = None

                            self.view.viewport().update()
                            self.draw = False
                            return True

                        else:
                            """ Move Selection - Mouse Release """
                            position = SELECTED_LAYER.item.mapFromScene(self.view.mapToScene(event.pos()))
                            x = int(position.x())
                            y = int(position.y())
                            selection_width = self.selectionRect.width()
                            selection_height = self.selectionRect.height()

                            preview_pixmap = QPixmap(self.layer_image)
                            painter = QPainter(preview_pixmap)
                            painter.drawPixmap(QPoint(), SELECTED_LAYER.pixmap)
                            painter.drawPixmap(x - int(selection_width / 2), y - int(selection_height / 2),
                                               self.selectionRect_CanvasPixmap)

                            self.selectionRect = QRect(x - int(selection_width / 2), y - int(selection_height / 2),
                                                       selection_width, selection_height)

                            SELECTED_LAYER.setPixmapItem(preview_pixmap)

                            # Mark the move selection action as finished
                            # This will be added to the layer's pixmap after the user clicks out of bounds
                            # of the selection
                            self.move_selectionSet = True

                            self.view.viewport().update()
                            self.move = False
                            return True

                # ---- Free Select ----
                if self.freeSelect_active:
                    if event.type() == QtCore.QEvent.MouseButtonPress:
                        position = SELECTED_LAYER.item.mapFromScene(self.view.mapToScene(event.pos()))
                        self.start_point = position
                        self.end_point = self.start_point
                        self.draw = True
                        self.area_freeSelected = False

                        # Reset Selection Path
                        self.selectionPath = None
                        self.selectionPath = QPainterPath()
                        self.selectionPath.moveTo(position)

                        # Clear selection
                        self.before_select_pixmap = self.pixmap_selection
                        self.item_selection.setPixmap(self.before_select_pixmap)
                        return True

                    if event.type() == QtCore.QEvent.MouseMove and self.draw:
                        position = SELECTED_LAYER.item.mapFromScene(self.view.mapToScene(event.pos()))
                        self.end_point = position

                        preview_pixmap = QPixmap(self.layer_image)
                        painter = QPainter(preview_pixmap)
                        painter.drawPixmap(QPoint(), self.pixmap_selection)
                        painter.setRenderHint(QPainter.HighQualityAntialiasing, True)

                        if self.canvas_height >= 2000 or self.canvas_width >= 2000:
                            painter.setPen(QPen(Qt.black, 5, Qt.DashLine, Qt.RoundCap, Qt.RoundJoin))
                        elif self.canvas_height <= 500 or self.canvas_width <= 500:
                            painter.setPen(QPen(Qt.black, 1, Qt.DashLine, Qt.RoundCap, Qt.RoundJoin))
                        else:
                            painter.setPen(QPen(Qt.black, 2, Qt.DashLine, Qt.RoundCap, Qt.RoundJoin))

                        self.selectionPath.lineTo(position)
                        painter.drawPath(self.selectionPath)

                        self.lastPoint = position
                        self.update()

                        self.item_selection.setPixmap(preview_pixmap)
                        self.area_freeSelected = False
                        return True

                    if event.type() == QtCore.QEvent.MouseButtonRelease:
                        self.before_select_pixmap = self.item_selection.pixmap()

                        preview_pixmap = QPixmap(self.layer_image)
                        painter = QPainter(preview_pixmap)
                        painter.drawPixmap(QPoint(), self.pixmap_selection)
                        painter.setRenderHint(QPainter.HighQualityAntialiasing, True)

                        if self.canvas_height >= 2000 or self.canvas_width >= 2000:
                            painter.setPen(QPen(Qt.black, 5, Qt.DashLine, Qt.RoundCap, Qt.RoundJoin))
                        elif self.canvas_height <= 500 or self.canvas_width <= 500:
                            painter.setPen(QPen(Qt.black, 1, Qt.DashLine, Qt.RoundCap, Qt.RoundJoin))
                        else:
                            painter.setPen(QPen(Qt.black, 2, Qt.DashLine, Qt.RoundCap, Qt.RoundJoin))

                        # Connect the last point to the start point
                        if self.start_point != self.end_point:
                            painter.drawLine(self.end_point, self.start_point)
                            self.area_freeSelected = True

                            self.actionDeselect.setEnabled(True)
                            self.actionFill_Selected_Area.setEnabled(True)
                            self.actionDelete_selectedArea.setEnabled(True)
                        else:
                            self.actionDeselect.setDisabled(True)
                            self.actionFill_Selected_Area.setDisabled(True)
                            self.actionDelete_selectedArea.setDisabled(True)

                        painter.drawPath(self.selectionPath)

                        self.item_selection.setPixmap(preview_pixmap)
                        self.view.viewport().update()
                        self.draw = False
                        return True

                # ---- View Zoom with Mouse Wheel Event ----
                if event.type() == QtCore.QEvent.Wheel:
                    if event.angleDelta().y() > 0:
                        zoom = self.zoomIn
                    else:
                        zoom = self.zoomOut

                    self.view.scale(zoom, zoom)
                    return True

                # ---- View Drag Event ----
                if event.type() == QtCore.QEvent.MouseButtonPress and self.drag_active:
                    self.view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
                    pressEvent = QMouseEvent(QEvent.GraphicsSceneMousePress, event.pos(), Qt.MouseButton.LeftButton,
                                             Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier)
                    self.view.mousePressEvent(pressEvent)
                    return True

                if event.type() == QtCore.QEvent.MouseButtonRelease and self.drag_active:
                    self.view.setDragMode(QGraphicsView.DragMode.NoDrag)

        return super().eventFilter(object, event)


"""================================
            Layer Class
================================"""


class Layer(QtWidgets.QFrame):
    def __init__(self, layer_number, canvas_width, canvas_height, scene, selectedPixmap=None):
        super().__init__()
        uic.loadUi('ui_files/LayerFrame.ui', self)

        self.frame = self.findChild(QFrame, "layer")
        self.hideBtn = self.findChild(QToolButton, "hideBtn")
        self.hideBtn.clicked.connect(self.hideLayer)
        self.visible = True

        self.label_layerName = self.findChild(QLabel, "layerName")
        self.lockIconBtn = self.findChild(QToolButton, "lockIconBtn")
        self.locked = False
        self.mask = None

        # ---- Default Settings ----

        # Create a transparent image
        self.image = QtGui.QImage(canvas_width, canvas_height, QtGui.QImage.Format_ARGB32_Premultiplied)
        self.image.fill(Qt.transparent)

        # If a pixmap is specified, add the pixmap to the layer’s pixmap
        # else add the transparent pixmap
        if selectedPixmap is not None:
            self.pixmap = QPixmap(self.image)
            painter = QPainter(self.pixmap)
            painter.drawPixmap(QPoint(), selectedPixmap)
        else:
            self.pixmap = QPixmap(self.image)

        # Add the pixmap to the scene
        self.item = scene.addPixmap(self.pixmap)
        self.item.setPixmap(self.pixmap)
        self.item.setZValue(layer_number)

        self.label_layerName.setText("Layer" + str(layer_number))
        self.layerName = self.label_layerName.text()
        self.layerNumber = layer_number

    def hideLayer(self):
        if self.visible:
            self.item.hide()
            self.visible = False
            self.hideBtn.setToolButtonStyle(Qt.ToolButtonTextOnly)
        else:
            self.item.show()
            self.visible = True
            self.hideBtn.setToolButtonStyle(Qt.ToolButtonIconOnly)

    def getPixmap(self):
        return self.pixmap

    def setPixmapItem(self, pixmap):
        self.item.setPixmap(pixmap)

    def getLayerNumber(self):
        return self.layerNumber

    def mousePressEvent(self, event):
        global SELECTED_LAYER
        if event.button() == Qt.LeftButton:
            if SELECTED_LAYER != self:
                self.set_activeBg()

                if SELECTED_LAYER is not None:
                    SELECTED_LAYER.set_defaultBg()

                SELECTED_LAYER = self.findLayer(self.getLayerNumber())

    def mouseDoubleClickEvent(self, event):
        self.layerName_window = LayerNameWindow(self.layerName)
        self.layerName_window.show()
        self.layerName_window.okBtn.clicked.connect(self.changeLayerName)
        self.layerName_window.cancelBtn.clicked.connect(self.closeLayerNameWindow)

    def changeLayerName(self):
        if self.layerName_window.getName() != "":
            self.layerName = self.layerName_window.getName()
            self.label_layerName.setText(self.layerName)

        self.layerName_window.close()

    def closeLayerNameWindow(self):
        self.layerName_window.close()

    def set_activeBg(self):
        self.setStyleSheet("QFrame, QToolButton{ background-color: rgb(99, 101, 135);} "
                           "QFrame:hover{ border: 1px solid rgb(152, 152, 208);}")

    def set_defaultBg(self):
        self.setStyleSheet("QFrame, QToolButton{ background-color: rgb(57, 58, 66);}"
                           "QFrame:hover{ border: 1px solid rgb(152, 152, 208);}")

    def findLayer(self, layer_number):
        global LAYERS
        for layer in LAYERS:
            if layer.getLayerNumber() == layer_number:
                return layer

    def findLayerPosition(self, layer_number):
        global LAYERS

        for i in range(0, len(LAYERS)):
            if LAYERS[i].getLayerNumber() == layer_number:
                return i

    def eraseLayer(self):
        self.pixmap = QPixmap(self.image)
        self.setPixmapItem(self.pixmap)

    def changeZValue(self, value):
        self.item.setZValue(value)

    def getZValue(self):
        return self.item.zValue()

    def updateLayerMask(self):
        image = self.pixmap.toImage()
        self.mask = self.pixmap.fromImage(image.createAlphaMask())

    def setLockIcon(self):
        self.lockIconBtn.setIcon(QIcon("icons/lock.png"))

    def removeLockIcon(self):
        self.lockIconBtn.setIcon(QIcon())


"""================================
       LayerNameWindow Class
================================"""


class LayerNameWindow(QtWidgets.QMainWindow):
    def __init__(self, layer_name):
        super().__init__()

        uic.loadUi('ui_files/LayerNameWindow.ui', self)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        self.default_name = layer_name

        # Icon
        self.icon = QPixmap("icons/pen_window.png")
        self.setWindowIcon(QIcon(self.icon))

        self.nameEdit = self.findChild(QLineEdit, "layerNameValue")
        self.nameEdit.setPlaceholderText(self.default_name)

        self.okBtn = self.findChild(QPushButton, "okBtn")
        self.okBtn.setShortcut("Return")
        self.cancelBtn = self.findChild(QPushButton, "cancelBtn")

    def getName(self):
        if self.nameEdit.text() == "":
            return self.default_name
        else:
            return self.nameEdit.text()


"""================================
       NewCanvasWindow Class
================================"""


class NewCanvasWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(NewCanvasWindow, self).__init__(parent)

        uic.loadUi('ui_files/NewCanvasWindow.ui', self)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        # Icon
        self.icon = QPixmap("icons/settings.png")
        self.setWindowIcon(QIcon(self.icon))

        self.nameEdit = self.findChild(QLineEdit, "canvasNameValue")
        self.widthEdit = self.findChild(QLineEdit, "widthValue")
        self.heightEdit = self.findChild(QLineEdit, "heightValue")
        self.widthEdit.setValidator(QIntValidator())
        self.heightEdit.setValidator(QIntValidator())

        self.okBtn = self.findChild(QPushButton, "okBtn")
        self.okBtn.setShortcut("Return")
        self.cancelBtn = self.findChild(QPushButton, "cancelBtn")
        self.pixelsValue = self.findChild(QLabel, "pixelsValue")

        self.widthEdit.textChanged.connect(self.widthChange)
        self.heightEdit.textChanged.connect(self.heightChange)

        self.width = "1200"
        self.height = "900"

    def widthChange(self):
        self.width = self.widthEdit.text()

        if self.width == "" or self.width == "-":
            self.width = "1200"
            self.widthEdit.setText("")
        elif int(self.width) > 3000:
            self.width = "3000"
            self.widthEdit.setText("3000")

        self.sizeChange()

    def heightChange(self):
        self.height = self.heightEdit.text()

        if self.height == "" or self.width == "-":
            self.height = "900"
            self.widthEdit.setText("")
        elif int(self.height) > 3000:
            self.height = "3000"
            self.heightEdit.setText("3000")
        self.sizeChange()

    def sizeChange(self):
        self.pixelsValue.setText(self.width + " x " + self.height)

    def getName(self):
        if self.nameEdit.text() == "":
            return "NewCanvas"
        else:
            return self.nameEdit.text()

    def getWidth(self):
        return self.width

    def getHeight(self):
        return self.height


"""================================
       CloseWindow Class
================================"""

class CloseWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(CloseWindow, self).__init__(parent)

        uic.loadUi('ui_files/CloseWindow.ui', self)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        # Icon
        self.icon = QPixmap("icons/settings.png")
        self.setWindowIcon(QIcon(self.icon))

        self.yesBtn = self.findChild(QPushButton, "yesBtn")
        self.noBtn = self.findChild(QPushButton, "noBtn")
        self.cancelBtn = self.findChild(QPushButton, "cancelBtn")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec_())
