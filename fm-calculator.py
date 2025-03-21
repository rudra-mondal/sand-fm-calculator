import sys
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                            QHeaderView, QMessageBox, QFileDialog, QDialog, QFormLayout)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, Image, Paragraph, Spacer, SimpleDocTemplate, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime

# Corrected ASTM C33 Standard Limits for Fine Aggregate
ASTM_LIMITS = {
    4.75: "95-100%",
    2.36: "85-100%",
    1.18: "40-80%",
    0.6: "20-60%",
    0.3: "10-40%",
    0.15: "0-20%",
    0: "0-10%"
}

# Define Sand Type based on Fineness Modulus (example ranges - adjust as per ASTM/standards)
SAND_TYPES = {
    "Fine Sand": (1.0, 2.2),
    "Medium Sand": (2.2, 3.0),
    "Coarse Sand": (3.0, 4.0)
}

def get_sand_type(fm_value):
    for sand_type, fm_range in SAND_TYPES.items():
        if fm_range[0] <= fm_value <= fm_range[1]:
            return sand_type
    return "Not Classified"

class ExportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Export Details")
        self.setWindowIcon(QIcon("fm_icon.png"))
        self.layout = QFormLayout(self)

        self.fields = {
            "lot_number": QLineEdit(),
            "site_name": QLineEdit(),
            "sample_name": QLineEdit(),
            "supplier_name": QLineEdit(),
            "total_weight": QLineEdit(),
            "sampling_date": QLineEdit(),
            "testing_date": QLineEdit() # Added testing_date field
        }

        for label, field in self.fields.items():
            self.layout.addRow(label.replace("_", " ").title() + ":", field)

        buttons = QHBoxLayout()
        self.ok_btn = QPushButton("OK")
        self.cancel_btn = QPushButton("Cancel")
        buttons.addWidget(self.ok_btn)
        buttons.addWidget(self.cancel_btn)

        self.layout.addRow(buttons)
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

    def get_data(self):
        return {key: field.text() for key, field in self.fields.items()}

class FMCalculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Professional Sand Fineness Modulus Calculator")
        self.setWindowIcon(QIcon("fm_icon.png"))
        self.setGeometry(100, 100, 1400, 900)

        self.sieve_sizes = [4.75, 2.36, 1.18, 0.6, 0.3, 0.15, 0]
        self.weights = {}
        self.fm_value = 0.0
        self.cumulative_percentages = []

        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.main_layout = QVBoxLayout()
        self.main_widget.setLayout(self.main_layout)

        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        input_group = QWidget()
        input_layout = QHBoxLayout(input_group)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Sieve (mm)", "Weight (g)", "Cumulative %", "% Passing", "ASTM Limit"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setRowCount(len(self.sieve_sizes))

        for row, size in enumerate(self.sieve_sizes):
            size_item = QTableWidgetItem(f"{size:.2f}" if size != 0 else "Pan")
            size_item.setFlags(size_item.flags() ^ Qt.ItemIsEditable)
            self.table.setItem(row, 0, size_item)

            self.table.setItem(row, 1, QTableWidgetItem())

            for col in [2, 3]:
                item = QTableWidgetItem()
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                self.table.setItem(row, col, item)

            astm_item = QTableWidgetItem(ASTM_LIMITS.get(size, "N/A"))
            astm_item.setFlags(astm_item.flags() ^ Qt.ItemIsEditable)
            self.table.setItem(row, 4, astm_item)

        input_layout.addWidget(self.table)

        control_panel = QWidget()
        control_layout = QVBoxLayout(control_panel)

        self.result_label = QLabel("Fineness Modulus: ")
        self.result_label.setAlignment(Qt.AlignCenter)

        self.calculate_btn = QPushButton("Calculate FM")
        self.calculate_btn.clicked.connect(self.calculate_fm)

        self.export_btn = QPushButton("Export Report")
        self.export_btn.clicked.connect(self.export_report)
        self.export_btn.setEnabled(False)

        self.figure = plt.figure(figsize=(6, 4)) # Adjust figure size for better PDF layout
        self.canvas = FigureCanvas(self.figure)

        control_layout.addWidget(self.result_label)
        control_layout.addWidget(self.calculate_btn)
        control_layout.addWidget(self.export_btn)
        control_layout.addWidget(self.canvas)

        input_layout.addWidget(control_panel)
        self.main_layout.addWidget(input_group)

    def apply_styles(self):
        sns.set_style("whitegrid")
        self.setStyleSheet("""
            QMainWindow { background-color: #f5f7fa; }
            QTableWidget {
                background-color: white;
                border: 1px solid #d1d5db;
                font-size: 12px;
            }
            QHeaderView::section {
                background-color: #e5e7eb;
                color: black;
                padding: 4px;
                border: 0px;
                border-bottom: 1px solid #d1d5db;
            }
            QTableWidget QTableCornerButton::section {
                background-color: #e5e7eb;
                border: 0px;
                border-bottom: 1px solid #d1d5db;
                border-right: 1px solid #d1d5db;
            }
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-size: 14px;
                min-width: 120px;
            }
            QPushButton:hover { background-color: #2563eb; }
            QLabel { font-size: 16px; padding: 10px; }
        """)
        self.result_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #1e3a8a;
                background-color: #dbeafe;
                border-radius: 5px;
                padding: 15px;
            }
        """)

    def calculate_fm(self):
        try:
            total_weight = 0
            weights = []

            for row in range(self.table.rowCount()):
                weight_text = self.table.item(row, 1).text()
                if not weight_text:
                    raise ValueError(f"Weight value is missing in row {row + 1}")
                weight = float(weight_text)
                weights.append(weight)
                total_weight += weight

            if total_weight <= 0:
                raise ValueError("Total weight must be greater than zero")

            cumulative_sum = 0
            self.cumulative_percentages = []

            for i, weight in enumerate(weights[:-1]):
                cumulative_sum += weight
                percent_retained = (cumulative_sum / total_weight) * 100
                percent_passing = 100 - percent_retained
                self.cumulative_percentages.append(percent_retained)
                self.table.item(i, 2).setText(f"{percent_retained:.2f}")
                self.table.item(i, 3).setText(f"{percent_passing:.2f}")

            self.table.item(len(weights)-1, 2).setText("0.00")
            self.table.item(len(weights)-1, 3).setText("0.00")

            self.fm_value = sum(self.cumulative_percentages) / 100
            self.result_label.setText(f"Fineness Modulus: {self.fm_value:.2f}")
            self.export_btn.setEnabled(True)
            self.update_graph()

        except ValueError as ve:
            QMessageBox.critical(self, "Input Error", str(ve))
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def update_graph(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        x = self.sieve_sizes[:-1]
        y = [100 - p for p in self.cumulative_percentages]

        sns.lineplot(x=x, y=y, marker='o', color='#3b82f6', linewidth=2, markersize=8, ax=ax)
        ax.set_xlabel('Sieve Size (mm)', fontsize=10, fontweight='bold', labelpad=10, color='#525252')
        ax.set_ylabel('% Passing', fontsize=10, fontweight='bold', labelpad=10, color='#525252')
        ax.set_title('Gradation Curve', fontsize=14, fontweight='bold', pad=15, color='#333333')
        ax.grid(True, linestyle='--', alpha=0.6, color='#d3d3d3') # Lighter grid lines
        ax.invert_xaxis()
        ax.tick_params(axis='both', which='major', labelsize=9, color='#737373', labelcolor='#737373') # Muted tick colors

        # Ensure equal spacing for x-axis labels
        ax.set_xticks(x)
        ax.set_xticklabels([f"{size} mm" for size in x], rotation=45, ha='right', color='#525252')
        ax.set_xlim(max(x) + 0.2, min(x) - 0.2) # Adjust x limits for better visual spacing

        for xs, ys in zip(x, y):
            ax.annotate(f'{ys:.1f}%', (xs, ys), textcoords="offset points",
                       xytext=(0,8), ha='center', fontsize=9, color='#525252')

        ax.spines['bottom'].set_color('#b0b0b0')
        ax.spines['top'].set_color('#b0b0b0')
        ax.spines['left'].set_color('#b0b0b0')
        ax.spines['right'].set_color('#b0b0b0')

        plt.tight_layout(rect=[0, 0, 1, 0.97]) # Adjust layout to fit title and labels
        self.canvas.draw()

    def export_report(self):
        try:
            dialog = ExportDialog(self)
            if dialog.exec_() != QDialog.Accepted:
                return

            meta_data = dialog.get_data()
            path, _ = QFileDialog.getSaveFileName(
                self, "Save Report", "", "PDF Files (*.pdf)")

            if path:
                doc = SimpleDocTemplate(path, pagesize=A4, rightMargin=inch*0.75, leftMargin=inch*0.75, topMargin=inch*0.75, bottomMargin=inch*0.75) # Adjusted margins
                story = []
                styles = getSampleStyleSheet()
                title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=22, alignment=1, spaceAfter=8, textColor=colors.HexColor('#2c3e50'), fontName='Helvetica-Bold') # Darker title color
                heading_style = ParagraphStyle('HeadingStyle', parent=styles['Heading2'], fontSize=16, spaceAfter=6, spaceBefore=12, textColor=colors.HexColor('#3498db'), fontName='Helvetica-Bold') # Vibrant heading color
                normal_style = styles['Normal']
                bold_style = ParagraphStyle('BoldStyle', parent=styles['Normal'], fontName='Helvetica-Bold')
                small_bold_style = ParagraphStyle('SmallBoldStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9) # Smaller font in tables
                small_normal_style = ParagraphStyle('SmallNormalStyle', parent=styles['Normal'], fontSize=9, leading=11, wordWrap='NoWrap', truncateAt='None') # Smaller font, adjusted leading, NoWrap
                footer_style = ParagraphStyle('FooterStyle', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=1) # Even smaller footer
                label_style = ParagraphStyle('LabelStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, textColor=colors.black, rightIndent=6) # Label style with right indent for spacing
                value_style = ParagraphStyle('ValueStyle', parent=styles['Normal'], fontSize=9, textColor=colors.black, wordWrap='NoWrap', truncateAt='None') # Value style, NoWrap

                # Report Header with Line
                story.append(Paragraph("SAND FINENESS MODULUS TEST REPORT", title_style))
                story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black, spaceAfter=6)) # Line under title
                story.append(Spacer(1, 0.1*inch))

                # Sample Information in Two Columns - No Table Style
                story.append(Paragraph("Sample Information", heading_style))
                story.append(Spacer(1, 0.1*inch))

                meta_content = [
                    ("Site Name", meta_data['site_name']),
                    ("Lot/Truck No", meta_data['lot_number']),
                    ("Supplier", meta_data['supplier_name']),
                    ("Sample ID", meta_data['sample_name']),
                    ("Total Weight", meta_data['total_weight'] + " g" if meta_data['total_weight'] else ""),
                    ("Sampling Date", meta_data['sampling_date']),
                    ("Testing Date", meta_data['testing_date'] if meta_data['testing_date'] else datetime.now().strftime("%d %b %Y; %I:%M %p")) # 12H format
                ]

                col1_flowables = []
                col2_flowables = []

                for i, (label, value) in enumerate(meta_content):
                    para_label = Paragraph(f"{label}:", label_style)
                    para_value = Paragraph(value if value else "-", value_style) # Display "-" if value is empty

                    if (i + 1) % 2 != 0: # Odd items in column 1
                        col1_flowables.append(para_label)
                        col1_flowables.append(para_value)
                        col1_flowables.append(Spacer(1, 0.04*inch)) # Added spacer between items
                    else: # Even items in column 2
                        col2_flowables.append(para_label)
                        col2_flowables.append(para_value)
                        col2_flowables.append(Spacer(1, 0.04*inch)) # Added spacer between items

                sample_info_table_data = [[col1_flowables, col2_flowables]] if col2_flowables else [[col1_flowables]]
                sample_info_table = Table(sample_info_table_data, colWidths=[3.2*inch, 3.2*inch] if col2_flowables else [6.4*inch]) # Adjust column widths
                sample_info_table.setStyle(TableStyle([
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                    ('LEFTPADDING', (0,0), (-1,-1), 0), # Remove padding
                    ('RIGHTPADDING', (0,0), (-1,-1), 0), # Remove padding
                    ('TOPPADDING', (0,0), (-1,-1), 0), # Remove padding
                    ('BOTTOMPADDING', (0,0), (-1,-1), 0), # Removed row spacing, using spacers now
                    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#fdfdfe')), # Very light background for consistency
                    ('GRID', (0,0), (-1,-1), 0.2, colors.HexColor('#fdfdfe')), #  No grid
                    ('BOX', (0,0), (-1,-1), 0.2, colors.HexColor('#fdfdfe')), # No box
                ]))
                story.append(sample_info_table)
                story.append(Spacer(1, 0.2*inch))

                # Test Results Section
                story.append(Paragraph("Test Results", heading_style))

                test_results_data = [
                    [Paragraph("Fineness Modulus:", small_bold_style), Paragraph(f"{self.fm_value:.2f}", small_normal_style)]
                ]

                # Sand Type Determination and Display
                sand_type = get_sand_type(self.fm_value)
                test_results_data.append([Paragraph("Sand Type:", small_bold_style), Paragraph(sand_type, small_normal_style)])

                test_table = Table(test_results_data, colWidths=[1.5*inch, 3*inch])
                test_table.setStyle(TableStyle([
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 3), # Reduced padding
                ]))
                story.append(test_table)
                story.append(Spacer(1, 0.2*inch))

                # Data Table Section
                story.append(Paragraph("Sieve Analysis Data", heading_style))
                data = [
                    [Paragraph("Sieve Size (mm)", small_bold_style), Paragraph("Weight (g)", small_bold_style),
                     Paragraph("Cumulative % Retained", small_bold_style), Paragraph("% Passing", small_bold_style),
                     Paragraph("ASTM Limit", small_bold_style)]
                ]
                reversed_astm_limits = [ASTM_LIMITS[size] for size in sorted(ASTM_LIMITS.keys(), reverse=True)] # Get ASTM limits in correct order
                for row in range(self.table.rowCount()):
                    data.append([
                        Paragraph(self.table.item(row, 0).text(), small_normal_style),
                        Paragraph(self.table.item(row, 1).text(), small_normal_style),
                        Paragraph(self.table.item(row, 2).text(), small_normal_style),
                        Paragraph(self.table.item(row, 3).text(), small_normal_style),
                        Paragraph(reversed_astm_limits[row], small_normal_style) # Use reversed ASTM limits
                    ])

                table = Table(data, colWidths=[0.9*inch, 1.0*inch, 1.4*inch, 1.0*inch, 1.3*inch]) # Further adjusted widths
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#3498db')), # Vibrant header color
                    ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0,0), (-1,0), 9), # Smaller header font
                    ('FONTSIZE', (0,1), (-1,-1), 8), # Even smaller data font
                    ('BOTTOMPADDING', (0,0), (-1,0), 6), # Reduced header padding
                    ('TOPPADDING', (0,0), (-1,0), 6), # Reduced header padding
                    ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#fdfdfe')), # Very light data background
                    ('GRID', (0,0), (-1,-1), 0.2, colors.HexColor('#e0e0e0')), # Light data grid
                    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#fdfdfe')]) # Alternating subtle row colors
                ]))
                story.append(table)
                story.append(Spacer(1, 0.3*inch))

                # Graph Section - Heading Removed
                # story.append(Paragraph("Gradation Curve", heading_style)) # Heading Removed
                graph_path = "temp_graph.png"
                self.figure.savefig(graph_path, dpi=150, bbox_inches='tight', facecolor='white')
                img = Image(graph_path, width=5*inch, height=2.8*inch) # Slightly smaller graph
                img.hAlign = 'CENTER'
                story.append(img)
                story.append(Spacer(1, 0.3*inch))

                # Footer with Line
                story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black, spaceBefore=6)) # Line above footer
                footer_text = "Generated by Professional FM Calculator | Confidential Report | Page 1 of 1"
                story.append(Paragraph(footer_text, footer_style))

                doc.build(story)
                QMessageBox.information(self, "Success", "Professional report generated successfully")

        except Exception as e:
            QMessageBox.critical(self, "Export Error", str(e))
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Arial", 10))
    window = FMCalculator()
    window.show()
    sys.exit(app.exec_())