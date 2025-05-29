import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib import colors
import os


def calculate_investment_growth(initial_investment, rate_of_return, phases, lump_sums, initial_age):
    """
    Calculates investment growth over multiple phases with varying contributions
    and lump sum additions.

    Args:
        initial_investment (float): The starting investment amount.
        rate_of_return (float): The annual rate of return (e.g., 0.07 for 7%).
        phases (list of dict): A list of dictionaries, each defining a phase:
                                {'start_age': int, 'end_age': int, 'monthly_contribution': float, 'annual_increase': float}
        lump_sums (list of dict): A list of dictionaries, each defining a lump sum:
                                  {'age': int, 'amount': float}
        initial_age (int): The starting age of the investor.
    Returns:
        tuple: (list of tuples (year, age, value), float final_value, float total_contributed, float total_lump_sums_added)
    """

    current_value = initial_investment
    total_contributed = initial_investment  # Includes initial investment
    total_lump_sums_added = 0

    growth_data = []  # To store (year, age, value) for plotting

    # Sort phases by start_age and lump_sums by age
    phases.sort(key=lambda x: x['start_age'])
    lump_sums.sort(key=lambda x: x['age'])

    # Determine the overall simulation period
    # The simulation should run from initial_age up to the max(end_age of phases, age of lump sums)
    max_sim_age = initial_age
    if phases:
        max_sim_age = max(max_sim_age, max(p['end_age'] for p in phases))
    if lump_sums:
        max_sim_age = max(max_sim_age, max(ls['age'] for ls in lump_sums))

    # Simulate year by year
    for age_at_start_of_year in range(initial_age, max_sim_age + 1):

        # Apply lump sums at the beginning of the year if applicable
        lump_sums_this_year = [ls for ls in lump_sums if ls['age'] == age_at_start_of_year]
        for ls in lump_sums_this_year:
            current_value += ls['amount']
            total_lump_sums_added += ls['amount']
            # messagebox.showinfo("Lump Sum Added", f"At age {age_at_start_of_year}, added ${ls['amount']:,.2f} as a lump sum.")

        monthly_contribution_this_year = 0
        annual_increase_this_year = 0

        # Determine monthly contribution for this year based on phases
        # Find the active phase for the current age
        active_phase = None
        for p in phases:
            if p['start_age'] <= age_at_start_of_year < p['end_age']:
                active_phase = p
                break  # Assuming non-overlapping phases

        if active_phase:
            monthly_contribution_base = active_phase['monthly_contribution']
            annual_increase_rate = active_phase['annual_increase']

            # Calculate the effective monthly contribution for this specific year
            # The increase applies for each *full year* passed within the phase
            years_into_phase = age_at_start_of_year - active_phase['start_age']
            monthly_contribution_this_year = monthly_contribution_base + (years_into_phase * annual_increase_rate)

        # Simulate monthly compounding for the current year
        for month in range(12):
            if age_at_start_of_year < max_sim_age:  # Only contribute if still within the simulation period for contributions
                current_value += monthly_contribution_this_year
                total_contributed += monthly_contribution_this_year
            current_value *= (1 + rate_of_return / 12)

        growth_data.append((age_at_start_of_year, current_value))

    return growth_data, current_value, total_contributed, total_lump_sums_added


def add_phase():
    """Adds a new row of input fields for a contribution phase."""
    row_num = len(phase_entries) + 1

    start_age_label = ttk.Label(phases_frame, text=f"Phase {row_num} Start Age:")
    start_age_label.grid(row=row_num, column=0, padx=5, pady=2, sticky='w')
    start_age_entry = ttk.Entry(phases_frame, width=10)
    start_age_entry.grid(row=row_num, column=1, padx=5, pady=2, sticky='ew')

    end_age_label = ttk.Label(phases_frame, text="End Age:")
    end_age_label.grid(row=row_num, column=2, padx=5, pady=2, sticky='w')
    end_age_entry = ttk.Entry(phases_frame, width=10)
    end_age_entry.grid(row=row_num, column=3, padx=5, pady=2, sticky='ew')

    monthly_contrib_label = ttk.Label(phases_frame, text="Monthly Cont.:")
    monthly_contrib_label.grid(row=row_num, column=4, padx=5, pady=2, sticky='w')
    monthly_contrib_entry = ttk.Entry(phases_frame, width=10)
    monthly_contrib_entry.grid(row=row_num, column=5, padx=5, pady=2, sticky='ew')

    annual_increase_label = ttk.Label(phases_frame, text="Annual Inc.:")
    annual_increase_label.grid(row=row_num, column=6, padx=5, pady=2, sticky='w')
    annual_increase_entry = ttk.Entry(phases_frame, width=10)
    annual_increase_entry.grid(row=row_num, column=7, padx=5, pady=2, sticky='ew')

    phase_entries.append({
        'start_age': start_age_entry,
        'end_age': end_age_entry,
        'monthly_contribution': monthly_contrib_entry,
        'annual_increase': annual_increase_entry
    })


def add_lump_sum():
    """Adds a new row of input fields for a lump sum."""
    row_num = len(lump_sum_entries) + 1

    age_label = ttk.Label(lump_sums_frame, text=f"Lump Sum {row_num} Age:")
    age_label.grid(row=row_num, column=0, padx=5, pady=2, sticky='w')
    age_entry = ttk.Entry(lump_sums_frame, width=10)
    age_entry.grid(row=row_num, column=1, padx=5, pady=2, sticky='ew')

    amount_label = ttk.Label(lump_sums_frame, text="Amount:")
    amount_label.grid(row=row_num, column=2, padx=5, pady=2, sticky='w')
    amount_entry = ttk.Entry(lump_sums_frame, width=15)
    amount_entry.grid(row=row_num, column=3, padx=5, pady=2, sticky='ew')

    lump_sum_entries.append({
        'age': age_entry,
        'amount': amount_entry
    })


def run_calculation():
    """Gathers inputs and performs the calculation, then displays results."""
    global current_growth_data, current_final_value, current_total_contributed, current_total_lump_sums_added, current_four_percent_income, current_input_details
    try:
        initial_investment = float(initial_investment_entry.get())
        rate_of_return = float(annual_rate_entry.get()) / 100
        initial_age = int(initial_age_entry_val.get())

        phases = []
        for p_entries in phase_entries:
            # Ensure all fields are filled for a phase
            if not all(e.get() for e in p_entries.values()):
                continue  # Skip incomplete phase entries
            start_age = int(p_entries['start_age'].get())
            end_age = int(p_entries['end_age'].get())
            monthly_contribution = float(p_entries['monthly_contribution'].get())
            annual_increase = float(p_entries['annual_increase'].get())
            # Basic validation
            if start_age >= end_age:
                messagebox.showerror("Input Error",
                                     f"Phase from {start_age} to {end_age}: Start age must be less than end age.")
                return
            phases.append({
                'start_age': start_age,
                'end_age': end_age,
                'monthly_contribution': monthly_contribution,
                'annual_increase': annual_increase
            })

        lump_sums = []
        for ls_entries in lump_sum_entries:
            if not all(e.get() for e in ls_entries.values()):
                continue  # Skip incomplete lump sum entries
            age = int(ls_entries['age'].get())
            amount = float(ls_entries['amount'].get())
            lump_sums.append({'age': age, 'amount': amount})

        # Sort phases by start_age for consistent processing
        phases.sort(key=lambda x: x['start_age'])

        growth_data, final_value, total_contributed_raw, total_lump_sums_added = calculate_investment_growth(
            initial_investment, rate_of_return, phases, lump_sums, initial_age
        )

        # Calculate total contributed by summing up monthly contributions as they happened
        # initial_investment is tracked separately.
        # total_contributed_raw from the function includes initial_investment and lump sums.
        # We want to show just the 'monthly contributions' part for clarity.
        # The growth_data is also useful for plotting.

        # Recalculate total contributed *excluding initial investment and lump sums* for display
        calculated_total_monthly_contributed = 0
        current_val_for_contributed = initial_investment  # Temporary variable to trace

        # Sort phases by start_age for consistent processing
        phases.sort(key=lambda x: x['start_age'])

        max_age_for_contributions = initial_age
        if phases:
            max_age_for_contributions = max(max_age_for_contributions, max(p['end_age'] for p in phases))

        for age_at_start_of_year in range(initial_age, max_age_for_contributions + 1):
            monthly_contribution_this_year = 0
            active_phase = None
            for p in phases:
                if p['start_age'] <= age_at_start_of_year < p['end_age']:
                    active_phase = p
                    break

            if active_phase:
                monthly_contribution_base = active_phase['monthly_contribution']
                annual_increase_rate = active_phase['annual_increase']
                years_into_phase = age_at_start_of_year - active_phase['start_age']
                monthly_contribution_this_year = monthly_contribution_base + (years_into_phase * annual_increase_rate)

            # Only add contributions if within the valid contribution period for this age
            if age_at_start_of_year < max_age_for_contributions:
                calculated_total_monthly_contributed += (monthly_contribution_this_year * 12)

        total_contributed = calculated_total_monthly_contributed  # This is just monthly contributions

        # Store data for PDF export
        current_growth_data = growth_data
        current_final_value = final_value
        current_total_contributed = total_contributed  # Use the adjusted total
        current_total_lump_sums_added = total_lump_sums_added
        current_four_percent_income = final_value * 0.04

        current_input_details = {
            "initial_investment": initial_investment,
            "rate_of_return": rate_of_return,
            "initial_age": initial_age,
            "phases": phases,
            "lump_sums": lump_sums
        }

        # Display results
        final_value_label.config(text=f"Final Investment Value: ${current_final_value:,.2f}")
        total_contributed_label.config(text=f"Total Monthly Contributions: ${current_total_contributed:,.2f}")
        total_lump_sums_label.config(text=f"Total Lump Sums Added: ${current_total_lump_sums_added:,.2f}")
        total_overall_invested_label.config(
            text=f"Overall Total Invested (Initial + Monthly + Lump Sums): ${initial_investment + current_total_contributed + current_total_lump_sums_added:,.2f}")
        four_percent_rule_label.config(text=f"4% Rule Annual Income: ${current_four_percent_income:,.2f}")

        # Update plot
        update_plot(current_growth_data)
        export_pdf_button.config(state=tk.NORMAL)  # Enable PDF export button

    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numerical values for all filled fields.")
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {e}")


def update_plot(growth_data):
    """Updates the matplotlib plot with new data."""
    ax.clear()
    if not growth_data:
        ax.set_title("Investment Growth Over Time (No Data)")
        ax.set_xlabel("Age")
        ax.set_ylabel("Portfolio Value ($)")
    else:
        ages = [item[0] for item in growth_data]
        values = [item[1] for item in growth_data]

        ax.plot(ages, values, marker='o', linestyle='-', color='skyblue')
        ax.set_title("Investment Growth Over Time")
        ax.set_xlabel("Age")
        ax.set_ylabel("Portfolio Value ($)")
        ax.ticklabel_format(style='plain', axis='y', useOffset=False)  # Prevent scientific notation on y-axis
        ax.grid(True)
    canvas.draw()


def export_to_pdf():
    """Exports the results and plot to a PDF file."""
    if not current_growth_data:
        messagebox.showwarning("Export Error", "No data to export. Please run calculation first.")
        return

    filepath = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
        title="Save Investment Report as PDF"
    )
    if not filepath:
        return  # User cancelled

    try:
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Title
        story.append(Paragraph("Investment Growth Report", styles['h1']))
        story.append(Spacer(1, 0.2 * inch))

        # Input Details
        story.append(Paragraph("<b>Input Details:</b>", styles['h2']))
        input_data = [
            ["Initial Investment:", f"${current_input_details['initial_investment']:,.2f}"],
            ["Starting Age:", str(current_input_details['initial_age'])],
            ["Annual Rate of Return:", f"{current_input_details['rate_of_return'] * 100:.2f}%"]
        ]

        # Contribution Phases Table
        story.append(Paragraph("<b>Contribution Phases:</b>", styles['h3']))
        phase_table_data = [["Start Age", "End Age", "Monthly Contribution", "Annual Increase"]]
        for p in current_input_details['phases']:
            phase_table_data.append([
                str(p['start_age']),
                str(p['end_age']),
                f"${p['monthly_contribution']:,.2f}",
                f"${p['annual_increase']:,.2f}"
            ])
        phase_table = Table(phase_table_data, colWidths=[1 * inch, 1 * inch, 1.5 * inch, 1.2 * inch])
        phase_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(phase_table)
        story.append(Spacer(1, 0.1 * inch))

        # Lump Sums Table
        story.append(Paragraph("<b>Lump Sum Additions:</b>", styles['h3']))
        lump_sum_table_data = [["Age", "Amount"]]
        for ls in current_input_details['lump_sums']:
            lump_sum_table_data.append([
                str(ls['age']),
                f"${ls['amount']:,.2f}"
            ])
        lump_sum_table = Table(lump_sum_table_data, colWidths=[1 * inch, 1.5 * inch])
        lump_sum_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(lump_sum_table)
        story.append(Spacer(1, 0.2 * inch))

        # Save plot to a temporary file
        plot_filename = "investment_growth_plot.png"
        fig.savefig(plot_filename, format='png', dpi=300, bbox_inches='tight')

        # Add plot to PDF
        img = Image(plot_filename)
        img.drawHeight = 6.5 * inch * img.drawHeight / img.drawWidth  # Maintain aspect ratio
        img.drawWidth = 6.5 * inch
        story.append(img)
        story.append(Spacer(1, 0.2 * inch))

        # Results Summary
        story.append(Paragraph("<b>Calculation Results:</b>", styles['h2']))
        results_data = [
            ["Final Investment Value:", f"${current_final_value:,.2f}"],
            ["Total Monthly Contributions:", f"${current_total_contributed:,.2f}"],
            ["Total Lump Sums Added:", f"${current_total_lump_sums_added:,.2f}"],
            ["Overall Total Invested (Initial + Monthly + Lump Sums):",
             f"${current_input_details['initial_investment'] + current_total_contributed + current_total_lump_sums_added:,.2f}"],
            ["4% Rule Annual Income:", f"${current_four_percent_income:,.2f} (Estimated Annual Withdrawal)"]
        ]
        results_table = Table(results_data)
        results_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(results_table)

        doc.build(story)
        messagebox.showinfo("PDF Export", f"Report successfully saved to:\n{filepath}")

    except Exception as e:
        messagebox.showerror("PDF Export Error", f"Failed to export PDF: {e}")
    finally:
        # Clean up temporary plot file
        if os.path.exists(plot_filename):
            os.remove(plot_filename)


# --- GUI Setup ---
root = tk.Tk()
root.title("Advanced Compound Interest Calculator")

# Variables to store current calculation results for PDF export
current_growth_data = None
current_final_value = 0.0
current_total_contributed = 0.0
current_total_lump_sums_added = 0.0
current_four_percent_income = 0.0
current_input_details = {}

# --- Main Frame ---
main_frame = ttk.Frame(root, padding="10")
main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# --- General Inputs Frame ---
general_inputs_frame = ttk.LabelFrame(main_frame, text="General Investment Details", padding="10")
general_inputs_frame.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky='ew')

ttk.Label(general_inputs_frame, text="Initial Investment ($):").grid(row=0, column=0, padx=5, pady=2, sticky='w')
initial_investment_entry = ttk.Entry(general_inputs_frame)
initial_investment_entry.grid(row=0, column=1, padx=5, pady=2, sticky='ew')
initial_investment_entry.insert(0, "80000")  # Default value

ttk.Label(general_inputs_frame, text="Estimated Annual Rate of Return (%):").grid(row=1, column=0, padx=5, pady=2,
                                                                                  sticky='w')
annual_rate_entry = ttk.Entry(general_inputs_frame)
annual_rate_entry.grid(row=1, column=1, padx=5, pady=2, sticky='ew')
annual_rate_entry.insert(0, "7")  # Default value

ttk.Label(general_inputs_frame, text="Your Starting Age:").grid(row=2, column=0, padx=5, pady=2, sticky='w')
initial_age_entry_val = ttk.Entry(general_inputs_frame)
initial_age_entry_val.grid(row=2, column=1, padx=5, pady=2, sticky='ew')
initial_age_entry_val.insert(0, "22")  # Default value

# --- Contribution Phases Frame ---
phases_frame = ttk.LabelFrame(main_frame, text="Contribution Phases (Monthly Contributions)", padding="10")
phases_frame.grid(row=1, column=0, padx=5, pady=5, sticky='ew')

phase_entries = []
add_phase_button = ttk.Button(phases_frame, text="Add Contribution Phase", command=add_phase)
add_phase_button.grid(row=0, column=0, columnspan=8, pady=5)

# Add initial example phases
# Phase 1: 22-25, 500/month, 0 increase
add_phase()
phase_entries[0]['start_age'].insert(0, "22")
phase_entries[0]['end_age'].insert(0, "25")
phase_entries[0]['monthly_contribution'].insert(0, "500")
phase_entries[0]['annual_increase'].insert(0, "0")

# Phase 2: 25-35, 3000/month, 100 increase

# --- Lump Sums Frame ---
lump_sums_frame = ttk.LabelFrame(main_frame, text="Lump Sum Additions", padding="10")
lump_sums_frame.grid(row=1, column=1, padx=5, pady=5, sticky='ew')

lump_sum_entries = []
add_lump_sum_button = ttk.Button(lump_sums_frame, text="Add Lump Sum", command=add_lump_sum)
add_lump_sum_button.grid(row=0, column=0, columnspan=4, pady=5)

# Add initial example lump sum
add_lump_sum()
lump_sum_entries[0]['age'].insert(0, "37")
lump_sum_entries[0]['amount'].insert(0, "100000")

# --- Control Buttons ---
control_buttons_frame = ttk.Frame(main_frame, padding="10")
control_buttons_frame.grid(row=2, column=0, columnspan=2, pady=5, sticky='ew')
control_buttons_frame.columnconfigure(0, weight=1)
control_buttons_frame.columnconfigure(1, weight=1)

calculate_button = ttk.Button(control_buttons_frame, text="Calculate Investment", command=run_calculation)
calculate_button.grid(row=0, column=0, padx=5, pady=5, sticky='ew')

export_pdf_button = ttk.Button(control_buttons_frame, text="Export to PDF", command=export_to_pdf, state=tk.DISABLED)
export_pdf_button.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

# --- Results Frame ---
results_frame = ttk.LabelFrame(main_frame, text="Results", padding="10")
results_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky='ew')

final_value_label = ttk.Label(results_frame, text="Final Investment Value: $0.00", font=('Helvetica', 10, 'bold'))
final_value_label.grid(row=0, column=0, padx=5, pady=2, sticky='w')

total_contributed_label = ttk.Label(results_frame, text="Total Monthly Contributions: $0.00")
total_contributed_label.grid(row=1, column=0, padx=5, pady=2, sticky='w')

total_lump_sums_label = ttk.Label(results_frame, text="Total Lump Sums Added: $0.00")
total_lump_sums_label.grid(row=2, column=0, padx=5, pady=2, sticky='w')

total_overall_invested_label = ttk.Label(results_frame,
                                         text="Overall Total Invested (Initial + Monthly + Lump Sums): $0.00",
                                         font=('Helvetica', 10, 'bold'))
total_overall_invested_label.grid(row=3, column=0, padx=5, pady=2, sticky='w')

four_percent_rule_label = ttk.Label(results_frame, text="4% Rule Annual Income: $0.00", font=('Helvetica', 10, 'bold'),
                                    foreground='darkgreen')
four_percent_rule_label.grid(row=4, column=0, padx=5, pady=2, sticky='w')

# --- Plotting Area ---
fig, ax = plt.subplots(figsize=(8, 4))
canvas = FigureCanvasTkAgg(fig, master=main_frame)
canvas_widget = canvas.get_tk_widget()
canvas_widget.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')

# Configure row and column weights for resizing
main_frame.grid_rowconfigure(4, weight=1)  # Plotting area expands vertically
main_frame.grid_columnconfigure(0, weight=1)
main_frame.grid_columnconfigure(1, weight=1)

# Initial plot setup
ax.set_title("Investment Growth Over Time")
ax.set_xlabel("Age")
ax.set_ylabel("Portfolio Value ($)")
ax.grid(True)
canvas.draw()

root.mainloop()