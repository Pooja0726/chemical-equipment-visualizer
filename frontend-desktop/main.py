import sys
import requests
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
                             QLabel, QFileDialog, QMessageBox, QComboBox, QGroupBox,
                             QGridLayout, QScrollArea, QStackedWidget, QFrame,
                             QSizePolicy, QHeaderView, QDialog, QLineEdit)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

API_BASE_URL = 'https://chemical-equipment-visualizer-production-999d.up.railway.app/api'

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chemical Visualizer - Login")
        self.setFixedSize(500, 400)
        self.setModal(True)
        
        # Set background gradient
        self.setStyleSheet('''
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #e3f2fd, stop:1 #bbdefb);
            }
        ''')
        
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setContentsMargins(50, 50, 50, 50)
        
        # Login card container
        card = QFrame()
        card.setStyleSheet('''
            QFrame {
                background: white;
                border-radius: 16px;
                padding: 40px;
            }
        ''')
        card.setFixedWidth(400)
        
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(20)
        card_layout.setAlignment(Qt.AlignCenter)
        
        # Title
        title = QLabel("Login to Chemical Visualizer")
        title.setFont(QFont('Arial', 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet('color: #2c3e50; margin-bottom: 10px;')
        card_layout.addWidget(title)
        
        # Email input
        self.email = QLineEdit()
        self.email.setPlaceholderText("Email")
        self.email.setMinimumHeight(45)
        self.email.setStyleSheet('''
            QLineEdit {
                padding: 14px 18px;
                border: 2px solid #d0e8f2;
                border-radius: 8px;
                font-size: 15px;
                background: white;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
                outline: none;
            }
        ''')
        card_layout.addWidget(self.email)
        
        # Password input
        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setMinimumHeight(45)
        self.password.setStyleSheet('''
            QLineEdit {
                padding: 14px 18px;
                border: 2px solid #d0e8f2;
                border-radius: 8px;
                font-size: 15px;
                background: white;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
                outline: none;
            }
        ''')
        self.password.returnPressed.connect(self.do_login)
        card_layout.addWidget(self.password)
        
        # Login button
        self.login_btn = QPushButton("LOGIN")
        self.login_btn.setFont(QFont('Arial', 12, QFont.Bold))
        self.login_btn.setMinimumHeight(50)
        self.login_btn.setCursor(Qt.PointingHandCursor)
        self.login_btn.setStyleSheet('''
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2980b9);
                color: white;
                padding: 14px;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2980b9, stop:1 #1f5f8b);
            }
            QPushButton:pressed {
                background: #1f5f8b;
            }
        ''')
        self.login_btn.clicked.connect(self.do_login)
        card_layout.addWidget(self.login_btn)
        
        main_layout.addWidget(card)
        
        self.token = None

    def do_login(self):
        email_text = self.email.text().strip()
        password_text = self.password.text().strip()
        
        if not email_text or not password_text:
            QMessageBox.warning(self, "Invalid Input", "Please enter both email and password.")
            return
        
        self.login_btn.setEnabled(False)
        self.login_btn.setText("Logging in...")
        
        try:
            resp = requests.post(
                f"{API_BASE_URL}/login/", 
                json={'username': email_text, 'password': password_text},
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if resp.status_code == 200:
                self.token = resp.json()['token']
                self.accept()
            else:
                self.login_btn.setEnabled(True)
                self.login_btn.setText("LOGIN")
                QMessageBox.warning(self, "Login Failed", "Invalid email or password.\n\nPlease try again.")
                
        except requests.exceptions.Timeout:
            self.login_btn.setEnabled(True)
            self.login_btn.setText("LOGIN")
            QMessageBox.critical(self, "Connection Error", "Request timed out.\n\nPlease check your internet connection.")
        except requests.exceptions.ConnectionError:
            self.login_btn.setEnabled(True)
            self.login_btn.setText("LOGIN")
            QMessageBox.critical(self, "Connection Error", "Could not connect to server.\n\nPlease check your internet connection.")
        except Exception as e:
            self.login_btn.setEnabled(True)
            self.login_btn.setText("LOGIN")
            QMessageBox.critical(self, "Error", f"An error occurred:\n\n{str(e)}")


class ChartWidget(QWidget):
    """Widget for displaying matplotlib charts"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
    
    def plot_bar_chart(self, labels, values, title):
        """Plot bar chart"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        colors = ['#36A2EB', '#FF6384', '#FFCE56']
        bars = ax.bar(labels, values, color=colors[:len(labels)], width=0.6)
        
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}',
                    ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
        ax.set_ylabel('Values', fontsize=12)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)
        self.figure.tight_layout()
        self.canvas.draw()
    
    def plot_pie_chart(self, labels, values, title):
        """Plot pie chart"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40']
        explode = [0.05] * len(labels)
        
        wedges, texts, autotexts = ax.pie(
            values, 
            labels=labels, 
            autopct='%1.1f%%', 
            colors=colors[:len(labels)],
            explode=explode,
            shadow=True,
            startangle=90
        )
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(11)
        
        for text in texts:
            text.set_fontsize(11)
            text.set_fontweight('bold')
        
        ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
        self.figure.tight_layout()
        self.canvas.draw()


class SidebarButton(QPushButton):
    """Custom styled sidebar button"""
    def __init__(self, text, icon_text="", parent=None):
        super().__init__(parent)
        self.setText(f"{icon_text}  {text}")
        self.setCheckable(True)
        self.setMinimumHeight(60)
        self.setStyleSheet(self.get_default_style())
    
    def get_default_style(self):
        return '''
            QPushButton {
                background: transparent;
                color: #2c3e50;
                text-align: left;
                padding: 15px 20px;
                border: none;
                border-left: 4px solid transparent;
                font-size: 15px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: rgba(173, 216, 230, 0.3);
                border-left: 4px solid #3498db;
            }
            QPushButton:checked {
                background: rgba(173, 216, 230, 0.5);
                border-left: 4px solid #2980b9;
                color: #2980b9;
                font-weight: bold;
            }
        '''


class StatCard(QFrame):
    """Custom stat card widget"""
    def __init__(self, title, value, color_start, color_end, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setMinimumHeight(120)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet('color: white; font-size: 14px; font-weight: 500;')
        
        value_label = QLabel(str(value))
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setStyleSheet('color: white; font-size: 28px; font-weight: bold;')
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        self.setLayout(layout)
        self.setStyleSheet(f'''
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {color_start}, stop:1 {color_end});
                border-radius: 12px;
                padding: 15px;
            }}
        ''')


class MainWindow(QMainWindow):
    def __init__(self, token):
        super().__init__()
        self.token = token # Store the auth token
        self.datasets = []
        self.current_dataset = None
        self.init_ui()
        self.load_datasets()
    
    def get_headers(self):
        """Helper to return auth headers"""
        return {'Authorization': f'Token {self.token}'}

    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle('Chemical Equipment Parameter Visualizer')
        self.setGeometry(50, 50, 1600, 950)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # ========== SIDEBAR ==========
        sidebar = QFrame()
        sidebar.setFixedWidth(300)
        sidebar.setStyleSheet('''
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f0f8ff, stop:1 #e6f2ff);
                border-right: 1px solid #d0e8f2;
            }
        ''')
        
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setSpacing(5)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        
        logo_label = QLabel('🧪 Chemical Equipment\nParameter\n Visualizer')
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet('''
            color: #2980b9;
            font-size: 22px;
            font-weight: bold;
            padding: 20px 0px;
            background: rgba(255, 255, 255, 0.5);
            border-bottom: 2px solid #3498db;
        ''')
        sidebar_layout.addWidget(logo_label)
        
        sidebar_layout.addSpacing(20)
        
        self.nav_buttons = []
        
        self.btn_upload = SidebarButton('Upload Dataset', '📤')
        self.btn_upload.clicked.connect(lambda: self.switch_page(0))
        self.nav_buttons.append(self.btn_upload)
        sidebar_layout.addWidget(self.btn_upload)
        
        self.btn_analyze = SidebarButton('Analyze Report', '📊')
        self.btn_analyze.clicked.connect(lambda: self.switch_page(1))
        self.nav_buttons.append(self.btn_analyze)
        sidebar_layout.addWidget(self.btn_analyze)
        
        self.btn_equipment = SidebarButton('Equipment Report', '📋')
        self.btn_equipment.clicked.connect(lambda: self.switch_page(2))
        self.nav_buttons.append(self.btn_equipment)
        sidebar_layout.addWidget(self.btn_equipment)
        
        sidebar_layout.addStretch()
        
        # Add logout button
        self.btn_logout = QPushButton('🚪 Logout')
        self.btn_logout.setMinimumHeight(60)
        self.btn_logout.setCursor(Qt.PointingHandCursor)
        self.btn_logout.setStyleSheet('''
            QPushButton {
                background: transparent;
                color: #e74c3c;
                text-align: left;
                padding: 15px 20px;
                border: none;
                border-left: 4px solid transparent;
                font-size: 15px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: rgba(231, 76, 60, 0.1);
                border-left: 4px solid #e74c3c;
            }
        ''')
        self.btn_logout.clicked.connect(self.logout)
        sidebar_layout.addWidget(self.btn_logout)
        
        footer = QLabel('Version 1.0\n© 2026')
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet('color: #7f8c8d; font-size: 11px; padding: 20px;')
        sidebar_layout.addWidget(footer)
        
        main_layout.addWidget(sidebar)
        
        # ========== CONTENT AREA ==========
        content_widget = QWidget()
        content_widget.setStyleSheet('background: #f8fbff;')
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(20)
        
        self.stacked_widget = QStackedWidget()
        
        self.page_upload = self.create_upload_page()
        self.stacked_widget.addWidget(self.page_upload)
        
        self.page_analysis = self.create_analysis_page()
        self.stacked_widget.addWidget(self.page_analysis)
        
        self.page_equipment = self.create_equipment_page()
        self.stacked_widget.addWidget(self.page_equipment)
        
        content_layout.addWidget(self.stacked_widget)
        main_layout.addWidget(content_widget)
        
        self.btn_upload.setChecked(True)
        self.stacked_widget.setCurrentIndex(0)
    
    def logout(self):
        """Handle logout"""
        reply = QMessageBox.question(
            self,
            'Logout',
            'Are you sure you want to logout?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.close()
            # Show login dialog again
            login = LoginDialog()
            if login.exec_() == QDialog.Accepted:
                new_window = MainWindow(login.token)
                new_window.show()
    
    def create_upload_page(self):
        """Create upload and select dataset page"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(25)
        
        title = QLabel('Upload & Select Dataset')
        title.setFont(QFont('Arial', 24, QFont.Bold))
        title.setStyleSheet('color: #2c3e50; margin-bottom: 10px;')
        layout.addWidget(title)
        
        upload_group = QGroupBox()
        upload_group.setStyleSheet('''
            QGroupBox {
                background: white;
                border-radius: 12px;
                padding: 30px;
            }
        ''')
        upload_layout = QVBoxLayout()
        upload_layout.setSpacing(15)
        
        upload_title = QLabel('📁 Upload New Dataset')
        upload_title.setFont(QFont('Arial', 16, QFont.Bold))
        upload_title.setStyleSheet('color: #34495e;')
        upload_layout.addWidget(upload_title)
        
        upload_desc = QLabel('Select a CSV file containing equipment data to upload and analyze.')
        upload_desc.setStyleSheet('color: #7f8c8d; font-size: 13px; margin-bottom: 10px;')
        upload_layout.addWidget(upload_desc)
        
        self.upload_btn = QPushButton('📤 Choose CSV File')
        self.upload_btn.setMinimumHeight(55)
        self.upload_btn.setCursor(Qt.PointingHandCursor)
        self.upload_btn.setStyleSheet('''
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2980b9);
                color: white;
                padding: 15px 30px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 16px;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2980b9, stop:1 #1f5f8b);
            }
            QPushButton:pressed {
                background: #1f5f8b;
            }
        ''')
        self.upload_btn.clicked.connect(self.upload_file)
        upload_layout.addWidget(self.upload_btn)
        
        upload_group.setLayout(upload_layout)
        layout.addWidget(upload_group)
        
        select_group = QGroupBox()
        select_group.setStyleSheet('''
            QGroupBox {
                background: white;
                border-radius: 12px;
                padding: 30px;
            }
        ''')
        select_layout = QVBoxLayout()
        select_layout.setSpacing(15)
        
        select_title = QLabel('📊 Select Existing Dataset')
        select_title.setFont(QFont('Arial', 16, QFont.Bold))
        select_title.setStyleSheet('color: #34495e;')
        select_layout.addWidget(select_title)
        
        select_desc = QLabel('Choose from previously uploaded datasets to view and analyze.')
        select_desc.setStyleSheet('color: #7f8c8d; font-size: 13px; margin-bottom: 10px;')
        select_layout.addWidget(select_desc)
        
        combo_layout = QHBoxLayout()
        combo_label = QLabel('Dataset:')
        combo_label.setStyleSheet('font-size: 14px; font-weight: 500; color: #2c3e50;')
        combo_layout.addWidget(combo_label)
        
        self.dataset_combo = QComboBox()
        self.dataset_combo.setMinimumHeight(45)
        self.dataset_combo.setStyleSheet('''
            QComboBox {
                padding: 10px;
                border: 2px solid #d0e8f2;
                border-radius: 8px;
                background: white;
                font-size: 14px;
            }
            QComboBox:hover {
                border: 2px solid #3498db;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 10px;
            }
        ''')
        self.dataset_combo.currentIndexChanged.connect(self.on_dataset_selected)
        combo_layout.addWidget(self.dataset_combo, 1)
        
        select_layout.addLayout(combo_layout)
        
        select_group.setLayout(select_layout)
        layout.addWidget(select_group)
        
        layout.addStretch()
        
        return page
    
    def create_analysis_page(self):
        """Create analysis page with stats and charts"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(25)
        
        title = QLabel('Data Analysis & Visualization')
        title.setFont(QFont('Arial', 24, QFont.Bold))
        title.setStyleSheet('color: #2c3e50; margin-bottom: 10px;')
        layout.addWidget(title)
        
        stats_container = QWidget()
        stats_container.setStyleSheet('background: transparent;')
        self.stats_layout = QGridLayout(stats_container)
        self.stats_layout.setSpacing(20)
        layout.addWidget(stats_container)
        
        charts_group = QGroupBox()
        charts_group.setStyleSheet('''
            QGroupBox {
                background: white;
                border-radius: 12px;
                padding: 25px;
            }
        ''')
        charts_layout = QVBoxLayout()
        charts_layout.setSpacing(15)
        
        charts_title = QLabel('📈 Visual Analytics')
        charts_title.setFont(QFont('Arial', 16, QFont.Bold))
        charts_title.setStyleSheet('color: #34495e; margin-bottom: 10px;')
        charts_layout.addWidget(charts_title)
        
        charts_row = QHBoxLayout()
        charts_row.setSpacing(20)
        
        self.avg_chart = ChartWidget()
        self.type_chart = ChartWidget()
        
        charts_row.addWidget(self.avg_chart)
        charts_row.addWidget(self.type_chart)
        
        charts_layout.addLayout(charts_row)
        charts_group.setLayout(charts_layout)
        layout.addWidget(charts_group, 1)
        
        return page
    
    def create_equipment_page(self):
        """Create equipment records page"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(25)
        
        header_layout = QHBoxLayout()
        
        title = QLabel('Equipment Records')
        title.setFont(QFont('Arial', 24, QFont.Bold))
        title.setStyleSheet('color: #2c3e50;')
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        self.download_pdf_btn = QPushButton('📄 Download PDF Report')
        self.download_pdf_btn.setMinimumHeight(50)
        self.download_pdf_btn.setCursor(Qt.PointingHandCursor)
        self.download_pdf_btn.setStyleSheet('''
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #27ae60, stop:1 #229954);
                color: white;
                padding: 12px 25px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 15px;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #229954, stop:1 #1e8449);
            }
            QPushButton:pressed {
                background: #1e8449;
            }
        ''')
        self.download_pdf_btn.clicked.connect(self.download_pdf)
        header_layout.addWidget(self.download_pdf_btn)
        
        layout.addLayout(header_layout)
        
        table_container = QGroupBox()
        table_container.setStyleSheet('''
            QGroupBox {
                background: white;
                border-radius: 12px;
                padding: 25px;
            }
        ''')
        table_layout = QVBoxLayout()
        
        table_title = QLabel('📋 Detailed Equipment Data')
        table_title.setFont(QFont('Arial', 16, QFont.Bold))
        table_title.setStyleSheet('color: #34495e; margin-bottom: 15px;')
        table_layout.addWidget(table_title)
        
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature'])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setMinimumHeight(500)
        self.table.setStyleSheet('''
            QTableWidget {
                border: 1px solid #d0e8f2;
                border-radius: 8px;
                background: white;
                gridline-color: #e8f4f8;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background: #d0e8f2;
                color: #2c3e50;
            }
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3498db, stop:1 #2980b9);
                color: white;
                padding: 12px;
                border: none;
                font-weight: bold;
                font-size: 14px;
            }
        ''')
        
        table_layout.addWidget(self.table)
        table_container.setLayout(table_layout)
        layout.addWidget(table_container, 1)
        
        return page
    
    def switch_page(self, index):
        """Switch between pages"""
        for btn in self.nav_buttons:
            btn.setChecked(False)
        
        self.nav_buttons[index].setChecked(True)
        self.stacked_widget.setCurrentIndex(index)
    
    def load_datasets(self):
        """Load datasets from API"""
        try:
            response = requests.get(f'{API_BASE_URL}/datasets/', headers=self.get_headers())
            response.raise_for_status()
            data = response.json()
            
            if isinstance(data, dict) and 'results' in data:
                self.datasets = data['results']
            elif isinstance(data, list):
                self.datasets = data
            else:
                self.datasets = []
            
            self.dataset_combo.blockSignals(True)
            self.dataset_combo.clear()
            self.current_dataset = None
            
            if not self.datasets:
                self.dataset_combo.addItem("No datasets available", None)
            else:
                for ds in self.datasets:
                    self.dataset_combo.addItem(
                        f"{ds['filename']} - {ds['upload_date'][:10]}", 
                        ds['id']
                    )
            
            self.dataset_combo.blockSignals(False)
            
        except Exception as e:
            print(f"Error loading datasets: {str(e)}")
            self.dataset_combo.blockSignals(True)
            self.dataset_combo.clear()
            self.current_dataset = None
            self.dataset_combo.addItem("Error loading datasets", None)
            self.dataset_combo.blockSignals(False)
    
    def upload_file(self):
        """Upload CSV file"""
        filepath, _ = QFileDialog.getOpenFileName(
            self, 
            'Select CSV File', 
            '', 
            'CSV Files (*.csv);;All Files (*)'
        )
        
        if not filepath:
            return
        
        self.upload_btn.setEnabled(False)
        self.upload_btn.setText('⏳ Uploading...')
        
        try:
            with open(filepath, 'rb') as f:
                file_content = f.read()
                files = {'file': (filepath.split('\\')[-1], file_content, 'text/csv')}
                response = requests.post(f'{API_BASE_URL}/datasets/upload/', files=files, headers=self.get_headers())
                
                if response.status_code == 201:
                    data = response.json()
                    self.upload_btn.setEnabled(True)
                    self.upload_btn.setText('📤 Choose CSV File')
                    
                    QMessageBox.information(
                        self, 
                        'Success', 
                        '✅ File uploaded successfully!\n\nSwitch to "Analyze Report" to view the data.'
                    )
                    self.load_datasets()
                    self.current_dataset = data
                    self.display_dataset(data)
                    self.switch_page(1)
                else:
                    error_msg = response.json().get('error', 'Unknown error')
                    raise Exception(error_msg)
                    
        except Exception as e:
            self.upload_btn.setEnabled(True)
            self.upload_btn.setText('📤 Choose CSV File')
            QMessageBox.critical(self, 'Upload Failed', f'❌ Error: {str(e)}')
    
    def on_dataset_selected(self, index):
        """Handle dataset selection"""
        if index < 0:
            return
        
        dataset_id = self.dataset_combo.itemData(index)
        
        if dataset_id is None:
            self.current_dataset = None
            return
        
        try:
            response = requests.get(f'{API_BASE_URL}/datasets/{dataset_id}/', headers=self.get_headers())
            
            if response.status_code == 404:
                QMessageBox.warning(
                    self, 
                    'Not Found', 
                    '⚠️ Dataset not found. It may have been deleted.\n\nRefreshing dataset list...'
                )
                self.current_dataset = None
                self.load_datasets()
                return
                
            response.raise_for_status()
            self.current_dataset = response.json()
            self.display_dataset(self.current_dataset)
            self.switch_page(1)
            
        except requests.exceptions.HTTPError as e:
            QMessageBox.warning(self, 'Error', f'❌ HTTP Error: {e.response.status_code}')
            self.current_dataset = None
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'❌ Failed to load dataset: {str(e)}')
            self.current_dataset = None
    
    def display_dataset(self, dataset):
        """Display dataset information"""
        if not isinstance(dataset, dict) or 'summary' not in dataset:
            QMessageBox.warning(self, 'Error', '❌ Invalid dataset format')
            return
            
        summary = dataset['summary']
        
        for i in reversed(range(self.stats_layout.count())): 
            widget = self.stats_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        stats = [
            ('Total Records', dataset.get('row_count', 0), '#3498db', '#2980b9'),
            ('Avg Flowrate', f"{summary.get('avg_flowrate', 0):.1f}", '#9b59b6', '#8e44ad'),
            ('Avg Pressure', f"{summary.get('avg_pressure', 0):.1f}", '#e74c3c', '#c0392b'),
            ('Avg Temperature', f"{summary.get('avg_temperature', 0):.1f}", '#f39c12', '#e67e22')
        ]
        
        for i, (label, value, color_start, color_end) in enumerate(stats):
            stat_card = StatCard(label, value, color_start, color_end)
            self.stats_layout.addWidget(stat_card, 0, i)
        
        if all(k in summary for k in ['avg_flowrate', 'avg_pressure', 'avg_temperature']):
            self.avg_chart.plot_bar_chart(
                ['Flowrate', 'Pressure', 'Temperature'],
                [summary['avg_flowrate'], summary['avg_pressure'], summary['avg_temperature']],
                'Average Parameter Values'
            )
        
        if 'equipment_types' in summary:
            types = list(summary['equipment_types'].keys())
            counts = list(summary['equipment_types'].values())
            self.type_chart.plot_pie_chart(types, counts, 'Equipment Type Distribution')
        
        records = dataset.get('records', [])
        self.table.setRowCount(len(records))
        
        for i, record in enumerate(records):
            self.table.setItem(i, 0, QTableWidgetItem(str(record.get('equipment_name', ''))))
            self.table.setItem(i, 1, QTableWidgetItem(str(record.get('equipment_type', ''))))
            self.table.setItem(i, 2, QTableWidgetItem(str(record.get('flowrate', ''))))
            self.table.setItem(i, 3, QTableWidgetItem(str(record.get('pressure', ''))))
            self.table.setItem(i, 4, QTableWidgetItem(str(record.get('temperature', ''))))
    
    def download_pdf(self):
        """Download PDF report"""
        if not self.current_dataset:
            QMessageBox.warning(
                self, 
                'Warning', 
                '⚠️ Please select a dataset first before downloading PDF\n\nGo to "Upload Dataset" page to select a dataset.'
            )
            return
        
        dataset_id = self.current_dataset.get('id')
        
        if not dataset_id:
            QMessageBox.warning(self, 'Warning', '❌ Invalid dataset - missing ID')
            return
        
        filepath, _ = QFileDialog.getSaveFileName(
            self, 
            'Save PDF Report', 
            f"equipment_report_{dataset_id}.pdf", 
            'PDF Files (*.pdf)'
        )
        
        if not filepath:
            return
        
        try:
            print(f"\n{'='*60}")
            print(f"📥 Downloading PDF for dataset ID: {dataset_id}")
            print(f"📂 Dataset: {self.current_dataset.get('filename')}")
            print(f"{'='*60}")
            
            url = f'{API_BASE_URL}/datasets/{dataset_id}/download_pdf/'
            response = requests.get(url, stream=True, timeout=30, headers=self.get_headers())
            
            if response.status_code == 404:
                print("❌ Dataset not found (404)")
                QMessageBox.warning(
                    self, 
                    'Not Found', 
                    f'⚠️ Dataset {dataset_id} not found or has been deleted.\n\nRefreshing dataset list...'
                )
                self.current_dataset = None
                self.load_datasets()
                return
            
            if response.status_code != 200:
                raise Exception(f'Server returned status code {response.status_code}')
            
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            file_size = len(response.content)
            print(f"✅ PDF saved successfully!")
            print(f"📦 File size: {file_size:,} bytes ({file_size/1024:.2f} KB)")
            print(f"📁 Location: {filepath}")
            print(f"{'='*60}\n")
            
            QMessageBox.information(
                self, 
                'Success', 
                f'✅ PDF report downloaded successfully!\n\nSaved to:\n{filepath}'
            )
            
        except requests.exceptions.Timeout:
            print("❌ Request timed out")
            QMessageBox.critical(
                self, 
                'Timeout Error', 
                '❌ Request timed out after 30 seconds.\n\nPlease check your connection and try again.'
            )
        except requests.exceptions.ConnectionError:
            print("❌ Connection error - Backend not running")
            QMessageBox.critical(
                self, 
                'Connection Error', 
                '❌ Cannot connect to backend server.\n\n' +
                'Make sure Django server is running:\n' +
                'cd backend\n' +
                'python manage.py runserver'
            )
        except requests.exceptions.HTTPError as e:
            print(f"❌ HTTP Error: {e}")
            QMessageBox.critical(
                self,
                'HTTP Error',
                f'❌ Server error: {e.response.status_code}\n\n{e.response.reason}'
            )
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            QMessageBox.critical(
                self,
                'Download Failed',
                f'❌ Failed to download PDF:\n\n{str(e)}'
            )


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Show login dialog
    login = LoginDialog()
    if login.exec_() == QDialog.Accepted and login.token:
        window = MainWindow(token=login.token)
        window.show()
        sys.exit(app.exec_())
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()