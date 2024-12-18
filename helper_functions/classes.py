# Classes
## Users
### Base Class

class User:
    def __init__(self, user_id, name, email, phone):
        """
        Initialize a new User object with the parameters: user_id, name, email, and phone.
        """
        self.user_id = user_id
        self.name = name
        self.email = email
        self.phone = phone

    def update_contact_info(self, email=None, phone=None):
        """
        Update the user's contact information with a new email and/or phone number (both are optional).
        """
        if email:
            self.email = email
        if phone:
            self.phone = phone

    def apply_discount(self, total_cost):
        """
        Default: no discount for a regular user.
        Override in subclasses for specific discount logic.
        """
        return total_cost  # Default: no discount

    def __str__(self):
        """
        Formatted string representation of the user.
        """
        return f"User ID: {self.user_id}\nName: {self.name}\nEmail: {self.email}\nPhone: {self.phone}"
#### Subclass: Regular User
class RegularUser(User):
    def __init__(self, user_id, name, email, phone):
        super().__init__(user_id, name, email, phone)
        self.order_history = []
        self.sandwich_count = 0

    def add_order(self, order):
        """
        Add an order to the user's order history and update sandwich count.
        """
        self.order_history.append(order)
        self.sandwich_count += len(order.sandwiches)

    def get_order_history(self):
        """
        Retrieve and return the user's order history.
        """
        return self.order_history

    def __str__(self):
        return super().__str__() + f"\nTotal Sandwiches Purchased: {self.sandwich_count}"
#### Subclass: Student User

class StudentUser(RegularUser):
    def __init__(self, user_id, name, email, phone, domain="@student.cbs.dk", discount_rate=0.05):
        super().__init__(user_id, name, email, phone)
        self.student_domain = domain
        self.student_discount_rate = discount_rate

    def apply_discount(self, total_cost):
        """
        Apply a 5% discount if the user's email ends with the student domain.
        """
        if self.email.lower().endswith(self.student_domain):
            return total_cost * (1 - self.student_discount_rate)
        return total_cost

    def __str__(self):
        return super().__str__() + "\nStatus: Student"
#### Subclass: Admin User

class AdminUser(User):
    def __init__(self, user_id, name, email, phone):
        super().__init__(user_id, name, email, phone)

    def view_all_orders(self, orders):
        """
        View all orders in the system (admin-only feature).
        """
        if not orders:
            return "No orders available."
        return orders
    
    def view_all_customers(self, customers):
        """
        View all customers in the system. If no customers exist, return an empty list.
        """
        return customers or []

    def manage_inventory(self, inventory, action, category, item_name, price=None):
        """
        Manage the inventory by adding or removing items (admin-only feature).
        """
        if action == "add":
            inventory.add_ingredient(category, item_name, price)
        elif action == "remove":
            inventory.remove_ingredient(category, item_name)
        else:
            raise ValueError("Invalid action. Use 'add' or 'remove'.")

    def __str__(self):
        return super().__str__() + "\nRole: Admin"
## Inventory
class Inventory:
    """
    Manages available ingredients and their corresponding prices.
    Allows adding and removing ingredients.
    """
    def __init__(self):
        # Initialize with some default values
        self.available_breads = {
            "White": 0,
            "Whole Wheat": 0
        }
        self.available_spreads = {
            "No spread": 0,
            "Chilimayo": 0,
            "Plain cream cheese": 0,
            "Hummus": 0
        }
        self.available_proteins = {
            "No protein": 0,
            "Chorizo": 0,
            "Chicken": 0,
            "Tandoori chicken": 0,
            "Tuna": 0,
            "Turkey": 0
        }
        self.available_vegetables = {
            "No vegetables": 0,
            "Iceberg": 0,
            "Mixed salad": 0,
            "Corn": 0,
            "Red onion": 0,
            "Feta": 0,
            "Jalapeños": 0,
            "Sundried tomatoes": 0,
            "Bell pepper": 0,
            "Carrot": 0,
            "Pickles": 0,
            "Tomato": 0,
            "Cucumber": 0,
            "Olive": 0
        }
        self.available_extras = {
            "No extras": 0,
            "Avocado": 6,
            "Cheddar cheese": 6,
            "Turkey bacon": 6
        }
        self.available_dressings = {
            "No Dressing": 0,
            "Sour cream dressing": 0,
            "Curry dressing": 0,
            "Pesto": 0,
            "Sweet chili dressing": 0,
            "Strong chili dressing": 0
        }

    def add_ingredient(self, category, name, price=0):
        """
        Add a new ingredient to a given category with a specified price.
        category: str, one of ["bread", "spread", "protein", "vegetable", "extra", "dressing"]
        name: str, name of the ingredient
        price: int or float, optional price of the ingredient (for extras or special breads)
        """
        category_dict = self._get_category_dict(category)
        if name in category_dict:
            raise ValueError(f"Ingredient '{name}' already exists.")
        category_dict[name] = price

    def remove_ingredient(self, category, name):
        """
        Remove an ingredient from a given category.
        """
        category_dict = self._get_category_dict(category)
        if name not in category_dict:
            raise ValueError(f"Ingredient '{name}' does not exist in {category} category.")
        if name.startswith("No "):      # Prevent removal of "No ..." options if you consider them mandatory placeholders
            raise ValueError(f"Cannot remove mandatory ingredient '{name}'.")
        del category_dict[name]

    def _get_category_dict(self, category):
        category_mapping = {
            "bread": self.available_breads,
            "spread": self.available_spreads,
            "protein": self.available_proteins,
            "vegetable": self.available_vegetables,
            "extra": self.available_extras,
            "dressing": self.available_dressings,
        }
        return category_mapping.get(category.lower())

    def is_valid_bread(self, bread):
        return bread in self.available_breads

    def is_valid_spread(self, spread):
        return spread in self.available_spreads

    def is_valid_protein(self, protein):
        return protein in self.available_proteins

    def is_valid_vegetables(self, vegetables):
        return all(veg in self.available_vegetables for veg in vegetables)

    def is_valid_dressing(self, dressing):
        return dressing in self.available_dressings

    def is_valid_extras(self, extras):
        return all(extra in self.available_extras for extra in extras)

    def get_extra_cost(self, extras):
        return sum(self.available_extras.get(e, 0) for e in extras if e != "No extras")
## Sandwich
class Sandwich:
    def __init__(self, inventory=None):
        """
        Initialize a new Sandwich object.
        Parameters:
        - inventory: An Inventory object to validate ingredient selections. Defaults to a new Inventory instance.
        """
        self.inventory = inventory if inventory else Inventory()
        self.bread = None
        self.spread = None
        self.protein = None
        self.vegetables = []
        self.dressing = None
        self.extras = []

    def get_price(self, base_price):
        """
        Calculates the price of the sandwich based on:
        - Base price
        - Cost of extra ingredients
        """
        valid_extras = [extra for extra in self.extras if extra != "No extras"]
        extra_cost = self.inventory.get_extra_cost(valid_extras)
        return base_price + extra_cost

    def select_bread(self, bread):
        if self.inventory.is_valid_bread(bread):
            self.bread = bread
        else:
            raise ValueError("Invalid bread choice.")

    def select_spread(self, spread):
        if self.inventory.is_valid_spread(spread):
            self.spread = spread
        else:
            raise ValueError("Invalid spread choice.")

    def select_protein(self, protein):
        if self.inventory.is_valid_protein(protein):
            self.protein = protein
        else:
            raise ValueError("Invalid protein choice.")

    def add_vegetables(self, vegetables):
        if self.inventory.is_valid_vegetables(vegetables):
            self.vegetables = vegetables
        else:
            raise ValueError("One or more invalid vegetable choices.")

    def select_dressing(self, dressing):
        if self.inventory.is_valid_dressing(dressing):
            self.dressing = dressing
        else:
            raise ValueError("Invalid dressing choice.")

    def add_extras(self, extras):
        if self.inventory.is_valid_extras(extras):
            self.extras = extras
        else:
            raise ValueError("One or more invalid extras.")

    def __str__(self):
        return (
            f"Bread: {self.bread}\n"
            f"Spread: {self.spread}\n"
            f"Protein: {self.protein}\n"
            f"Vegetables: {', '.join(self.vegetables)}\n"
            f"Dressing: {self.dressing}\n"
            f"Extras: {', '.join(self.extras)}"
        )
## Loyalty Program
class Loyalty:
    """
    Encapsulates the logic for loyalty benefits:
    - Every nth sandwich (based on threshold) is free.
    """
    def __init__(self, threshold=10):
        self.threshold = threshold  # e.g. every 10th sandwich is free

    def free_sandwiches_earned(self, previous_sandwich_count, current_sandwich_count):
        """
        Given the customer's previous sandwich count and the new cumulative count (after current order),
        determine how many free sandwiches should be awarded in the current order.
        """
        total_free_sandwiches_after = current_sandwich_count // self.threshold
        total_free_sandwiches_before = previous_sandwich_count // self.threshold

        # Difference is how many free sandwiches to apply to this order
        return total_free_sandwiches_after - total_free_sandwiches_before
## Order
from datetime import datetime

class Order:
    def __init__(self, order_id, customer, order_time=None, inventory=None, loyalty_program=None):
        """
        Initializes an Order instance with order details and dependencies.
        """
        self.order_id = order_id
        self.customer = customer
        self.sandwiches = []
        self.status = "Pending"
        self.order_time = order_time if order_time else datetime.now()
        self.inventory = inventory if inventory else Inventory()
        self.loyalty_program = loyalty_program if loyalty_program else Loyalty(10)

    def add_sandwich(self, sandwich):
        """
        Adds a sandwich to the order.
        """
        if isinstance(sandwich, Sandwich):
            self.sandwiches.append(sandwich)
        else:
            raise ValueError("Only Sandwich objects can be added.")

    def calculate_total(self):
        base_price = self.get_time_based_price()
        sandwich_costs = [s.get_price(base_price) for s in self.sandwiches]

        free_sandwich_count = self.loyalty_program.free_sandwiches_earned(
            self.customer.sandwich_count, self.customer.sandwich_count + len(self.sandwiches)
        )

        # Apply loyalty discount
        sandwich_costs.sort()
        for _ in range(free_sandwich_count):
            if sandwich_costs:
                sandwich_costs.pop(0)

        total = sum(sandwich_costs)
        total_with_discount = self.customer.apply_discount(total)

        st_discount = f"\nLoyalty Program: {free_sandwich_count} Sandwich(es) Free" if free_sandwich_count else ""
        return total_with_discount, st_discount

    def get_time_based_price(self):
        """
        Returns the base price of a sandwich based on the time of the order.
        Price is 77 DKK during 8:00 - 14:00 and 80 DKK at other times.
        """
        hour = self.order_time.hour
        return 77 if 8 <= hour < 14 else 80

    def update_status(self, new_status):
        """
        Updates the status of the order.
        """
        self.status = new_status

    def __str__(self):
        if not self.sandwiches:
            return "No sandwiches in this order."

        sandwiches_str = "\n\n".join(
            [f"Sandwich {i+1}:\n{str(s)}" for i, s in enumerate(self.sandwiches)]
        )
        total, st_discount = self.calculate_total()

        return (f"Order ID: {self.order_id}\n"
                f"Customer: {self.customer.name} (ID: {self.customer.user_id})\n"
                f"Sandwiches:\n{sandwiches_str}\n"
                f"Status: {self.status}\n"
                f"Total Cost: {total:.2f} DKK{st_discount}")
