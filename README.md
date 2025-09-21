# Sand Fineness Modulus (FM) Calculator 🏗️

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![Python Version](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/)
[![GitHub issues](https://img.shields.io/github/issues/rudra-mondal/sand-fm-calculator)](https://github.com/rudra-mondal/sand-fm-calculator/issues)
[![GitHub forks](https://img.shields.io/github/forks/rudra-mondal/sand-fm-calculator)](https://github.com/rudra-mondal/sand-fm-calculator/network)
[![GitHub stars](https://img.shields.io/github/stars/rudra-mondal/sand-fm-calculator)](https://github.com/rudra-mondal/sand-fm-calculator/stargazers)

A professional desktop application for civil engineers, lab technicians, and students to perform sieve analysis of sand, calculate its Fineness Modulus (FM), classify the sand type, and generate detailed, professional-grade PDF reports.

![Main Application Window](https://raw.githubusercontent.com/rudra-mondal/sand-fm-calculator/main/screenshots/main_window.png)

## 🌟 About The Project

In the field of civil engineering and material science, determining the fineness modulus of sand is a crucial step in concrete mix design. It helps in understanding the gradation of fine aggregate, which directly impacts the workability, strength, and durability of concrete.

This Sand FM Calculator was built to simplify and automate this process. It provides an intuitive graphical user interface (GUI) to input sieve analysis data, instantly calculates the FM, visualizes the grain size distribution curve, and exports all the information into a polished, ready-to-share PDF report.

### ✨ Key Features

*   📊 **Intuitive Data Entry:** A clean table-based interface for entering weights retained on standard sieve sizes.
*   🔢 **Automatic Calculation:** Instantly calculates cumulative percentage retained, percentage passing, and the final Fineness Modulus.
*   🏷️ **Sand Classification:** Automatically classifies the sand as "Fine," "Medium," or "Coarse" based on the calculated FM value.
*   📈 **Dynamic Gradation Curve:** Generates and displays a beautiful gradation curve using Matplotlib and Seaborn, providing a clear visual representation of the sand's particle size distribution.
*   📄 **Professional PDF Reporting:** Exports a comprehensive, multi-section PDF report with a single click. The report includes:
    *   Project & Sample Details
    *   Final Test Results (FM and Sand Type)
    *   A detailed Sieve Analysis Data Table
    *   The Gradation Curve Graph
*   ✅ **ASTM Standard Reference:** Displays ASTM standard limits for percentage passing on each sieve for quick compliance checks.

## 🚀 Getting Started

Follow these instructions to get a copy of the project up and running on your local machine.

### Prerequisites

*   Python 3.6 or higher
*   `pip` (Python package installer)

### ⚙️ Installation & Setup

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/rudra-mondal/sand-fm-calculator.git
    ```

2.  **Navigate to the project directory:**
    ```sh
    cd sand-fm-calculator
    ```

3.  **Create and activate a virtual environment (Recommended):**
    *   **On Windows:**
        ```sh
        python -m venv venv
        .\venv\Scripts\activate
        ```
    *   **On macOS/Linux:**
        ```sh
        python3 -m venv venv
        source venv/bin/activate
        ```

4.  **Install the required dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

## 🎮 Usage

Once the setup is complete, you can run the application with the following command:

```sh
python fm-calculator.py
```

The main application window will appear, and you can start your analysis.

### Workflow

1.  **Enter Data:** Input the weight (in grams) of sand retained on each sieve into the "Weight (g)" column of the table.
2.  **Calculate:** Click the **"Calculate FM"** button. The application will populate the table with calculated values and display the Fineness Modulus. The gradation curve will also be generated on the right.
3.  **Export Report:** Click the **"Export Report"** button (which is now enabled).
4.  **Enter Details:** A dialog box will pop up asking for project/sample information (e.g., Site Name, Supplier, Sampling Date). Fill in the relevant details.
5.  **Save PDF:** Choose a location on your computer to save the generated PDF report.
6.  **Done!** 🎉 A professional report is now ready.

### 📄 Sample PDF Report

![Sample PDF Report](https://raw.githubusercontent.com/rudra-mondal/sand-fm-calculator/main/screenshots/report.png)

## 📁 Project Structure

The repository is organized as follows:

```
sand-fm-calculator/
│
├── LICENCE            # The MIT License file.
├── README.md          # This README file.
├── fm-calculator.py   # The main application source code.
├── icon.ico           # The application icon.
└── requirements.txt   # A list of Python dependencies for the project.
```

## 🤝 Contributing

Contributions make the open-source community an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

Don't forget to give the project a star! Thanks again! ⭐

## 📜 License

This project is distributed under the MIT License. See the `LICENSE` file for more information.

## 🙏 Acknowledgments

   Special thanks to the developers of **PyQt5**, **Matplotlib**, **Seaborn**, and **ReportLab** for their incredible libraries that made this project possible.