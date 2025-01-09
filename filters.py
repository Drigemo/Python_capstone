import json


class Filters:
    VALID_CUISINES = [
        "African", "American", "British", "Cajun", "Caribbean", "Chinese",
        "Eastern European", "European", "French", "German", "Greek", "Indian",
        "Irish", "Italian", "Japanese", "Jewish", "Korean", "Latin American",
        "Mediterranean", "Mexican", "Middle Eastern", "Nordic", "Southern",
        "Spanish", "Thai", "Vietnamese"
    ]

    VALID_DIETS = [
        "Vegetarian", "Vegan", "Pescetarian", "Ketogenic",
        "Gluten-Free", "Paleo", "Primal", "Low FODMAP", "Whole30"
    ]

    def __init__(self):
        self.filters = self.load_filters()

    def load_filters(self):
        try:
            with open("filters.json", "r") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_filters(self):
        with open("filters.json", "w") as file:
            json.dump(self.filters, file, indent=4)
        print("Filters saved.")

    def update_filters(self):
        print("\n--- Add or Update Filters ---")
        while True:
            diet = input("Enter dietary preference (e.g., vegetarian, vegan) or press Enter to skip: ").strip().title()
            if not diet or diet.capitalize() in self.VALID_DIETS:
                break
            print("Invalid dietary preference. Choose from:", ", ".join(self.VALID_DIETS))
        while True:
            cuisine = input("Enter cuisine type (e.g., Italian, Mexican) or press Enter to skip: ").strip().title()
            if not cuisine or cuisine.capitalize() in self.VALID_CUISINES:
                break
            print("Invalid cuisine. Choose from:", ", ".join(self.VALID_CUISINES))
        max_time = input("Enter max cooking time in minutes or press Enter to skip: ").strip()
        max_time = int(max_time) if max_time.isdigit() else None
        self.filters = {"diet": diet.capitalize() if diet else None, "cuisine": cuisine.capitalize() if cuisine else None, "max_time": max_time}
        self.save_filters()

    def view_active_filters(self):
        print("\n--- Active Filters ---")
        if not any(self.filters.values()):
            print("No active filters.")
        else:
            print(f"Diet: {self.filters.get('diet', 'None')}")
            print(f"Cuisine: {self.filters.get('cuisine', 'None')}")
            print(f"Max Time: {self.filters.get('max_time', 'None')} minutes")
