import json
import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText

class ShoppingListManager:
    def __init__(self, recipe_manager):
        self.recipe_manager = recipe_manager

    def generate_shopping_list(self):
        """
        Generate a shopping list with full recipe details for enabled recipes and write it to a file.
        """
        try:
            with open("favorites.json", "r") as file:
                favorites = json.load(file)

            if not favorites:
                print("No favorite recipes available to generate a shopping list.")
                return

            shopping_list = []
            full_recipe_details = []

            # Collect missing ingredients and recipe details for enabled recipes
            for recipe in favorites:
                if recipe.get("enabled", True):  # Only include enabled recipes
                    shopping_list.extend([item['name'] for item in recipe.get('missedIngredients', [])])
                    full_recipe_details.append({
                        "title": recipe["title"],
                        "ingredients": [ingredient['name'] for ingredient in recipe["usedIngredients"]],
                        "missing_ingredients": [ingredient['name'] for ingredient in recipe["missedIngredients"]],
                        "instructions": recipe.get("instructions", "No instructions available."),
                        "link": recipe.get("sourceUrl", "No link available")
                    })

            shopping_list = list(set(shopping_list))  # Remove duplicates

            # Write shopping list and recipes to file
            with open("shopping_list.txt", "w") as file:
                file.write("--- Shopping List ---\n")
                for item in shopping_list:
                    file.write(f"- {item}\n")

                file.write("\n--- Full Recipe Details ---\n")
                for recipe in full_recipe_details:
                    file.write(f"\nTitle: {recipe['title']}\n")
                    file.write(f"Ingredients: {', '.join(recipe['ingredients'])}\n")
                    file.write(f"Missing Ingredients: {', '.join(recipe['missing_ingredients'])}\n")
                    file.write(f"Instructions: {recipe['instructions']}\n")
                    file.write(f"Link: {recipe['link']}\n")
                    file.write("-" * 40 + "\n")

            print("Shopping list and full recipes saved to shopping_list.txt.")

            # Ask user if they want to email the shopping list
            send_email = input("Do you want to email this shopping list? (yes/no): ").strip().lower()
            if send_email == "yes":
                self.email_shopping_list()

        except (FileNotFoundError, json.JSONDecodeError):
            print("No favorite recipes available to generate a shopping list.")

    def email_shopping_list(self):
        """
        Send the shopping list via email.
        """
        load_dotenv("passwords.env")
        email_user = os.getenv("EMAIL_USER")
        email_password = os.getenv("EMAIL_PASS")

        if not email_user or not email_password:
            print("Email credentials are missing in the .env file.")
            return

        recipient = input("Enter the recipient's email address: ").strip()

        try:
            with open("shopping_list.txt", "r") as file:
                shopping_list_content = file.read()

            # Create the email
            msg = MIMEText(shopping_list_content)
            msg["Subject"] = "Your Shopping List and Recipe Details"
            msg["From"] = email_user
            msg["To"] = recipient

            # Send the email
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(email_user, email_password)
                server.send_message(msg)

            print("Shopping list sent successfully via email.")

        except Exception as e:
            print(f"Failed to send email: {e}")
