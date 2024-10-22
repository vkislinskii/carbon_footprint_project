electricity_bill = int(input('What is your average monthly electricity bill in euros? '))
gas_bill = int(input('What is your average monthly gas bill in euros? '))
fuel_bill = int(input('What is your average monthly fuel bill for transportation in euros? '))

energy_usage = round((electricity_bill * 12 * 0.0005) + (gas_bill * 12 * 0.0053) + (fuel_bill * 12 * 2.32), 3)
print(f"Energy's part in your carbot footprint is {energy_usage} euros")
