from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.exporter import DataExporter
from app.file_loader import FileLoader
from app.merger import NATradiusMerger


class ProcessThread(QThread):
    """Thread that processes NAT/RADIUS files in the background."""

    progress = pyqtSignal(str)
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, nat_files, radius_files):
        super().__init__()
        self.nat_files = nat_files
        self.radius_files = radius_files

    def run(self):
        try:
            self.progress.emit("Loading NAT files...")
            nat_records = FileLoader.load_all_nat_records(self.nat_files)

            self.progress.emit("Loading RADIUS files...")
            radius_records = FileLoader.load_all_radius_records(self.radius_files)

            self.progress.emit("Merging NAT and RADIUS data...")
            merger = NATradiusMerger(time_window_minutes=5)
            merged = merger.merge(nat_records, radius_records)

            self.progress.emit(f"Merge complete: {len(merged)} records")
            self.finished.emit(merged)
        except Exception as exc:  # pragma: no cover
            self.error.emit(str(exc))


class MainWindow(QMainWindow):
    """Main GUI window for the NAT/RADIUS merger."""

    def __init__(self):
        super().__init__()
        self.nat_files = []
        self.radius_files = []
        self.merged_data = []
        self.init_ui()
        self.setWindowTitle("NAT/RADIUS Merger")
        self.resize(1400, 900)

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()

        file_layout = QHBoxLayout()

        nat_button = QPushButton("Add NAT files (.gz)")
        nat_button.clicked.connect(self.select_nat_files)
        file_layout.addWidget(nat_button)

        self.nat_label = QLabel("0 NAT file(s)")
        file_layout.addWidget(self.nat_label)

        radius_button = QPushButton("Add RADIUS files (.txt)")
        radius_button.clicked.connect(self.select_radius_files)
        file_layout.addWidget(radius_button)

        self.radius_label = QLabel("0 RADIUS file(s)")
        file_layout.addWidget(self.radius_label)

        main_layout.addLayout(file_layout)

        action_layout = QHBoxLayout()
        merge_button = QPushButton("Merge")
        merge_button.clicked.connect(self.merge_files)
        action_layout.addWidget(merge_button)

        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self.clear_files)
        action_layout.addWidget(clear_button)

        main_layout.addLayout(action_layout)

        self.status_label = QLabel("Ready")
        main_layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        self.results_table = QTableWidget()
        self.results_table.setColumnCount(11)
        self.results_table.setHorizontalHeaderLabels([
            "NAT Time",
            "MSISDN",
            "IP Private",
            "NAT Type",
            "Event Type",
            "Original Source IP",
            "Translated IP",
            "Destination IP",
            "Device",
            "Protocol",
            "RADIUS State",
        ])
        main_layout.addWidget(self.results_table)

        export_layout = QHBoxLayout()
        csv_button = QPushButton("Export CSV")
        csv_button.clicked.connect(self.export_csv)
        export_layout.addWidget(csv_button)

        excel_button = QPushButton("Export Excel")
        excel_button.clicked.connect(self.export_excel)
        export_layout.addWidget(excel_button)

        main_layout.addLayout(export_layout)

        central_widget.setLayout(main_layout)

    def select_nat_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select NAT files",
            "",
            "GZ Files (*.gz);;All Files (*)",
        )
        if files:
            self.nat_files.extend(files)
            self.nat_label.setText(f"{len(self.nat_files)} NAT file(s)")
            self.status_label.setText(f"Added {len(files)} NAT file(s)")

    def select_radius_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select RADIUS files",
            "",
            "Text Files (*.txt);;All Files (*)",
        )
        if files:
            self.radius_files.extend(files)
            self.radius_label.setText(f"{len(self.radius_files)} RADIUS file(s)")
            self.status_label.setText(f"Added {len(files)} RADIUS file(s)")

    def clear_files(self):
        self.nat_files = []
        self.radius_files = []
        self.nat_label.setText("0 NAT file(s)")
        self.radius_label.setText("0 RADIUS file(s)")
        self.status_label.setText("Ready")

    def merge_files(self):
        if not self.nat_files or not self.radius_files:
            QMessageBox.warning(self, "Error", "Please select NAT and RADIUS files before merging.")
            return

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        self.thread = ProcessThread(self.nat_files, self.radius_files)
        self.thread.progress.connect(self.update_status)
        self.thread.finished.connect(self.display_results)
        self.thread.error.connect(self.show_error)
        self.thread.start()

    def update_status(self, message):
        self.status_label.setText(message)
        self.progress_bar.setValue((self.progress_bar.value() + 25) % 100)

    def display_results(self, merged_records):
        self.merged_data = merged_records
        self.results_table.setRowCount(len(merged_records))

        for row, record in enumerate(merged_records):
            self.results_table.setItem(row, 0, QTableWidgetItem(str(record.nat_time)))
            self.results_table.setItem(row, 1, QTableWidgetItem(record.msisdn))
            self.results_table.setItem(row, 2, QTableWidgetItem(record.ip_private))
            self.results_table.setItem(row, 3, QTableWidgetItem(record.nat_type))
            self.results_table.setItem(row, 4, QTableWidgetItem(record.event_type))
            self.results_table.setItem(row, 5, QTableWidgetItem(record.original_source_ip))
            self.results_table.setItem(row, 6, QTableWidgetItem(record.translated_ip))
            self.results_table.setItem(row, 7, QTableWidgetItem(record.destination_ip))
            self.results_table.setItem(row, 8, QTableWidgetItem(record.device_name))
            self.results_table.setItem(row, 9, QTableWidgetItem(record.protocol))
            state = "Connection" if record.radius_state == 1 else "Disconnection"
            self.results_table.setItem(row, 10, QTableWidgetItem(state))

        self.progress_bar.setVisible(False)
        self.status_label.setText(f"Done: {len(merged_records)} records")

    def show_error(self, message):
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "Error", f"{message}")
        self.status_label.setText("Processing failed")

    def export_csv(self):
        if not self.merged_data:
            QMessageBox.warning(self, "Error", "No data to export.")
            return

        path, _ = QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV Files (*.csv);;All Files (*)")
        if path:
            if DataExporter.export_to_csv(self.merged_data, path):
                QMessageBox.information(self, "Success", f"Saved to {path}")
            else:
                QMessageBox.warning(self, "Error", "CSV export failed.")

    def export_excel(self):
        if not self.merged_data:
            QMessageBox.warning(self, "Error", "No data to export.")
            return

        path, _ = QFileDialog.getSaveFileName(self, "Save Excel", "", "Excel Files (*.xlsx);;All Files (*)")
        if path:
            if DataExporter.export_to_excel(self.merged_data, path):
                QMessageBox.information(self, "Success", f"Saved to {path}")
            else:
                QMessageBox.warning(self, "Error", "Excel export failed.")
