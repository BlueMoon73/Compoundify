-----

# Compoundify

Compoundify is an advanced, user-friendly tool designed to calculate and visualize your investment growth over time, accounting for various contribution strategies, lump sum changes, and the crucial impact of inflation.

-----

## Features

  * **Flexible Contributions:** Define multiple phases with varying monthly contributions and optional annual increases.
  * **Lump Sums:** Incorporate one-time additions or subtractions at specific ages.
  * **Inflation Adjustment:** Get accurate real (inflation-adjusted) values by using either an annual inflation rate or a total rate over your investment period.
  * **4% Rule Projection:** See potential annual retirement income based on the 4% rule, both nominally and inflation-adjusted.
  * **Interactive Plot:** Visualize your portfolio's nominal and inflation-adjusted growth over time.
  * **PDF Export:** Generate a detailed report of your analysis for easy sharing or record-keeping.

-----

## How to Use

### Option 1: Run the Python Script

1.  **Prerequisites:** Ensure you have Python installed, along with the necessary libraries.

    ```bash
    pip install matplotlib reportlab
    ```

    *(Note: `tkinter` is usually included with Python; if not, you may need to install it via your OS package manager.)*

2.  **Download:** Get the `compoundify.py` file from this repository.

3.  **Run:** Open your terminal or command prompt, navigate to the directory where you saved the file, and execute:

    ```bash
    python compoundify.py
    ```

### Option 2: Use the Executable (Windows Only)

1.  **Download:** Go to the [Releases](https://github.com/BlueMoon73/compoundify/releases/) section of this repository and download the `compoundify.exe` file from the latest release.
2.  **Run:** Simply double-click `compoundify.exe` to launch the application. No Python installation is required.

-----
## Simulate your future

Compoundify aims to allow maximum customization with "contribution" phases, depending on age ranges. This is very powerful, and allows you to mimic your expected earnings over time and your expected investments. This can also simulate annual raises, or just an annual increase in monthly savings, due to to various factors. Compoundify's contribution phases allow for a very accurate simulation of expected earnigns and portfolio growth!


## Understanding Inflation

Compoundify highlights the significant impact of inflation on your long-term wealth. Even a low annual inflation rate, compounded over decades, can drastically reduce the future purchasing power of your money. The "inflation-adjusted" figures provide a realistic view of what your future wealth will truly be worth in today's dollars.

-----
