import requests
import json
from bs4 import BeautifulSoup


class RecipeManager:
    def __init__(self, api_key, filters):
        self.api_key = api_key
        self.filters = filters

    def search_recipes_online(self, ingredients):
        url = "https://api.spoonacular.com/recipes/findByIngredients"
        params = {
            "ingredients": ingredients,
            "number": 5,
            "apiKey": self.api_key
        }

        # Apply active filters
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

                # Fetch detailed information for the recipe
                recipe_id = recipe.get("id")
                if recipe_id:
                    detail_url = f"https://api.spoonacular.com/recipes/{recipe_id}/information"
                    detail_params = {"apiKey": self.api_key}
                    try:
                        detail_response = requests.get(detail_url, params=detail_params)
                        detail_response.raise_for_status()
                        recipe_details = detail_response.json()
                        recipe["sourceUrl"] = recipe_details.get("sourceUrl", "No link available")
                        
                        # Clean up the HTML instructions
                        raw_instructions = recipe_details.get("instructions", "No instructions available.")
                        soup = BeautifulSoup(raw_instructions, "html.parser")
                        recipe["instructions"] = soup.get_text()

                        detailed_recipes.append(recipe)

                        # Print the cleaned instructions and source link
                        print(f"   Instructions: {recipe['instructions']}")
                        print(f"   Link: {recipe['sourceUrl']}")
                    except requests.exceptions.RequestException:
                        print(f"   Could not fetch details for recipe: {recipe['title']}")
                else:
                    print(f"   Skipping recipe {recipe['title']} - Missing ID.")
                print("-" * 40)

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
        try:
            with open("favorites.json", "r") as file:
                favorites = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            favorites = []
        for recipe in recipes:
            favorites.append(recipe)
        with open("favorites.json", "w") as file:
            json.dump(favorites, file, indent=4)
        print("Selected recipes saved to favorites.")

    def toggle_favorite_recipes(self):
        try:
            with open("favorites.json", "r") as file:
                favorites = json.load(file)
            if not favorites:
                print("No favorite recipes saved.")
                return

            print("\n--- Favorite Recipes ---")
            for i, recipe in enumerate(favorites, start=1):
                status = "Enabled" if recipe.get("enabled", True) else "Disabled"
                print(f"{i}. {recipe['title']} - {status}")

            print("\nEnter the numbers of the recipes to toggle, separated by commas:")
            try:
                choices = list(map(int, input("Your choices: ").strip().split(",")))
                for idx in choices:
                    if 1 <= idx <= len(favorites):
                        recipe = favorites[idx - 1]
                        recipe["enabled"] = not recipe.get("enabled", True)
                        status = "Enabled" if recipe["enabled"] else "Disabled"
                        print(f"Recipe '{recipe['title']}' is now {status}.")

                with open("favorites.json", "w") as file:
                    json.dump(favorites, file, indent=4)
            except (ValueError, IndexError):
                print("Invalid input.")
        except (FileNotFoundError, json.JSONDecodeError):
            print("No favorite recipes saved.")

    def generate_shopping_list_from_favorites(self):
        try:
            with open("favorites.json", "r") as file:
                favorites = json.load(file)

            if not favorites:
                print("No favorite recipes available to generate a shopping list.")
                return

            shopping_list = []
            for recipe in favorites:
                if recipe.get("enabled", True):
                    shopping_list.extend(
                        [item["name"] for item in recipe.get("missedIngredients", [])]
                    )

            shopping_list = list(set(shopping_list))
            with open("shopping_list.txt", "w") as file:
                for item in shopping_list:
                    file.write(f"{item}\n")
            print("Shopping list saved to shopping_list.txt.")
        except (FileNotFoundError, json.JSONDecodeError):
            print("No favorite recipes available.")

    def view_favorites(self):
        try:
            with open("favorites.json", "r") as file:
                favorites = json.load(file)
            if not favorites:
                print("No favorite recipes saved.")
                return

            print("\n--- Favorite Recipes ---")
            for recipe in favorites:
                status = "Enabled" if recipe.get("enabled", True) else "Disabled"
                print(f"Title: {recipe['title']} ({status})")
                print(f"Link: {recipe.get('sourceUrl', 'No link available')}")
                print(f"Instructions: {recipe.get('instructions', 'No instructions available.')}")
                print("-" * 40)
        except (FileNotFoundError, json.JSONDecodeError):
            print("No favorite recipes saved.")
