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
# st.markdown(hide_decoration_bar_style, unsafe_allow_html=True) # Hiding the Streamlit header

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


# Navigation
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
                    st.error("All fields are required to create an account.")
                elif customer_id in st.session_state.customers:
                    st.error("Customer ID already exists. Please use a different ID.")
                else:
                    # Check for student email and create the appropriate customer type
                    if email.endswith("@student.cbs.dk"):
                        customer = StudentUser(customer_id, name, email, phone)
                    else:
                        customer = RegularUser(customer_id, name, email, phone)
                    st.session_state.customers[customer_id] = customer
                    update_customers_df()
                    st.success("Account created successfully!")

        # Log in
        st.subheader("Log In")
        with st.form("Log In"):
            login_id = st.text_input("Enter your Customer ID")
            login_submit = st.form_submit_button("Log In")

            if login_submit:
                if login_id in st.session_state.customers:
                    st.session_state.logged_in_customer = st.session_state.customers[login_id]
                    st.success(f"Welcome back, {st.session_state.logged_in_customer.name}!")
                    st.rerun()
                else:
                    st.error("Customer ID not found. Please create an account first.")

    else:
        # Customer is logged in
        customer = st.session_state.logged_in_customer
        st.subheader(f"Welcome, {customer.name}! 🥪")
        st.write("**Your Sandwich, Your Way** – Crafted just for you!")

        # Initialize a new order for the customer if not already started
        if st.session_state.current_order is None:
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
                    sandwich = Sandwich(inventory=inventory)
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
                        st.error(str(e))

        with col9:
            # Button to place the order
            st.subheader("Submit Your Order")
            if st.button("Place Order"):
                if not order.sandwiches:
                    st.error("No sandwiches in the order! Add at least one sandwich before placing the order.")
                else:
                    total, discount_message = order.calculate_total()
                    customer.add_order(order)
                    st.session_state.orders.append(order)
                    update_customers_df()
                    update_orders_df()
                    st.session_state.current_order = None
                    st.success(f"Order placed successfully! Total cost: {total:.2f} DKK")
                    if discount_message:
                        st.info(discount_message)
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
        st.session_state.admin_logged_in = False

    # If admin is not logged in, show login form
    if not st.session_state.admin_logged_in:
        st.title("🔒 Admin Login")
        st.info("**For testing:**\n\n- **Username**: `admin`\n- **Password**: `admin123`")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if username == "admin" and password == "admin123":
                st.session_state.admin_logged_in = True
                st.success("Login successful! Redirecting to Admin Dashboard...")
                st.rerun()
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
            

            # Fetch all orders
            all_orders = st.session_state.orders

            # Separate orders by status
            pending_orders = [o for o in all_orders if o.status == "Pending"]
            in_progress_orders = [o for o in all_orders if o.status == "In Progress"]
            ready_orders = [o for o in all_orders if o.status == "Ready for Pickup"]
            done_orders = [o for o in all_orders if o.status == "Done"]

            col_pending, col_in_progress, col_ready, col_done = st.columns(4)

            with col_pending:
                st.markdown("**Pending**")
                st.markdown("---")
                for order in pending_orders:
                    with st.expander(f"Order {order.order_id}"):
                        st.write(str(order))
                        next_status = status_flow[order.status]
                        if next_status and st.button(f"Move to '{next_status}'", key=f"pending_{order.order_id}"):
                            order.update_status(next_status)
                            update_orders_df()
                            st.rerun()

            with col_in_progress:
                st.markdown("**In Progress**")
                st.markdown("---")
                for order in in_progress_orders:
                    with st.expander(f"Order {order.order_id}"):
                        st.write(str(order))
                        next_status = status_flow[order.status]
                        if next_status and st.button(f"Move to '{next_status}'", key=f"inprogress_{order.order_id}"):
                            order.update_status(next_status)
                            update_orders_df()
                            st.rerun()

            with col_ready:
                st.markdown("**Ready for Pickup**")
                st.markdown("---")
                for order in ready_orders:
                    with st.expander(f"Order {order.order_id}"):
                        st.write(str(order))
                        next_status = status_flow[order.status]
                        if next_status and st.button(f"Move to '{next_status}'", key=f"ready_{order.order_id}"):
                            order.update_status(next_status)
                            update_orders_df()
                            st.rerun()

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
            total_revenue = orders_df["Total Cost (DKK)"].sum() if not orders_df.empty else 0
            total_customers = customers_df["Customer ID"].nunique() if not customers_df.empty else 0
            total_orders = orders_df["Order ID"].nunique() if not orders_df.empty else 0

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Revenue (DKK)", f"{total_revenue:,.2f}")
            with col2:
                st.metric("Total Customers", total_customers)
            with col3:
                st.metric("Total Orders", total_orders)

            # Revenue over time
            st.subheader("Revenue Over Time")
            if not orders_df.empty:
                revenue_by_date = (
                    orders_df.groupby(orders_df["Order Time"].str[:10])["Total Cost (DKK)"]
                    .sum()
                    .reset_index()
                )
                revenue_by_date.columns = ["Date", "Revenue"]
                revenue_by_date["Date"] = pd.to_datetime(revenue_by_date["Date"])

                fig_revenue = px.line(revenue_by_date, x="Date", y="Revenue", title="Revenue Over Time")
                st.plotly_chart(fig_revenue, use_container_width=True)
            else:
                st.info("No revenue data available.")

            # Row for "Top Customers" and "Ingredient Popularity"
            st.markdown("---")
            st.subheader("Top Insights")
            col4, col5 = st.columns(2)

            with col4:
                st.subheader("Top Customers")
                if not customers_df.empty:
                    top_customers = (
                        customers_df[["Name", "Total Sandwiches Purchased"]]
                        .sort_values(by="Total Sandwiches Purchased", ascending=False)
                        .head(10)
                    )
                    st.table(top_customers)
                else:
                    st.info("No customer data available.")

            with col5:
                st.subheader("Ingredient Popularity")
                if not ingredients_df.empty and "Usage" in ingredients_df.columns:
                    top_ingredients = ingredients_df.sort_values(by="Usage", ascending=False).head(10)
                    st.table(top_ingredients)
                else:
                    st.info("No ingredient usage data available.")

            # Row for "Order Volume by Date" and "Customers by Total Orders"
            st.markdown("---")
            col6, col7 = st.columns(2)

            with col6:
                st.subheader("Order Volume by Date")
                if not orders_df.empty:
                    orders_by_date = (
                        orders_df.groupby(orders_df["Order Time"].str[:10])["Order ID"]
                        .count()
                        .reset_index()
                    )
                    orders_by_date.columns = ["Date", "Order Count"]
                    orders_by_date["Date"] = pd.to_datetime(orders_by_date["Date"])

                    fig_orders = px.bar(orders_by_date, x="Date", y="Order Count", title="Order Volume by Date")
                    st.plotly_chart(fig_orders, use_container_width=True)
                else:
                    st.info("No order data available.")

            with col7:
                st.subheader("Customers by Total Orders")
                if not customers_df.empty:
                    customer_orders = customers_df[["Name", "Number of Orders"]].sort_values(
                        by="Number of Orders", ascending=False
                    ).head(10)

                    fig_customers = px.bar(customer_orders, x="Name", y="Number of Orders", title="Top Customers by Total Orders")
                    st.plotly_chart(fig_customers, use_container_width=True)
                else:
                    st.info("No customer data available.")

        # Tab 3: Manage Inventory
        with tab3:
            st.header("Manage Inventory")

            categories = ["Bread", "Spread", "Protein", "Vegetable", "Extra", "Dressing"]
            selected_category = st.selectbox("Choose Category", categories)

            if selected_category:
                category_key = selected_category.lower()
                inventory = st.session_state.inventory
                category_dict = inventory._get_category_dict(category_key)

                if category_dict:
                    st.write(f"### Current Ingredients in {selected_category}:")
                    for ingredient, price in category_dict.items():
                        st.write(f"- **{ingredient}:** {price:.2f} DKK")
                else:
                    st.error(f"Invalid category '{selected_category}'.")

                # Add New Ingredient
                st.markdown("### Add New Ingredient")
                with st.form("Add Ingredient", clear_on_submit=True):
                    add_category = st.selectbox("Category for New Ingredient", [c for c in categories])
                    new_ingredient = st.text_input("Ingredient Name")
                    new_price = st.number_input("Ingredient Price (DKK)", min_value=0.0, value=0.0, step=0.1)
                    add_ingredient_btn = st.form_submit_button("Add Ingredient")

                    if add_ingredient_btn:
                        try:
                            inventory.add_ingredient(add_category, new_ingredient, new_price)
                            st.success(f"Added **{new_ingredient}** to **{add_category.capitalize()}** category.")
                            st.rerun()
                        except ValueError as e:
                            st.error(str(e))

                # Remove Ingredient
                st.markdown("### Remove Ingredient")
                if category_dict:
                    ingredient_to_remove = st.selectbox("Choose Ingredient to Remove", list(category_dict.keys()))
                    if st.button("Remove Ingredient"):
                        try:
                            inventory.remove_ingredient(category_key, ingredient_to_remove)
                            st.success(f"Removed **{ingredient_to_remove}** from **{selected_category.capitalize()}**.")
                            st.rerun()
                        except ValueError as e:
                            st.error(str(e))