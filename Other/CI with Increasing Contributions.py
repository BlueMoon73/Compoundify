def compound_interest_calculator():
    print("Compound Interest Calculator with Increasing Contributions and 4% Rule")
    print("-----------------------------------------------------------------")

    # User inputs
    initial_investment = float(input("Enter your initial investment amount (e.g., 80000): $"))
    starting_monthly_contribution = float(input("Enter your starting monthly contribution (e.g., 2500): $"))
    annual_contribution_increase = float(input("Enter the annual increase in your monthly contribution (e.g., 100): $"))
    annual_rate_of_return = float(input("Enter the estimated annual rate of return (e.g., 7 for 7%): ")) / 100
    years_of_growth = int(input("Enter the number of years you plan to grow your investment (e.g., 30): "))
    starting_age = int(input("Enter your starting age (e.g., 22): "))

    # Initialize variables
    total_investment_value = initial_investment
    monthly_contribution = starting_monthly_contribution
    total_contributed = initial_investment

    print("\n--- Investment Growth Over Time ---")
    print(f"{'Year':<5} | {'Age':<5} | {'Monthly Cont.':<15} | {'Year End Value':<20} | {'Total Contributed':<20}")
    print("-" * 80)

    for year in range(1, years_of_growth + 1):
        # Calculate monthly growth
        for month in range(12):
            total_investment_value += monthly_contribution
            total_investment_value *= (1 + annual_rate_of_return / 12)  # Monthly compounding

        # Update monthly contribution for the next year
        if year < years_of_growth:  # Don't increase contribution after the last year of growth
            monthly_contribution += annual_contribution_increase

        # Track total contributed amount for the current year
        if year == 1:
            total_contributed += (starting_monthly_contribution * 12)
        else:
            total_contributed += (
                                             monthly_contribution - annual_contribution_increase) * 12  # Adjust for the increase in contribution

        print(
            f"{year:<5} | {starting_age + year - 1:<5} | ${monthly_contribution - annual_contribution_increase:<14.2f} | ${total_investment_value:<19.2f} | ${total_contributed:<19.2f}")

    print("\n--- Summary ---")
    print(f"Initial Investment: ${initial_investment:,.2f}")
    print(f"Starting Monthly Contribution: ${starting_monthly_contribution:,.2f}")
    print(f"Annual Contribution Increase: ${annual_contribution_increase:,.2f}")
    print(f"Estimated Annual Rate of Return: {annual_rate_of_return * 100:.2f}%")
    print(f"Years of Growth: {years_of_growth}")
    print(f"Starting Age: {starting_age}")
    print(f"Final Investment Value: ${total_investment_value:,.2f}")
    print(f"Total Amount You Contributed: ${total_contributed:,.2f}")

    # Calculate amount you can live off using the 4% rule
    four_percent_rule_income = total_investment_value * 0.04
    print(f"\n--- 4% Rule Calculation ---")
    print(
        f"Based on the 4% rule, you could potentially live off: ${four_percent_rule_income:,.2f} per year from your investments.")


# Run the calculator
compound_interest_calculator()