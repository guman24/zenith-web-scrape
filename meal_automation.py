import json

import numpy as np

# Constants
# MAX_DEV_PERCENT = 5  # Maximum allowed deviation in percentage
MAX_DEV_PERCENT = 1  # Maximum allowed deviation in percentage
FINE_TUNE_LIMIT = 0.20  # Maximum adjustment ratio for fine-tuning
ITERATION_LIMIT = 100  # Max number of iterations to avoid infinite loops

def calculate_total_nutrients(meal):
    """
    Calculate and return the total macros and calories of the meal.
    """
    totals = {'protein': 0, 'carbs': 0, 'fats': 0, 'calorie': 0}
    for item in meal:
        for nutrient in ['protein', 'carbs', 'fats', 'calorie']:
            totals[nutrient] += item[nutrient]
    return totals

def calculate_deviation(current_nutrients, target_nutrients):
    """
    Calculate the average deviation in percentage from the target nutrients.
    """
    deviations = []
    for nutrient in ['protein', 'carbs', 'fats', 'calorie']:
        target = target_nutrients[nutrient]
        current = current_nutrients[nutrient]
        deviation = 100 * abs((current - target) / target) if target != 0 else 0
        deviations.append(deviation)
    return np.mean(deviations)



def adjust_meal_global(meal, target_nutrients):
    """
    Adjust the whole meal globally to approach target nutrients by finding the best scale factor.
    Iteratively searches for the best scale factor to minimize cumulative deviation from target nutrients.
    """
    # Define initial parameters for the search
    best_scale_factor = 1
    lowest_deviation = float('inf')
    scale_factors = np.linspace(0.1, 1.5, 101)  # Search in range 50% to 150% in 1% increments

    for scale_factor in scale_factors:
        # Apply scale factor and recalculate nutrient contents for each item
        scaled_meal = []

        for item in meal:
            scaled_item = item.copy()
            scaled_quantity = item['quantity'] * scale_factor
            # Directly apply scale factor to nutrient values since they are given for the original quantity
            for nutrient in ['protein', 'carbs', 'fats', 'calorie']:
                scaled_item[nutrient] = item[nutrient] * scale_factor
            # Update the quantity to the scaled value
            scaled_item['quantity'] = scaled_quantity
            scaled_meal.append(scaled_item)


        # Calculate total nutrients for scaled meal
        total_nutrients_scaled = calculate_total_nutrients(scaled_meal)

        # Calculate deviation for scaled meal
        deviation = calculate_deviation(total_nutrients_scaled, target_nutrients)

        print(f"Scale Factor: {scale_factor:.2f}, Deviation: {deviation:.2f}%")

        # Update best scale factor if current deviation is lower
        if deviation < lowest_deviation:
            best_scale_factor = scale_factor
            lowest_deviation = deviation

    print(f"Best Scale Factor: {best_scale_factor:.2f}, Lowest Deviation: {lowest_deviation:.2f}%")

    # Apply best scale factor to original meal quantities and recalculate nutrients
    for item in meal:
        item['quantity'] = item['quantity'] * best_scale_factor
        for nutrient in ['protein', 'carbs', 'fats', 'calorie']:
            #item[nutrient] = (item[nutrient] * item['quantity']) / 100.0
            item[nutrient] = item[nutrient] * best_scale_factor

    return meal




def fine_tune_meal(meal, target_nutrients, initial_meal):
    for iteration in range(ITERATION_LIMIT):
        total_nutrients = calculate_total_nutrients(meal)
        deviation = calculate_deviation(total_nutrients, target_nutrients)

        print(f"Iteration {iteration}: Total deviation = {deviation}%")

        if deviation <= MAX_DEV_PERCENT:
            print("Target achieved within allowed deviation.")
            break

        # Assume we are directly adjusting based on deviation, without averaging across nutrients
        for item_index, item in enumerate(meal):
            # Simplified adjustment: directly proportional to deviation, for debugging
            for nutrient in ['protein', 'carbs', 'fats', 'calorie']:
                target = target_nutrients[nutrient]
                current = total_nutrients[nutrient]
                # Calculate the direct proportional adjustment needed for each nutrient
                if target != 0:
                    nutrient_deviation = (current - target) / target
                    adjustment_ratio = -nutrient_deviation * 0.05  # Apply a direct but small adjustment
                    item[nutrient] += item[nutrient] * adjustment_ratio  # Adjust nutrient directly

            # Ensure updated quantities are recalculated for adjustments to take effect
            item['quantity'] = item['quantity'] * (1 + adjustment_ratio)  # Adjust quantity

        # Recalculate the nutrient content based on adjusted quantities
        for item in meal:
            item['quantity'] = item['quantity'] * (1 + adjustment_ratio)
            for nutrient in ['protein', 'carbs', 'fats', 'calorie']:
                item[nutrient] = item[nutrient] * (1 + adjustment_ratio)


    return meal



def parse_meal(input_json):
    """
    Parse the input JSON to extract meal details into a suitable structure.
    """
    meal_data = input_json['food_items']
    meal = []

    for item in meal_data:
        meal.append({
        'name': item.get('mame', ''), # Note: Assuming 'mame' is a typo in the input JSON.
        'quantity': float(item['quantity']),
        'protein': item['protein'],
        'carbs': item['carbs'],
        'fats': item['fats'],
        'calorie': item['calorie'],
        })

    return meal

def meal_automation(input_json):
    target_nutrients = input_json['target']
    meal = parse_meal(input_json)

    # Store a copy of the initial meal for reference in fine tuning
    initial_meal = [item.copy() for item in meal]

    # Global adjustment
    adjusted_meal = adjust_meal_global(meal, target_nutrients)


    output = {
        "adjusted_meal": adjusted_meal,
        "total_nutrients": calculate_total_nutrients(adjusted_meal)
    }

    print(json.dumps(output, indent=2))

    #total_nutrients = calculate_total_nutrients(adjusted_meal)
    #print(total_nutrients)
    #deviation = calculate_deviation(total_nutrients, target_nutrients)
    #print(deviation)


    # Fine-tuning
    print("======================================")
    print("Now fine tuning")
    print("======================================")
    fine_tuned_meal = fine_tune_meal(adjusted_meal, target_nutrients, initial_meal)

    # Calculate the total nutritional values for the adjusted meal
    total_nutrients = calculate_total_nutrients(fine_tuned_meal)

    # Include the total nutrients in the output
    output = {
        "adjusted_meal": fine_tuned_meal,
        "total_nutrients": total_nutrients
    }

    return output

input_json = {

	"target": {
    "calorie": 2504.0,
    "protein": 210.0,
    "fats": 75.0,
    "carbs": 469.0
  },

	"meal":
	{
		"meal_name": "Lean Beef and Jasmine Rice Bowl with Beetroot and Avocado",
		"food_items":
		[
			{
      "name": "TEST FOOD",
      "quantity": 1.0,
      "protein": 1.0,
      "carbs": 0.0,
      "fats": 0.0,
      "calorie": 4.0
    }
        ]
	}

}

# fine_tuned_meal_result = meal_automation(input_json)
# print(json.dumps(fine_tuned_meal_result, indent=2))