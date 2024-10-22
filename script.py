electricity_bill = int(input('What is your average monthly electricity bill in euros? '))
gas_bill = int(input('What is your average monthly gas bill in euros? '))
fuel_bill = int(input('What is your average monthly fuel bill for transportation in euros? '))

energy_usage = round((electricity_bill * 12 * 0.0005) + (gas_bill * 12 * 0.0053) + (fuel_bill * 12 * 2.32), 3)
print(f"Energy's part in your carbot footprint is {energy_usage} kgCO2")


waste_amt = int(input('How much waste do you generate per month in kilograms? '))
recycled_prc = float(input('How much of that waste is recycled or composed (in percentage)? '))

waste = round(waste_amt * 12 * (0.57-recycled_prc), 3)
print(f"Waste's part in your carbot footprint is {waste} kgCO2")


travel_km = int(input('How many kilometers do your employees travel per year for business purposes? '))
fuel_eff = int(input('What is the average fuel efficiency of the vehicles used for business travel in liters per 100 kilometers? '))
travel = round(travel_km * 1/fuel_eff/100 * 2.31, 3)
print(f"Travel's part in your carbot footprint is {travel} kgCO2")