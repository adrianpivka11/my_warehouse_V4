"""

Initializing script with text menu for warehouse system.

Initialize app by running this file.

"""

from my_warehouse_V4 import my_warehouse


MENU_OPTIONS = [
    "1. List products in stock",
    "2. Add product to stock",
    "3. Remove product",
    "4. UPDATE product",
    "5. ANALYTICS",
    "6. Stock value",
    "7. Export stock to TXT",
    "8. Export data to CSV",
    "9. Export log to .txt",
    "10. Export data to JSON",
    "0. Exit program",
]


def display_menu() -> None:
    print("\nmy.Warehouse v. 4.0")
    print("-" * 10, "MENU", "-" * 10)
    for option in MENU_OPTIONS:
        print(option)
    print()


def user_choice() -> int:
    while True:
        raw = input("Choose one of the options above: ")
        try:
            return int(raw)
        except ValueError:
            print("Enter number.")


def main_menu() -> None:
    while True:
        display_menu()
        choice = user_choice()

        try:
            if choice == 0:
                my_warehouse.exit_program()
            elif choice == 1:
                my_warehouse.print_product_list2()
            elif choice == 2:
                my_warehouse.add_product2()
            elif choice == 3:
                my_warehouse.delete_product2()
            elif choice == 4:
                my_warehouse.update_product()
            elif choice == 5:
                my_warehouse.analytika.my_analytics()
            elif choice == 6:
                my_warehouse.total_price()
            elif choice == 7:
                my_warehouse.export.export_txt()
            elif choice == 8:
                my_warehouse.export.export_to_CSV()
            elif choice == 9:
                my_warehouse.log.export_log_txt()
            elif choice == 10:
                my_warehouse.export.export_to_JSON()
            else:
                print("You have entered a non-existent option...")
        except Exception as exc:
            print(f"Error: {exc}")


if __name__ == "__main__":
    main_menu()
