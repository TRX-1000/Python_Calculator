import math
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QGridLayout, QPushButton, QVBoxLayout, QSizePolicy, \
     QLabel, QHBoxLayout, QListWidget, QMainWindow, QFrame, QStackedWidget, QComboBox, QMenu, QAction, QRadioButton

# QSizePolicy helps to scale the widgets in accordance to the window size
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect, QEasingCurve  # For alignment and animations

from PyQt5.QtGui import QIcon

class Calculator(QMainWindow):
    def __init__(self):
        super().__init__()
        # Calls the parent QWidget constructor

        self.setWindowTitle("Calculator")

        self.setGeometry(600, 200, 400, 700)
        self.setMinimumSize(400, 700)
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
        display_layout.setSpacing(0)

        # Create the actual QLineEdit display
        self.display = QLineEdit()
        self.display.setAlignment(Qt.AlignRight)
        # Use a fixed height but allow the width to expand with the window
        self.display.setFixedHeight(80)
        self.display.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        # Reduce padding slightly so the display doesn't overhang neighboring widgets
        self.display.setStyleSheet("font-size: 32px; padding: 8px; margin: 0px;")

        display_layout.addWidget(self.display)
        self.display_container.setLayout(display_layout)

        # Creating a button to toggle the history panel
        self.history_button = QPushButton()
        self.history_button.setIcon(QIcon("icons/history_icon.svg"))  
        self.history_button.setToolTip("Show/Hide History")
        self.history_button.setFixedSize(40, 40)

        # Create central widget: In QMainWindow, you can't just add layouts directly; you need to set a centralWidget
        # that holds the main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Creating an overlay-type sidebar (like the Windows calculator) to display additional options
        self.sidebar = QFrame(self)
        # Ensure object name matches stylesheet selectors that target #sidebar
        self.sidebar.setObjectName('sidebar')
        self.sidebar.setGeometry(0, 0, 200, self.height())
        self.sidebar.setStyleSheet("background-color: #2c2c2c;"
                                   "color: white;")
        self.sidebar.hide()  # Sidebar is hidden initially
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(0, 0, 0, 0)
        self.sidebar_layout.setSpacing(0)

        # Menu options:
        self.menu_list = QListWidget(self.sidebar)
        self.menu_list.setObjectName("menu_list")
        self.menu_list.addItems(["Standard", "Advanced", "Conversions"])
        self.menu_list.itemClicked.connect(self.change_mode)
        self.sidebar_layout.addWidget(self.menu_list)  # Add to layout instead

        self.sidebar_layout.addStretch()  # Pushes menu to the top

        # Settings button at the bottom of the sidebar
        self.settings_button = QPushButton("⚙️ Settings", self.sidebar)
        self.settings_button.setStyleSheet("font-size: 18px; padding: 10px; background: none; border: none;")
        self.settings_button.setToolTip("Settings")
        self.sidebar_layout.addWidget(self.settings_button, alignment=Qt.AlignBottom)

        # Creating a right side sidebar for displaying history
        self.right_sidebar = QWidget(self)
        self.right_sidebar.setFixedWidth(250)
        self.right_sidebar.setGeometry(self.width(), 0, 250, self.height() - 60)

        right_layout = QVBoxLayout(self.right_sidebar)
        right_layout.setContentsMargins(10, 10, 10, 10)

        # History title
        history_title = QLabel("History")
        history_title.setStyleSheet("font-size: 24px; font-weight: bold; font-family: Roboto;")
        right_layout.addWidget(history_title)

        self.history_open = False
        self.menu_open = False

        # Separate histories for standard and advanced modes
        self.standard_history = QListWidget()
        self.advanced_history = QListWidget()

        # Adding double click functionality to history items
        self.standard_history.itemDoubleClicked.connect(self.use_history_item)
        self.advanced_history.itemDoubleClicked.connect(self.use_history_item)


        # Creating a stacked widget (switches with mode)
        self.history_stack = QStackedWidget()
        self.history_stack.addWidget(self.standard_history)  # index 0
        self.history_stack.addWidget(self.advanced_history)  # index 1
        right_layout.addWidget(self.history_stack)
        self.history_stack.setCurrentIndex(0)  # Default to standard history
        self.history_button.clicked.connect(self.toggle_history)

        # Clear button at bottom
        right_layout.addStretch()
        clear_btn = QPushButton("Clear History")
        clear_btn.clicked.connect(lambda: self.current_history().clear())
        right_layout.addWidget(clear_btn, alignment=Qt.AlignBottom)

        self.overlay = QWidget(self)
        self.overlay.setStyleSheet("background-color: rgba(0, 0, 0, 80);")
        self.overlay.hide()

        self.overlay.mousePressEvent = self.close_sidebar_on_click


        self.initUI()
        # Calling the function that creates the user interface

    def create_settings_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        theme_container = QWidget()
        theme_layout = QVBoxLayout(theme_container)
        theme_layout.setContentsMargins(0, 0, 0, 0)

        self.theme_toggle_button = QPushButton("Appearance  ▼")
        self.theme_toggle_button.setFixedSize(175, 40)
        self.theme_toggle_button.setCheckable(True)
        self.theme_toggle_button.setChecked(False)
        self.theme_toggle_button.setStyleSheet("""
            QPushButton {
                text-align: left;
                font-size: 22px;
                font-weight: bold;
                border: none;
                padding: 5px;
                font-family: Roboto;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #bdbdbd;
            }
        """)
        theme_layout.addWidget(self.theme_toggle_button)

        # Collapsible content area
        self.theme_content = QFrame()
        self.theme_content.setMaximumHeight(0)
        self.theme_content.setStyleSheet("background: transparent;")

        theme_content_layout = QVBoxLayout(self.theme_content)
        theme_content_layout.setContentsMargins(0, 0, 0, 0)

        # Description label
        desc = QLabel("Select which app theme to display")
        desc.setStyleSheet("font-size: 15px; color: #666; text-align: left;")
        theme_layout.addWidget(desc)

        # Theme radio buttons
        themes = {
            "Light": "light",
            "Dark": "dark",
            "Ocean": "ocean",
            "Forest": "forest",
            "Sunset": "sunset"
        }

        for name, value in themes.items():
            radio = QRadioButton(name)
            radio.toggled.connect(lambda checked, v=value: checked and self.change_theme(v))
            radio.setStyleSheet("font-size: 18px;")
            theme_content_layout.addWidget(radio)

        # Add the collapsible area
        theme_layout.addWidget(self.theme_content)
        layout.addWidget(theme_container)

        # --- Animation for collapsing ---
        self.theme_anim = QPropertyAnimation(self.theme_content, b"maximumHeight")
        self.theme_anim.setDuration(300)
        self.theme_anim.setEasingCurve(QEasingCurve.InOutCubic)

        def toggle_theme_section():
            checked = self.theme_toggle_button.isChecked()
            text = "Appearance  ▲" if checked else "Appearance  ▼"
            self.theme_toggle_button.setText(text)
            start, end = (0, self.theme_content.sizeHint().height()) if checked else (self.theme_content.height(), 0)
            self.theme_anim.setStartValue(start)
            self.theme_anim.setEndValue(end)
            self.theme_anim.start()

        self.theme_toggle_button.clicked.connect(toggle_theme_section)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)

        layout.addSpacing(20)
        
        self.about_container = QWidget()
        self.about_layout = QVBoxLayout(self.about_container)
        self.about_button = QPushButton("About ▼")
        self.about_button.setFixedSize(100, 40)
        self.about_button.setCheckable(True)
        self.about_button.setChecked(False)
        self.about_button.setStyleSheet("""
            QPushButton {
                text-align: left;
                font-size: 22px;
                font-weight: bold;
                border: none;
                padding: 5px;
                font-family: Roboto;
                border-radius: 5px;
            }
            
            QPushButton:hover {
                background-color: #bdbdbd;
            }
        """)

        self.about_layout.addWidget(self.about_button)

        # Collapsible content area:
        self.about_content = QFrame()
        self.about_content.setMaximumHeight(0)
        self.about_content.setStyleSheet("background: tranparent;")
        self.about_content_layout = QVBoxLayout(self.about_content)

        # About label:
        about = QLabel("Calculator\n© 2025 Microsoft. All rights reserved.\nBuild Version: 2.01.25")
        about.setStyleSheet("font-size: 15px; color: #666; text-align: left;")
        
        self.about_layout.addWidget(about)

        self.about_layout.addWidget(self.about_content)
        layout.addWidget(self.about_container)

        # Animation for collapsing:
        self.about_anim = QPropertyAnimation(self.about_content, b"maximumHeight")
        self.about_anim.setDuration(250)
        self.about_anim.setEasingCurve(QEasingCurve.InOutCubic)

        def toggle_about_section():
            checked = self.about_button.isChecked()
            text = "About ▲" if checked else "About ▼"
            self.about_button.setText(text)
            start, end = (0, self.about_content.sizeHint().height()) if checked else (self.about_content.height(), 0)      
            self.about_anim.setStartValue(start)
            self.about_anim.setEndValue(end)
            self.about_anim.start()
        self.about_button.clicked.connect(toggle_about_section)

        layout.addStretch()

        return page
    
    def show_theme_menu_in_settings(self):
        """Show theme menu when button is clicked in settings"""
        theme_menu = QMenu(self)

        # Create theme actions
        light_action = QAction("Light", self)
        light_action.setCheckable(True)
        light_action.triggered.connect(lambda: self.change_theme_from_settings("light"))

        dark_action = QAction("Dark", self)
        dark_action.setCheckable(True)
        dark_action.triggered.connect(lambda: self.change_theme_from_settings("dark"))

        ocean_action = QAction("Ocean", self)
        ocean_action.setCheckable(True)
        ocean_action.triggered.connect(lambda: self.change_theme_from_settings("ocean"))

        forest_action = QAction("Forest", self)
        forest_action.setCheckable(True)
        forest_action.triggered.connect(lambda: self.change_theme_from_settings("forest"))

        sunset_action = QAction("Sunset", self)
        sunset_action.setCheckable(True)
        sunset_action.triggered.connect(lambda: self.change_theme_from_settings("sunset"))

        # Add actions to menu
        theme_menu.addAction(light_action)
        theme_menu.addAction(dark_action)
        theme_menu.addAction(ocean_action)
        theme_menu.addAction(forest_action)
        theme_menu.addAction(sunset_action)

        # Check current theme
        if self.current_theme == "light":
            light_action.setChecked(True)
        elif self.current_theme == "dark":
            dark_action.setChecked(True)
        elif self.current_theme == "ocean":
            ocean_action.setChecked(True)
        elif self.current_theme == "forest":
            forest_action.setChecked(True)
        elif self.current_theme == "sunset":
            sunset_action.setChecked(True)

        # Style the menu based on current theme
        if self.current_theme == "dark":
            theme_menu.setStyleSheet("""
                QMenu {
                    background-color: #2c2c2c;
                    color: white;
                    border: 1px solid #444;
                    font-family: Roboto;
                    font-size: 14px;
                }
                QMenu::item {
                    padding: 8px 16px;
                }
                QMenu::item:selected {
                    background-color: #0078d7;
                }
                QMenu::item:checked {
                    background-color: #0078d7;
                    color: white;
                }
            """)
        else:
            theme_menu.setStyleSheet("""
                QMenu {
                    background-color: white;
                    color: black;
                    border: 1px solid #ccc;
                    font-family: Roboto;
                    font-size: 14px;
                }
                QMenu::item {
                    padding: 8px 16px;
                }
                QMenu::item:selected {
                    background-color: #e0e0e0;
                }
                QMenu::item:checked {
                    background-color: #0078d7;
                    color: white;
                }
            """)

        # Show menu at button position
        menu_pos = self.theme_select_button.mapToGlobal(self.theme_select_button.rect().bottomLeft())
        theme_menu.exec_(menu_pos)

    def change_theme_from_settings(self, theme_name):
        """Change theme and update the settings page label"""
        self.change_theme(theme_name)
        # Update the current theme label in settings
        if hasattr(self, 'current_theme_label'):
            self.current_theme_label.setText(f"Current: {theme_name.capitalize()}")
    
    def apply_settings_light_theme(self):
        self.back_button.setStyleSheet("font-size: 20px; color: black; background-color: white;")
        self.theme_label.setStyleSheet("font-size: 18px; color: black; font-family: Inter; margin-top: 15px;")
        self.theme_dropdown.setFixedSize(200, 40)
        self.theme_dropdown.setStyleSheet("""QComboBox {
                background-color: white;
                color: black;
                font-size: 18px;
                font-family: Roboto;
                border: 2px solid #ccc;
                border-radius: 8px;
            }""")
        self.info_label.setStyleSheet("font-size: 16px; color: gray; font-family: Inter; padding: 10px;")
        
        self.apply_light_theme()
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.overlay.setGeometry(self.centralWidget().rect())

    def show_settings_page(self):
        # Close any open sidebars first
        if self.sidebar.isVisible():
            self.sidebar.hide()
        if self.right_sidebar.isVisible():
            self.right_sidebar.hide()
        
        # Hide overlay
        self.overlay.hide()
        
        # Switch to settings page
        self.page_layout.setCurrentWidget(self.settings_page)
        self.mode_label.setText("Settings")
        self.display_container.hide()

    def current_history(self):
        return self.standard_history if self.history_stack.currentIndex() == 0 else self.advanced_history
    
    def add_to_history(self, expression, result):
        """Add a new item to the appropriate history (standard/advanced)."""
        self.history_item = f"{expression} = {result}"

        if self.mode_label.text().startswith("Standard"):
            self.standard_history.addItem(self.history_item)
        elif self.mode_label.text().startswith("Advanced"):
            self.advanced_history.addItem(self.history_item)

    def use_history_item(self, item):
        """Load expression back into the display when double-clicked."""
        text = item.text()
        if "=" in text:
            expression, result = text.split("=", 1)
            self.display.setText(expression.strip())

    def close_sidebar_on_click(self, event):
        """Close history if overlay is clicked"""
        if self.sidebar.isVisible():
            self.toggle_sidebar()
        elif self.right_sidebar.isVisible():
            self.toggle_history()
        event.accept()

    def toggle_history(self):
        if self.history_open:
                # Slide out (hide)
                anim = QPropertyAnimation(self.right_sidebar, b"geometry")
                anim.setDuration(250)
                anim.setEasingCurve(QEasingCurve.InOutCubic)
                anim.setStartValue(QRect(self.width() - 250, 0, 250, self.height()))
                anim.setEndValue(QRect(self.width(), 0, 250, self.height()))
                anim.finished.connect(lambda: self.right_sidebar.setVisible(False))  # ✅ hide only after animation
                anim.start()
                self.anim = anim
                self.overlay.hide()
                self.history_open = False
        else:
            # Slide in (show)
            self.right_sidebar.setVisible(True)
            self.overlay.setGeometry(self.centralWidget().rect())
            self.overlay.show()
            self.overlay.raise_()
            self.right_sidebar.raise_()

            anim = QPropertyAnimation(self.right_sidebar, b"geometry")
            anim.setDuration(250)
            anim.setEasingCurve(QEasingCurve.InOutCubic)
            anim.setStartValue(QRect(self.width(), 0, 250, self.height()))
            anim.setEndValue(QRect(self.width() - 250, 0, 250, self.height()))
            anim.start()
            self.anim = anim
            self.history_open = True

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

    def initUI(self):
        # Creating the main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)  # Add margins to prevent overhang
        main_layout.setSpacing(5)  # Add consistent spacing

        # Creating a new layout at the top that contains the menu button and the menu label
        # (what screen they are currently on)
        top_bar = QHBoxLayout()
        self.menu_button = QPushButton("☰")
        self.menu_button.setToolTip("Menu")
        self.menu_button.setStyleSheet("font-size: 30px; padding: 2px; background: none;")
        self.menu_button.clicked.connect(self.toggle_sidebar)

        self.mode_label = QLabel("Standard")
        self.mode_label.setStyleSheet("font-size: 30px; font-weight: bold; font-family: Roboto;")
        top_bar.addWidget(self.menu_button)
        top_bar.addWidget(self.mode_label)

        top_bar.addWidget(self.history_button)

        self.theme_button = QPushButton("🎨")
        self.theme_button.setToolTip("Change Theme")
        self.theme_button.setStyleSheet("font-size: 30px; padding: 2px; background: none; border: none;")
        self.theme_button.clicked.connect(self.show_theme_menu)

        top_bar.addStretch()  # Pushes everything to the left side
        top_bar.addWidget(self.theme_button)

        main_layout.insertLayout(0, top_bar)  # Added the top bar to the main layout of the display

        # Adding radio buttons to allow the user to choose between degrees and radians for trigonometric functions:
        angle_mode_layout = QHBoxLayout()
        self.angle_label = QLabel("Angle mode:")
        self.angle_label.setStyleSheet("font-size: 18px; font-family: Roboto;")

        self.angle_mode_combo = QComboBox()
        self.angle_mode_combo.setObjectName("angle_mode_combo")
        self.angle_mode_combo.addItems(["Degrees", "Radians"])
        self.angle_mode_combo.setCurrentText("Degrees")  # Default to degrees
        self.angle_mode_combo.setFixedWidth(120)
        
        self.angle_mode = "deg"  # Default
        self.angle_mode_combo.currentTextChanged.connect(self.set_angle_mode_from_dropdown)
        
        angle_mode_layout.addWidget(self.angle_label)
        angle_mode_layout.addWidget(self.angle_mode_combo)
        angle_mode_layout.addStretch()  # Push to left
        
        main_layout.addLayout(angle_mode_layout)
        
        # Initially hide the angle mode dropdown (instead of radio buttons)
        self.angle_label.hide()
        self.angle_mode_combo.hide()

        main_layout.addWidget(self.display_container)
        # Now this display shows up


        # Creating a page container so that when the user clicks a button in the sidebar,
        # the page changes (page container contains all the pages so that switching is easy)
        self.page_layout = QStackedWidget()
        self.standard_page = self.create_standard_calc()
        self.advanced_page = self.create_adv_calc()
        self.conversions_page = self.create_conversions_page()
        self.settings_page = self.create_settings_page()

        self.page_layout.addWidget(self.standard_page)  # Added Standard page to the stack widget
        self.page_layout.addWidget(self.advanced_page)  # Added Advanced page to the stack widget
        self.page_layout.addWidget(self.conversions_page)  # Added Conversions page to the stack widget
        self.page_layout.addWidget(self.settings_page)  # Added settings page to the stack widget
        self.page_layout.setCurrentWidget(self.standard_page)  # Defaults to the standard page
        main_layout.addWidget(self.page_layout)

        self.settings_button.clicked.connect(self.show_settings_page)


        self.central_widget.setLayout(main_layout)

        # Apply light theme by default:
        self.apply_light_theme()

    def set_angle_mode_from_dropdown(self):
        selected = self.angle_mode_combo.currentText()
        if selected == "Degrees":
            self.angle_mode = "deg"
        else:
            self.angle_mode = "rad"

    def show_theme_menu(self):
        """Show the theme selection menu directly"""
        theme_menu = QMenu(self)

        # Create theme actions directly
        light_action = QAction("Light", self)
        light_action.setCheckable(True)
        light_action.triggered.connect(lambda: self.change_theme("light"))

        dark_action = QAction("Dark", self)
        dark_action.setCheckable(True)
        dark_action.triggered.connect(lambda: self.change_theme("dark"))

        ocean_action = QAction("Ocean", self)
        ocean_action.setCheckable(True)
        ocean_action.triggered.connect(lambda: self.change_theme("ocean"))

        forest_action = QAction("Forest", self)
        forest_action.setCheckable(True)
        forest_action.triggered.connect(lambda: self.change_theme("forest"))

        sunset_action = QAction("Sunset", self)
        sunset_action.setCheckable(True)
        sunset_action.triggered.connect(lambda: self.change_theme("sunset"))

        # Add actions directly to menu
        theme_menu.addAction(light_action)
        theme_menu.addAction(dark_action)
        theme_menu.addAction(ocean_action)
        theme_menu.addAction(forest_action)
        theme_menu.addAction(sunset_action)

        # Check the current theme
        if self.current_theme == "light":
            light_action.setChecked(True)
        elif self.current_theme == "dark":
            dark_action.setChecked(True)
        elif self.current_theme == "ocean":
            ocean_action.setChecked(True)
        elif self.current_theme == "forest":
            forest_action.setChecked(True)
        elif self.current_theme == "sunset":
            sunset_action.setChecked(True)

        # Style the menu based on current theme
        if self.current_theme == "dark":
            theme_menu.setStyleSheet("""
                QMenu {
                    background-color: #2c2c2c;
                    color: white;
                    border: 1px solid #444;
                    font-family: Roboto;
                    font-size: 14px;
                }
                QMenu::item {
                    padding: 8px 16px;
                }
                QMenu::item:selected {
                    background-color: #0078d7;
                }
                QMenu::item:checked {
                    background-color: #0078d7;
                    color: white;
                }
            """)
        else:
            theme_menu.setStyleSheet("""
                QMenu {
                    background-color: white;
                    color: black;
                    border: 1px solid #ccc;
                    font-family: Roboto;
                    font-size: 14px;
                }
                QMenu::item {
                    padding: 8px 16px;
                }
                QMenu::item:selected {
                    background-color: #e0e0e0;
                }
                QMenu::item:checked {
                    background-color: #0078d7;
                    color: white;
                }
            """)

        # Show menu at button position
        menu_pos = self.theme_button.mapToGlobal(self.theme_button.rect().bottomLeft())
        theme_menu.exec_(menu_pos)

    def change_theme(self, theme_name):
        """Change the theme based on selection"""
        self.current_theme = theme_name

        if theme_name == "light":
            self.apply_light_theme()
            self.apply_sidebar_theme_light()

        elif theme_name == "dark":
            self.apply_dark_theme()
            self.apply_sidebar_theme_dark()

        elif theme_name == "ocean":
            self.apply_ocean_theme()
            self.apply_sidebar_theme_ocean()

        elif theme_name == "forest":
            self.apply_forest_theme()
            self.apply_sidebar_theme_forest()

        elif theme_name == "sunset":
            self.apply_sunset_theme()
            self.apply_sidebar_theme_sunset()

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


        self.menu_button.setStyleSheet("""
                QPushButton {
                    background-color: white;
                    color: #000; 
                    border: none;
                    font-size: 30px;
                    border-radius: 5px;
                    padding: 7px; }
                                       
                QPushButton:hover {
                    background-color: #bdbdbd;
                    }
                """)
        
        self.theme_button.setStyleSheet("""
                QPushButton {
                    background: none;
                    font-size: 30px;
                    border: none;
                    padding: 2px;
                    color: #ffffff;
                }
                QPushButton:hover {
                    background-color: #bdbdbd;
                    border-radius: 5px;
                }
            """)
        
        self.mode_label.setStyleSheet("font-size: 30px; font-weight: bold; font-family: Roboto; color: #000000;")

    def apply_sidebar_theme_ocean(self):
        self.sidebar.setStyleSheet("""
                            QFrame {
                                background-color: #74c0fc;
                                border-right: 1px solid #d0ebff;
                            }
                            QListWidget {
                                background: #d0ebff;
                                color: #0b3954;
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

        # Theme button - Style it BEFORE calling sidebar theme
        self.theme_button.setStyleSheet("""
            QPushButton {
                background: none;
                font-size: 30px;
                border: none;
                padding: 2px;
                color: #275569;
            }
            QPushButton:hover {
                background-color: #b8eaff;
                border-radius: 5px;
            }
        """)

        # Menu button - Style it BEFORE calling sidebar theme  
        self.menu_button.setStyleSheet("""
            QPushButton {
                background-color: #e0f7fa;
                color: #0a3d62; 
                border: none;
                font-size: 30px;
                border-radius: 5px;
                padding: 7px;
            }
            QPushButton:hover {
                background-color: #b8eaff;
            }
        """)

        # Mode label
        self.mode_label.setStyleSheet("font-size: 30px; font-weight: bold; font-family: Roboto; color: #0a3d62;")

    def apply_sidebar_theme_forest(self):
        self.sidebar.setStyleSheet("""
        QFrame {
            background-color: #d4e6d4;
            border-right: 1px solid #9cbf9c;
        }
        QListWidget {
            background: transparent;
            color: #2d3a2d;
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
            background-color: #c4dcc4;
        }
        QListWidget::item:selected {
            background-color: #7ba05b;
            color: white;
        }
    """)
        
        # Theme button
        self.theme_button.setStyleSheet("""
            QPushButton {
                background: none;
                font-size: 30px;
                border: none;
                padding: 2px;
                color: #2d3a2d;
            }
            QPushButton:hover {
                background-color: #b9d1a9;
                border-radius: 5px;
            }
        """)

        # Menu button  
        self.menu_button.setStyleSheet("""
            QPushButton {
                background-color: #f3f7f2;
                color: #2d3a2d; 
                border: none;
                font-size: 30px;
                border-radius: 5px;
                padding: 7px;
            }
            QPushButton:hover {
                background-color: #b9d1a9;
            }
        """)

        # Mode label
        self.mode_label.setStyleSheet("font-size: 30px; font-weight: bold; font-family: Roboto; color: #2d3a2d;")

    def apply_sidebar_theme_sunset(self):
        self.sidebar.setStyleSheet("""
        QFrame {
            background-color: #ffe0b2;
            border-right: 2px solid #f7b267;
        }
        QListWidget {
            background: transparent;
            color: #5c2e1f;
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
            background-color: #ffcc80;
        }
        QListWidget::item:selected {
            background-color: #ff7043;
            color: white;
        }
    """)

    # Theme button
        self.theme_button.setStyleSheet("""
            QPushButton {
                background: none;
                font-size: 30px;
                border: none;
                padding: 2px;
                border-radius: 5px;

                color: #ffffff;
            }
            QPushButton:hover {
                background-color: #f7c59f;
            }
        """)

        # Menu button  
        self.menu_button.setStyleSheet("""
            QPushButton {
                background-color: #fff4e6;
                color: #5c2e1f; 
                border: none;
                font-size: 30px;
                border-radius: 5px;
                padding: 7px;
            }
            QPushButton:hover {
                background-color: #f7c59f;
            }
        """)

        # Mode label
        self.mode_label.setStyleSheet("font-size: 30px; font-weight: bold; font-family: Roboto; color: #5c2e1f;")

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

        # Theme button
        self.theme_button.setStyleSheet("""
            QPushButton {
                background: none;
                font-size: 30px;
                border: none;
                padding: 2px;
                border-radius: 5px;

                color: #ffffff;
            }
            QPushButton:hover {
                background-color: #3c3c3c;
            }
        """)

        # Menu button  
        self.menu_button.setStyleSheet("""
            QPushButton {
                background-color: #2c2c2c;
                color: #ffffff; 
                border: none;
                font-size: 30px;
                border-radius: 5px;
                padding: 7px;
            }
            QPushButton:hover {
                background-color: #3c3c3c;
            }
        """)

        # Mode label
        self.mode_label.setStyleSheet("font-size: 30px; font-weight: bold; font-family: Roboto; color: #ffffff;")
        
    def toggle_sidebar(self):
        if self.sidebar.isVisible():
            # Hide sidebar
            anim = QPropertyAnimation(self.sidebar, b"geometry")
            anim.setDuration(250)
            anim.setEasingCurve(QEasingCurve.InOutCubic)
            anim.setStartValue(QRect(0, 0, 250, self.height()))     
            anim.setEndValue(QRect(-250, 0, 250, self.height()))    
            anim.finished.connect(lambda: self.sidebar.setVisible(False))  
            anim.start()
            self.anim = anim
            self.overlay.hide()
            self.menu_open = False
        else:
            # Show sidebar
            self.sidebar.setVisible(True)
            self.overlay.setGeometry(self.centralWidget().rect())
            self.overlay.show()
            self.overlay.raise_()
            self.sidebar.raise_()
            anim = QPropertyAnimation(self.sidebar, b"geometry")
            anim.setDuration(250)
            anim.setEasingCurve(QEasingCurve.InOutCubic)
            anim.setStartValue(QRect(-250, 0, 250, self.height()))
            anim.setEndValue(QRect(0, 0, 200, self.height()))
            anim.start()
            self.anim_sidebar = anim

    def change_mode(self, item):
        mode = item.text()
        self.mode_label.setText(mode)

        if self.overlay.isVisible():
            self.overlay.hide()
        if hasattr(self, "right_sidebar") and self.right_sidebar.isVisible():
            self.right_sidebar.setVisible(False)
        if hasattr(self, "sidebar") and self.sidebar.isVisible():
            self.sidebar.setVisible(False)

        if mode == 'Standard':
            self.page_layout.setCurrentWidget(self.standard_page)
            # If you only pass self.create_standard_calc, you are only passing the function to the change_mode
            # function, not the page, so it will throw an error
            self.display_container.show()
            self.display.clear()  # Clear the display while switching modes
            self.history_stack.setCurrentIndex(0)  # Switch to standard history

        elif mode == "Advanced":
            self.page_layout.setCurrentWidget(self.advanced_page)
            self.display_container.show()
            self.display.clear()
            

        elif mode == "Conversions":
            self.page_layout.setCurrentWidget(self.conversions_page)
            self.display_container.hide()
        self.sidebar.hide()
        # Hide the sidebar when the user selects desired button

    def apply_light_theme(self):
        self.display.setStyleSheet("""QLineEdit {
                background-color: #ffffff;
                color: #000000;
                font-size: 42px;
                font-family: SF Mono, monospace;
                padding: 7px;
                border: 2px solid #999;
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
                border-radius: 5px;
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


        self.apply_sidebar_theme_light()
        # Here, if we call the same function (apply_light_theme), Python will throw a RecursionError
        # as the function is being called infinite number of times

    def apply_ocean_theme(self):
        # Display
        self.display.setStyleSheet("""
            QLineEdit {
                background-color: #e0f7fa;
                color: #275569;
                font-size: 42px;
                font-family: SF Mono, monospace;
                padding: 7px;
                border: 2px solid #0277bd;
                border-radius: 8px;
            }
        """)

        # Base widget + conversion inputs
        self.setStyleSheet("""
            QWidget {
                background-color: #e0f7fa;
                color: #275569;
            }
            QLineEdit#conversion_input, QLineEdit#conversion_result {
                background-color: #f1fbff;
                color: #0a3d62;
                font-size: 20px;
                font-family: SF Mono;
                border: 2px solid #74a9cf;
                border-radius: 8px;
            }
            QComboBox#conversion_combo {
                    background-color: #b8eaff;
                    color: #133c55;
                    font-size: 18px;
                    font-family: Roboto;
                    border: 2px solid #74a9cf;
                    border-radius: 8px;
                }
            """)

            # Buttons
        for button in self.standard_buttons + self.advanced_buttons:
                text = button.text()
                if text in ['+', '-', '×', '÷', '1/x', '%']:
                    button.setStyleSheet("""
                        QPushButton {
                            background-color: #bcd4e6;  
                            color: #133c55;
                            font-size: 25px;
                            font-family: Inter;
                            border-radius: 5px;
                            border: 1px solid #74a9cf;
                        }
                        QPushButton:hover {
                            background-color: #74a9cf;
                            color: white;
                        }
                    """)
                elif text in ['C', '⌫']:
                    button.setStyleSheet("""
                        QPushButton {
                            background-color: #ffb3b3; 
                            color: #7f1d1d;
                            font-size: 25px;
                            font-family: Inter;
                            border-radius: 5px;
                            border: 1px solid #ff6b6b;
                        }
                        QPushButton:hover {
                            background-color: #ff6b6b;
                        }
                    """)
                elif text == '=':
                    button.setStyleSheet("""
                        QPushButton {
                            background-color: #99e2b4; 
                            color: #1b4332;
                            font-size: 25px;
                            font-family: Inter;
                            border-radius: 5px;
                            border: 1px solid #52b788;
                        }
                        QPushButton:hover {
                            background-color: #52b788;
                            color: white;
                        }
                    """)
                elif text in ['n!', 'mod', 'sin', 'asin', 'cos', 'acos', 'tan', 'atan',
                            'log', 'ln', 'π', 'e', 'x²', 'x³', '√x', '³√x', '10^x', 'exp',
                            'xʸ', 'nCr', 'nPr', '(', ')']:
                    button.setStyleSheet("""
                        QPushButton {
                            background-color: #dbd9fc;  
                            color: #343161;
                            font-size: 22px;
                            font-family: Inter;
                            border-radius: 5px;
                        }
                        QPushButton:hover {
                            background-color: #bab6fa;
                        }
                    """)
                else:
                    button.setStyleSheet("""
                        QPushButton {
                            background-color: #f1fbff;  
                            color: #0a3d62;
                            font-size: 25px;
                            font-family: Inter;
                            border-radius: 5px;
                            border: 1px solid #cce9f9;
                        }
                        QPushButton:hover {
                            background-color: #cce9f9;
                        }
                    """)

            # Extra buttons
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

            # More functions button
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
                    background-color: #ffd9b3;
                    border: 2px solid #cbd5e1;
                }
            """)

            # Numpad buttons
        for button in self.numpad_buttons:
            text = button.text()
            if text in ['C', '⌫']:
                    button.setStyleSheet("""
                        QPushButton {
                            background-color: #ffb3b3; 
                            color: #7f1d1d;
                            font-size: 25px;
                            font-family: Inter;
                            border-radius: 5px;
                            border: 1px solid #ff6b6b;
                        }
                        QPushButton:hover {
                            background-color: #ff6b6b;
                        }
                    """)
            else:
                    button.setStyleSheet("""
                        QPushButton {
                            background-color: #f1fbff;  
                            color: #0a3d62;
                            font-size: 25px;
                            font-family: Inter;
                            border-radius: 5px;
                            border: 1px solid #cce9f9;
                        }
                        QPushButton:hover {
                            background-color: #cce9f9;
                        }
                    """)
            
            self.conversion_list.setStyleSheet("""
                QListWidget {
                    font-size: 18px;
                    font-family: Inter;
                    background-color: #f1fbff;
                    color: #0a3d62;
                    border: 2px solid #74a9cf;  
                    border-radius: 8px;
                    padding: 5px;
                }
                QListWidget::item {
                    padding: 12px;
                    margin: 2px;
                    border-radius: 5px;
                }
                QListWidget::item:hover {
                    background-color: #e3f2fd;
                }
                QListWidget::item:selected {
                    background-color: #2196f3;
                    color: white;
                }
            """)

    # Apply sidebar theme LAST to avoid overwriting the button styles
        self.apply_sidebar_theme_ocean()

    def apply_forest_theme(self):
        # Display
        self.display.setStyleSheet("""
            QLineEdit {
                background-color: #f3f7f2;
                color: #2d3a2d;
                font-size: 42px;
                font-family: SF Mono, monospace;
                padding: 7px;
                border: 2px solid #a3c9a8;
                border-radius: 8px;
            }
        """)

        # Base widget + conversion inputs
        self.setStyleSheet("""
            QWidget {
                background-color: #f3f7f2;
                color: #2d3a2d;
            }
            QLineEdit#conversion_input, QLineEdit#conversion_result {
                background-color: #f9fdf7;
                color: #2f4430;
                font-size: 20px;
                font-family: SF Mono;
                border: 2px solid #9cbf9c;
                border-radius: 8px;
            }
            QComboBox#conversion_combo {
                background-color: #dbead1;
                color: #2f4430;
                font-size: 18px;
                font-family: Roboto;
                border: 2px solid #9cbf9c;
                border-radius: 8px;
            }
        """)

        # Buttons
        for button in self.standard_buttons + self.advanced_buttons:
            text = button.text()
            if text in ['+', '-', '×', '÷', '1/x', '%']:
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #cddfbf;  
                        color: #2a3d1f;
                        font-size: 25px;
                        font-family: Inter;
                        border-radius: 5px;
                        border: 1px solid #7ba05b;
                    }
                    QPushButton:hover {
                        background-color: #b6d1a6;
                        color: white;
                    }
                """)
            elif text in ['C', '⌫']:
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #f2d6c1;  
                        color: #5c2c0c;
                        font-size: 25px;
                        font-family: Inter;
                        border-radius: 5px;
                        border: 1px solid #d4a373;
                    }
                    QPushButton:hover {
                        background-color: #eac2a3;
                    }
                """)
            elif text == '=':
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #8fbc8f;  
                        color: #ffffff;
                        font-size: 25px;
                        font-family: Inter;
                        border-radius: 5px;
                        border: 1px solid #5f8d5f;
                    }
                    QPushButton:hover {
                        background-color: #769f76;
                        color: white;
                    }
                """)
            elif text in ['n!', 'mod', 'sin', 'asin', 'cos', 'acos', 'tan', 'atan',
                        'log', 'ln', 'π', 'e', 'x²', 'x³', '√x', '³√x', '10^x', 'exp',
                        'xʸ', 'nCr', 'nPr', '(', ')']:
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #e9dccd;  
                        color: #4a3728;
                        font-size: 22px;
                        font-family: Inter;
                        border-radius: 5px;
                        border: 1px solid #c8ad7f;
                    }
                    QPushButton:hover {
                        background-color: #dbc9b4;
                    }
                """)
            else:
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #dcefe2;  
                        color: #2e4733;
                        font-size: 25px;
                        font-family: Inter;
                        border-radius: 5px;
                        border: 1px solid #a3c9a8;
                    }
                    QPushButton:hover {
                        background-color: #cde6d4;
                    }
                """)

        # Extra buttons
        for button in self.extra_btn_objs:
            button.setStyleSheet("""
                QPushButton {
                    background-color: #e6b980;  
                    color: #4a2c0a;
                    font-size: 25px;
                    font-family: Inter;
                    border-radius: 5px;
                    border: 1px solid #d1904f;
                }
                QPushButton:hover {
                    background-color: #d9a868;
                }
            """)

        # More functions button
        self.more_functions_button.setStyleSheet("""
            QPushButton {
                background-color: #e6b980; 
                color: #4a2c0a;
                font-size: 20px;
                font-family: Inter;
                border-radius: 5px;
                border: 1px solid #d1904f;
            }
            QPushButton:hover {
                background-color: #d9a868;
            }
            QPushButton:checked {
                background-color: #d9a868;
                border: 2px solid #c89f7a;
            }
        """)

        # Numpad buttons
        for button in self.numpad_buttons:
            text = button.text()
            if text in ['C', '⌫']:
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #f2d6c1;  
                        color: #5c2c0c;
                        font-size: 25px;
                        font-family: Inter;
                        border-radius: 5px;
                        border: 1px solid #d4a373;
                    }
                    QPushButton:hover {
                        background-color: #eac2a3;
                    }
                """)
            else:
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #dcefe2;  
                        color: #2e4733;
                        font-size: 25px;
                        font-family: Inter;
                        border-radius: 5px;
                        border: 1px solid #a3c9a8;
                    }
                    QPushButton:hover {
                        background-color: #cde6d4;
                    }
                """)

        self.conversion_list.setStyleSheet("""
            QListWidget {
                font-size: 18px;
                font-family: Inter;
                background-color: #f9fdf7;
                color: #2f4430;
                border: 2px solid #9cbf9c;
                border-radius: 8px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 12px;
                margin: 2px;
                border-radius: 5px;
            }
            QListWidget::item:hover {
                background-color: #e0f0e0;
            }
            QListWidget::item:selected {
                background-color: #5f8d5f;
                color: white;
            }
        """)

        self.apply_sidebar_theme_forest()

    def apply_sunset_theme(self):
        # Display
        self.display.setStyleSheet("""
            QLineEdit {
                background-color: #fff4e6;
                color: #5c2e1f;
                font-size: 42px;
                font-family: SF Mono, monospace;
                padding: 7px;
                border: 2px solid #f7c59f;
                border-radius: 8px;
            }
        """)

        # Base widget + conversion inputs
        self.setStyleSheet("""
            QWidget {
                background-color: #fff4e6;
                color: #5c2e1f;
            }
            QLineEdit#conversion_input, QLineEdit#conversion_result {
                background-color: #fff9f4;
                color: #4a1f1f;
                font-size: 20px;
                font-family: SF Mono;
                border: 2px solid #f7c59f;
                border-radius: 8px;
            }
            QComboBox#conversion_combo {
                background-color: #ffe0b2;
                color: #4a1f1f;
                font-size: 18px;
                font-family: Roboto;
                border: 2px solid #f7c59f;
                border-radius: 8px;
            }
        """)

        # Buttons
        for button in self.standard_buttons + self.advanced_buttons:
            text = button.text()
            if text in ['+', '-', '×', '÷', '1/x', '%']:
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #ffccbc;  
                        color: #5c2e1f;
                        font-size: 25px;
                        font-family: Inter;
                        border-radius: 5px;
                        border: 1px solid #ff8a65;
                    }
                    QPushButton:hover {
                        background-color: #ffab91;
                        color: white;
                    }
                """)
            elif text in ['C', '⌫']:
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #fcefe6; 
                        color: #6d2f1a;
                        font-size: 25px;
                        font-family: Inter;
                        border-radius: 5px;
                        border: 1px solid #e0b7a0;
                    }
                    QPushButton:hover {
                        background-color: #f7d9c4;
                    }
                """)
            elif text == '=':
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #ff7043; 
                        color: #ffffff;
                        font-size: 25px;
                        font-family: Inter;
                        border-radius: 5px;
                        border: 1px solid #d84315;
                    }
                    QPushButton:hover {
                        background-color: #e64a19;
                        color: white;
                    }
                """)
            elif text in ['n!', 'mod', 'sin', 'asin', 'cos', 'acos', 'tan', 'atan',
                        'log', 'ln', 'π', 'e', 'x²', 'x³', '√x', '³√x', '10^x', 'exp',
                        'xʸ', 'nCr', 'nPr', '(', ')']:
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #ffd180;
                        color: #4a2500;
                        font-size: 22px;
                        font-family: Inter;
                        border-radius: 5px;
                        border: 1px solid #ffab40;
                    }
                    QPushButton:hover {
                        background-color: #ffb74d;
                    }
                """)
            else:
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #ffe0b2;  
                        color: #5c2e1f;
                        font-size: 25px;
                        font-family: Inter;
                        border-radius: 5px;
                        border: 1px solid #f7c59f;
                    }
                    QPushButton:hover {
                        background-color: #ffcc80;
                    }
                """)

        # Extra buttons
        for button in self.extra_btn_objs:
            button.setStyleSheet("""
                QPushButton {
                    background-color: #fdd9a0;  
                    color: #5c2e1f;
                    font-size: 25px;
                    font-family: Inter;
                    border-radius: 5px;
                    border: 1px solid #f7b267;
                }
                QPushButton:hover {
                    background-color: #fbb76b;
                }
            """)

        # More functions button
        self.more_functions_button.setStyleSheet("""
            QPushButton {
                background-color: #fdd9a0; 
                color: #5c2e1f;
                font-size: 20px;
                font-family: Inter;
                border-radius: 5px;
                border: 1px solid #f7b267;
            }
            QPushButton:hover {
                background-color: #fbb76b;
            }
            QPushButton:checked {
                background-color: #ffab91;
                border: 2px solid #f7c59f;
            }
        """)

        # Numpad buttons
        for button in self.numpad_buttons:
            text = button.text()
            if text in ['C', '⌫']:
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #fcefe6; 
                        color: #6d2f1a;
                        font-size: 25px;
                        font-family: Inter;
                        border-radius: 5px;
                        border: 1px solid #e0b7a0;
                    }
                    QPushButton:hover {
                        background-color: #f7d9c4;
                    }
                """)
            else:
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #ffe0b2;  
                        color: #5c2e1f;
                        font-size: 25px;
                        font-family: Inter;
                        border-radius: 5px;
                        border: 1px solid #f7c59f;
                    }
                    QPushButton:hover {
                        background-color: #ffcc80;
                    }
                """)

        self.conversion_list.setStyleSheet("""
            QListWidget {
                font-size: 18px;
                font-family: Inter;
                background-color: #fff9f4;
                color: #4a1f1f;
                border: 2px solid #f7c59f;
                border-radius: 8px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 12px;
                margin: 2px;
                border-radius: 5px;
            }
            QListWidget::item:hover {
                background-color: #ffe0b2;
            }
            QListWidget::item:selected {
                background-color: #ff7043;
                color: white;
            }
        """)

        self.apply_sidebar_theme_sunset()

    def apply_dark_theme(self):
        self.display.setStyleSheet("""QLineEdit {
                background-color: #2b2b2b;
                color: #ffffff;
                font-size: 42px;
                font-family: SF Mono;
                padding: 7px;
                border: 2px solid #666666;
                border-radius: 8px;
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
                border-radius: 8px;
            }
            QLineEdit#conversion_result {
                background-color: #1e1e1e;
                color: #ffffff;
                font-size: 23px;
                font-family: SF Mono;
                border: 2px solid #444;
                border-radius: 8px;
            }
            QComboBox#conversion_combo {
                background-color: #1e1e1e;
                color: white;
                font-size: 18px;
                font-family: SF Mono, monospaced;
                border: 2px solid #444;
                border-radius: 8px;
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
                        border-radius: 5px;
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

        self.apply_sidebar_theme_dark()

    def create_standard_calc(self):
        widget = QWidget()
        layout = QVBoxLayout()

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
        # display container is managed by the main layout; don't add it here

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
                        self.add_to_history(f"√{result}".format(value), result)
                        self.display.setText(str(result))

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
                    self.display.setText(str(result))
                    self.add_to_history(f"{value}²", result)
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
                        self.display.setText(str(result))
                        self.add_to_history(f"1/({value})", result)
                else:
                    self.display.setText("Error")

            except ValueError:
                self.display.setText("Error")

        elif text == '%':
            try:
                value = self.display.text()

                if value:
                    result = float(value) / 100
                    self.display.setText(str(result))
                    self.add_to_history(f"{value}%", result)
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
                    self.add_to_history(f"{value}^y", "Waiting for y")
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

    def evaluate_expression(self):

        try:
            expression = self.display.text().strip()
            # Getting the expression typed in by the user

            original_expression = expression

            # 1. Handling the nCr operation:
            if 'C' in expression and not any(func in expression for func in ['cos', 'acos']):
                # Adding this line because if the user types in 'cos' or 'acos', it contains a 'C' which will create conflicts
                try:
                    parts = expression.split('C')
                    if len(parts) == 2:
                        n = int(float(parts[0]))
                        r = int(float(parts[1]))

                        if n >= 0 and r >= 0 and n >= r:
                            result = math.factorial(n) // (math.factorial(r) * math.factorial(n - r))
                            self.display.setText(str(result))
                            self.add_to_history(original_expression, result)
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
                            result = math.factorial(n) // math.factorial(n - r)
                            self.display.setText(str(result))
                            self.add_to_history(original_expression, result)
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
                                self.display.setText(str(result))
                                self.add_to_history(original_expression, result)
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
            self.add_to_history(original_expression, result)

            self.display.setText(result)
            self.just_calculated = True

        except ZeroDivisionError:
            self.display.setText("Error")

        except:
            self.display.setText('Error')

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
            self.angle_mode_combo.show()
        else:
            for btn in self.extra_btn_objs:
                btn.hide()
                # Hiding the degree and radians button when pressed
            self.angle_label.hide()
            self.angle_mode_combo.hide()

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

            elif text == "cos":
                num_radians = math.radians(num) if self.angle_mode == "deg" else num
                result = math.cos(num_radians)

            elif text == "tan":
                num_radians = math.radians(num) if self.angle_mode == "deg" else num
                result = math.tan(num_radians)

            elif text == "log":
                result = math.log10(num)

            elif text == "ln":
                result = math.log(num)

            elif text == "exp":
                value = float(current) if current else 0
                result = math.exp(value)

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
                self.display.setText(str(result))
                self.add_to_history(f"{value}²", result)

            elif text == 'x³':
                result = value ** 3
                self.display.setText(str(result))
                self.add_to_history(f"{value}³", result)

            elif text == '√x':
                result = math.sqrt(abs(value))
                self.display.setText(str(result))
                self.add_to_history(f"√{value}", result)

            elif text == '³√x':
                result = value ** (1 / 3)
                self.display.setText(str(result))
                self.add_to_history(f"³√{value}", result)

            elif text == '10^x':
                result = 10 ** value
                self.display.setText(str(result))
                self.add_to_history(f"10^{value}", result)

            elif text == 'exp':
                result = math.exp(value)
                self.display.setText(str(result))
                self.add_to_history(f"exp({value})", result)

            elif text == 'n!':
                if value == int(value) and value >= 0:
                    result = math.factorial(int(value))
                    self.display.setText(str(result))
                    self.add_to_history(f"{int(value)}!", result)
                else:
                    self.display.setText("Error")
                    return

            # Trigonometric functions
            elif text == "sin":
                angle_rad = math.radians(value) if self.angle_mode == "deg" else value
                result = math.sin(angle_rad)
                self.display.setText(str(result))
                self.add_to_history(f"sin({value})", result)

            elif text == "cos":
                angle_rad = math.radians(value) if self.angle_mode == "deg" else value
                result = math.cos(angle_rad)
                self.display.setText(str(result))
                self.add_to_history(f"cos({value})", result)

            elif text == "tan":
                angle_rad = math.radians(value) if self.angle_mode == "deg" else value
                result = math.tan(angle_rad)
                self.display.setText(str(result))
                self.add_to_history(f"tan({value})", result)

            elif text == "asin":
                if -1 <= value <= 1:
                    result_rad = math.asin(value)
                    result = math.degrees(result_rad) if self.angle_mode == "deg" else result_rad
                    self.display.setText(str(result))
                    self.add_to_history(f"asin({value})", result)
                else:
                    self.display.setText("Error")
                    return

            elif text == "acos":
                if -1 <= value <= 1:
                    result_rad = math.acos(value)
                    result = math.degrees(result_rad) if self.angle_mode == "deg" else result_rad
                    self.display.setText(str(result))
                    self.add_to_history(f"acos({value})", result)
                else:
                    self.display.setText("Error")
                    return

            elif text == "atan":
                result_rad = math.atan(value)
                result = math.degrees(result_rad) if self.angle_mode == "deg" else result_rad
                self.display.setText(str(result))
                self.add_to_history(f"atan({value})", result)

            elif text == "log":
                if value > 0:
                    result = math.log10(value)
                    self.display.setText(str(result))
                    self.add_to_history(f"log({value})", result)
                else:
                    self.display.setText("Error")
                    return

            elif text == "ln":
                if value > 0:
                    result = math.log(value)
                    self.display.setText(str(result))
                    self.add_to_history(f"ln({value})", result)
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

        # Theme-specific styles
        if self.current_theme == "ocean":
            self.conversion_list.setStyleSheet("""
                QListWidget {
                    font-size: 18px;
                    font-family: Inter;
                    background-color: #f1fbff;
                    color: #0a3d62;
                    border: 2px solid #74a9cf;
                    border-radius: 8px;
                    padding: 5px;
                }
                QListWidget::item {
                    padding: 12px;
                    margin: 2px;
                    border-radius: 5px;
                }
                QListWidget::item:hover {
                    background-color: #e3f2fd;
                }
                QListWidget::item:selected {
                    background-color: #2196f3;
                    color: white;
                }
            """)
        elif self.current_theme == "forest":
            self.conversion_list.setStyleSheet("""
                QListWidget {
                    font-size: 18px;
                    font-family: Inter;
                    background-color: #e9f5e9;
                    color: #2e4d2c;
                    border: 2px solid #a9c9a9;
                    border-radius: 8px;
                    padding: 5px;
                }
                QListWidget::item {
                    padding: 12px;
                    margin: 2px;
                    border-radius: 5px;
                }
                QListWidget::item:hover {
                    background-color: #cde3cd;
                }
                QListWidget::item:selected {
                    background-color: #4d7c4d;
                    color: white;
                }
            """)
        elif self.current_theme == "sunset":
            self.conversion_list.setStyleSheet("""
                QListWidget {
                    font-size: 18px;
                    font-family: Inter;
                    background-color: #fff3e0;
                    color: #5c2e1f;
                    border: 2px solid #f7c59f;
                    border-radius: 8px;
                    padding: 5px;
                }
                QListWidget::item {
                    padding: 12px;
                    margin: 2px;
                    border-radius: 5px;
                }
                QListWidget::item:hover {
                    background-color: #ffe0b2;
                }
                QListWidget::item:selected {
                    background-color: #ff7043;
                    color: white;
                }
            """)
        else:  # fallback default
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
                    border-radius: 5px;
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
        conversion_types = ["Length", "Weight and Mass", "Volume", "Temperature", "Energy",
                            "Area", "Speed", "Time", "Power", "Data", "Pressure", "Angle", "Number Systems"]

        self.conversion_list.addItems(conversion_types)
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
            },
            "Number Systems": {
                "special": True,  # Special handling needed
                "units": ["Binary", "Octal", "Decimal", "Hexadecimal"]
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
        self.mode_label.setText("Conversions")
        # Re-apply the current theme to ensure newly shown conversion page widgets get styled
        self.change_theme(self.current_theme)

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
        if self.current_theme == 'ocean':
            back_button.setStyleSheet("font-size: 16px;"
                                      "font-family: Roboto;")
        if self.current_theme == 'forest':
            back_button.setStyleSheet("font-size: 16px;"
                                      "font-family: Roboto;")
        if self.current_theme == 'sunset':
            back_button.setStyleSheet("font-size: 16px;"
                                      "font-family: Roboto;"
)

        # No parameters needed - uses instance variable approach
        back_button.clicked.connect(self.go_back_to_conversions)
        back_layout.addWidget(back_button)
        back_layout.addStretch()
        layout.addLayout(back_layout)

        # Creating a title based on the selected conversion type:
        title = QLabel(f"{conversion_type} Conversion")
        title.setStyleSheet("font-size: 25px;"
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

        numpad_layout.setHorizontalSpacing(1)  
        numpad_layout.setVerticalSpacing(10)   


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

                numpad_layout.setColumnStretch(col, 0)
                numpad_layout.setRowStretch(row, 0)

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

        # Apply the currently selected theme so conversion widgets get the correct styles
        self.change_theme(self.current_theme)
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
            # Handle special conversion types (Temperature and Number Systems)
            if self.conversion_data[conversion_type].get("special"):
                units = self.conversion_data[conversion_type]["units"]
                from_combo.addItems(units)
                to_combo.addItems(units)
                # Set different defaults
                if len(units) > 1:
                    to_combo.setCurrentIndex(1)
            else:
                # Handle normal conversion types (Length, Weight, Volume, etc.)
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

            from_unit_name = from_unit.currentText()
            to_unit_name = to_unit.currentText()

            if conversion_type == "Number Systems":
                result = self.convert_number_systems(input_text, from_unit_name, to_unit_name)
                to_value.setText(result)
                return

            # For all other conversions, convert to float
            value = float(input_text)

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

    def convert_number_systems(self, value, from_unit, to_unit):
        """Handle number system conversions"""
        if from_unit == to_unit:
            return value

        try:
            # Convert to decimal first
            if from_unit == "Binary":
                decimal = int(value, 2)
            elif from_unit == "Octal":
                decimal = int(value, 8)
            elif from_unit == "Decimal":
                decimal = int(value)
            elif from_unit == "Hexadecimal":
                decimal = int(value, 16)
            else:
                return "Error"

            # Convert from decimal to target
            if to_unit == "Binary":
                return bin(decimal)[2:]  # Remove '0b' prefix
            elif to_unit == "Octal":
                return oct(decimal)[2:]  # Remove '0o' prefix
            elif to_unit == "Decimal":
                return str(decimal)
            elif to_unit == "Hexadecimal":
                return hex(decimal)[2:].upper()  # Remove '0x' prefix and uppercase
            else:
                return "Error"

        except ValueError:
            return "Invalid input"

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