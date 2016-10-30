from blizzardui.pyqt.QtGui import QWidget, QDesktopWidget 
from blizzardui.pyqt.QtCore import Qt, QEvent

class Chatroom(QWidget):
    minSize = (300, 300) # width, height
    def __init__(self):
        super(QWidget, self).__init__()
        self._init_window()
        self._init_components()
    def _init_window(self):
        ''' set basic settings of window '''
        # set size and margins
        self.resize(500, 600)
        self.setContentsMargins(0, 0, 0, 0)
        # locate in center
        size = self.geometry()
        screen = QDesktopWidget().screenGeometry()
        self.move((screen.width() - size.width())/2, (screen.height() - size.height())/2)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setMouseTracking(True)
    def _init_components(self):
        ''' load components of widget '''
        pass
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.startFrameGeometry = self.frameGeometry()
            self.startPosition =  event.globalPos()
            self.startResizeMask = self._determine_position(event)
            event.accept()
    def mouseMoveEvent(self, event):
        ''' track mouse whether it's pressed or not
         * close track by deleting this in _init_window: self.setMouseTracking(True)
         * determine is pressed mode is on first
        '''
        if event.buttons() == Qt.LeftButton:
            if 0 < self.startResizeMask:
                self._drag_resize(event)
            else:
                self.move(self.startFrameGeometry.topLeft()
                    - self.startPosition + event.globalPos())
        else:
            m = self._determine_position(event)
            if 0 < m:
                if event.buttons() == Qt.LeftButton:
                    self._drag_resize(event, m)
                else:
                    if not 0b0011 ^ m or not 0b1100 ^ m: # topleft or bottomright
                        self.setCursor(Qt.SizeFDiagCursor)
                    elif not 0b1001 ^ m or not 0b0110 ^ m: # topright or bottomleft
                        self.setCursor(Qt.SizeBDiagCursor)
                    elif 0b1010 & m:
                        self.setCursor(Qt.SizeHorCursor)
                    elif 0b0101 & m:
                        self.setCursor(Qt.SizeVerCursor)
            else:
                self.setCursor(Qt.ArrowCursor)
        event.accept()
    def _determine_position(self, event):
        ''' 0b0000 bin mask for left, top, right, bottom '''
        p = event.globalPos() - self.frameGeometry().topLeft()
        m = 5
        r = int(('%i' * 4) % (p.x() < m, p.y() < m,
            self.width() - m < p.x(), self.height() - m < p.y()), 2)
        return r
    def _drag_resize(self, event):
        i, marginChange = 0b1000, []
        for _ in range(4):
            marginChange.append(i & self.startResizeMask)
            i = i >> 1
        f = self.startFrameGeometry
        marginValue = [f.left(), f.top(), f.right(), f.bottom()]
        move = event.globalPos() - self.startPosition
        for i, additionalValue in enumerate((move.x(), move.y(), move.x(), move.y())):
            if marginChange[i]: marginValue[i] += additionalValue
        w, h = marginValue[2] - marginValue[0], marginValue[3] - marginValue[1]
        if w < self.minSize[0]:
            w = self.minSize[0]
            if marginChange[0]: marginValue[0] = marginValue[2] - w
        if h < self.minSize[1]:
            h = self.minSize[1]
            if marginChange[1]: marginValue[1] = marginValue[3] - h
        self.setGeometry(*(marginValue[:2] + [w, h]))
