# Classes
## Users
### Base Class

class User:
    def __init__(self, user_id, name, email, phone): 
        """
        Initialize a new User object with the parameters: user_id, name, email, and phone.
        """
        self.user_id = user_id # Unique user ID
        self.name = name # User's full name
        self.email = email # User's email address
        self.phone = phone # User's phone number

    def update_contact_info(self, email=None, phone=None):
        """
        Update the user's contact information with a new email and/or phone number (both are optional).
        """
        if email:
            self.email = email # Update email if provided
        if phone:
            self.phone = phone # Update phone number if provided

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
        return f"User ID: {self.user_id}\nName: {self.name}\nEmail: {self.email}\nPhone: {self.phone}" #
#### Subclass: Regular User
class RegularUser(User):
    def __init__(self, user_id, name, email, phone):
        super().__init__(user_id, name, email, phone) # Call the parent class constructor
        self.order_history = [] # List to store the user's order history
        self.sandwich_count = 0 # Total number of sandwiches purchased

    def add_order(self, order):
        """
        Add an order to the user's order history and update sandwich count.
        """
        self.order_history.append(order) # Add the order to the history
        self.sandwich_count += len(order.sandwiches) # Update the total sandwich count

    def get_order_history(self):
        """
        Retrieve and return the user's order history.
        """
        return self.order_history

    def __str__(self):
        return super().__str__() + f"\nTotal Sandwiches Purchased: {self.sandwich_count}" # Include sandwich count in the string representation

#### Subclass: Student User
class StudentUser(RegularUser):
    def __init__(self, user_id, name, email, phone, domain="@student.cbs.dk", discount_rate=0.05): # Default domain and discount rate for CBS/Student users
        super().__init__(user_id, name, email, phone)  # Call the parent class constructor
        self.student_domain = domain # Domain for student emails
        self.student_discount_rate = discount_rate # Discount rate for student users

    def apply_discount(self, total_cost):
        """
        Apply a 5% discount if the user's email ends with the student domain.
        """
        if self.email.lower().endswith(self.student_domain): # Check if the email ends with the student domain
            return total_cost * (1 - self.student_discount_rate) # Apply the discount
        return total_cost # No discount if the email does not match the student domain

    def __str__(self):
        return super().__str__() + "\nStatus: Student" # Include student status in the string representation

#### Subclass: Admin User
class AdminUser(User):
    def __init__(self, user_id, name, email, phone):
        super().__init__(user_id, name, email, phone) # Call the parent class constructor

    def view_all_orders(self, orders):
        """
        View all orders in the system (admin-only feature).
        """
        if not orders:
            return "No orders available." # Return a message if no orders exist
        return orders # Return the list of orders
    
    def view_all_customers(self, customers):
        """
        View all customers in the system. If no customers exist, return an empty list.
        """
        return customers or [] # Return the list of customers or an empty list if no customers exist

    def manage_inventory(self, inventory, action, category, item_name, price=None):
        """
        Manage the inventory by adding or removing items (admin-only feature).
        """
        if action == "add":
            inventory.add_ingredient(category, item_name, price) # Add a new ingredient
        elif action == "remove":
            inventory.remove_ingredient(category, item_name) # Remove an existing ingredient
        else:
            raise ValueError("Invalid action. Use 'add' or 'remove'.") # Raise an error for invalid actions

    def __str__(self):
        return super().__str__() + "\nRole: Admin" # Include role in the string representation

## Inventory
class Inventory:
    """
    Manages available ingredients and their corresponding prices.
    Allows adding and removing ingredients.
    """
    def __init__(self):
        # Initialize with some default values for each category of ingredients 
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
        category_dict = self._get_category_dict(category) # Get the corresponding category dictionary
        if name in category_dict: # Check if the ingredient already exists
            raise ValueError(f"Ingredient '{name}' already exists.")
        category_dict[name] = price # Add the new ingredient with the specified price

    def remove_ingredient(self, category, name):
        """
        Remove an ingredient from a given category.
        """
        category_dict = self._get_category_dict(category) # Get the corresponding category dictionary
        if name not in category_dict: # Check if the ingredient exists
            raise ValueError(f"Ingredient '{name}' does not exist in {category} category.")
        if name.startswith("No "): # Prevent removal of "No ..." options if you consider them mandatory placeholders
            raise ValueError(f"Cannot remove mandatory ingredient '{name}'.")
        del category_dict[name] # Remove the ingredient from the dictionary

    def _get_category_dict(self, category):
        category_mapping = {
            "bread": self.available_breads,
            "spread": self.available_spreads,
            "protein": self.available_proteins,
            "vegetable": self.available_vegetables,
            "extra": self.available_extras,
            "dressing": self.available_dressings,
        } # Mapping of category names to corresponding dictionaries
        return category_mapping.get(category.lower()) # Return the dictionary for the specified category

    def is_valid_bread(self, bread):
        return bread in self.available_breads # Check if the bread is in the available breads

    def is_valid_spread(self, spread):
        return spread in self.available_spreads # Check if the spread is in the available spreads

    def is_valid_protein(self, protein):
        return protein in self.available_proteins # Check if the protein is in the available proteins

    def is_valid_vegetables(self, vegetables):
        return all(veg in self.available_vegetables for veg in vegetables) # Check if all vegetables are valid

    def is_valid_dressing(self, dressing):
        return dressing in self.available_dressings # Check if the dressing is in the available dressings

    def is_valid_extras(self, extras):
        return all(extra in self.available_extras for extra in extras) # Check if all extras are valid

    def get_extra_cost(self, extras):
        return sum(self.available_extras.get(e, 0) for e in extras if e != "No extras") # Calculate the total cost of extras

## Sandwich
class Sandwich:
    def __init__(self, inventory=None):
        """
        Initialize a new Sandwich object.
        """
        self.inventory = inventory if inventory else Inventory() # Inventory object to validate ingredients
        self.bread = None # Bread type (e.g., White, Whole Wheat)
        self.spread = None # Spread type (e.g., Chilimayo, Hummus)
        self.protein = None # Protein type (e.g., Chicken, Tuna)
        self.vegetables = [] # List of vegetable types (e.g., Iceberg, Tomato)
        self.dressing = None # Dressing type (e.g., Pesto, Curry dressing)
        self.extras = [] # List of extra ingredients (e.g., Avocado, Cheddar cheese)

    def get_price(self, base_price):
        """
        Calculates the price of the sandwich based on:
        - Base price
        - Cost of extra ingredients
        """
        valid_extras = [extra for extra in self.extras if extra != "No extras"] # Exclude "No extras" from the calculation
        extra_cost = self.inventory.get_extra_cost(valid_extras) # Calculate the total cost of extras
        return base_price + extra_cost # Total price is the sum of the base price and extra cost

    def select_bread(self, bread):
        if self.inventory.is_valid_bread(bread): # Check if the bread is valid
            self.bread = bread # Set the bread type
        else:
            raise ValueError("Invalid bread choice.") # Raise an error for invalid bread choice

    def select_spread(self, spread):
        if self.inventory.is_valid_spread(spread): # Check if the spread is valid
            self.spread = spread # Set the spread type
        else:
            raise ValueError("Invalid spread choice.") # Raise an error for invalid spread choice

    def select_protein(self, protein):
        if self.inventory.is_valid_protein(protein): # Check if the protein is valid
            self.protein = protein # Set the protein type
        else:
            raise ValueError("Invalid protein choice.") # Raise an error for invalid protein choice

    def add_vegetables(self, vegetables):
        if self.inventory.is_valid_vegetables(vegetables): # Check if all vegetables are valid
            self.vegetables = vegetables # Set the list of vegetables
        else:
            raise ValueError("One or more invalid vegetable choices.") # Raise an error for invalid vegetable choices

    def select_dressing(self, dressing):
        if self.inventory.is_valid_dressing(dressing): # Check if the dressing is valid
            self.dressing = dressing # Set the dressing type
        else:
            raise ValueError("Invalid dressing choice.") # Raise an error for invalid dressing choice

    def add_extras(self, extras):
        if self.inventory.is_valid_extras(extras): # Check if all extras are valid
            self.extras = extras # Set the list of extras
        else:
            raise ValueError("One or more invalid extras.") # Raise an error for invalid extras

    def __str__(self): # String representation of the sandwich object
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
        total_free_sandwiches_after = current_sandwich_count // self.threshold # Total free sandwiches after this order
        total_free_sandwiches_before = previous_sandwich_count // self.threshold # Total free sandwiches before this order

        # Difference is how many free sandwiches to apply to this order
        return total_free_sandwiches_after - total_free_sandwiches_before
    
## Order
from datetime import datetime

class Order:
    def __init__(self, order_id, customer, order_time=None, inventory=None, loyalty_program=None):
        """
        Initializes an Order instance with order details and dependencies.
        """
        self.order_id = order_id # Unique order ID
        self.customer = customer # Customer object
        self.sandwiches = [] # List of Sandwich objects
        self.status = "Pending" # Order status
        self.order_time = order_time if order_time else datetime.now() # Order time (default: current time)
        self.inventory = inventory if inventory else Inventory() # Inventory object
        self.loyalty_program = loyalty_program if loyalty_program else Loyalty(10) # Loyalty program object

    def add_sandwich(self, sandwich):
        """
        Adds a sandwich to the order.
        """
        if isinstance(sandwich, Sandwich): # Check if the input is a Sandwich object
            self.sandwiches.append(sandwich) # Add the sandwich to the order
        else:
            raise ValueError("Only Sandwich objects can be added.") # Raise an error for invalid sandwich input

    def calculate_total(self):
        base_price = self.get_time_based_price() # Get the base price based on the order
        sandwich_costs = [s.get_price(base_price) for s in self.sandwiches] # Calculate the cost of each sandwich

        free_sandwich_count = self.loyalty_program.free_sandwiches_earned( 
            self.customer.sandwich_count, self.customer.sandwich_count + len(self.sandwiches)
        ) # Calculate the number of free sandwiches earned

        # Apply loyalty discount
        sandwich_costs.sort() # Sort the sandwich costs in ascending order
        for _ in range(free_sandwich_count): # Deduct the cost of free sandwiches
            if sandwich_costs:
                sandwich_costs.pop(0) # Remove the lowest cost sandwich

        total = sum(sandwich_costs) # Calculate the total cost
        total_with_discount = self.customer.apply_discount(total) # Apply customer-specific discount

        st_discount = f"\nLoyalty Program: {free_sandwich_count} Sandwich(es) Free" if free_sandwich_count else "" # Loyalty discount message
        return total_with_discount, st_discount

    def get_time_based_price(self):
        """
        Returns the base price of a sandwich based on the time of the order.
        Price is 77 DKK during 8:00 - 14:00 and 80 DKK at other times.
        """
        hour = self.order_time.hour # Get the hour of the order time
        return 77 if 8 <= hour < 14 else 80 # Return the base price based on the time

    def update_status(self, new_status):
        """
        Updates the status of the order.
        """
        self.status = new_status 

    def __str__(self):
        if not self.sandwiches: # Check if there are no sandwiches in the order
            return "No sandwiches in this order." 

        sandwiches_str = "\n\n".join(
            [f"Sandwich {i+1}:\n{str(s)}" for i, s in enumerate(self.sandwiches)]
        ) # Format each sandwich in the order
        total, st_discount = self.calculate_total() # Calculate the total cost and discount message

        return (f"Order ID: {self.order_id}\n"
                f"Customer: {self.customer.name} (ID: {self.customer.user_id})\n"
                f"Sandwiches:\n{sandwiches_str}\n"
                f"Status: {self.status}\n"
                f"Total Cost: {total:.2f} DKK{st_discount}") # Return the order details
