import math
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QGridLayout, QPushButton, QVBoxLayout, QSizePolicy, \
    QRadioButton, QLabel, QHBoxLayout, QButtonGroup, QListWidget, QMainWindow, QFrame, QStackedWidget, QComboBox

# QListWidget helps to display history
# QSizePolicy helps to scale the widgets in accordance to the window size
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect, QEasingCurve # For alignment and animations


class Calculator(QMainWindow):
    # The 'Calculator' class has to inherit from the QMainWindow class instead of the QWidget class because
    # 'addDockWidget' is only available in QMainWindow
    def __init__(self):
        super().__init__()
        # Calls the parent QWidget constructor

        self.setWindowTitle("Calculator")

        self.setGeometry(600, 200, 450, 800)
        # Set the position of the window

        self.current_theme = "light"

        self.just_calculated = False

        self.standard_buttons = []
        self.advanced_buttons = []
        self.more_buttons = []
        self.numpad_buttons = []

        # Fixing the display issue so that both the standard and the advanced modes
        # use the same display

        # Create the universal display container
        self.display_container = QWidget()
        display_layout = QVBoxLayout()
        display_layout.setContentsMargins(0, 0, 0, 0)

        # Create the actual QLineEdit display
        self.display = QLineEdit()
        self.display.setAlignment(Qt.AlignRight)
        self.display.setFixedSize(450, 80)
        self.display.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.display.setStyleSheet("font-size: 35px; padding: 5px;")

        display_layout.addWidget(self.display)
        self.display_container.setLayout(display_layout)

        # Creating a history widget for standard mode:
        self.standard_history = QListWidget()
        self.standard_history.setFixedHeight(100)
        self.standard_history.setObjectName("standard")

        # Creating a history widget for advanced mode:
        self.adv_history = QListWidget()
        self.adv_history.setFixedHeight(100)
        self.adv_history.setObjectName("advanced")

        self.set_current_history("standard")
        # Default history is 'standard' since default page is 'standard

        # Create central widget: In QMainWindow, you can't just add layouts directly; you need to set a centralWidget
        # that holds the main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Creating an overlay-type sidebar (like the Windows calculator) to display additional options
        self.sidebar = QFrame(self)
        self.sidebar.setGeometry(0, 0, 200, self.height())
        self.sidebar.setStyleSheet("background-color: #2c2c2c;"
                                   "color: white;")
        self.sidebar.hide() # Sidebar is hidden initially

        # Menu options:
        self.menu_list = QListWidget(self.sidebar)
        self.menu_list.setObjectName("menu_list")
        self.menu_list.addItems(["Standard", "Advanced", "Conversions"])
        self.menu_list.itemClicked.connect(self.change_mode)
        self.menu_list.setGeometry(0, 0, 200, self.height())

        self.initUI()
        # Calling the function that creates the user interface

    # Adding keyboard functionality
    def keyPressEvent(self, event):  # Overrides the Qt event handler for key presses
        key = event.key()
        # Extracts the key code from the event

        # Handling number keys:
        if Qt.Key_0 <= key <= Qt.Key_9:
            self.display.setText(self.display.text() + str(key - Qt.Key_0))
            # Last part: Suppose we press the number '3', internally, the value of 'key' = Qt.Key_3 = 51
            # Hence, when we subtract Qt.Key_0 (which is 48 internally, we will get the actual value of key pressed

        # Adding a decimal point:
        elif key == Qt.Key_Period:
            self.display.setText(self.display.text() + ".")

        # Adding operators:
        elif key == Qt.Key_Plus:
            self.display.setText(self.display.text() + " + ")
        elif key == Qt.Key_Minus:
            self.display.setText(self.display.text() + " - ")
        elif key == Qt.Key_Asterisk:
            self.display.setText(self.display.text() + " × ")
        elif key == Qt.Key_Slash:
            self.display.setText(self.display.text() + " ÷ ")
        elif event.text() == "±":
            current = self.display.text()
            if current.startswith("-"):
                # If negative, remove the minus
                self.display.setText(current[1:])
            elif current:  # If not empty
                # Add minus in front
                self.display.setText("-" + current)

        # Enter / return button -> '='
        elif key in (Qt.Key_Enter, Qt.Key_Return):
            self.evaluate_expression()
            # Lets the evaluate_expression function handle this operation

        # Backspace key:
        elif key == Qt.Key_Backspace:
            self.display.setText(self.display.text()[:-1])

        # Clear key:
        elif key == Qt.Key_C:
            self.display.clear()

        else:
            super().keyPressEvent(event)
            # Example:
            # You press 5 → Your custom code handles it and adds 5 to the display.
            # You press Enter → Your custom code handles it and does =.
            # You press Tab → Your code doesn’t handle it → goes to else → super().keyPressEvent(event)
            # → QWidget handles it → moves focus to the next widget.

            # In short:
            # That line is like saying:
            # “For the keys I don’t understand, let the default system handle them.”

    # CREATING THE UI

    def initUI(self):
        # Creating the main layout
        main_layout = QVBoxLayout()

        # Creating a new layout at the top that contains the menu button and the menu label
        # (what screen they are currently on)
        top_bar = QHBoxLayout()
        self.menu_button = QPushButton("☰")
        self.menu_button.setToolTip("Menu")
        self.menu_button.setStyleSheet("font-size: 25px; padding: 2px; background: none;")
        self.menu_button.clicked.connect(self.toggle_sidebar)

        self.mode_label = QLabel("Standard")
        self.mode_label.setStyleSheet("font-size: 25px; font-weight: bold; font-family: Roboto;")
        top_bar.addWidget(self.menu_button)
        top_bar.addWidget(self.mode_label)
        top_bar.addStretch()  # Pushes everything to the left side

        main_layout.insertLayout(0, top_bar)  # Added the top car to the main layout of the display


        # Code to toggle between themes:
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Theme:")
        self.light_mode = QRadioButton("Light mode")
        self.dark_mode = QRadioButton("Dark mode")
        self.light_mode.setChecked(True)  # Defaults to light mode

        theme_label.setStyleSheet("font-size: 15px;"
                                  "font-family: Roboto;")
        self.light_mode.setStyleSheet("font-size: 15px;"
                                      "font-family: Roboto;")
        self.dark_mode.setStyleSheet("font-size: 15px;"
                                     "font-family: Roboto;")


        # Grouping the theme buttons together
        self.theme_group = QButtonGroup(self)
        self.theme_group.addButton(self.light_mode)
        self.theme_group.addButton(self.dark_mode)

        self.light_mode.toggled.connect(self.toggle_theme)
        self.dark_mode.toggled.connect(self.toggle_theme)

        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.light_mode)
        theme_layout.addWidget(self.dark_mode)
        main_layout.addLayout(theme_layout)

        # Adding radio buttons to allow the user to choose between degrees and radians for trigonometric functions:
        angle_mode_layout = QHBoxLayout()
        self.angle_label = QLabel("Angle mode:")
        self.deg_mode = QRadioButton("Degrees")
        self.rad_mode = QRadioButton("Radians")
        self.deg_mode.setChecked(True)  # Default mode is degrees

        self.angle_label.setStyleSheet("""
        font-size: 18px;
        font-family: Roboto;""")

        self.deg_mode.setStyleSheet("""
                font-size: 18px;
                font-family: Roboto;""")

        self.rad_mode.setStyleSheet("""
                font-size: 18px;
                font-family: Roboto;""")

        # Grouping all the angle buttons in one group
        self.angle_group = QButtonGroup(self)
        self.angle_group.addButton(self.deg_mode)
        self.angle_group.addButton(self.rad_mode)


        self.angle_mode = "deg"
        self.deg_mode.toggled.connect(self.set_angle_mode)
        self.rad_mode.toggled.connect(self.set_angle_mode)

        angle_mode_layout.addWidget(self.angle_label)
        angle_mode_layout.addWidget(self.deg_mode)
        angle_mode_layout.addWidget(self.rad_mode)
        main_layout.addLayout(angle_mode_layout)

        main_layout.addWidget(self.display_container)
        # Now this display shows up

        # Making sure that the angle buttons show up only after clicking the "More Functions" button
        self.angle_label.hide()
        self.rad_mode.hide()
        self.deg_mode.hide()

        # Creating a page container so that when the user clicks a button in the sidebar,
        # the page changes (page container contains all the pages so that switching is easy)
        self.page_layout = QStackedWidget()
        self.standard_page = self.create_standard_calc()
        self.advanced_page = self.create_adv_calc()

        self.page_layout.addWidget(self.standard_page) # Added Standard page to the stack widget
        self.page_layout.addWidget(self.advanced_page) # Added Advanced page to the stack widget
        self.page_layout.setCurrentWidget(self.standard_page) # Defaults to the standard page
        main_layout.addWidget(self.page_layout)

        self.conversions_page = self.create_conversions_page()
        self.page_layout.addWidget(self.conversions_page)

        self.central_widget.setLayout(main_layout)

        # Apply light theme by default:
        self.apply_light_theme()

    # Applying light and dark mode themes to the sidebar:
    def apply_sidebar_theme_light(self):
        self.sidebar.setStyleSheet("""
                    QFrame {
                        background-color: #f0f0f0;
                        border-right: 1px solid #ccc;
                    }
                    QListWidget {
                        background: transparent;
                        color: #000;
                        font-size: 16px;
                        font-family: Roboto;
                        border: none;
                    }
                    QListWidget::item {
                        padding: 12px;
                        font-family: Roboto;
                        border-radius: 8px;
                    }
                    QListWidget::item:hover {
                        background-color: #e0e0e0;
                    }
                    QListWidget::item:selected {
                        background-color: #0078d7;
                        color: white;
                    }
                """)

        self.menu_button.setStyleSheet("background-color: white; font-size: 25px; border: none; padding: 7px;")

    def apply_sidebar_theme_dark(self):
        self.sidebar.setStyleSheet("""
            QFrame {
                background-color: #2c2c2c;
                border-right: 1px solid #444;
            }
            QListWidget#menu_list {
                background: transparent;
                color: #fff;
                font-size: 16px;
                font-family: Roboto;
                border: none;
            }
            QListWidget#menu_list::item {
                padding: 12px;
                font-family: Roboto;
                border-radius: 8px;
            }
            QListWidget#menu_list::item:hover {
                background-color: #3c3c3c;
            }
            QListWidget#menu_list::item:selected {
                background-color: #0078d7;
                color: white;
            }
        """)

        self.menu_button.setStyleSheet("background-color: #2c2c2c; font-size: 25px; border: none; padding: 7px;")

    def toggle_sidebar(self):
        sidebar_width = 200
        sidebar_height = self.height()

        if self.sidebar.isVisible():
            # Sidebar is visible → slide it out
            start_rect = QRect(0, 0, sidebar_width, sidebar_height)
            end_rect = QRect(-sidebar_width, 0, sidebar_width, sidebar_height)
        else:
            # Sidebar is hidden → slide it in
            start_rect = QRect(-sidebar_width, 0, sidebar_width, sidebar_height)
            end_rect = QRect(0, 0, sidebar_width, sidebar_height)
            self.sidebar.setGeometry(start_rect)
            self.sidebar.show()

        # Create animation
        self.sidebar_anim = QPropertyAnimation(self.sidebar, b"geometry")
        self.sidebar_anim.setDuration(300)  # ms
        self.sidebar_anim.setStartValue(start_rect)
        self.sidebar_anim.setEndValue(end_rect)
        self.sidebar_anim.setEasingCurve(QEasingCurve.OutCubic)

        # Hide after animation if sliding out
        if end_rect.x() < 0:
            self.sidebar_anim.finished.connect(self.sidebar.hide)
        else:
            try:
                self.sidebar_anim.finished.disconnect(self.sidebar.hide)
            except TypeError:
                pass

        self.sidebar_anim.start()

    # Creating a function to handle sidebar mode selection
    def change_mode(self, item):
        mode = item.text()
        self.mode_label.setText(mode)

        if mode == 'Standard':
            self.page_layout.setCurrentWidget(self.standard_page)
            self.set_current_history("standard")  # or "advanced"
            # If you only pass self.create_standard_calc, you are only passing the function to the change_mode
            # function, not the page, so it will throw an error
            self.display_container.show()
            self.display.clear() # Clear the display while switching modes

        elif mode == "Advanced":
            self.page_layout.setCurrentWidget(self.advanced_page)
            self.set_current_history("advanced")
            self.display_container.show()
            self.display.clear()

        elif mode == "Conversions":
            self.page_layout.setCurrentWidget(self.conversions_page)
            self.display_container.hide()
        self.sidebar.hide()
        # Hide the sidebar when the user selects desired button

    
    def toggle_theme(self):
        if self.light_mode.isChecked():
            self.apply_light_theme()
            self.current_theme = "light"
            self.apply_sidebar_theme_light()
        else:
            self.apply_dark_theme()
            self.current_theme = "dark"

    def apply_light_theme(self):
        self.display.setStyleSheet("""QLineEdit {
                background-color: #ffffff;
                color: #000000;
                font-size: 42px;
                font-family: SF Mono, monospace;
                padding: 7px;
                border: 2px solid #ccc;
                border-radius: 10px;
                }""")

        self.setStyleSheet("""
            QWidget {
                background-color: #f9f9f9;
                color: #000000;
            }
            QLineEdit#conversion_input {
                background-color: white;
                color: black;
                font-size: 20px;
                font-family: SF Mono;
                border: 2px solid #ccc;
                border-radius: 8px;
            }
            QLineEdit#conversion_result {
                background-color: #f5f5f5;
                color: black;
                font-size: 20px;
                font-family: SF Mono;
                border: 2px solid #ccc;
                border-radius: 8px;
            }
            QComboBox#conversion_combo {
                background-color: white;
                color: black;
                font-size: 18px;
                font-family: Roboto;
                border: 2px solid #ccc;
                border-radius: 8px;
            }
        """)

        for button in self.standard_buttons + self.advanced_buttons:
            text = button.text()
            if text in ['+', '-', '×', '÷', '1/x', '%']:
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #e0e7ff;  
                        color: #1e3a8a;
                        font-size: 25px;
                        font-family: Inter;
                        border-radius: 5px;
                        border: 1px solid #cbd5e1;
                    }
                    QPushButton:hover {
                        background-color: #c7d2fe;
                    }
                """)
            elif text in ['C', '⌫']:
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #f8d7da; 
                        color: #842029;
                        font-size: 25px;
                        font-family: Inter;
                        border-radius: 8px;
                        border: 1px solid #f5c2c7;
                    }
                    QPushButton:hover {
                        background-color: #f5c2c7;
                    }
                """)
            elif text == '=':
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #198754; 
                        color: white;
                        font-size: 25px;
                        font-family: Inter;
                        border-radius: 5px;
                    }
                    QPushButton:hover {
                        background-color: #157347;
                    }
                """)

            elif text in ['n!', 'mod', 'sin', 'asin', 'cos', 'acos', 'tan', 'atan',
                          'log', 'ln', 'π', 'e', 'x²', 'x³', '√x', '³√x', '10^x', 'exp', 'xʸ', 'nCr', 'nPr', '(', ')',
                          'x²', '√x', 'xʸ']:
                button.setStyleSheet("""
                                    QPushButton {
                                        background-color: #fbd9ff;  
                                        color: #8f249c;
                                        font-size: 22px;
                                        font-family: Inter;
                                        border-radius: 8px;
                                        border: 1px solid #fff;
                                    }
                                    QPushButton:hover {
                                        background-color: #f6c9f9;
                                    }
                                """)
            else:
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #e9ecef;  
                        color: #212529;
                        font-size: 25px;
                        font-family: Inter;
                        border-radius: 5px;
                        border: 1px solid #dee2e6;
                    }
                    QPushButton:hover {
                        background-color: #dee2e6;
                    }
                """)

        self.more_functions_button.setStyleSheet("""
                            QPushButton {
                                background-color: #ffebd6; 
                                color: #cc6600;
                                font-size: 20px;
                                font-family: Inter;
                                border-radius: 5px;
                                border: 1px solid #cbd5e1;
                            }
                            QPushButton:hover {
                                background-color: #ffd9b3;
                            }
                            QPushButton:checked {
                                background-color: #ffd9b3;  /* ✅ Active state */
                                border: 2px solid #cbd5e1;
                            }
                        """)

        for button in self.extra_btn_objs:
            button.setStyleSheet("""
                                QPushButton {
                                background-color: #e0e7ff;  
                                color: #1e3a8a;
                                font-size: 25px;
                                font-family: Inter;
                                border-radius: 5px;
                                border: 1px solid #cbd5e1;
                                }

                                QPushButton:hover {
                                background-color: #c7d2fe;
                                }
                            """)
            self.standard_history.setStyleSheet("""
                QListWidget#standard {
                    background-color: white;
                    color: black;
                    font-size: 18px;
                    font-family: Inter;
                    border: 2px solid #ccc;
                    border-radius: 10px;
                    padding: 5px;
                }
                QListWidget::item#history_list {
                    padding: 8px;
                }
                QListWidget::item:selected#history_list {
                    background-color: #ddd;   
                    color: black;
                }
            """)

            self.adv_history.setStyleSheet("""
                            QListWidget#advanced {
                                background-color: white;
                                color: black;
                                font-size: 18px;
                                font-family: Inter;
                                border: 2px solid #ccc;
                                border-radius: 10px;
                                padding: 5px;
                            }
                            QListWidget::item#history_list {
                                padding: 8px;
                            }
                            QListWidget::item:selected#history_list {
                                background-color: #ddd;   
                                color: black;
                            }
                        """)

            for button in self.numpad_buttons:
                text = button.text()
                if text in ['C', '⌫']:
                    button.setStyleSheet("""
                                        QPushButton {
                                            background-color: #f8d7da; 
                                            color: #842029;
                                            font-size: 25px;
                                            font-family: Inter;
                                            border-radius: 8px;
                                            border: 1px solid #f5c2c7;
                                        }
                                        QPushButton:hover {
                                            background-color: #f5c2c7;
                                        }
                                                """)
                else:
                    button.setStyleSheet("""
                                        QPushButton {
                                            color: #212529;
                                            background-color: #e9ecef;
                                            border: 1px solid #dee2e6;
                                            border-radius: 5px;
                                            font-size: 25px;
                                            font-family: Inter;
                                            color: #333;
                                        }
                                        QPushButton:hover {
                                            background-color: #dee2e6; 
                                         }
                                                """)

            self.conversion_list.setStyleSheet("""
            QListWidget{
                font-size: 18px;
                padding: 5px;
                border: 2px solid #ccc;
                border-radius: 8px;
                font-family: Inter;
                background-color: white;
                color: black;
            }
            QListWidget::item {
                padding: 12px;
                border-radius: 4px;
                margin: 2px;
                background-color: white;
            }
            QListWidget::item:hover {
                background-color: #e3f2fd;
            }
            QListWidget::item:selected {
                background-color: #2196f3;
                color: white;
            }""")

            self.angle_label.setStyleSheet("font-size: 15px; font-family: Roboto;")
            self.deg_mode.setStyleSheet("font-size: 15px; font-family: Roboto;")
            self.rad_mode.setStyleSheet("font-size: 15px; font-family: Roboto;")



        self.apply_sidebar_theme_light()
        # Here, if we call the same function (apply_light_theme), Python will throw a RecursionError
        # as the function is being called infinite number of times

    def apply_dark_theme(self):
        self.display.setStyleSheet("""QLineEdit {
                background-color: #2b2b2b;
                color: #ffffff;
                font-size: 42px;
                font-family: SF Mono;
                padding: 10px;
                border: 2px solid #444;
                border-radius: 10px;
            }""")

        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            
            QLineEdit#conversion_input {
                background-color: #1e1e1e;
                color: #ffffff;
                font-size: 23px;
                font-family: SF Mono;
                border: 2px solid #444;
                border-radius: 10px;
            }
            QLineEdit#conversion_result {
                background-color: #1e1e1e;
                color: #ffffff;
                font-size: 23px;
                font-family: SF Mono;
                border: 2px solid #444;
                border-radius: 10px;
            }
            QComboBox#conversion_combo {
                background-color: #1e1e1e;
                color: white;
                font-size: 18px;
                font-family: SF Mono, monospaced;
                border: 2px solid #444;
                border-radius: 10px;
            }
        """)

        for button in self.numpad_buttons:
            text = button.text()
            if text in ['C', '⌫']:
                button.setStyleSheet("""
                        QPushButton {
                            color: #fca5a5;
                            background-color: #5b2d2d;
                            border: 1px solid #7f1d1d;
                            border-radius: 5px;
                            font-size: 25px;
                            font-family: Inter;
                            color: #fff;
                        }
                        QPushButton:hover { background-color: #7f1d1d; }
                    """)
            else:
                button.setStyleSheet("""
                        QPushButton {
                            background-color: #2d2d2d;
                            color: #e5e7eb;
                            font-size: 25px;
                            font-family: Inter;
                            border-radius: 5px;
                            border: 1px solid #3f3f3f;
                        }
                        QPushButton:hover {
                        background-color: #3f3f3f; }
                    """)

        for button in self.standard_buttons + self.advanced_buttons:
            text = button.text()
            if text in ['+', '-', '×', '÷', '1/x', '%']:
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #374151;  
                        color: #93c5fd;            
                        font-size: 25px;
                        font-family: Inter;
                        border-radius: 5px;
                        border: 1px solid #4b5563;
                    }
                    QPushButton:hover {
                        background-color: #4b5563;
                    }
                """)
            elif text in ['C', '⌫']:
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #5b2d2d;  
                        color: #fca5a5;
                        font-size: 25px;
                        font-family: Inter;
                        border-radius: 5px;
                        border: 1px solid #7f1d1d;
                    }
                    QPushButton:hover {
                        background-color: #7f1d1d;
                    }
                """)
            elif text == '=':
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #14532d;  
                        color: #bbf7d0;
                        font-size: 25px;
                        font-family: Inter;
                        border-radius: 5px;
                    }
                    QPushButton:hover {
                        background-color: #166534;
                    }
                """)

            elif text in ['n!', 'mod', 'sin', 'asin', 'cos', 'acos', 'tan', 'atan',
                          'log', 'ln', 'π', 'e', 'x²', 'x³', '√x', '³√x', '10^x', 'exp', 'xʸ', 'nCr', 'nPr', '(', ')']:
                button.setStyleSheet("""
                                    QPushButton {
                                        background-color: #473a7a;  
                                        color: #bdabff;
                                        font-size: 25px;
                                        font-family: Inter;
                                        border-radius: 8px;
                                        border: 1px solid #1e1e1e;
                                    }
                                    QPushButton:hover {
                                        background-color: #584896;
                                    }
                                """)

            else:
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #2d2d2d;
                        color: #e5e7eb;
                        font-size: 25px;
                        font-family: Inter;
                        border-radius: 5px;
                        border: 1px solid #3f3f3f;
                    }
                    QPushButton:hover {
                        background-color: #3f3f3f;
                    }
                """)

        self.more_functions_button.setStyleSheet("""
                            QPushButton {
                                background-color: #3b2a1f;  
                                color: #ff9933;
                                font-size: 20px;
                                font-family: Inter;
                                border-radius: 5px;
                                border: 1px solid #3f3f3f;
                            }
                            QPushButton:hover {
                                background-color: #4a372b;
                            }
                            QPushButton:checked {
                                background-color: #4a372b;  /* ✅ Active state */
                                border: 2px solid #3f3f3f;
                            }
                        """)

        for button in self.extra_btn_objs:
            button.setStyleSheet("""
                    QPushButton {
                        background-color: #374151;  
                        color: #93c5fd;            
                        font-size: 25px;
                        font-family: Inter;
                        border-radius: 5px;
                        border: 1px solid #4b5563;
                    }
                    QPushButton:hover {
                        background-color: #4b5563;
                    }
                            """)
        self.display.setStyleSheet("""
        QLineEdit {
            background-color: #1e1e1e;
            color: white;
            font-size: 50px;
            font-family: SF Mono;
            padding: 10px;
            border: 2px #444;
            border-radius: 10px
        }""")

        self.standard_history.setStyleSheet("""
                        QListWidget#standard {
                            background-color: #1e1e1e;
                            color: white;
                            font-size: 18px;
                            font-family: Inter;
                            border: 2px solid #444;
                            border-radius: 10px;
                            padding: 5px;
                        }
                        QListWidget::item#history_list {
                            padding: 8px;
                        }
                        QListWidget::item:selected#history_list {
                            background-color: #444;  
                            color: white;
                        }
                    """)

        self.adv_history.setStyleSheet("""
                                QListWidget#advanced {
                                    background-color: #1e1e1e;
                                    color: white;
                                    font-size: 18px;
                                    font-family: Inter;
                                    border: 2px solid #444;
                                    border-radius: 10px;
                                    padding: 5px;
                                }
                                QListWidget::item#history_list {
                                    padding: 8px;
                                }
                                QListWidget::item:selected#history_list {
                                    background-color: #444;   
                                    color: white;
                                }
                            """)

        self.conversion_list.setStyleSheet("""
                    QListWidget {
                        font-size: 18px;
                        padding: 5px;
                        border: 2px solid #444;
                        font-family: Inter;
                        border-radius: 8px;
                        background-color: #1e1e1e;
                        color: white;
                    }
                    QListWidget::item {
                        padding: 12px;
                        border-radius: 4px;
                        font-family: Inter;
                        margin: 2px;
                        background-color: #1e1e1e;
                    }
                    QListWidget::item:hover {
                        background-color: #3c3c3c;
                    }
                    QListWidget::item:selected {
                        background-color: #2196f3;
                        color: white;
                    }
                """)

        self.angle_label.setStyleSheet("font-size: 15px; font-family: Roboto; color: #ffffff;")
        self.deg_mode.setStyleSheet("font-size: 15px; font-family: Roboto; color: #ffffff;")
        self.rad_mode.setStyleSheet("font-size: 15px; font-family: Roboto; color: #ffffff;")

        self.apply_sidebar_theme_dark()

    def create_standard_calc(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.display_container)
        # Adding the universal display to the layout of the standard mode layout

        # --- History ---
        self.standard_history.itemDoubleClicked.connect(self.use_history_items)
        layout.addWidget(self.standard_history)

        # --- More Functions button ---
        self.more_functions_button = QPushButton("More Functions")
        self.more_functions_button.setCheckable(True)
        self.more_functions_button.clicked.connect(self.toggle_extra_functions)
        self.more_functions_button.setFixedHeight(40)
        layout.addWidget(self.more_functions_button)

        # --- Extra functions (trig/log etc., hidden initially) ---
        self.extra_layout = QGridLayout()
        self.extra_buttons = ['sin', 'cos', 'tan', 'log', 'ln', 'exp', '(', ')']
        self.extra_btn_objs = []

        tool_tips_extra = {
            'sin': 'Sine function',
            'cos': 'Cosine function',
            'tan': "Tangent function",
            'log': 'Logarithm Base-10',
            'ln': 'Natural Logarithm',
            'exp': 'Exponential (x * 10^x)',
            '(': 'Open brackets',
            ')': 'Close brackets'
        }

        row, col = 0, 0
        for text in self.extra_buttons:
            button = QPushButton(text)
            button.setFixedSize(100, 50)
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            button.clicked.connect(self.extra_buttons_clicked)

            if text in tool_tips_extra:
                button.setToolTip(tool_tips_extra[text])

            self.extra_btn_objs.append(button)
            self.extra_layout.addWidget(button, row, col)

            col += 1
            if col > 3:  # Wrap after 2 columns for 2 x 4 grid
                col = 0
                row += 1

        # Hiding the extra functions initially
        for btn in self.extra_btn_objs:
            btn.hide()

        layout.addLayout(self.extra_layout)

        # --- Basic number/operator grid ---
        grid = QGridLayout()
        buttons = [
            ['C', '⌫', '%', '÷'],
            ['7', '8', '9', '×'],
            ['4', '5', '6', '-'],
            ['1', '2', '3', '+'],
            ['.', '0', '±', '=']
        ]

        self.buttons = []
        tool_tips = {
            'C': 'Clear display',
            '⌫': 'Backspace',
            '÷': 'Division',
            '×': 'Multiplication',
            '+': 'Addition',
            '-': 'Subtraction',
            '=': 'Calculate result'
        }

        for row, row_data in enumerate(buttons):
            for col, btn_text in enumerate(row_data):
                button = QPushButton(btn_text)
                if btn_text in tool_tips:
                    button.setToolTip(tool_tips[btn_text])
                button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                button.clicked.connect(self.action_on_click)
                self.standard_buttons.append(button)
                grid.addWidget(button, row, col)
                grid.setColumnStretch(col, 1)
                grid.setRowStretch(row, 1)

        layout.addLayout(grid)


        widget.setLayout(layout)
        return widget

    def create_adv_calc(self):
        page = QWidget()
        layout = QVBoxLayout()

        # Creating the top bar:
        top_bar = QHBoxLayout()
        top_bar.addStretch()  # Pushes everything to the left side

        # Doing the same thing as in the create_standard_calc (re-using the universal display)
        layout.addWidget(self.display_container)

        self.adv_history.itemDoubleClicked.connect(self.use_history_items)
        layout.addWidget(self.adv_history)

        # --- Advanced buttons grid ---
        grid = QGridLayout()
        buttons = [
            ["C", "⌫", "(", ")", "n!", "mod"],
            ["π", "e", "x²", "x³", "√x", "³√x"],
            ["10^x", "exp", "xʸ", "nCr", "nPr", "log"],
            ["7", "8", "9", "÷", "sin", "asin"],
            ["4", "5", "6", "×", "cos", "acos"],
            ["1", "2", "3", "-", "tan", "atan"],
            ["0", ".", "±", "+", "ln", "="]
        ]
        tool_tips_adv = {
            'C': "Clear display",
            '⌫': "Backspace",
            '(': "Open brackets",
            ')': "Close brackets",
            'n!': "Factorial",
            'mod': "Modulus",
            'sin': "Sine function",
            'asin': "Inverse of sine function",
            'cos': "Cosine function",
            'acos': "Inverse of cosine function",
            'tan': "Tangent function",
            'atan': "Inverse of tangent function",
            'log': "Logarithm (Base 10)",
            'ln': "Natural Logarithm",
            'π': "Pi",
            'e': "Euler's constant",
            'x²': "Square function",
            'x³': "Cube function",
            '√x': "Square root function",
            '³√x': "Cube root function",
            '10^x': "Ten raised to the power",
            'exp': "Exponential function",
            'xʸ': "x raised to the power y",
            'nCr': "Combinations function",
            'nPr': "Permutations functions"

        }

        self.buttons = []

        for row, row_data in enumerate(buttons):
            for col, btn_text in enumerate(row_data):
                button = QPushButton(btn_text)
                if btn_text in tool_tips_adv:
                    button.setToolTip(tool_tips_adv[btn_text])

                button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                button.clicked.connect(self.advanced_buttons_clicked)
                grid.addWidget(button, row, col)
                self.advanced_buttons.append(button)

        layout.addLayout(grid)

        page.setLayout(layout)
        return page

    # Adding a function to append expressions to the correct history widget
    def set_current_history(self, mode):
        if mode == "standard":
            self.current_history = self.standard_history
        elif mode == "advanced":
            self.current_history = self.adv_history
        elif mode == "conversions":
            self.current_history = None # Conversions page doesn't need history


    def action_on_click(self):
        button = self.sender()
        # return the object that triggered this event (here, clicked button is the sender)

        text = button.text()
        # Gets the label (text) that is on the clicked button

        if text == 'C':
            self.display.clear()

        elif text == '=':
            self.evaluate_expression()

        elif text == '√x':
            try:
                value = self.display.text()
                num = float(value)
                # Gets the current text from the calculator display

                if value:  # If value is not empty
                    if num < 0:  # Checks if value is empty or not
                        self.display.setText("Error")
                    else:
                        result = math.sqrt(num)
                        self.add_to_history("√", num, result)
                else:
                    self.display.setText("Error")

            except ValueError:
                self.display.setText("Error")

        elif text == 'x²':
            try:
                value = self.display.text()
                # Gets the current text from the calculator display

                if value:  # Checks if value is empty or not
                    result = float(value) ** 2
                    self.add_to_history(f'{value}²', "", result)
                else:
                    print("Error")

            except ValueError:
                self.display.setText("Error")

        elif text == '1/x':
            try:
                value = self.display.text().strip()  # strip function removes any spaces
                # Gets the current text from the calculator display

                if value:  # Checks if value is empty or not
                    num = float(value)
                    if num == 0:
                        self.display.setText("Error")
                    else:
                        result = 1 / num
                        self.add_to_history('1/', num, result)
                else:
                    self.display.setText("Error")

            except ValueError:
                self.display.setText("Error")

        elif text == '%':
            try:
                value = self.display.text()

                if value:
                    result = float(value) / 100
                    self.add_to_history('%', value, result)
                else:
                    self.display.setText("Error")

            except ValueError:
                print("Error")

        elif text == 'xʸ':
            try:
                value = self.display.text()

                if value:
                    self.display.setText(value + ' ** ')
                    # To display in the format of '3 ** 3'
                else:
                    self.display.setText('Error')

            except ValueError:
                self.display.setText('Error')

        elif text == '⌫':
            current = self.display.text()
            self.display.setText(current[:-1])
            # Python slicing -> string[start:end]
            # current[:-1] -> take everything from the beginning upto the last character, leaving the last character out

        elif text == '±':
            try:
                value = self.display.text()

                if value:  # Checks if value is empty or not
                    num = float(value)
                    num = -num
                    self.display.setText(str(num))

                else:
                    self.display.setText("Error")

            except ValueError:
                self.display.setText("Error")

        else:
            self.display.setText(self.display.text() + text)
            # If there is no error, this will append the button's text to the text box

    # Creating a function to add items to history when the extra functions / functions like √x, x², 1/x, %, etc
    def add_to_history(self, operation, num, result, extra=""):
        # Accept four parameters:
        # Operation: the operation performed
        # num: the input value before the operation
        # result: the output value after the operation has been performed
        # extra: optional details (like 'deg' or 'rad') which defaults to "" if nothing is given

        try:
            num_str = self.format_result(num)
            result_str = self.format_result(result)

            # Update the display:
            self.display.setText(result_str)

            # Add it to the history widget:
            if extra:
                self.current_history.addItem(f"{operation}{num_str}{extra} = {result_str}")
            else:
                self.current_history.addItem(f"{operation}{num_str} = {result_str}")

        except Exception as error:
            print("History add error", error)
            self.display.setText("Error")

    # Creating a function to let the user re-use the items stores in the history list:
    def use_history_items(self, item):
        # When an item in the history list is double-clicked, display that expression in the Line Edit widget
        expression = item.text().split("=")[0].strip()
        # Splitting the expression from the '=' sign and display the rest
        self.display.setText(expression)

    # Creating a new function to handle evaluation of expressions
    # without having to fake an '=' click when the 'Enter' key is pressed
    def evaluate_expression(self):

        try:
            expression = self.display.text().strip()
            # Getting the expression typed in by the user

            original_expression = expression
            # Keeping the original expression for adding to history

            # 1. Handling the nCr operation:
            if 'C' in expression and not any(func in expression for func in ['cos', 'acos']):
                # Adding this line because if the user types in 'cos' or 'acos', it contains a 'C' which will create conflicts
                try:
                    parts = expression.split('C')
                    if len(parts) == 2:
                        n = int(float(parts[0]))
                        r = int(float(parts[1]))

                        if n >= 0 and r >= 0 and n >= r:
                            result = math.factorial(n) // (math.factorial(r) * math.factorial(n-r))
                            self.current_history.addItem(f"{original_expression} = {result}")
                            self.current_history.scrollToBottom()
                            self.display.setText(str(result))
                            self.just_calculated = True
                            return

                        else:
                            self.display.setText("Error")
                            return

                except:
                    self.display.setText("Error")
                    return

            # 2. Handling the nPr operation:
            if 'P' in expression and not any(func in expression for func in ['exp']):
                # Adding this line because if the user types in 'exp', it contains a 'P' which will create conflicts

                try:
                    parts = expression.split('P')
                    if len(parts) == 2:
                        n = int(float(parts[0]))
                        r = int(float(parts[1]))

                        if n >= 0 and r >= 0 and n >= r:
                            result = math.factorial(n) // math.factorial(n-r)
                            self.current_history.addItem(f"{original_expression} = {result}")
                            self.current_history.scrollToBottom()
                            self.display.setText(str(result))
                            self.just_calculated = True
                            return

                        else:
                            self.display.setText("Error")
                            return

                except:
                    self.display.setText("Error")
                    return

                # Handle mod operations
                if ' mod ' in expression:
                    try:
                        parts = expression.split(' mod ')
                        if len(parts) == 2:
                            a = float(parts[0])
                            b = float(parts[1])
                            if b != 0:
                                result = a % b
                                self.current_history.addItem(f"{original_expression} = {result}")
                                self.current_history.scrollToBottom()
                                self.display.setText(str(result))
                                self.just_calculated = True
                                return
                            else:
                                self.display.setText("Error")
                                return
                    except:
                        self.display.setText("Error")
                        return

            expression = expression.replace('×', '*').replace('÷', '/')
            expression = expression.replace('e', str(math.e))

            result = str(eval(expression))
            # Built-in function to evaluate expressions in python and then typecasting it back to a string

            # Adding the expression to the history widget
            self.current_history.addItem(f"{expression} = {result}")
            self.current_history.scrollToBottom()
            self.display.setText(result)
            self.just_calculated = True

        except ZeroDivisionError:
            self.display.setText("Error")

        except:
            self.display.setText('Error')
    # Adding functions to clear the display every time a calculation has been performed and the user types in a new
    # expression
    def calculate_result(self):
        try:
            expression = self.display.text()
            result = str(eval(expression))
            self.display.setText(result)
            self.just_calculated = True
        except Exception:
            self.display.setText("Error")
            self.just_calculated = True

    def digit_clicked(self, digit):
        if self.just_calculated:
            self.display.clear()
            self.just_calculated = False
        self.display.insert(digit)


    def toggle_extra_functions(self):
        if self.more_functions_button.isChecked():  # ✅ button pressed
            for btn in self.extra_btn_objs:
                btn.show()
            # Showing the degree and radians button when pressed
            self.angle_label.show()
            self.deg_mode.show()
            self.rad_mode.show()
        else:
            for btn in self.extra_btn_objs:
                btn.hide()
                # Hiding the degree and radians button when pressed
                self.angle_label.hide()
                self.deg_mode.hide()
                self.rad_mode.hide()

    def set_angle_mode(self):
        if self.deg_mode.isChecked():
            self.angle_mode = 'deg'
        else:
            self.angle_mode = 'rad'

    def format_result(self, value):
        """
        Format calculation results:
        - If the number is an integer (like 16.0), drop the .0
        - Otherwise, show up to 10 decimal places (strip trailing zeros)
        """
        try:
            # Convert to float to handle both strings and floats
            value = float(value)

            # Check if it's effectively an integer (16.0 → 16)
            if value == int(value):
                return str(int(value))
            else:
                # Format to 10 decimal places and strip extra zeros
                return f"{value:.10f}".rstrip("0").rstrip(".")
        except Exception:
            return str(value)  # Fallback for safety

    def extra_buttons_clicked(self):
        button = self.sender()
        # return the object that triggered this event (here, clicked button is the sender)

        text = button.text()
        # Gets the label (text) that is on the clicked button

        current = self.display.text()
        # To get the tet from the display to append brackets to it (and also something else if it needs to)

        try:
            # Make sure there is a number in the display
            if not self.display.text():
                self.display.setText("Error")
                return

            num = float(self.display.text())  # Convert once safely

            if text == "sin":
                num_radians = math.radians(num) if self.angle_mode == "deg" else num
                result = math.sin(num_radians)
                self.add_to_history("sin", num, result, self.angle_mode)

            elif text == "cos":
                num_radians = math.radians(num) if self.angle_mode == "deg" else num
                result = math.cos(num_radians)
                self.add_to_history("cos", num, result, self.angle_mode)

            elif text == "tan":
                num_radians = math.radians(num) if self.angle_mode == "deg" else num
                result = math.tan(num_radians)
                self.add_to_history("tan", num, result, self.angle_mode)

            elif text == "log":
                result = math.log10(num)
                self.add_to_history("log", num, result)

            elif text == "ln":
                result = math.log(num)
                self.add_to_history("ln", num, result)

            elif text == "exp":
                value = float(current) if current else 0
                result = math.exp(value)
                self.add_to_history("exp", current, result)

            elif text == '(':
                self.display.setText(current + '(')

            elif text == ')':
                self.display.setText(current + ')')

        except ValueError:
            self.display.setText("Error")

    def advanced_buttons_clicked(self):
        button = self.sender()
        text = button.text()

        # Handle buttons that don't need numeric conversion first
        if text == 'C':
            self.display.clear()
            return

        elif text == "⌫":
            current = self.display.text()
            self.display.setText(current[:-1])
            return

        elif text == '=':
            self.evaluate_expression()
            return

        elif text in ['(', ')']:
            current = self.display.text()
            self.display.setText(current + text)
            return

        elif text == 'π':
            current = self.display.text()
            self.display.setText(current + str(math.pi))
            return

        elif text == 'e':
            current = self.display.text()
            self.display.setText(current + "e")
            return

        elif text.isdigit() or text in ['+', '-', '×', '÷', '.', '±']:
            current = self.display.text()
            if text == '×':
                self.display.setText(current + '*')
            elif text == '÷':
                self.display.setText(current + '/')
            elif text == '±':
                if current.startswith("-"):
                    self.display.setText(current[1:])
                elif current:
                    self.display.setText("-" + current)
            else:
                self.display.setText(current + text)
            return


        elif text in ['mod', 'nCr', 'nPr', 'xʸ']:
            current = self.display.text()

            if text == 'mod':
                self.display.setText(current + ' mod ')
            elif text == 'nCr':
                self.display.setText(current + 'C')
            elif text == 'nPr':
                self.display.setText(current + 'P')
            elif text == 'xʸ':
                self.display.setText(current + '**')

            return

        # Now handle buttons that need numeric input
        try:
            if not self.display.text():
                self.display.setText("Error")
                return

            value = float(self.display.text())  # Now we define 'value' here

            # Mathematical functions
            if text == 'x²':
                result = value ** 2
                self.add_to_history(f"{value}²", value, result)

            elif text == 'x³':
                result = value ** 3
                self.add_to_history(f"{value}³", value, result)

            elif text == '√x':
                result = math.sqrt(abs(value))
                self.add_to_history(f"√{value}", value, result)

            elif text == '³√x':
                result = value ** (1 / 3)
                self.add_to_history(f"³√{value}", value, result)

            elif text == '10^x':
                result = 10 ** value
                self.add_to_history(f"10^{value}", value, result)

            elif text == 'exp':
                result = math.exp(value)
                self.add_to_history(f"e^{value}", value, result)

            elif text == 'n!':
                if value == int(value) and value >= 0:
                    result = math.factorial(int(value))
                    self.add_to_history(f"{int(value)}!", int(value), result)
                else:
                    self.display.setText("Error")
                    return

            # Trigonometric functions
            elif text == "sin":
                angle_rad = math.radians(value) if self.angle_mode == "deg" else value
                result = math.sin(angle_rad)
                self.add_to_history("sin", value, result, f"({self.angle_mode})")

            elif text == "cos":
                angle_rad = math.radians(value) if self.angle_mode == "deg" else value
                result = math.cos(angle_rad)
                self.add_to_history("cos", value, result, f"({self.angle_mode})")

            elif text == "tan":
                angle_rad = math.radians(value) if self.angle_mode == "deg" else value
                result = math.tan(angle_rad)
                self.add_to_history("tan", value, result, f"({self.angle_mode})")

            elif text == "asin":
                if -1 <= value <= 1:
                    result_rad = math.asin(value)
                    result = math.degrees(result_rad) if self.angle_mode == "deg" else result_rad
                    self.add_to_history("asin", value, result, f"({self.angle_mode})")
                else:
                    self.display.setText("Error")
                    return

            elif text == "acos":
                if -1 <= value <= 1:
                    result_rad = math.acos(value)
                    result = math.degrees(result_rad) if self.angle_mode == "deg" else result_rad
                    self.add_to_history("acos", value, result, f"({self.angle_mode})")
                else:
                    self.display.setText("Error")
                    return

            elif text == "atan":
                result_rad = math.atan(value)
                result = math.degrees(result_rad) if self.angle_mode == "deg" else result_rad
                self.add_to_history("atan", value, result, f"({self.angle_mode})")

            elif text == "log":
                if value > 0:
                    result = math.log10(value)
                    self.add_to_history("log", value, result)
                else:
                    self.display.setText("Error")
                    return

            elif text == "ln":
                if value > 0:
                    result = math.log(value)
                    self.add_to_history("ln", value, result)
                else:
                    self.display.setText("Error")
                    return

        except ValueError:
            self.display.setText("Error")

    def create_conversions_page(self):
        page = QWidget()
        layout = QVBoxLayout()

        # Creating the title:
        title = QLabel("Unit Converter")
        title.setStyleSheet("font-size: 35px;"
                            "font-family: Roboto;"
                            "font-weight: bold;"
                            "padding: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Creating the conversion types list:
        self.conversion_list = QListWidget()
        self.conversion_list.setStyleSheet("""
                QListWidget {
                    font-size: 18px;
                    padding: 5px;
                    font-family: Inter;
                    border: 2px solid #ccc;
                    border-radius: 8px;
                }
                QListWidget::item {
                    padding: 12px;
                    border-radius: 4px;
                    font-family: Inter;
                    margin: 2px;
                }
                QListWidget::item:hover {
                    background-color: #e3f2fd;
                }
                QListWidget::item:selected {
                    background-color: #2196f3;
                    color: white;
                }
            """)

        # Adding conversion categories to the list:
        conversion_types = ["Length", "Weight and Mass", "Volume", "Temperature", "Energy", "Area", "Speed", "Time",
                            "Power", "Data", "Pressure", "Angle"]

        self.conversion_list.addItems(conversion_types)
        # Fixed: using itemClicked instead of clicked
        self.conversion_list.itemClicked.connect(self.open_conversion_calculator)

        self.conversion_list.setFixedHeight(350)

        layout.addWidget(self.conversion_list)

        # Add some instructions
        instruction = QLabel("Select a conversion type above to get started")
        instruction.setStyleSheet("font-size: 16px; "
                                  "color: #666; "
                                  "padding: 15px;"
                                  "font-family: Roboto;")
        instruction.setAlignment(Qt.AlignCenter)
        layout.addWidget(instruction)

        # Adding conversion data types for all types:
        self.conversion_data = {
            "Length": {
                "base_unit": "meter",
                "units": {
                    "Nanometer": 1e-9,
                    "Micrometer": 1e-6,
                    "Millimeter": 0.001,
                    "Centimeter": 0.01,
                    "Meter": 1.0,
                    "Kilometer": 1000.0,
                    "Inch": 0.0254,
                    "Foot": 0.3048,
                    "Yard": 0.9144,
                    "Mile": 1609.34,
                    "Nautical Mile": 1852.0
                }
            },
            "Weight and Mass": {
                "base_unit": "kilogram",
                "units": {
                    "Microgram": 1e-9,
                    "Milligram": 1e-6,
                    "Gram": 0.001,
                    "Kilogram": 1.0,
                    "Metric Ton": 1000.0,
                    "Ounce": 0.0283495,
                    "Pound": 0.453592,
                    "Stone": 6.35029,
                    "Short Ton": 907.185,
                    "Long Ton": 1016.05
                }
            },
            "Temperature": {
                "special": True,  # Special handling needed
                "units": ["Celsius", "Fahrenheit", "Kelvin", "Rankine"]
            },
            "Area": {
                "base_unit": "square meter",
                "units": {
                    "Square Millimeter": 1e-6,
                    "Square Centimeter": 1e-4,
                    "Square Meter": 1.0,
                    "Hectare": 10000.0,
                    "Square Kilometer": 1e6,
                    "Square Inch": 0.00064516,
                    "Square Foot": 0.092903,
                    "Square Yard": 0.836127,
                    "Acre": 4046.86,
                    "Square Mile": 2.59e6
                }
            },
            "Volume": {
                "base_unit": "liter",
                "units": {
                    "Milliliter": 0.001,
                    "Liter": 1.0,
                    "Cubic Centimeter": 0.001,
                    "Cubic Meter": 1000.0,
                    "Fluid Ounce (US)": 0.0295735,
                    "Cup (US)": 0.236588,
                    "Pint (US)": 0.473176,
                    "Quart (US)": 0.946353,
                    "Gallon (US)": 3.78541,
                    "Cubic Inch": 0.0163871,
                    "Cubic Foot": 28.3168
                }
            },
            "Speed": {
                "base_unit": "meter per second",
                "units": {
                    "Meter per Second": 1.0,
                    "Kilometer per Hour": 0.277778,
                    "Mile per Hour": 0.44704,
                    "Knot": 0.514444,
                    "Foot per Second": 0.3048,
                    "Mach": 343.0
                }
            },
            "Time": {
                "base_unit": "second",
                "units": {
                    "Nanosecond": 1e-9,
                    "Microsecond": 1e-6,
                    "Millisecond": 0.001,
                    "Second": 1.0,
                    "Minute": 60.0,
                    "Hour": 3600.0,
                    "Day": 86400.0,
                    "Week": 604800.0,
                    "Month": 2.628e6,
                    "Year": 3.154e7
                }
            },
            "Power": {
                "base_unit": "watt",
                "units": {
                    "Watt": 1.0,
                    "Kilowatt": 1000.0,
                    "Horsepower": 745.7,
                    "BTU per Hour": 0.293071,
                    "Calorie per Second": 4.184,
                    "Foot-Pound per Second": 1.35582
                }
            },
            "Data": {
                "base_unit": "byte",
                "units": {
                    "Bit": 0.125,
                    "Byte": 1.0,
                    "Kilobyte": 1024.0,
                    "Megabyte": 1.049e6,
                    "Gigabyte": 1.074e9,
                    "Terabyte": 1.1e12,
                    "Petabyte": 1.126e15
                }
            },
            "Pressure": {
                "base_unit": "pascal",
                "units": {
                    "Pascal": 1.0,
                    "Kilopascal": 1000.0,
                    "Bar": 100000.0,
                    "PSI": 6894.76,
                    "Atmosphere": 101325.0,
                    "Torr": 133.322,
                    "mmHg": 133.322
                }
            },
            "Angle": {
                "base_unit": "radian",
                "units": {
                    "Degree": 0.0174533,
                    "Radian": 1.0,
                    "Gradian": 0.0157080,
                    "Turn": 6.28319,
                    "Arcminute": 0.000290888,
                    "Arcsecond": 4.8481e-6
                }
            },
            "Energy": {
                "base_unit": "joule",
                "units": {
                    "Joule": 1.0,
                    "Kilojoule": 1000.0,
                    "Calorie": 4.184,
                    "Kilocalorie": 4184.0,
                    "BTU": 1055.06,
                    "Watt Hour": 3600.0,
                    "Kilowatt Hour": 3.6e6,
                    "Electronvolt": 1.602e-19,
                    "Foot-Pound": 1.35582
                }
            }
        }

        page.setLayout(layout)
        return page

    def open_conversion_calculator(self, item):
        """Open the specific conversion calculator for the selected type"""
        conversion_type = item.text()

        # Store the current conversion type as instance variable
        self.current_conversion_type = conversion_type

        # Create a new page for this specific conversion
        conversion_page = self.create_specific_conversion_page(conversion_type)

        # Add to stack if not already there
        page_name = f"{conversion_type.lower().replace(' ', '_')}_page"
        if not hasattr(self, page_name):
            setattr(self, page_name, conversion_page)
            self.page_layout.addWidget(conversion_page)

        # Switch to this conversion page
        self.page_layout.setCurrentWidget(getattr(self, page_name))
        self.mode_label.setText(f"Conversions - {conversion_type}")

    def create_specific_conversion_page(self, conversion_type):
        """Create a specific conversion calculator page"""
        page = QWidget()
        layout = QVBoxLayout()

        # Back button
        back_layout = QHBoxLayout()
        back_button = QPushButton("← Back to Conversions")
        if self.current_theme == 'dark':
            back_button.setStyleSheet("font-size: 16px;"
                                      "font-family: Roboto;")
        if self.current_theme == 'light':
            back_button.setStyleSheet("font-size: 16px;"
                                      "font-family: Roboto;")

        # No parameters needed - uses instance variable approach
        back_button.clicked.connect(self.go_back_to_conversions)
        back_layout.addWidget(back_button)
        back_layout.addStretch()
        layout.addLayout(back_layout)

        # Creating a title based on the selected conversion type:
        title = QLabel(f"{conversion_type} Conversion")
        title.setStyleSheet("font-size: 22px;"
                            "font-family: Roboto;"
                            "font-weight: bold;"
                            "padding: 15px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Fixed: Creating a proper VBoxLayout for conversions
        conversion_layout = QVBoxLayout()

        # Creating the 'From' part:
        from_layout = QHBoxLayout()

        from_value = QLineEdit()
        from_value.setFixedHeight(45)
        from_value.setObjectName("conversion_input")
        from_value.setPlaceholderText("Enter value")

        from_unit = QComboBox()
        from_unit.setFixedWidth(125)
        from_unit.setObjectName("conversion_combo")

        from_label = QLabel("From:")
        from_label.setStyleSheet("font-size: 16px;"
                                 "font-family: Roboto;")
        from_label.setFixedWidth(50)

        from_layout.addWidget(from_label)
        from_layout.addWidget(from_value)
        from_layout.addWidget(from_unit)
        conversion_layout.addLayout(from_layout)

        # Creating the 'To' part:
        to_layout = QHBoxLayout()
        to_value = QLineEdit()
        to_value.setFixedHeight(45)
        to_value.setObjectName("conversion_result")
        to_value.setReadOnly(True)  # Result field should be read-only

        to_unit = QComboBox()
        to_unit.setFixedWidth(125)
        to_unit.setObjectName("conversion_combo")

        to_label = QLabel("To:")
        to_label.setStyleSheet("font-size: 16px;"
                               "font-family: Roboto;")
        to_label.setFixedWidth(50)

        to_layout.addWidget(to_label)

        to_layout.addWidget(to_value)
        to_layout.addWidget(to_unit)
        conversion_layout.addLayout(to_layout)

        # Add the conversion layout to main layout
        layout.addLayout(conversion_layout)

        layout.addSpacing(70)

        # NUMPAD SECTION
        numpad_widget = QWidget()
        numpad_layout = QGridLayout()
        numpad_layout.setSpacing(5)

        # Define numpad buttons
        numpad_buttons = [
            ['C', '⌫', '±'],
            ['7', '8', '9'],
            ['4', '5', '6'],
            ['1', '2', '3'],
            ['.', '0', '00']
        ]

        self.num_buttons = []

        # Create numpad buttons
        for row, button_row in enumerate(numpad_buttons):
            for col, button_text in enumerate(button_row):
                button = QPushButton(button_text)
                button.setFixedSize(100, 70)
                button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

                self.numpad_buttons.append(button)
                # Connect button clicks using lambda
                button.clicked.connect(lambda checked, text=button_text: self.handle_numpad_input(text, from_value))
                numpad_layout.addWidget(button, row, col)

        numpad_widget.setLayout(numpad_layout)
        layout.addWidget(numpad_widget)

        # Store references for this conversion type
        setattr(self, f"{conversion_type.lower().replace(' ', '_')}_from_value", from_value)
        setattr(self, f"{conversion_type.lower().replace(' ', '_')}_to_value", to_value)
        setattr(self, f"{conversion_type.lower().replace(' ', '_')}_from_unit", from_unit)
        setattr(self, f"{conversion_type.lower().replace(' ', '_')}_to_unit", to_unit)

        # Setup units for the dropdowns
        self.setup_conversion_units(conversion_type, from_unit, to_unit)

        # Connect to parameterless methods using instance variables
        from_value.textChanged.connect(self.perform_current_conversion)
        from_unit.currentTextChanged.connect(self.perform_current_conversion)
        to_unit.currentTextChanged.connect(self.perform_current_conversion)

        layout.addStretch()
        page.setLayout(layout)

        if self.current_theme == 'light':
            self.apply_light_theme()
        else:
            self.apply_dark_theme()
        return page

    def handle_numpad_input(self, button_text, target_field):
        """Handle numpad button clicks"""
        current_text = target_field.text()

        if button_text == 'C':
            target_field.clear()
        elif button_text == '⌫':
            target_field.setText(current_text[:-1])
        elif button_text == '±':
            if current_text and current_text != '0':
                if current_text.startswith('-'):
                    target_field.setText(current_text[1:])
                else:
                    target_field.setText('-' + current_text)
        elif button_text == '00':
            target_field.setText(current_text + '00')
        else:  # Numbers and decimal point
            if button_text == '.' and '.' in current_text:
                return  # Prevent multiple decimal points
            target_field.setText(current_text + button_text)

    def perform_current_conversion(self):
        """Perform conversion using the stored current_conversion_type"""
        if hasattr(self, 'current_conversion_type'):
            self.perform_specific_conversion(self.current_conversion_type)

    def go_back_to_conversions(self):
        """Return to the main conversions list"""
        self.page_layout.setCurrentWidget(self.conversions_page)
        self.mode_label.setText("Conversions")

    def setup_conversion_units(self, conversion_type, from_combo, to_combo):
        """Setup the units for a specific conversion type"""
        if conversion_type in self.conversion_data:
            if conversion_type == "Temperature":
                units = self.conversion_data[conversion_type]["units"]
            else:
                units = list(self.conversion_data[conversion_type]["units"].keys())

            from_combo.addItems(units)
            to_combo.addItems(units)

            # Set different defaults
            if len(units) > 1:
                to_combo.setCurrentIndex(1)

    def perform_specific_conversion(self, conversion_type):
        """Perform conversion for a specific type"""
        try:
            # Get the widgets for this conversion type
            attr_base = conversion_type.lower().replace(' ', '_')
            from_value = getattr(self, f"{attr_base}_from_value")
            to_value = getattr(self, f"{attr_base}_to_value")
            from_unit = getattr(self, f"{attr_base}_from_unit")
            to_unit = getattr(self, f"{attr_base}_to_unit")

            input_text = from_value.text().strip()
            if not input_text:
                to_value.clear()
                return

            value = float(input_text)
            from_unit_name = from_unit.currentText()
            to_unit_name = to_unit.currentText()

            # Perform conversion
            if conversion_type == "Temperature":
                result = self.convert_temperature(value, from_unit_name, to_unit_name)
            else:
                # Standard conversion
                units_data = self.conversion_data[conversion_type]["units"]
                from_factor = units_data[from_unit_name]
                to_factor = units_data[to_unit_name]

                # Convert to base unit, then to target unit
                base_value = value * from_factor
                result = base_value / to_factor

            # Display result
            result_text = self.format_result(result)
            to_value.setText(result_text)

        except ValueError:
            to_value.setText("Invalid input")
        except Exception:
            to_value.setText("Error")

    def convert_temperature(self, value, from_unit, to_unit):
        """Handle temperature conversions"""
        if from_unit == to_unit:
            return value

        # Convert to Celsius first
        if from_unit == "Fahrenheit":
            celsius = (value - 32) * 5 / 9
        elif from_unit == "Kelvin":
            celsius = value - 273.15
        elif from_unit == "Rankine":
            celsius = (value - 491.67) * 5 / 9
        else:  # Celsius
            celsius = value

        # Convert from Celsius to target
        if to_unit == "Fahrenheit":
            return celsius * 9 / 5 + 32
        elif to_unit == "Kelvin":
            return celsius + 273.15
        elif to_unit == "Rankine":
            return celsius * 9 / 5 + 491.67
        else:  # Celsius
            return celsius

def main():
    app = QApplication(sys.argv)
    window = Calculator()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()