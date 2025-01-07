import requests
import json
import re


class RecipeManager:
    def __init__(self, api_key, filters):
        self.api_key = api_key
        self.filters = filters  # Use Filters instance

    def strip_html_tags(self, text):
        """
        Remove HTML tags from a string.
        :param text: The input string with HTML tags.
        :return: A clean string without HTML tags.
        """
        if text:
            clean = re.sub(r"<.*?>", "", text)  # Regex to remove anything within <>
            return clean.strip()
        return "No instructions available."

    def search_recipes_online(self, ingredients=None):
        """
        Search recipes online using the Spoonacular API. Optionally, prompt the user for ingredients if not provided.
        :param ingredients: A comma-separated string of ingredients. If None, prompts the user for input.
        """
        if not ingredients:
            ingredients = input("Enter the ingredients you have (comma-separated): ").strip()

        url = "https://api.spoonacular.com/recipes/findByIngredients"
        params = {
            "ingredients": ingredients,
            "number": 5,
            "apiKey": self.api_key
        }

        # Apply active filters from Filters class
        active_filters = self.filters.filters
        if active_filters.get("diet"):
            params["diet"] = active_filters["diet"]
        if active_filters.get("cuisine"):
            params["cuisine"] = active_filters["cuisine"]
        if active_filters.get("max_time"):
            params["maxReadyTime"] = active_filters["max_time"]

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            recipes = response.json()

            if not recipes:
                print("\nNo recipes found matching your criteria.")
                return []

            detailed_recipes = []
            print("\n--- Recipes Found ---")
            for i, recipe in enumerate(recipes, start=1):
                print(f"{i}. {recipe['title']}")
                print(f"   Used Ingredients: {[i['name'] for i in recipe['usedIngredients']]}")
                print(f"   Missing Ingredients: {[i['name'] for i in recipe['missedIngredients']]}")

                # Fetch detailed recipe information
                recipe_id = recipe.get("id")
                if recipe_id:
                    detail_url = f"https://api.spoonacular.com/recipes/{recipe_id}/information"
                    detail_params = {"apiKey": self.api_key}
                    try:
                        detail_response = requests.get(detail_url, params=detail_params)
                        detail_response.raise_for_status()
                        recipe_details = detail_response.json()
                        recipe["sourceUrl"] = recipe_details.get("sourceUrl", "No link available")
                        recipe["instructions"] = self.strip_html_tags(recipe_details.get("instructions", "No instructions available."))
                        detailed_recipes.append(recipe)
                        print(f"   Instructions: {recipe['instructions']}")
                        print(f"   Link: {recipe['sourceUrl']}")
                    except requests.exceptions.RequestException:
                        print(f"   Could not fetch details for recipe: {recipe['title']}")
                print("-" * 40)

            # Allow saving favorite recipes
            save_choice = input("Do you want to save any recipes to favorites? (yes/no): ").strip().lower()
            if save_choice == "yes":
                print("Enter the numbers of the recipes to save, separated by commas:")
                try:
                    choices = list(map(int, input("Your choices: ").strip().split(",")))
                    selected_recipes = [detailed_recipes[i - 1] for i in choices if 1 <= i <= len(detailed_recipes)]
                    self.save_favorite_recipes(selected_recipes)
                except (ValueError, IndexError):
                    print("Invalid input. No recipes saved.")

            return detailed_recipes

        except requests.exceptions.RequestException as e:
            print(f"Error fetching recipes: {e}")
            return []

    def save_favorite_recipes(self, recipes):
        """
        Save selected recipes to favorites.json.
        """
        try:
            with open("favorites.json", "r") as file:
                favorites = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            favorites = []

        for recipe in recipes:
            recipe['enabled'] = True
            favorites.append(recipe)

        with open("favorites.json", "w") as file:
            json.dump(favorites, file, indent=4)
        print("Selected recipes saved to favorites.")

    def view_and_toggle_favorites(self):
        """
        View saved favorite recipes and allow the user to enable/disable them.
        """
        try:
            with open("favorites.json", "r") as file:
                favorites = json.load(file)

            if not favorites:
                print("No favorite recipes saved.")
                return

            while True:
                print("\n--- Favorite Recipes ---")
                for i, recipe in enumerate(favorites, start=1):
                    status = "\033[92mEnabled\033[0m" if recipe.get("enabled", True) else "\033[91mDisabled\033[0m"
                    print(f"{i}. {recipe['title']} ({status})")
                    print(f"   Ingredients: {', '.join([ingredient['name'] for ingredient in recipe['usedIngredients']])}")
                    print(f"   Link: {recipe.get('sourceUrl', 'No link available')}")
                    print("-" * 40)

                print("\nOptions:")
                print("1. Enable/Disable Recipes")
                print("2. Back to Main Menu")

                choice = input("Enter your choice: ").strip()
                if choice == "1":
                    print("\nEnter the numbers of the recipes to toggle, separated by commas (e.g., 1,3,5).")
                    choices = input("Your choices: ").strip()
                    try:
                        selected_indices = [int(choice) - 1 for choice in choices.split(",") if choice.strip().isdigit()]
                        for idx in selected_indices:
                            if 0 <= idx < len(favorites):
                                favorites[idx]["enabled"] = not favorites[idx].get("enabled", True)
                                status = "Enabled" if favorites[idx]["enabled"] else "Disabled"
                                print(f"Recipe '{favorites[idx]['title']}' is now {status}.")
                        with open("favorites.json", "w") as file:
                            json.dump(favorites, file, indent=4)
                    except ValueError:
                        print("Invalid input. Please enter numbers separated by commas.")
                elif choice == "2":
                    break
                else:
                    print("Invalid choice. Please try again.")
        except (FileNotFoundError, json.JSONDecodeError):
            print("No favorite recipes saved.")

    def generate_shopping_list_from_favorites(self):
        """
        Generate a shopping list based on enabled favorite recipes.
        """
        try:
            with open("favorites.json", "r") as file:
                favorites = json.load(file)
            if not favorites:
                print("No favorite recipes available to generate a shopping list.")
                return

            shopping_list = []
            for recipe in favorites:
                if recipe.get("enabled", True):
                    shopping_list.extend([item['name'] for item in recipe.get('missedIngredients', [])])

            shopping_list = list(set(shopping_list))  # Remove duplicates
            with open("shopping_list.txt", "w") as file:
                for item in shopping_list:
                    file.write(f"{item}\n")
            print("Shopping list saved to shopping_list.txt.")
        except (FileNotFoundError, json.JSONDecodeError):
            print("No favorite recipes available to generate a shopping list.")
