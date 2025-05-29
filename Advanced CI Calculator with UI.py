import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def calculate_investment_growth(initial_investment, rate_of_return, phases, lump_sums):
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
    Returns:
        tuple: (list of tuples (year, age, value), float final_value, float total_contributed, float total_lump_sums)
    """

    current_value = initial_investment
    total_contributed = initial_investment  # Includes initial investment
    total_lump_sums_added = 0

    growth_data = []  # To store (year, age, value) for plotting

    # Sort phases by start_age and lump_sums by age
    phases.sort(key=lambda x: x['start_age'])
    lump_sums.sort(key=lambda x: x['age'])

    current_age = phases[0]['start_age'] if phases else 0  # Start from the first phase's age

    # Simulate year by year
    max_end_age = max([p['end_age'] for p in phases]) if phases else current_age
    if lump_sums:
        max_end_age = max(max_end_age, max([ls['age'] for ls in lump_sums]))

    # Find the earliest starting age across all phases and initial age
    min_start_age = initial_age_entry_val.get() if initial_age_entry_val.get() else current_age  # Use initial_age for loop start

    # Ensure current_age starts from the user's initial age
    current_age = int(min_start_age) if min_start_age else (
        phases[0]['start_age'] if phases else 22)  # Default to 22 if no phases or initial age

    # Extend max_end_age to ensure full simulation period
    if phases:
        max_end_age = max(max_end_age, max(p['end_age'] for p in phases))

    # Simulate year by year
    for year_num in range(1, max_end_age - current_age + 2):  # +1 to include the end age, +1 for loop range
        age_at_start_of_year = current_age + year_num - 1

        # Apply lump sums at the beginning of the year if applicable
        lump_sums_this_year = [ls for ls in lump_sums if ls['age'] == age_at_start_of_year]
        for ls in lump_sums_this_year:
            current_value += ls['amount']
            total_lump_sums_added += ls['amount']
            messagebox.showinfo("Lump Sum Added",
                                f"At age {age_at_start_of_year}, added ${ls['amount']:,.2f} as a lump sum.")

        monthly_contribution_this_year = 0
        annual_increase_this_year = 0

        # Determine monthly contribution for this year based on phases
        active_phases = [p for p in phases if p['start_age'] <= age_at_start_of_year < p['end_age']]
        if active_phases:
            # If multiple phases overlap (which shouldn't happen if defined correctly),
            # this will take the last one. You might want a different logic here.
            monthly_contribution_this_year = active_phases[-1]['monthly_contribution']
            annual_increase_this_year = active_phases[-1]['annual_increase']

            # Adjust monthly contribution for annual increase from previous years within the phase
            # Calculate how many full years this phase has been active for this age
            years_in_current_phase = age_at_start_of_year - active_phases[-1]['start_age']
            monthly_contribution_this_year += (years_in_current_phase * annual_increase_this_year)

        # Simulate monthly compounding for the current year
        for month in range(12):
            current_value += monthly_contribution_this_year
            total_contributed += monthly_contribution_this_year
            current_value *= (1 + rate_of_return / 12)

        growth_data.append((year_num, age_at_start_of_year, current_value))

    # Calculate total contributed for phases (adjusting for annual increase across years)
    for p in phases:
        num_years_in_phase = p['end_age'] - p['start_age']
        for y in range(num_years_in_phase):
            effective_monthly_contribution = p['monthly_contribution'] + (y * p['annual_increase'])
            # We add 12 * effective_monthly_contribution in the loop above for each year
            # total_contributed already includes these implicitly if initial_investment is added at start
            # The calculation of total_contributed in the loop is more accurate as it adds real monthly contributions
            pass  # The monthly loop correctly accumulates total_contributed

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
    try:
        initial_investment = float(initial_investment_entry.get())
        rate_of_return = float(annual_rate_entry.get()) / 100
        initial_age = int(initial_age_entry_val.get())

        phases = []
        for p_entries in phase_entries:
            start_age = int(p_entries['start_age'].get())
            end_age = int(p_entries['end_age'].get())
            monthly_contribution = float(p_entries['monthly_contribution'].get())
            annual_increase = float(p_entries['annual_increase'].get())
            phases.append({
                'start_age': start_age,
                'end_age': end_age,
                'monthly_contribution': monthly_contribution,
                'annual_increase': annual_increase
            })

        lump_sums = []
        for ls_entries in lump_sum_entries:
            age = int(ls_entries['age'].get())
            amount = float(ls_entries['amount'].get())
            lump_sums.append({'age': age, 'amount': amount})

        growth_data, final_value, total_contributed, total_lump_sums_added = calculate_investment_growth(
            initial_investment, rate_of_return, phases, lump_sums
        )

        # Display results
        final_value_label.config(text=f"Final Investment Value: ${final_value:,.2f}")
        total_contributed_label.config(
            text=f"Total Contributed (excluding initial/lump sums): ${total_contributed - initial_investment - total_lump_sums_added:,.2f}")
        total_lump_sums_label.config(text=f"Total Lump Sums Added: ${total_lump_sums_added:,.2f}")

        four_percent_rule_income = final_value * 0.04
        four_percent_rule_label.config(text=f"4% Rule Annual Income: ${four_percent_rule_income:,.2f}")

        # Update plot
        update_plot(growth_data)

    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numerical values for all fields.")
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {e}")


def update_plot(growth_data):
    """Updates the matplotlib plot with new data."""
    if not growth_data:
        ax.clear()
        ax.set_title("Investment Growth Over Time")
        ax.set_xlabel("Age")
        ax.set_ylabel("Portfolio Value ($)")
        canvas.draw()
        return

    years = [item[0] for item in growth_data]
    ages = [item[1] for item in growth_data]
    values = [item[2] for item in growth_data]

    ax.clear()
    ax.plot(ages, values, marker='o', linestyle='-', color='skyblue')
    ax.set_title("Investment Growth Over Time")
    ax.set_xlabel("Age")
    ax.set_ylabel("Portfolio Value ($)")
    ax.ticklabel_format(style='plain', axis='y')  # Prevent scientific notation on y-axis
    ax.grid(True)
    canvas.draw()


# --- GUI Setup ---
root = tk.Tk()
root.title("Advanced Compound Interest Calculator")

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
# Phase 1: 20-25, 500/month, 0 increase
add_phase()
phase_entries[0]['start_age'].insert(0, "22")
phase_entries[0]['end_age'].insert(0, "25")
phase_entries[0]['monthly_contribution'].insert(0, "500")
phase_entries[0]['annual_increase'].insert(0, "0")

# Phase 2: 25-35, 3000/month, 100 increase
add_phase()
phase_entries[1]['start_age'].insert(0, "25")
phase_entries[1]['end_age'].insert(0, "35")
phase_entries[1]['monthly_contribution'].insert(0, "3000")
phase_entries[1]['annual_increase'].insert(0, "100")

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

# --- Calculate Button ---
calculate_button = ttk.Button(main_frame, text="Calculate Investment", command=run_calculation)
calculate_button.grid(row=2, column=0, columnspan=2, pady=10)

# --- Results Frame ---
results_frame = ttk.LabelFrame(main_frame, text="Results", padding="10")
results_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky='ew')

final_value_label = ttk.Label(results_frame, text="Final Investment Value: $0.00")
final_value_label.grid(row=0, column=0, padx=5, pady=2, sticky='w')

total_contributed_label = ttk.Label(results_frame, text="Total Contributed: $0.00")
total_contributed_label.grid(row=1, column=0, padx=5, pady=2, sticky='w')

total_lump_sums_label = ttk.Label(results_frame, text="Total Lump Sums Added: $0.00")
total_lump_sums_label.grid(row=2, column=0, padx=5, pady=2, sticky='w')

four_percent_rule_label = ttk.Label(results_frame, text="4% Rule Annual Income: $0.00")
four_percent_rule_label.grid(row=3, column=0, padx=5, pady=2, sticky='w')

# --- Plotting Area ---
fig, ax = plt.subplots(figsize=(8, 4))
canvas = FigureCanvasTkAgg(fig, master=main_frame)
canvas_widget = canvas.get_tk_widget()
canvas_widget.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')

# Configure row and column weights for resizing
main_frame.grid_rowconfigure(4, weight=1)
main_frame.grid_columnconfigure(0, weight=1)
main_frame.grid_columnconfigure(1, weight=1)

# Initial plot setup
ax.set_title("Investment Growth Over Time")
ax.set_xlabel("Age")
ax.set_ylabel("Portfolio Value ($)")
ax.grid(True)
canvas.draw()

root.mainloop()