from filters import Filters
from recipe_manager import RecipeManager
from menu import Menu

if __name__ == "__main__":
    api_key = "c44bbe543bd2426b830522a7643feabc"
    filters = Filters()
    recipe_manager = RecipeManager(api_key, filters)
    menu = Menu(recipe_manager)
    menu.display()
