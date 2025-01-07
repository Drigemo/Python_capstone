class Menu:
    def __init__(self, recipe_manager):
        self.recipe_manager = recipe_manager

    def display(self):
        while True:
            print("\n--- Main Menu ---")
            print("1. Search Recipes Online")
            print("2. Add or Update Filters")
            print("3. View Active Filters")
            print("4. View Favorite Recipes")
            print("5. Enable/Disable Favorite Recipes")
            print("6. Generate Shopping List")
            print("X - Exit")

            choice = input("Enter your choice: ").strip().lower()
            if choice == "1":
                ingredients = input("Enter the ingredients you have (comma-separated): ").strip()
                self.recipe_manager.search_recipes_online(ingredients)
            elif choice == "2":
                self.recipe_manager.filters.update_filters()
            elif choice == "3":
                self.recipe_manager.filters.view_active_filters()
            elif choice == "4":
                self.recipe_manager.view_favorites()
            elif choice == "5":
                self.recipe_manager.toggle_favorite_recipes()
            elif choice == "6":
                self.recipe_manager.generate_shopping_list_from_favorites()
            elif choice == "x":
                print("Exiting the program.")
                break
            else:
                print("Invalid choice. Please try again.")
