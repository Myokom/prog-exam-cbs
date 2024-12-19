# Importing the necessary classes and libraries
from helper_functions.classes import User, StudentUser, RegularUser, AdminUser, Inventory, Sandwich, Order, Loyalty
from helper_functions.update_dfs import update_customers_df, update_orders_df
import streamlit as st
from datetime import datetime
import pandas as pd
import plotly.express as px

hide_decoration_bar_style = '''
    <style>
        header {visibility: hidden;}
    </style>
'''
st.markdown(hide_decoration_bar_style, unsafe_allow_html=True) # Hiding the Streamlit header

# Global variables to hold data
customers = {}
orders = []

# Initialize session state for inventory, customers, orders, etc.
if "inventory" not in st.session_state:
    st.session_state.inventory = Inventory()  # Store the inventory
if "customers" not in st.session_state:
    st.session_state.customers = {}  # Store all customers
if "orders" not in st.session_state:
    st.session_state.orders = []  # Store all orders
if "current_order" not in st.session_state:
    st.session_state.current_order = None  # Store the current order being created
if "logged_in_customer" not in st.session_state:
    st.session_state.logged_in_customer = None  # Track the currently logged-in customer

# Load the datasets into session state
if "ingredients_df" not in st.session_state:
    st.session_state.ingredients_df = pd.read_csv("simulated_data/ingredients.csv")

if "customers_df" not in st.session_state:
    st.session_state.customers_df = pd.read_csv("simulated_data/customers.csv")

if "orders_df" not in st.session_state:
    st.session_state.orders_df = pd.read_csv("simulated_data/orders.csv")


# Navigation sidebar for Customer and Admin views
st.sidebar.title("Navigation")
view = st.sidebar.radio("Select a View:", ["Customer View", "Admin View"])

# Customer View
if view == "Customer View":

    # Check if a customer is logged in
    if st.session_state.logged_in_customer is None:
        st.title("Welcome to Hiko Sandwiches! 🥪")
        st.subheader("🔐 Create an Account or Log In")

        # Create an account
        with st.form("Create Account", clear_on_submit=True):
            customer_id = st.text_input("Customer ID")
            name = st.text_input("Name")
            email = st.text_input("Email")
            phone = st.text_input("Phone")
            submitted = st.form_submit_button("Create Account")

            if submitted:
                if not customer_id or not name or not email or not phone:
                    st.error("All fields are required to create an account.") # Error message if any field is empty
                elif customer_id in st.session_state.customers:
                    st.error("Customer ID already exists. Please use a different ID.")
                else:
                    # Check for student email and create the appropriate customer type
                    if email.endswith("@student.cbs.dk"):
                        customer = StudentUser(customer_id, name, email, phone) # Creating a student user
                    else:
                        customer = RegularUser(customer_id, name, email, phone) # Creating a regular user
                    st.session_state.customers[customer_id] = customer # Add the customer to the session state
                    update_customers_df() # Update the customers dataframe
                    st.success("Account created successfully!")

        # Log in
        st.subheader("Log In") 
        with st.form("Log In"):
            login_id = st.text_input("Enter your Customer ID") # Text input for the customer ID
            login_submit = st.form_submit_button("Log In") # Submit button for the form

            if login_submit:
                if login_id in st.session_state.customers:
                    st.session_state.logged_in_customer = st.session_state.customers[login_id] # Log in the customer if ID is found
                    st.success(f"Welcome back, {st.session_state.logged_in_customer.name}!")
                    st.rerun() # Rerun the app to show the logged-in view
                else:
                    st.error("Customer ID not found. Please create an account first.")

    else:
        # Customer is logged in
        customer = st.session_state.logged_in_customer # Reference the logged-in customer
        st.subheader(f"Welcome, {customer.name}! 🥪") 
        st.write("**Your Sandwich, Your Way** – Crafted just for you!")

        # Initialize a new order for the customer if not already started
        if st.session_state.current_order is None: # If no order is in progress
            st.session_state.current_order = Order(
                order_id=len(st.session_state.orders) + 1,
                customer=customer,
                inventory=st.session_state.inventory
            )

        # Reference the current order from session state
        order = st.session_state.current_order
        inventory = st.session_state.inventory
        
        # Place an order
        st.subheader("Place an Order")
        # Info Box for User Guidance
        st.info(
                "Here’s how it works:\n"
                "1. **Make a Sandwich** – Choose your favorite ingredients.\n"
                "2. **Add the Sandwich** – Add it to your order list.\n"
                "3. **Place Your Order** – Submit your order when ready or add more sandwiches."
            )
        # Two columns layout
        col8, col9 = st.columns([7, 3])

        with col8:
            with st.form("Create Order", clear_on_submit=True):
                # Single selections using st.pills
                bread = st.pills("Choose Bread", list(inventory.available_breads.keys()), selection_mode="single", default="White")
                spread = st.pills("Choose Spread", list(inventory.available_spreads.keys()), selection_mode="single", default="No spread")
                protein = st.pills("Choose Protein", list(inventory.available_proteins.keys()), selection_mode="single", default="No protein")
                dressing = st.pills("Choose Dressing", list(inventory.available_dressings.keys()), selection_mode="single", default="No Dressing")
                
                # Multi selections using st.pills
                vegetables = st.pills("Choose Vegetables", list(inventory.available_vegetables.keys()), selection_mode="multi", default=["No vegetables"])
                extras = st.pills("Choose Extras", list(inventory.available_extras.keys()), selection_mode="multi", default=["No extras"])

                # Add a sandwich to the order
                add_sandwich = st.form_submit_button("Add Sandwich")
                if add_sandwich:
                    sandwich = Sandwich(inventory=inventory) # Create a new sandwich object
                    try:
                        sandwich.select_bread(bread)
                        sandwich.select_spread(spread)
                        sandwich.select_protein(protein)
                        sandwich.add_vegetables(vegetables)
                        sandwich.select_dressing(dressing)
                        sandwich.add_extras(extras)
                        order.add_sandwich(sandwich)
                        st.success("Sandwich added to order!")
                    except ValueError as e:
                        st.error(str(e)) # Display error message if ingredient is not available

        with col9:
            # Button to place the order
            st.subheader("Submit Your Order")
            if st.button("Place Order"):
                if not order.sandwiches:
                    st.error("No sandwiches in the order! Add at least one sandwich before placing the order.")
                else:
                    total, discount_message = order.calculate_total() # Calculate the total cost of the order
                    customer.add_order(order) # Add the order to the customer's order history
                    st.session_state.orders.append(order) # Add the order to the global orders list
                    update_customers_df() # Update the customers dataframe
                    update_orders_df() # Update the orders dataframe
                    st.session_state.current_order = None # Reset the current order
                    st.success(f"Order placed successfully! Total cost: {total:.2f} DKK") 
                    if discount_message:
                        st.info(discount_message) # Display discount message if applicable
                    st.write("Order details:")
                    st.write(str(order))

            # View order history
            st.subheader("Order History")
            if customer.order_history:
                for idx, past_order in enumerate(customer.order_history, start=1):
                    with st.expander(f"Order {idx}"):
                        st.text(str(past_order))

            # Log out
            if st.button("Log Out"):
                st.session_state.logged_in_customer = None
                st.success("Logged out successfully!")
                st.rerun()


# Admin View
if view == "Admin View":
    # Ensure admin_logged_in is in session state
    if "admin_logged_in" not in st.session_state:
        st.session_state.admin_logged_in = False # Track if admin is logged in

    # If admin is not logged in, show login form
    if not st.session_state.admin_logged_in: # If admin is not logged in
        st.title("🔒 Admin Login")
        st.info("**For testing:**\n\n- **Username**: `admin`\n- **Password**: `admin123`")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if username == "admin" and password == "admin123":
                st.session_state.admin_logged_in = True # Log in the admin
                st.success("Login successful! Redirecting to Admin Dashboard...")
                st.rerun() # Rerun the app to show the admin dashboard
            else:
                st.error("Invalid username or password. Please try again.")
    else:
        st.title("📊 Admin Dashboard")
        st.info(
            """
        **Admin Dashboard Overview:**
        Use the tabs below to access key functionalities:

        - **Manage Orders**: Track and update the status of orders.
        - **Analytics**: View sales, top customers, ingredient trends, and order volume.
        - **Manage Inventory**: Add, update, or remove ingredients to keep stock optimized.
            """
        )

        # Create tabs, including the new "Manage Orders" tab
        tab1, tab2, tab3 = st.tabs(["Manage Orders", "Analytics", "Manage Inventory"])

        # Tab 1: Manage Orders
        with tab1:
            st.header("Manage Orders")

            # Define the statuses and how they flow
            status_flow = {
                "Pending": "In Progress",
                "In Progress": "Ready for Pickup",
                "Ready for Pickup": "Done",
                "Done": None
            }
            

            # Fetch all orders from session state
            all_orders = st.session_state.orders

            # Separate orders by status
            pending_orders = [o for o in all_orders if o.status == "Pending"] # Orders with status "Pending"
            in_progress_orders = [o for o in all_orders if o.status == "In Progress"] # Orders with status "In Progress"
            ready_orders = [o for o in all_orders if o.status == "Ready for Pickup"] # Orders with status "Ready for Pickup"
            done_orders = [o for o in all_orders if o.status == "Done"] # Orders with status "Done"

            col_pending, col_in_progress, col_ready, col_done = st.columns(4) # Create 4 columns layout
            with col_pending:
                st.markdown("**Pending**")
                st.markdown("---")
                for order in pending_orders:
                    with st.expander(f"Order {order.order_id}"): # Expander to show order details
                        st.write(str(order))
                        next_status = status_flow[order.status] # Get the next status for the order
                        if next_status and st.button(f"Move to '{next_status}'", key=f"pending_{order.order_id}"):
                            order.update_status(next_status) # Update the status of the order
                            update_orders_df() # Update the orders dataframe
                            st.rerun() # Rerun the app to show the updated order status

            with col_in_progress:
                st.markdown("**In Progress**")
                st.markdown("---")
                for order in in_progress_orders:
                    with st.expander(f"Order {order.order_id}"):
                        st.write(str(order))
                        next_status = status_flow[order.status] # Get the next status for the order
                        if next_status and st.button(f"Move to '{next_status}'", key=f"inprogress_{order.order_id}"):
                            order.update_status(next_status) # Update the status of the order
                            update_orders_df() # Update the orders dataframe
                            st.rerun() # Rerun the app to show the updated order status

            with col_ready:
                st.markdown("**Ready for Pickup**")
                st.markdown("---")
                for order in ready_orders:
                    with st.expander(f"Order {order.order_id}"):
                        st.write(str(order))
                        next_status = status_flow[order.status] # Get the next status for the order
                        if next_status and st.button(f"Move to '{next_status}'", key=f"ready_{order.order_id}"):
                            order.update_status(next_status) # Update the status of the order
                            update_orders_df() # Update the orders dataframe
                            st.rerun() # Rerun the app to show the updated order status

            with col_done:
                st.markdown("**Done**")
                st.markdown("---")
                for order in done_orders:
                    with st.expander(f"Order {order.order_id}"):
                        st.write(str(order))
                        # No next status for done orders

        # Tab 2: Analytics
        with tab2:
            st.header("Analytics")

            # Access the updated dataframes from session state
            customers_df = st.session_state.customers_df 
            orders_df = st.session_state.orders_df
            ingredients_df = st.session_state.get("ingredients_df", pd.DataFrame())

            # Metrics
            total_revenue = orders_df["Total Cost (DKK)"].sum() if not orders_df.empty else 0 # Total revenue
            total_customers = customers_df["Customer ID"].nunique() if not customers_df.empty else 0 # Total customers
            total_orders = orders_df["Order ID"].nunique() if not orders_df.empty else 0 # Total orders

            col1, col2, col3 = st.columns(3) # Create 3 columns layout
            with col1:
                st.metric("Total Revenue (DKK)", f"{total_revenue:,.2f}") # Display total revenue
            with col2:
                st.metric("Total Customers", total_customers) # Display total customers
            with col3:
                st.metric("Total Orders", total_orders) # Display total orders

            # Revenue over time
            st.subheader("Revenue Over Time")
            if not orders_df.empty:
                revenue_by_date = (
                    orders_df.groupby(orders_df["Order Time"].str[:10])["Total Cost (DKK)"] # Group by date
                    .sum() # Sum the total cost
                    .reset_index() # Reset the index
                ) # Calculate the revenue by date
                revenue_by_date.columns = ["Date", "Revenue"] # Rename the columns
                revenue_by_date["Date"] = pd.to_datetime(revenue_by_date["Date"]) # Convert the date to datetime

                fig_revenue = px.line(revenue_by_date, x="Date", y="Revenue", title="Revenue Over Time") # Create a line plot for revenue over time 
                st.plotly_chart(fig_revenue, use_container_width=True) # Display the line plot
            else:
                st.info("No revenue data available.")

            # Row for "Top Customers" and "Ingredient Popularity"
            st.markdown("---")
            st.subheader("Top Insights")
            col4, col5 = st.columns(2) # Create 2 columns layout

            with col4:
                st.subheader("Top Customers")
                if not customers_df.empty:
                    top_customers = (
                        customers_df[["Name", "Total Sandwiches Purchased"]] # Select columns
                        .sort_values(by="Total Sandwiches Purchased", ascending=False) # Sort by total sandwiches purchased
                        .head(10) # Select top 10 customers
                    )
                    st.table(top_customers) # Display the top customers
                else:
                    st.info("No customer data available.")

            with col5:
                st.subheader("Ingredient Popularity")
                if not ingredients_df.empty and "Usage" in ingredients_df.columns:
                    top_ingredients = ingredients_df.sort_values(by="Usage", ascending=False).head(10) # Select top 10 ingredients
                    st.table(top_ingredients)
                else:
                    st.info("No ingredient usage data available.")

            # Row for "Order Volume by Date" and "Customers by Total Orders"
            st.markdown("---")
            col6, col7 = st.columns(2) # Create 2 columns layout

            with col6:
                st.subheader("Order Volume by Date")
                if not orders_df.empty:
                    orders_by_date = (
                        orders_df.groupby(orders_df["Order Time"].str[:10])["Order ID"] # Group by date
                        .count() # Count the number of orders
                        .reset_index() # Reset the index
                    )
                    orders_by_date.columns = ["Date", "Order Count"] # Rename the columns
                    orders_by_date["Date"] = pd.to_datetime(orders_by_date["Date"]) # Convert the date to datetime

                    fig_orders = px.bar(orders_by_date, x="Date", y="Order Count", title="Order Volume by Date") # Create a bar plot for order volume by date
                    st.plotly_chart(fig_orders, use_container_width=True) # Display the bar plot
                else: 
                    st.info("No order data available.")

            with col7:
                st.subheader("Customers by Total Orders")
                if not customers_df.empty:
                    customer_orders = customers_df[["Name", "Number of Orders"]].sort_values(
                        by="Number of Orders", ascending=False
                    ).head(10) # Select top 10 customers by total orders

                    fig_customers = px.bar(customer_orders, x="Name", y="Number of Orders", title="Top Customers by Total Orders") # Create a bar plot for top customers by total orders
                    st.plotly_chart(fig_customers, use_container_width=True) # Display the bar plot
                else:
                    st.info("No customer data available.")

        # Tab 3: Manage Inventory
        with tab3:
            st.header("Manage Inventory")

            categories = ["Bread", "Spread", "Protein", "Vegetable", "Extra", "Dressing"] # List of categories
            selected_category = st.selectbox("Choose Category", categories) # Selectbox to choose a category

            if selected_category:
                category_key = selected_category.lower() # Convert the category to lowercase
                inventory = st.session_state.inventory # Reference the inventory
                category_dict = inventory._get_category_dict(category_key) # Get the category dictionary

                if category_dict:
                    st.write(f"### Current Ingredients in {selected_category}:") # Display the current ingredients in the selected category
                    for ingredient, price in category_dict.items():
                        st.write(f"- **{ingredient}:** {price:.2f} DKK") # Display the ingredient and its price
                else:
                    st.error(f"Invalid category '{selected_category}'.")

                # Add New Ingredient
                st.markdown("### Add New Ingredient")
                with st.form("Add Ingredient", clear_on_submit=True): 
                    add_category = st.selectbox("Category for New Ingredient", [c for c in categories]) # Selectbox to choose a category
                    new_ingredient = st.text_input("Ingredient Name") # Text input for the ingredient name
                    new_price = st.number_input("Ingredient Price (DKK)", min_value=0.0, value=0.0, step=0.1) # Number input for the ingredient price 
                    add_ingredient_btn = st.form_submit_button("Add Ingredient") # Submit button to add the ingredient

                    if add_ingredient_btn:
                        try:
                            inventory.add_ingredient(add_category, new_ingredient, new_price) # Add the new ingredient
                            st.success(f"Added **{new_ingredient}** to **{add_category.capitalize()}** category.")
                            st.rerun() # Rerun the app to show the updated inventory
                        except ValueError as e:
                            st.error(str(e)) # Display error message if ingredient already exists

                # Remove Ingredient
                st.markdown("### Remove Ingredient")
                if category_dict:
                    ingredient_to_remove = st.selectbox("Choose Ingredient to Remove", list(category_dict.keys())) # Selectbox to choose an ingredient to remove
                    if st.button("Remove Ingredient"):
                        try:
                            inventory.remove_ingredient(category_key, ingredient_to_remove) # Remove the ingredient
                            st.success(f"Removed **{ingredient_to_remove}** from **{selected_category.capitalize()}**.") 
                            st.rerun() # Rerun the app to show the updated inventory
                        except ValueError as e:
                            st.error(str(e)) # Display error message if ingredient does not exist