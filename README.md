# Compoundify

**Compoundify** is an advanced Python application designed to help you visualize and plan your long-term investment growth, accounting for various contribution strategies and the crucial impact of inflation. Understand the true potential of your wealth over time.

-----

## ✨ Features

  * **Initial Investment & Rate of Return:** Start your calculations with a foundational lump sum and an estimated annual growth rate.
  * **Flexible Contribution Phases:** Define multiple periods where you consistently contribute a monthly amount. Each phase can include an optional annual increase to simulate salary raises or stepped-up savings plans.
  * **Lump Sum Adjustments:** Integrate one-time additions (e.g., bonuses, inheritance) or subtractions (e.g., major purchases) at specific ages.
  * **Inflation Adjustment:**
      * Calculate **real (inflation-adjusted) values** using a specified annual inflation rate.
      * Alternatively, input a **total inflation rate** which the application will automatically distribute over your **entire investment period**, providing a comprehensive view of its compounded effect.
  * **Interactive Growth Plot:** Visualize your portfolio's value over time, clearly showing both its nominal (future dollars) and inflation-adjusted (today's purchasing power) growth.
  * **Comprehensive Results Summary:** Get instant insights into your final nominal and inflation-adjusted values, total capital contributed, and projected annual income based on the **4% rule** (presented in both nominal and inflation-adjusted terms).
  * **PDF Export:** Generate a professional report detailing all your input parameters, calculation results, and the investment growth plot for easy sharing or record-keeping.

-----

## 🚀 How to Use

### Prerequisites

Ensure you have Python installed. Then, install the necessary libraries using pip:

```bash
pip install matplotlib reportlab tkinter
```

*(Note: `tkinter` is typically included with Python installations. If you encounter issues, you might need to install it separately depending on your operating system or Python distribution.)*

### Running the Application

1.  **Download:** Clone this repository or download the `compound_interest_calculator.py` file.

2.  **Execute:** Open your terminal or command prompt, navigate to the directory containing the file, and run:

    ```bash
    python compound_interest_calculator.py
    ```

### Interacting with the Interface

1.  **General Details:** Input your starting investment, estimated annual rate of return, and your current age.
2.  **Inflation Settings:** Choose your inflation calculation method and specify the rate.
3.  **Contributions:** Add multiple contribution phases, defining start/end ages, monthly amounts, and annual increases.
4.  **Lump Sums:** Add one-time financial events at specific ages.
5.  **Calculate:** Click "Calculate Investment" to update the results and plot.
6.  **Export:** Use "Export to PDF" to save a detailed report.

-----

## 🧐 Understanding Inflation-Adjusted Values

It's common for the **inflation-adjusted value** of your portfolio (and its corresponding 4% rule income) to be significantly lower than its **nominal value**, especially over long investment horizons (e.g., 20, 30, or 40+ years), even with seemingly moderate inflation rates (like 2-3%).

This phenomenon is due to the **compounding effect of inflation**. Just as your investments grow exponentially, inflation consistently erodes the purchasing power of money over time. Your calculator accurately reflects this real-world financial reality, providing a crucial perspective for true wealth planning. It ensures you understand what your future money will *actually* be able to buy in today's terms.

-----

## 🛠️ Technologies Used

  * **Python 3:** The core programming language.
  * **Tkinter:** For building the graphical user interface.
  * **Matplotlib:** For generating interactive plots of investment growth.
  * **ReportLab:** For creating PDF reports of the calculation results.

-----

## 🤝 Contributing

Contributions are welcome\! If you have suggestions for improvements, new features, or bug fixes, please open an issue or submit a pull request.

-----

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](https://www.google.com/search?q=LICENSE) file for details.

-----
