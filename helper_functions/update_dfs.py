import pandas as pd
import streamlit as st

# Helper functions to update dataframes

def update_customers_df():
    # Extract data from current session state customers
    new_data = []
    for customer_id, customer in st.session_state.customers.items():
        new_data.append({
            "Customer ID": customer.user_id,
            "Name": customer.name,
            "Email": customer.email,
            "Phone": customer.phone,
            "Total Sandwiches Purchased": customer.sandwich_count,
            "Number of Orders": len(customer.order_history)
        })

    # Convert to DataFrame
    new_customers_df = pd.DataFrame(new_data)

    # Merge with existing customers_df to retain preloaded data
    if "customers_df" in st.session_state and not st.session_state.customers_df.empty:
        st.session_state.customers_df = pd.concat(
            [st.session_state.customers_df, new_customers_df]
        ).drop_duplicates(subset=["Customer ID"], keep="last").reset_index(drop=True)
    else:
        st.session_state.customers_df = new_customers_df


def update_orders_df():
    # Extract data from current session state orders
    new_data = []
    for order in st.session_state.orders:
        new_data.append({
            "Order ID": order.order_id,
            "Customer ID": order.customer.user_id,
            "Order Time": order.order_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Total Cost (DKK)": order.calculate_total()[0],
            "Number of Sandwiches": len(order.sandwiches),
            "Status": order.status
        })

    # Convert to DataFrame
    new_orders_df = pd.DataFrame(new_data)

    # Merge with existing orders_df to retain preloaded data
    if "orders_df" in st.session_state and not st.session_state.orders_df.empty:
        st.session_state.orders_df = pd.concat(
            [st.session_state.orders_df, new_orders_df]
        ).drop_duplicates(subset=["Order ID"], keep="last").reset_index(drop=True)
    else:
        st.session_state.orders_df = new_orders_df