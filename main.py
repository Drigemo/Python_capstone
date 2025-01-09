from filters import Filters
from recipe_manager import RecipeManager
from menu import Menu
from dotenv import load_dotenv
import os

if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("SPOONACULAR_API_KEY")
    filters = Filters()
    recipe_manager = RecipeManager(api_key, filters)
    menu = Menu(recipe_manager)
    menu.display()
