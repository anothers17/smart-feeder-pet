"""Main Window for Smart Pet Feeder Application.

Refactored UI logic with dependency injection, configuration management,
and separation of concerns.
"""

# pylint: disable=no-name-in-module,c-extension-no-member,too-many-branches,too-many-statements,broad-exception-caught

import sys
from pathlib import Path
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTimer
import pyqtgraph as pg
import numpy as np

# Import generated UI
try:
    from .petfeed import Ui_MainWindow
except ImportError:
    # Fallback for direct execution
    from petfeed import Ui_MainWindow

from src.utils.logger import get_logger
from config.settings import Settings
from config.constants import Constants


class SmartPetFeederApp(QtCore.QObject, Ui_MainWindow):
    """Main application window for Smart Pet Feeder."""

    # Signal for thread-safe UI updates
    update_signal = QtCore.pyqtSignal(dict)

    def __init__(self, main_window, mqtt_client, database, settings: Settings):
        """Initialize the application.

        Args:
            main_window: QMainWindow instance
            mqtt_client: MQTT client instance (real or simulator)
            database: Database handler instance (real or mock)
            settings: Application settings
        """
        super().__init__()
        self.setupUi(main_window)

        self.main_window = main_window
        self.mqtt = mqtt_client
        self.db = database
        self.settings = settings
        self.logger = get_logger(__name__)

        # UI state
        self.status = {}

        # Setup window
        self.main_window.setWindowTitle(Constants.APP_NAME)

        # Setup components
        self._setup_ui_extras()
        self._setup_connections()
        self._setup_graph()
        self._setup_timers()

        # Setup MQTT callback
        self.update_signal.connect(self._on_update_signal)
        self.mqtt.set_callback(self._on_mqtt_message)

        # Initial data load
        self._update_feed_weight()
        self._update_feed_amount()

        mode_text = "SIMULATOR" if self.settings.is_simulator else "REAL"
        self.logger.info(f"Smart Pet Feeder UI initialized (Mode: {mode_text})")

    def _setup_ui_extras(self):
        """Add extra UI components not in generated file."""
        # Add Motor Status Label
        self.lbl_motor_status = QtWidgets.QLabel(self.frame_11)
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        self.lbl_motor_status.setFont(font)
        self.lbl_motor_status.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_motor_status.setText("Motor: STOP")
        self.lbl_motor_status.setStyleSheet("color: #555555; margin: 2px;")

        # Insert before buttons (index 0)
        self.verticalLayout_6.insertWidget(0, self.lbl_motor_status)

    def _on_mqtt_message(self, topic: str, data: dict):
        """Handle incoming MQTT messages (background thread)."""
        if topic == self.settings.mqtt_topic_monitoring:
            self.update_signal.emit(data)

    def _on_update_signal(self, data: dict):
        """Handle UI update signal (main thread)."""
        # 1. Update Motor Status - อัปเดตข้อความสถานะมอเตอร์บนหน้าจอ
        if Constants.KEY_MOTOR in data:
            motor_state = data[Constants.KEY_MOTOR]
            self.lbl_motor_status.setText(f"Motor: {motor_state}")

            # Change color based on state
            if motor_state == Constants.MOTOR_OPEN:
                self.lbl_motor_status.setStyleSheet("color: green; margin: 2px; font-weight: bold;")
            else:
                self.lbl_motor_status.setStyleSheet("color: red; margin: 2px; font-weight: bold;")

        # 2. Update Food Weight (Bowl) - อัปเดตตัวเลขน้ำหนักในชามอาหาร
        if Constants.KEY_FOOD_WEIGHT in data:
            try:
                weight = float(data[Constants.KEY_FOOD_WEIGHT])
                self.feed_weight.setText(f"{int(weight)} g")

                # Update Bowl Icon - เปลี่ยนรูปไอคอนตามว่ามีอาหารเหลือไหม
                if weight <= 0:
                    icon_path = self.settings.icon_food_empty or ":/icon/pet-food_10551725.png"
                else:
                    icon_path = self.settings.icon_food_full or ":/icon/pet-food_10551327.png"

                if icon_path.startswith(":/") or Path(icon_path).exists():
                    self.food_icon_label.setPixmap(QtGui.QPixmap(icon_path))
            except (ValueError, TypeError):
                pass

        # 3. Update Food Amount (Storage)
        if Constants.KEY_AMOUNT in data:
            try:
                amount = float(data[Constants.KEY_AMOUNT])
                self.label_5.setText(f"{int(amount)} g")

                # Update Storage Icon
                if amount <= 0:
                    icon_path = self.settings.icon_feeder_empty or ":/icon/pet-feeder_emthy.png"
                elif amount <= self.settings.weight_threshold_mid:
                    icon_path = self.settings.icon_feeder_mid or ":/icon/pet-feeder_mid.png"
                else:
                    icon_path = self.settings.icon_feeder_full or ":/icon/pet-feeder_full.png"

                if icon_path.startswith(":/") or Path(icon_path).exists():
                    self.food_icon_label_2.setPixmap(QtGui.QPixmap(icon_path))
            except (ValueError, TypeError):
                pass

    def _setup_connections(self):
        """Setup button click connections."""
        self.feed_bt.clicked.connect(self._on_feed_open)
        self.stop_bt.clicked.connect(self._on_feed_close)
        self.fill_food.clicked.connect(self._on_fill_food)
        self.comboBox.currentIndexChanged.connect(self._on_month_changed)

        self.logger.debug("Button connections established")

    def _setup_graph(self):
        """Setup the graph widget."""
        self.mygraph = pg.PlotWidget(self.centralwidget)
        self.mygraph.setGeometry(QtCore.QRect(390, 80, 320, 200))
        self.mygraph.setBackground((253, 235, 255))
        self.mygraph.setObjectName("graphview")

        # Setup date axis
        axis = pg.DateAxisItem(orientation='bottom')
        self.mygraph.setAxisItems({'bottom': axis})

        self.logger.debug("Graph widget initialized")

    def _setup_timers(self):
        """Setup update timers."""
        self.timer = QTimer(self.main_window)
        self.timer.timeout.connect(self._update_feed_weight)
        self.timer.timeout.connect(self._update_feed_amount)
        self.timer.start(self.settings.ui_update_interval)

        self.logger.debug(f"Update timer started ({self.settings.ui_update_interval}ms)")

    def _on_feed_open(self):
        """Handle FEED button click."""
        self.logger.info("User clicked FEED button")
        self.status[Constants.KEY_STATUS] = Constants.CMD_FEED_ON
        self.mqtt.publish(self.settings.mqtt_topic_control, self.status)

    def _on_feed_close(self):
        """Handle STOP button click."""
        self.logger.info("User clicked STOP button")
        self.status[Constants.KEY_STATUS] = Constants.CMD_FEED_OFF
        self.mqtt.publish(self.settings.mqtt_topic_control, self.status)

    def _on_fill_food(self):
        """Handle FILL FOOD button click."""
        self.logger.info("User clicked FILL FOOD button")
        self.status[Constants.KEY_STATUS] = Constants.CMD_RESET
        self.mqtt.publish(self.settings.mqtt_topic_control, self.status)

    def _on_month_changed(self):
        """Handle month selection change."""
        self._load_and_plot_monthly_data()

    def _update_feed_weight(self):
        """Update food weight display from database."""
        try:
            food_weight = self.db.get_latest_food_weight()

            if food_weight is not None:
                self.feed_weight.setText(f"{int(food_weight)} g")

                # Update icon based on weight
                if food_weight <= 0:
                    # Use configured icon path or fallback to resource
                    icon_path = self.settings.icon_food_empty or ":/icon/pet-food_10551725.png"
                else:
                    icon_path = self.settings.icon_food_full or ":/icon/pet-food_10551327.png"

                # Only update if icon path is valid
                if icon_path.startswith(":/") or Path(icon_path).exists():
                    self.food_icon_label.setPixmap(QtGui.QPixmap(icon_path))
            else:
                self.feed_weight.setText("No data")

        except Exception as e:
            self.logger.error(f"Error updating feed weight: {e}")
            self.feed_weight.setText("Error")

    def _update_feed_amount(self):
        """Update food amount display from database."""
        try:
            status_mount = self.db.get_latest_status_mount()

            if status_mount is not None:
                # Try to parse as float
                try:
                    amount = float(status_mount)
                    self.label_5.setText(f"{int(amount)} g")

                    # Update icon based on amount
                    if amount <= 0:
                        icon_path = self.settings.icon_feeder_empty or ":/icon/pet-feeder_emthy.png"
                    elif amount <= self.settings.weight_threshold_mid:
                        icon_path = self.settings.icon_feeder_mid or ":/icon/pet-feeder_mid.png"
                    else:
                        icon_path = self.settings.icon_feeder_full or ":/icon/pet-feeder_full.png"

                    # Only update if icon path is valid
                    if icon_path.startswith(":/") or Path(icon_path).exists():
                        self.food_icon_label_2.setPixmap(QtGui.QPixmap(icon_path))

                except ValueError:
                    # Status mount is not a number (e.g., "empty")
                    self.label_5.setText(status_mount)
                    icon_path = self.settings.icon_feeder_empty or ":/icon/pet-feeder_emthy.png"
                    if icon_path.startswith(":/") or Path(icon_path).exists():
                        self.food_icon_label_2.setPixmap(QtGui.QPixmap(icon_path))
            else:
                self.label_5.setText("No data")

        except Exception as e:
            self.logger.error(f"Error updating feed amount: {e}")
            self.label_5.setText("Error")

    def _load_and_plot_monthly_data(self):
        """Load and plot feeding data for selected month."""
        month_name = self.comboBox.currentText().strip()

        if month_name not in Constants.MONTHS:
            self.mygraph.setTitle("Invalid month selected")
            self.logger.warning(f"Invalid month selected: {month_name}")
            return

        month_number = Constants.MONTHS[month_name]

        try:
            # Get data from database
            data = self.db.get_monthly_data(month_number)

            if data:
                weights = [weight for weight, _ in data]
                timestamps = [ts for _, ts in data]

                # Clear and plot
                self.mygraph.clear()
                x_values = np.arange(len(timestamps))
                self.mygraph.plot(x_values, weights, pen=pg.mkPen(color='b', width=2))
                self.mygraph.setLabel('left', "Food Weight (g)")
                self.mygraph.setLabel('bottom', "Date")
                self.mygraph.setTitle(f"Food Weight for {month_name}")
                self.mygraph.showGrid(x=True, y=True)

                self.logger.debug(f"Plotted {len(data)} data points for {month_name}")
            else:
                self.mygraph.clear()
                self.mygraph.setTitle(f"No Data Available for {month_name}")
                self.logger.info(f"No data available for {month_name}")

        except Exception as e:
            self.logger.error(f"Error loading monthly data: {e}")
            self.mygraph.setTitle("Error loading data")


def create_application(mqtt_client, database, settings):
    """Create and initialize the application.

    Args:
        mqtt_client: MQTT client instance
        database: Database handler instance
        settings: Application settings

    Returns:
        tuple: (QApplication, QMainWindow, SmartPetFeederApp)
    """
    app = QtWidgets.QApplication(sys.argv)
    main_window = QtWidgets.QMainWindow()
    ui = SmartPetFeederApp(main_window, mqtt_client, database, settings)
    return app, main_window, ui
