import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import io  # To save the plot to a buffer before adding to PDF


def calculate_investment_growth(initial_investment, rate_of_return, phases, lump_sums, initial_age,
                                inflation_rate, inflation_type):
    """
    Calculates investment growth over multiple phases with varying contributions
    and lump sum additions, also accounting for inflation.
    """
    current_value = initial_investment
    total_contributed_monthly = 0
    total_lump_sums_added = 0
    growth_data = []

    phases.sort(key=lambda x: x['start_age'])
    lump_sums.sort(key=lambda x: x['age'])

    min_sim_age = initial_age
    if phases:
        min_sim_age = min(min_sim_age, phases[0]['start_age'])
    if lump_sums:
        min_sim_age = min(min_sim_age, lump_sums[0]['age'])

    max_sim_age = initial_age
    if phases:
        max_sim_age = max(max_sim_age, max(p['end_age'] for p in phases))
    if lump_sums:
        max_sim_age = max(max_sim_age, max(ls['age'] for ls in lump_sums))

    if max_sim_age <= initial_age and initial_investment > 0:
        max_sim_age = initial_age + 1

    annual_inflation_rate_for_calc = 0.0
    if inflation_type == 'annual':
        annual_inflation_rate_for_calc = inflation_rate
    elif inflation_type == 'total_over_investment_period':
        investment_duration_years = max_sim_age - initial_age
        if investment_duration_years > 0:
            annual_inflation_rate_for_calc = (1 + inflation_rate) ** (1 / investment_duration_years) - 1

    current_sim_age = min_sim_age
    while current_sim_age <= max_sim_age:  # Loop until the end of max_sim_age

        # Apply lump sums at the beginning of the year if applicable
        lump_sums_this_year = [ls for ls in lump_sums if ls['age'] == current_sim_age]
        for ls in lump_sums_this_year:
            current_value += ls['amount']
            total_lump_sums_added += ls['amount']

        monthly_contribution_this_year = 0
        active_phases = [p for p in phases if p['start_age'] <= current_sim_age < p['end_age']]
        if active_phases:
            base_monthly = active_phases[-1]['monthly_contribution']
            annual_increase = active_phases[-1]['annual_increase']
            years_in_current_phase = current_sim_age - active_phases[-1]['start_age']
            monthly_contribution_this_year = base_monthly + (years_in_current_phase * annual_increase)

        # Simulate monthly compounding for the current year
        for month in range(12):
            if current_sim_age >= initial_age:
                current_value += monthly_contribution_this_year
                total_contributed_monthly += monthly_contribution_this_year
            current_value *= (1 + rate_of_return / 12)

        if current_sim_age >= initial_age:
            years_elapsed_since_investing_start = current_sim_age - initial_age
            inflation_adjusted_value = current_value
            if years_elapsed_since_investing_start >= 0 and annual_inflation_rate_for_calc != 0.0:
                inflation_factor = (1 + annual_inflation_rate_for_calc) ** years_elapsed_since_investing_start
                if inflation_factor > 0:
                    inflation_adjusted_value = current_value / inflation_factor
            growth_data.append((current_sim_age, current_value, inflation_adjusted_value))

        current_sim_age += 1

    # Add one last data point for the final value at the start of the next age period if max_sim_age was reached
    # This ensures the plot represents the value at the END of the last simulated year (which is start of next age)
    if growth_data and growth_data[-1][0] < max_sim_age:  # and max_sim_age > initial_age:
        # Recalculate inflation for this final point if needed.
        years_elapsed_final = max_sim_age - initial_age
        final_inflation_adjusted_val = current_value
        if years_elapsed_final >= 0 and annual_inflation_rate_for_calc != 0.0:
            inflation_factor_final = (1 + annual_inflation_rate_for_calc) ** years_elapsed_final
            if inflation_factor_final > 0:
                final_inflation_adjusted_val = current_value / inflation_factor_final
        growth_data.append((max_sim_age, current_value, final_inflation_adjusted_val))

    final_nominal_value = current_value
    final_inflation_adjusted_value = 0.0
    if growth_data:
        final_inflation_adjusted_value = growth_data[-1][2]
    elif initial_investment > 0:
        final_inflation_adjusted_value = initial_investment

    final_total_contributed_sum = initial_investment + total_contributed_monthly + total_lump_sums_added
    return growth_data, final_nominal_value, final_inflation_adjusted_value, final_total_contributed_sum, total_lump_sums_added


def add_phase():
    """Adds a new row of input fields for a contribution phase."""
    phase_row_frame = ttk.Frame(phases_frame)
    # Grid is handled by relabel_and_regrid_phases

    phase_num = len(phase_entries) + 1

    start_age_label = ttk.Label(phase_row_frame, text=f"Phase {phase_num} Start Age:")
    start_age_label.grid(row=0, column=0, padx=2, pady=2, sticky='w')
    start_age_entry = ttk.Entry(phase_row_frame, width=8)
    start_age_entry.grid(row=0, column=1, padx=2, pady=2, sticky='ew')

    end_age_label = ttk.Label(phase_row_frame, text="End Age:")
    end_age_label.grid(row=0, column=2, padx=2, pady=2, sticky='w')
    end_age_entry = ttk.Entry(phase_row_frame, width=8)
    end_age_entry.grid(row=0, column=3, padx=2, pady=2, sticky='ew')

    monthly_contrib_label = ttk.Label(phase_row_frame, text="Monthly Cont.:")
    monthly_contrib_label.grid(row=0, column=4, padx=2, pady=2, sticky='w')
    monthly_contrib_entry = ttk.Entry(phase_row_frame, width=10)
    monthly_contrib_entry.grid(row=0, column=5, padx=2, pady=2, sticky='ew')

    annual_increase_label = ttk.Label(phase_row_frame, text="Annual Inc.:")
    annual_increase_label.grid(row=0, column=6, padx=2, pady=2, sticky='w')
    annual_increase_entry = ttk.Entry(phase_row_frame, width=10)
    annual_increase_entry.grid(row=0, column=7, padx=2, pady=2, sticky='ew')

    current_phase_widgets = {
        'container_frame': phase_row_frame,
        'start_age_label': start_age_label,
        'start_age': start_age_entry,
        'end_age_label': end_age_label,
        'end_age': end_age_entry,
        'monthly_contribution_label': monthly_contrib_label,
        'monthly_contribution': monthly_contrib_entry,
        'annual_increase_label': annual_increase_label,
        'annual_increase': annual_increase_entry
    }

    remove_button = ttk.Button(phase_row_frame, text="Remove", width=8,
                               command=lambda w=current_phase_widgets: remove_phase_entry(w))
    remove_button.grid(row=0, column=8, padx=(5, 2), pady=2)
    current_phase_widgets['remove_button'] = remove_button

    # Configure column weights for the phase_row_frame to make entries expand
    for i in [1, 3, 5, 7]:  # Columns with entry widgets
        phase_row_frame.columnconfigure(i, weight=1)

    phase_entries.append(current_phase_widgets)
    relabel_and_regrid_phases()


def remove_phase_entry(widgets_dict_to_remove):
    """Removes a phase entry and its UI elements."""
    if widgets_dict_to_remove in phase_entries:
        phase_entries.remove(widgets_dict_to_remove)
    widgets_dict_to_remove['container_frame'].destroy()
    relabel_and_regrid_phases()


def relabel_and_regrid_phases():
    """Updates labels and re-grids all phase entries."""
    add_phase_button.grid_forget()  # Temporarily remove to re-grid properly
    add_phase_button.grid(row=0, column=0, sticky='ew', pady=5,
                          columnspan=2)  # Span if phases_frame has multiple columns

    for i, widgets_dict in enumerate(phase_entries):
        widgets_dict['start_age_label'].config(text=f"Phase {i + 1} Start Age:")
        widgets_dict['container_frame'].grid(row=i + 1, column=0, columnspan=2, sticky='ew', pady=2)
        # Ensure container_frame spans if phases_frame is configured for multiple columns at this level


def add_lump_sum():
    """Adds a new row of input fields for a lump sum."""
    lump_sum_row_frame = ttk.Frame(lump_sums_frame)
    # Grid is handled by relabel_and_regrid_lump_sums

    lump_sum_num = len(lump_sum_entries) + 1

    age_label = ttk.Label(lump_sum_row_frame, text=f"Lump Sum {lump_sum_num} Age:")
    age_label.grid(row=0, column=0, padx=2, pady=2, sticky='w')
    age_entry = ttk.Entry(lump_sum_row_frame, width=10)
    age_entry.grid(row=0, column=1, padx=2, pady=2, sticky='ew')

    amount_label = ttk.Label(lump_sum_row_frame, text="Amount:")
    amount_label.grid(row=0, column=2, padx=2, pady=2, sticky='w')
    amount_entry = ttk.Entry(lump_sum_row_frame, width=15)
    amount_entry.grid(row=0, column=3, padx=2, pady=2, sticky='ew')

    current_lump_sum_widgets = {
        'container_frame': lump_sum_row_frame,
        'age_label': age_label,
        'age': age_entry,
        'amount_label': amount_label,
        'amount': amount_entry
    }

    remove_button = ttk.Button(lump_sum_row_frame, text="Remove", width=8,
                               command=lambda w=current_lump_sum_widgets: remove_lump_sum_entry(w))
    remove_button.grid(row=0, column=4, padx=(5, 2), pady=2)
    current_lump_sum_widgets['remove_button'] = remove_button

    lump_sum_row_frame.columnconfigure(1, weight=1)  # Age entry
    lump_sum_row_frame.columnconfigure(3, weight=1)  # Amount entry

    lump_sum_entries.append(current_lump_sum_widgets)
    relabel_and_regrid_lump_sums()


def remove_lump_sum_entry(widgets_dict_to_remove):
    """Removes a lump sum entry and its UI elements."""
    if widgets_dict_to_remove in lump_sum_entries:
        lump_sum_entries.remove(widgets_dict_to_remove)
    widgets_dict_to_remove['container_frame'].destroy()
    relabel_and_regrid_lump_sums()


def relabel_and_regrid_lump_sums():
    """Updates labels and re-grids all lump sum entries."""
    add_lump_sum_button.grid_forget()
    add_lump_sum_button.grid(row=0, column=0, sticky='ew', pady=5, columnspan=2)

    for i, widgets_dict in enumerate(lump_sum_entries):
        widgets_dict['age_label'].config(text=f"Lump Sum {i + 1} Age:")
        widgets_dict['container_frame'].grid(row=i + 1, column=0, columnspan=2, sticky='ew', pady=2)


def run_calculation():
    global current_growth_data, current_final_value, current_inflation_adjusted_final_value, \
        current_total_contributed, current_total_lump_sums_added, current_initial_age, \
        current_initial_investment, current_rate_of_return, current_phases, current_lump_sums, \
        current_inflation_rate, current_inflation_type

    try:
        initial_investment = float(initial_investment_entry.get())
        rate_of_return = float(annual_rate_entry.get()) / 100
        initial_age = int(initial_age_entry_val.get())

        phases = []
        for p_dict in phase_entries:  # Iterate through list of widget dictionaries
            start_age_str = p_dict['start_age'].get()
            end_age_str = p_dict['end_age'].get()
            monthly_contribution_str = p_dict['monthly_contribution'].get()
            annual_increase_str = p_dict['annual_increase'].get()

            if not all([start_age_str, end_age_str, monthly_contribution_str, annual_increase_str]):
                continue

            start_age = int(start_age_str)
            end_age = int(end_age_str)
            monthly_contribution = float(monthly_contribution_str)
            annual_increase = float(annual_increase_str)
            phases.append({
                'start_age': start_age,
                'end_age': end_age,
                'monthly_contribution': monthly_contribution,
                'annual_increase': annual_increase
            })

        lump_sums = []
        for ls_dict in lump_sum_entries:  # Iterate through list of widget dictionaries
            age_str = ls_dict['age'].get()
            amount_str = ls_dict['amount'].get()

            if not all([age_str, amount_str]):
                continue

            age = int(age_str)
            amount = float(amount_str)
            lump_sums.append({'age': age, 'amount': amount})

        inflation_rate = float(inflation_rate_entry.get()) / 100
        inflation_type = inflation_type_var.get()

        current_initial_investment = initial_investment
        current_rate_of_return = rate_of_return
        current_phases = phases  # Store the processed data, not widget dicts
        current_lump_sums = lump_sums  # Store the processed data
        current_initial_age = initial_age
        current_inflation_rate = inflation_rate
        current_inflation_type = inflation_type

        current_growth_data, current_final_value, current_inflation_adjusted_final_value, \
            current_total_contributed, current_total_lump_sums_added = calculate_investment_growth(
            initial_investment, rate_of_return, phases, lump_sums, initial_age,
            inflation_rate, inflation_type
        )

        final_value_label.config(text=f"Final Nominal Value: ${current_final_value:,.2f}")
        inflation_adjusted_final_value_label.config(
            text=f"Final Inflation-Adjusted Value: ${current_inflation_adjusted_final_value:,.2f}")
        total_contributed_label.config(
            text=f"Total Contributed (Initial + Monthly + Lump Sums): ${current_total_contributed:,.2f}")
        total_monthly_only = current_total_contributed - initial_investment - current_total_lump_sums_added
        total_monthly_contributed_label.config(text=f"Total Monthly Contributions Only: ${total_monthly_only:,.2f}")
        total_lump_sums_label.config(text=f"Total Lump Sums Added: ${current_total_lump_sums_added:,.2f}")
        four_percent_rule_income = current_final_value * 0.04
        four_percent_rule_label.config(text=f"4% Rule Annual Income (Nominal): ${four_percent_rule_income:,.2f}")
        four_percent_rule_income_adjusted = current_inflation_adjusted_final_value * 0.04
        four_percent_rule_label_adjusted.config(
            text=f"4% Rule Annual Income (Inflation-Adjusted): ${four_percent_rule_income_adjusted:,.2f}")

        update_plot(current_growth_data)

    except ValueError as ve:
        messagebox.showerror("Input Error", f"Please enter valid numerical values for all fields: {ve}")
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()


def update_plot(growth_data):
    ax.clear()
    if growth_data:
        ages = [item[0] for item in growth_data]
        nominal_values = [item[1] for item in growth_data]
        adjusted_values = [item[2] for item in growth_data]

        ax.plot(ages, nominal_values, marker='o', linestyle='-', color='skyblue', label='Nominal Value')
        ax.plot(ages, adjusted_values, marker='x', linestyle='--', color='orange', label='Inflation-Adjusted Value')
        ax.legend()

    ax.set_title("Investment Growth Over Time")
    ax.set_xlabel("Age")
    ax.set_ylabel("Portfolio Value ($)")
    ax.ticklabel_format(style='plain', axis='y')
    ax.grid(True)
    canvas.draw()


def export_to_pdf():
    if not current_growth_data:
        messagebox.showinfo("No Data", "Please calculate the investment growth first.")
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
        title="Save Investment Report as PDF"
    )

    if not file_path:
        return

    try:
        doc = SimpleDocTemplate(file_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        story.append(Paragraph("Investment Growth Report", styles['h1']))
        story.append(Spacer(1, 0.2 * inch))

        story.append(Paragraph("<b>Input Parameters:</b>", styles['h2']))
        story.append(Paragraph(f"Initial Investment: ${current_initial_investment:,.2f}", styles['Normal']))
        story.append(Paragraph(f"Starting Age: {current_initial_age}", styles['Normal']))
        story.append(
            Paragraph(f"Estimated Annual Rate of Return: {current_rate_of_return * 100:.2f}%", styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))

        story.append(Paragraph("<b>Inflation Settings:</b>", styles['h3']))
        inflation_desc = f"Inflation Rate: {current_inflation_rate * 100:.2f}%"
        if current_inflation_type == 'annual':
            inflation_desc += " (Annual Rate)"
        else:
            min_sim_age_for_pdf = current_initial_age
            if current_phases: min_sim_age_for_pdf = min(min_sim_age_for_pdf, current_phases[0]['start_age'])
            if current_lump_sums: min_sim_age_for_pdf = min(min_sim_age_for_pdf, current_lump_sums[0]['age'])
            max_sim_age_for_pdf = current_initial_age
            if current_phases: max_sim_age_for_pdf = max(max_sim_age_for_pdf, max(p['end_age'] for p in current_phases))
            if current_lump_sums: max_sim_age_for_pdf = max(max_sim_age_for_pdf,
                                                            max(ls['age'] for ls in current_lump_sums))
            if max_sim_age_for_pdf <= current_initial_age and current_initial_investment > 0:
                max_sim_age_for_pdf = current_initial_age + 1
            investment_duration_years_for_pdf = max_sim_age_for_pdf - current_initial_age
            inflation_desc += f" (Total Rate over Investment Period of {investment_duration_years_for_pdf} years)"
        story.append(Paragraph(inflation_desc, styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))

        story.append(Paragraph("<b>Contribution Phases:</b>", styles['h3']))
        if current_phases:
            for i, phase in enumerate(current_phases):
                story.append(Paragraph(f"  Phase {i + 1}: Ages {phase['start_age']} to {phase['end_age'] - 1} "
                                       f"(Monthly: ${phase['monthly_contribution']:,.2f}, Annual Inc.: ${phase['annual_increase']:,.2f})",
                                       styles['Normal']))
        else:
            story.append(Paragraph("  No specific contribution phases defined.", styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))

        story.append(Paragraph("<b>Lump Sum Additions:</b>", styles['h3']))
        if current_lump_sums:
            for i, ls in enumerate(current_lump_sums):
                story.append(
                    Paragraph(f"  Lump Sum {i + 1}: At Age {ls['age']} - ${ls['amount']:,.2f}", styles['Normal']))
        else:
            story.append(Paragraph("  No lump sum additions.", styles['Normal']))
        story.append(Spacer(1, 0.2 * inch))

        story.append(Paragraph("<b>Results Summary:</b>", styles['h2']))
        story.append(Paragraph(f"Final Nominal Value: ${current_final_value:,.2f}", styles['Normal']))
        story.append(Paragraph(f"Final Inflation-Adjusted Value: ${current_inflation_adjusted_final_value:,.2f}",
                               styles['Normal']))
        story.append(
            Paragraph(f"Total Amount Contributed (Initial + Monthly + Lump Sums): ${current_total_contributed:,.2f}",
                      styles['Normal']))
        total_monthly_only = current_total_contributed - current_initial_investment - current_total_lump_sums_added
        story.append(Paragraph(f"Total Monthly Contributions Only: ${total_monthly_only:,.2f}", styles['Normal']))
        story.append(Paragraph(f"Total Lump Sums Added: ${current_total_lump_sums_added:,.2f}", styles['Normal']))
        four_percent_rule_income = current_final_value * 0.04
        story.append(
            Paragraph(f"Annual Income (4% Rule - Nominal): ${four_percent_rule_income:,.2f}", styles['Normal']))
        four_percent_rule_income_adjusted = current_inflation_adjusted_final_value * 0.04
        story.append(
            Paragraph(f"Annual Income (4% Rule - Inflation-Adjusted): ${four_percent_rule_income_adjusted:,.2f}",
                      styles['Normal']))
        story.append(Spacer(1, 0.3 * inch))

        img_buffer = io.BytesIO()
        fig.savefig(img_buffer, format='png', bbox_inches='tight')
        img_buffer.seek(0)
        img = Image(img_buffer)
        img_width = 6 * inch
        img_height = (img_width / fig.get_figwidth()) * fig.get_figheight()
        img.drawWidth = img_width
        img.drawHeight = img_height
        story.append(Paragraph("<b>Investment Growth Plot:</b>", styles['h2']))
        story.append(img)
        story.append(Spacer(1, 0.2 * inch))

        doc.build(story)
        messagebox.showinfo("PDF Export", f"Report saved successfully to {file_path}")

    except Exception as e:
        messagebox.showerror("PDF Export Error", f"Failed to export PDF: {e}")
        import traceback
        traceback.print_exc()


# Global storage for UI elements and calculation data
current_growth_data = []
current_final_value = 0.0
current_inflation_adjusted_final_value = 0.0
current_total_contributed = 0.0
current_total_lump_sums_added = 0.0
current_initial_investment = 0.0
current_rate_of_return = 0.0
current_phases = []  # Stores processed data for PDF
current_lump_sums = []  # Stores processed data for PDF
current_initial_age = 0
current_inflation_rate = 0.0
current_inflation_type = "annual"

# --- GUI Setup ---
root = tk.Tk()
root.title("Advanced Compound Interest Calculator")

main_frame = ttk.Frame(root, padding="10")
main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# --- General Inputs Frame ---
general_inputs_frame = ttk.LabelFrame(main_frame, text="General Investment Details", padding="10")
general_inputs_frame.grid(row=0, column=0, padx=5, pady=5, sticky='new')
general_inputs_frame.columnconfigure(1, weight=1)

ttk.Label(general_inputs_frame, text="Initial Investment ($):").grid(row=0, column=0, padx=5, pady=2, sticky='w')
initial_investment_entry = ttk.Entry(general_inputs_frame)
initial_investment_entry.grid(row=0, column=1, padx=5, pady=2, sticky='ew')
initial_investment_entry.insert(0, "10000")

ttk.Label(general_inputs_frame, text="Estimated Annual Rate of Return (%):").grid(row=1, column=0, padx=5, pady=2,
                                                                                  sticky='w')
annual_rate_entry = ttk.Entry(general_inputs_frame)
annual_rate_entry.grid(row=1, column=1, padx=5, pady=2, sticky='ew')
annual_rate_entry.insert(0, "9")

ttk.Label(general_inputs_frame, text="Your Starting Age:").grid(row=2, column=0, padx=5, pady=2, sticky='w')
initial_age_entry_val = ttk.Entry(general_inputs_frame)
initial_age_entry_val.grid(row=2, column=1, padx=5, pady=2, sticky='ew')
initial_age_entry_val.insert(0, "18")

# --- Inflation Settings Frame ---
inflation_frame = ttk.LabelFrame(main_frame, text="Inflation Settings", padding="10")
inflation_frame.grid(row=0, column=1, padx=5, pady=5, sticky='new')
inflation_frame.columnconfigure(1, weight=1)

ttk.Label(inflation_frame, text="Inflation Rate (%):").grid(row=0, column=0, padx=5, pady=2, sticky='w')
inflation_rate_entry = ttk.Entry(inflation_frame)
inflation_rate_entry.grid(row=0, column=1, padx=5, pady=2, sticky='ew')
inflation_rate_entry.insert(0, "2.3")

inflation_type_var = tk.StringVar(value="annual")
radio_annual = ttk.Radiobutton(inflation_frame, text="Annual Inflation Rate", variable=inflation_type_var,
                               value="annual")
radio_annual.grid(row=1, column=0, columnspan=2, padx=5, pady=2, sticky='w')
radio_total_investment_period = ttk.Radiobutton(inflation_frame, text="Total Inflation Rate over Investment Period",
                                                variable=inflation_type_var, value="total_over_investment_period")
radio_total_investment_period.grid(row=2, column=0, columnspan=2, padx=5, pady=2, sticky='w')

# --- Contribution Phases Frame ---
phases_frame = ttk.LabelFrame(main_frame, text="Contribution Phases (Monthly Contributions)", padding="10")
phases_frame.grid(row=1, column=0, padx=5, pady=5, sticky='new')
phases_frame.columnconfigure(0, weight=1)  # Allow inner frames to expand

phase_entries = []  # Stores dictionaries of widgets for each phase row
add_phase_button = ttk.Button(phases_frame, text="Add Contribution Phase", command=add_phase)
# Initial gridding of button is handled by relabel_and_regrid_phases, called by add_phase

# --- Lump Sums Frame ---
lump_sums_frame = ttk.LabelFrame(main_frame, text="Lump Sum Additions", padding="10")
lump_sums_frame.grid(row=1, column=1, padx=5, pady=5, sticky='new')
lump_sums_frame.columnconfigure(0, weight=1)  # Allow inner frames to expand

lump_sum_entries = []  # Stores dictionaries of widgets for each lump sum row
add_lump_sum_button = ttk.Button(lump_sums_frame, text="Add Lump Sum", command=add_lump_sum)
# Initial gridding of button is handled by relabel_and_regrid_lump_sums, called by add_lump_sum

# --- Control Buttons Frame ---
control_buttons_frame = ttk.Frame(main_frame)
control_buttons_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky='ew')
control_buttons_frame.columnconfigure(0, weight=1)
control_buttons_frame.columnconfigure(1, weight=1)

calculate_button = ttk.Button(control_buttons_frame, text="Calculate Investment", command=run_calculation)
calculate_button.grid(row=0, column=0, padx=5, pady=0, sticky='ew')
export_pdf_button = ttk.Button(control_buttons_frame, text="Export to PDF", command=export_to_pdf)
export_pdf_button.grid(row=0, column=1, padx=5, pady=0, sticky='ew')

# --- Results Frame ---
results_frame = ttk.LabelFrame(main_frame, text="Results", padding="10")
results_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky='ew')

final_value_label = ttk.Label(results_frame, text="Final Nominal Value: $0.00")
final_value_label.grid(row=0, column=0, padx=5, pady=2, sticky='w')
inflation_adjusted_final_value_label = ttk.Label(results_frame, text="Final Inflation-Adjusted Value: $0.00")
inflation_adjusted_final_value_label.grid(row=1, column=0, padx=5, pady=2, sticky='w')
total_contributed_label = ttk.Label(results_frame, text="Total Contributed (Initial + Monthly + Lump Sums): $0.00")
total_contributed_label.grid(row=2, column=0, padx=5, pady=2, sticky='w')
total_monthly_contributed_label = ttk.Label(results_frame, text="Total Monthly Contributions Only: $0.00")
total_monthly_contributed_label.grid(row=3, column=0, padx=5, pady=2, sticky='w')
total_lump_sums_label = ttk.Label(results_frame, text="Total Lump Sums Added: $0.00")
total_lump_sums_label.grid(row=4, column=0, padx=5, pady=2, sticky='w')
four_percent_rule_label = ttk.Label(results_frame, text="4% Rule Annual Income (Nominal): $0.00")
four_percent_rule_label.grid(row=5, column=0, padx=5, pady=2, sticky='w')
four_percent_rule_label_adjusted = ttk.Label(results_frame, text="4% Rule Annual Income (Inflation-Adjusted): $0.00")
four_percent_rule_label_adjusted.grid(row=6, column=0, padx=5, pady=2, sticky='w')

# --- Plotting Area ---
fig, ax = plt.subplots(figsize=(8, 4))  # Adjusted figsize for better default layout
canvas = FigureCanvasTkAgg(fig, master=main_frame)
canvas_widget = canvas.get_tk_widget()
canvas_widget.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')

# Configure main_frame row/column weights for resizing
main_frame.grid_rowconfigure(1, weight=0)  # Phase/LumpSum frames should not expand vertically excessively
main_frame.grid_rowconfigure(4, weight=1)  # Plot area should expand
main_frame.grid_columnconfigure(0, weight=1)
main_frame.grid_columnconfigure(1, weight=1)

# Add initial example phase and lump sum
add_phase()
phase_entries[0]['start_age'].insert(0, "18")
phase_entries[0]['end_age'].insert(0, "25")
phase_entries[0]['monthly_contribution'].insert(0, "500")
phase_entries[0]['annual_increase'].insert(0, "0")

add_lump_sum()
lump_sum_entries[0]['age'].insert(0, "22")
lump_sum_entries[0]['amount'].insert(0, "10000")

# Initial plot setup
update_plot([])  # Or run a default calculation if desired

root.mainloop()