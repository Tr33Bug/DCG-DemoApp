import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QPushButton, QWidget, QLabel, QCheckBox, 
                             QScrollArea, QSizePolicy, QSpinBox, QTextEdit, QGridLayout)
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtCore import Qt
import requests
import json

# test prompt: <START> { "@class" : "nitrox.dlc.mirror.model.EntityModel"

def get_response_from_model_test(message):
    url = 'http://11.11.11.254:5000/chat'
    response = requests.post(url, json={'message': message})
    return response.json().get('response', '')

def postprocessing(response):
    # remove <START> token
    response = response.replace("<START>", "")

    # remove after <END> token
    if "<END>" in response:
        response = response[:response.find("<END>")]

    # delete to the first komma
    response = response[:response.rfind(",")]

    # close the JSON object
    stack = []

    for char in response:
        if char in '{[':
            stack.append(char)
        elif char in '}]':
            if stack:
                stack.pop()

    while stack:
        char = stack.pop()
        if char == '{':
            response += '}'
        elif char == '[':
            response += ']'

    # replace double quotation marks
    response = response.replace('""', '"')

    return response

def pars_and_format(response):
    # parse and format json
    try:
        response = json.loads(response)
        response = json.dumps(response, indent=4)
    except Exception as e:
        return str(e) + "\n\nOutput:\n" +response
    return response

class ServerSettings(QWidget):
    def __init__(self, default_url, parent=None):
        super().__init__(parent)
        
        layout = QHBoxLayout()
        
        self.server_label = QLabel("Server URL:")
        self.server_label.setStyleSheet("color: #FFFFFF;")
        layout.addWidget(self.server_label)
        
        self.server_field = QLineEdit(default_url)
        self.server_field.setMinimumWidth(200)
        self.server_field.setStyleSheet("background-color: #CCCCCC; color: #333333; border: none; border-radius: 5px; padding: 5px;")
        self.server_field.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(self.server_field)
        
        layout.addStretch(1)
        
        self.setLayout(layout)

    def get_server_url(self):
        return self.server_field.text()
    
class ChatBubble(QWidget):
    def __init__(self, text, is_user=True):
        super().__init__()
        layout = QVBoxLayout()
        
        if is_user:
            headline = QLabel("Prompt:")
            headline.setAlignment(Qt.AlignLeft)
            bubble = QTextEdit()
            bubble.setText(text)
            bubble.setReadOnly(True)
            bubble.setWordWrapMode(True)
            bubble.setFixedHeight(self.calculate_height(bubble))
            bubble.setFixedWidth(self.calculate_width(bubble))
            bubble.setStyleSheet("""
                background-color: #99CC33; 
                color: #333333; 
                padding: 10px; 
                border-radius: 10px;
                margin: 5px;
            """)
            layout.setAlignment(Qt.AlignRight)
        else:
            headline = QLabel("DCG Output:")
            headline.setAlignment(Qt.AlignLeft)
            bubble = QTextEdit()
            bubble.setText(text)
            bubble.setReadOnly(True)
            bubble.setWordWrapMode(True)
            bubble.setFixedHeight(self.calculate_height(bubble))
            bubble.setFixedWidth(self.calculate_width(bubble))
            bubble.setStyleSheet("""
                background-color: #333333; 
                color: #FFFFFF; 
                padding: 10px; 
                border-radius: 10px;
                margin: 5px;
            """)
            layout.setAlignment(Qt.AlignLeft)
        
        headline.setStyleSheet("font-weight: bold;")
        
        bubble.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        layout.addWidget(headline)
        layout.addWidget(bubble)
        layout.setContentsMargins(2, 2, 2, 2)  # Set margins to avoid extra space
        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
    def calculate_height(self, text_edit):
        document = text_edit.document()
        document.setTextWidth(text_edit.viewport().width())
        return int(document.size().height() + 20)  # Add some padding for better appearance
    
    def calculate_width(self, text_edit):
        document = text_edit.document()
        document.setTextWidth(text_edit.viewport().width())
        return int(document.size().width() + 20)

class ChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Domainlifecycles Code Generator Demo")
        self.setGeometry(100, 100, 1400, 700)

        main_layout = QGridLayout()

        # Title and Server Settings Layout
        title_layout = QHBoxLayout()
        
        # Logo/Icon
        self.icon_label = QSvgWidget("images/e-mit-stern-grün.svg", self)
        self.icon_label.setStyleSheet("border: 2px solid #99CC33; border-radius: 10px;")
        self.icon_label.setFixedSize(64, 64)
        title_layout.addWidget(self.icon_label)

        # Title Label
        self.title_label = QLabel("Domainlifecycles Code Generator Demo", self)
        self.title_label.setStyleSheet("color: #99CC33; font-size: 30px; font-weight: italic;")
        title_layout.addWidget(self.title_label)

        # Server Settings Widget
        self.server_settings = ServerSettings("http://11.11.11.254:5000/chat")
        title_layout.addWidget(self.server_settings, alignment=Qt.AlignRight)

        main_layout.addLayout(title_layout, 0, 0)

        # Scrollable Chat Display
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("background-color: #444444; border: none;")
        self.chat_display_container = QWidget()
        self.chat_display_layout = QVBoxLayout(self.chat_display_container)
        self.chat_display_container.setLayout(self.chat_display_layout)
        self.scroll_area.setWidget(self.chat_display_container)

        main_layout.addWidget(self.scroll_area, 1, 0)

        # User Input and Controls Layout
        input_layout = QHBoxLayout()

        # Text Input Field
        self.input_field = QLineEdit(self)
        self.input_field.setPlaceholderText("Type your message here...")
        self.input_field.setStyleSheet("background-color: #CCCCCC; color: #333333; border: none; border-radius: 5px;")
        self.input_field.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.input_field.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.input_field)

        # Timeout Label
        timeout_label = QLabel("Timeout:", self)
        timeout_label.setStyleSheet("color: #FFFFFF;")
        input_layout.addWidget(timeout_label)

        # Timeout Input
        self.timeout_input = QSpinBox(self)
        self.timeout_input.setStyleSheet("background-color: #CCCCCC; color: #333333; border: none; border-radius: 5px;")
        self.timeout_input.setValue(50)
        self.timeout_input.setSuffix(" s")
        self.timeout_input.setRange(1, 600)
        self.timeout_input.setButtonSymbols(QSpinBox.NoButtons)  # Removes up/down buttons
        input_layout.addWidget(self.timeout_input)

        # Postprocessing Checkbox
        self.postprocessing_checkbox = QCheckBox("Post-Processing", self)
        input_layout.addWidget(self.postprocessing_checkbox)
        self.postprocessing_checkbox.setChecked(True)

        # Format Checkbox
        self.format_checkbox = QCheckBox("JSON Format", self)
        input_layout.addWidget(self.format_checkbox)
        self.format_checkbox.setChecked(True)

        # Send Button
        self.send_button = QPushButton("Generate! ↵ ", self)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #99CC33;
                color: #333333;
                border: none;
                border-radius: 10px;
                margin-left: 10px;
            }
            QPushButton:hover {
                background-color: #88BB29;
            }
        """)
        self.send_button.setFixedSize(100, 40)
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)

        main_layout.addLayout(input_layout, 2, 0)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #333333;
            }
            QLineEdit {
                background-color: #CCCCCC;
                color: #333333;
                border: none;
                border-radius: 5px;
            }
            QPushButton {
                background-color: #99CC33;
                color: #333333;
                border: none;
                border-radius: 10px;
            }
            QSpinBox {
                background-color: #CCCCCC;
                color: #333333;
                border: none;
            }
        """)
        self.input_field.setFocus()

    def send_message(self):
        user_message = self.input_field.text()
        if not user_message:
            return
        self.add_chat_bubble(user_message, is_user=True)
        # self.input_field.clear()

        response = self.get_response_from_model(user_message)
        
        if self.postprocessing_checkbox.isChecked():
            response = postprocessing(response)
        
        if self.format_checkbox.isChecked():
            response = pars_and_format(response)
        
        self.add_chat_bubble(response, is_user=False)

        # scroll 

    def add_chat_bubble(self, message, is_user):
        bubble = ChatBubble(message, is_user)
        self.chat_display_layout.addWidget(bubble)
        self.chat_display_layout.addStretch(1)

        # scroll_bar = self.scroll_area.verticalScrollBar()
        # scroll_bar.setValue(scroll_bar.maximum())   
        
        # self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())

    def get_response_from_model(self, message):
        url = self.server_settings.get_server_url()  # Fetching server URL from ServerSettings widget
        timeout = self.timeout_input.value()
        try:
            response = requests.post(url, json={'message': message}, timeout=timeout)
            response.raise_for_status()
            return response.json().get('response', '')
        except requests.exceptions.Timeout:
            return 'Request timed out'
        except requests.exceptions.RequestException as e:
            return f'Request failed: {e}'

    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatWindow()
    window.show()
    sys.exit(app.exec_())