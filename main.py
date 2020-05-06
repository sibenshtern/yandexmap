import sys

from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtWidgets import QLabel, QPushButton, QLineEdit
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout

from PyQt5.QtGui import QPixmap, QKeyEvent
from PyQt5.QtCore import Qt

from api import API, Point, config


class Widget(QWidget):
    
    def __init__(self, *args, **kwargs):
        super(Widget, self).__init__(*args, **kwargs)

        self.api = API(coordinates=(40.498011, 52.893913))
        self.map_type = "map"
        self.zoom = 17

        self.api.config_by_argument(argument=self.api.COORDINATES_ARG)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        button_layout = QHBoxLayout()
        address_layout = QHBoxLayout()

        self.image = QLabel()
        self.image.setMinimumSize(600, 450)
        self.api.add_point(Point(self.api.return_coordinates()))
        self.put_image_in_label()

        self.address_input = QLineEdit()
        search_button = QPushButton('Найти адрес')
        search_button.clicked.connect(self.search_address)

        scheme_map_style_button = QPushButton('Схема')
        scheme_map_style_button.setObjectName('map')
        scheme_map_style_button.clicked.connect(self.set_map_style)

        satellite_map_style_button = QPushButton('Спутник')
        satellite_map_style_button.setObjectName('sat')
        satellite_map_style_button.clicked.connect(self.set_map_style)

        hybrid_map_style_button = QPushButton('Гибрид')
        hybrid_map_style_button.setObjectName('sat,skl')
        hybrid_map_style_button.clicked.connect(self.set_map_style)

        button_layout.addWidget(scheme_map_style_button)
        button_layout.addWidget(satellite_map_style_button)
        button_layout.addWidget(hybrid_map_style_button)

        address_layout.addWidget(self.address_input)
        address_layout.addWidget(search_button)

        main_layout.addLayout(address_layout)
        main_layout.addWidget(self.image)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def put_image_in_label(self):
        image = QPixmap()
        image.loadFromData(self.api.get_map(
            map_type=self.map_type, zoom=self.zoom
        ))
        self.image.setPixmap(image)

    def set_map_style(self):
        self.map_type = self.sender().objectName()
    
        self.put_image_in_label()

        self.setFocus()

    def search_address(self):
        address = self.address_input.text()

        if self.api.validate_address(address):
            self.api.set_address(address)
            self.put_image_in_label()

        self.setFocus()

    def keyPressEvent(self, event):
        pressed_key = event.key()

        if pressed_key == Qt.Key_PageUp:
            self.zoom += (1 if self.zoom < 19 else 0)
        elif pressed_key == Qt.Key_PageDown:
            self.zoom -= (1 if self.zoom > 1 else 0)

        movement = config.move_coefficient[self.zoom]
        coordinates = list(self.api.return_coordinates())

        if pressed_key == Qt.Key_Up:
            coordinates[1] += movement
        if pressed_key == Qt.Key_Right:
            coordinates[0] += movement
        if pressed_key == Qt.Key_Down:
            coordinates[1] -= movement
        if pressed_key == Qt.Key_Left:
            coordinates[0] -= movement

        self.api.set_coordinates(tuple(coordinates))
        self.put_image_in_label()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = Widget()
    widget.show()
    sys.exit(app.exec_())
