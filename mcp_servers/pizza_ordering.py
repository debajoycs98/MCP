#!/usr/bin/env python3
"""
MCP Server for Pizza Ordering
Allows AI assistants to order pizzas from various restaurants
"""

import asyncio
import os
from typing import List, Optional, Dict
from datetime import datetime
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Import FastMCP
try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    from mcp.server import Server
    from mcp.types import Tool, TextContent

# Initialize MCP server
mcp = FastMCP("Pizza Ordering")

# Mock pizza menu data
PIZZA_MENU = {
    "margherita": {"name": "Margherita Pizza", "price": 12.99, "description": "Classic tomato sauce, mozzarella, and basil"},
    "pepperoni": {"name": "Pepperoni Pizza", "price": 14.99, "description": "Tomato sauce, mozzarella, and pepperoni"},
    "veggie": {"name": "Veggie Supreme", "price": 16.99, "description": "Tomato sauce, mozzarella, bell peppers, onions, mushrooms, olives"},
    "meat_lovers": {"name": "Meat Lovers", "price": 18.99, "description": "Tomato sauce, mozzarella, pepperoni, sausage, bacon, ham"},
    "hawaiian": {"name": "Hawaiian Pizza", "price": 15.99, "description": "Tomato sauce, mozzarella, ham, and pineapple"},
    "supreme": {"name": "Supreme Pizza", "price": 19.99, "description": "Tomato sauce, mozzarella, pepperoni, sausage, bell peppers, onions, mushrooms, olives"}
}

# Mock restaurant data
RESTAURANTS = {
    "pizza_hut": {"name": "Pizza Hut", "phone": "1-800-PIZZA-HUT", "delivery_fee": 3.99},
    "dominos": {"name": "Domino's", "phone": "1-800-DOMINOS", "delivery_fee": 2.99},
    "papa_johns": {"name": "Papa John's", "phone": "1-800-PAPA-JOHN", "delivery_fee": 4.99}
}

# Order storage
orders_db = []

@mcp.tool()
async def get_pizza_menu() -> str:
    """
    Get the available pizza menu.
    
    Returns:
        List of available pizzas with prices and descriptions
    """
    try:
        menu_text = "🍕 Available Pizzas:\n\n"
        
        for pizza_id, pizza_info in PIZZA_MENU.items():
            menu_text += f"• {pizza_info['name']} - ${pizza_info['price']:.2f}\n"
            menu_text += f"  {pizza_info['description']}\n"
            menu_text += f"  ID: {pizza_id}\n\n"
        
        return menu_text
        
    except Exception as e:
        return f"Error getting menu: {str(e)}"

@mcp.tool()
async def get_restaurants() -> str:
    """
    Get available pizza restaurants.
    
    Returns:
        List of available restaurants with contact info
    """
    try:
        restaurants_text = "🍕 Available Restaurants:\n\n"
        
        for restaurant_id, restaurant_info in RESTAURANTS.items():
            restaurants_text += f"• {restaurant_info['name']}\n"
            restaurants_text += f"  Phone: {restaurant_info['phone']}\n"
            restaurants_text += f"  Delivery Fee: ${restaurant_info['delivery_fee']:.2f}\n"
            restaurants_text += f"  ID: {restaurant_id}\n\n"
        
        return restaurants_text
        
    except Exception as e:
        return f"Error getting restaurants: {str(e)}"

@mcp.tool()
async def order_pizza(
    pizza_type: str,
    size: str = "large",
    quantity: int = 1,
    restaurant: str = "dominos",
    customer_name: str = "Customer",
    customer_phone: str = "",
    delivery_address: str = "",
    special_instructions: str = ""
) -> str:
    """
    Place a pizza order.
    
    Args:
        pizza_type: Type of pizza (use pizza ID from menu)
        size: Pizza size (small, medium, large, extra_large)
        quantity: Number of pizzas
        restaurant: Restaurant ID
        customer_name: Customer name
        customer_phone: Customer phone number
        delivery_address: Delivery address
        special_instructions: Special instructions for the order
    
    Returns:
        Order confirmation with details
    """
    try:
        # Validate pizza type
        if pizza_type not in PIZZA_MENU:
            available_pizzas = ", ".join(PIZZA_MENU.keys())
            return f"Error: Pizza type '{pizza_type}' not found. Available types: {available_pizzas}"
        
        # Validate restaurant
        if restaurant not in RESTAURANTS:
            available_restaurants = ", ".join(RESTAURANTS.keys())
            return f"Error: Restaurant '{restaurant}' not found. Available restaurants: {available_restaurants}"
        
        # Calculate pricing
        base_price = PIZZA_MENU[pizza_type]["price"]
        size_multiplier = {"small": 0.8, "medium": 1.0, "large": 1.2, "extra_large": 1.4}.get(size, 1.0)
        pizza_price = base_price * size_multiplier
        subtotal = pizza_price * quantity
        delivery_fee = RESTAURANTS[restaurant]["delivery_fee"]
        total = subtotal + delivery_fee
        
        # Create order
        order = {
            "order_id": len(orders_db) + 1,
            "pizza_type": pizza_type,
            "pizza_name": PIZZA_MENU[pizza_type]["name"],
            "size": size,
            "quantity": quantity,
            "restaurant": restaurant,
            "restaurant_name": RESTAURANTS[restaurant]["name"],
            "customer_name": customer_name,
            "customer_phone": customer_phone,
            "delivery_address": delivery_address,
            "special_instructions": special_instructions,
            "pizza_price": pizza_price,
            "subtotal": subtotal,
            "delivery_fee": delivery_fee,
            "total": total,
            "status": "pending",
            "order_time": datetime.now().isoformat()
        }
        
        orders_db.append(order)
        
        # Create confirmation
        confirmation = f"🍕 Pizza Order Confirmed!\n\n"
        confirmation += f"Order ID: #{order['order_id']}\n"
        confirmation += f"Pizza: {order['pizza_name']} ({size})\n"
        confirmation += f"Quantity: {quantity}\n"
        confirmation += f"Restaurant: {order['restaurant_name']}\n"
        confirmation += f"Customer: {customer_name}\n"
        
        if customer_phone:
            confirmation += f"Phone: {customer_phone}\n"
        if delivery_address:
            confirmation += f"Address: {delivery_address}\n"
        if special_instructions:
            confirmation += f"Special Instructions: {special_instructions}\n"
        
        confirmation += f"\n💰 Pricing:\n"
        confirmation += f"Pizza Price: ${pizza_price:.2f} each\n"
        confirmation += f"Subtotal: ${subtotal:.2f}\n"
        confirmation += f"Delivery Fee: ${delivery_fee:.2f}\n"
        confirmation += f"Total: ${total:.2f}\n\n"
        confirmation += f"📞 To complete your order, call: {RESTAURANTS[restaurant]['phone']}\n"
        confirmation += f"Status: {order['status']}"
        
        return confirmation
        
    except Exception as e:
        return f"Error placing order: {str(e)}"

@mcp.tool()
async def check_order_status(order_id: int) -> str:
    """
    Check the status of a pizza order.
    
    Args:
        order_id: Order ID to check
    
    Returns:
        Order status and details
    """
    try:
        for order in orders_db:
            if order["order_id"] == order_id:
                status_text = f"🍕 Order #{order_id} Status\n\n"
                status_text += f"Pizza: {order['pizza_name']} ({order['size']})\n"
                status_text += f"Quantity: {order['quantity']}\n"
                status_text += f"Restaurant: {order['restaurant_name']}\n"
                status_text += f"Customer: {order['customer_name']}\n"
                status_text += f"Total: ${order['total']:.2f}\n"
                status_text += f"Status: {order['status']}\n"
                status_text += f"Order Time: {order['order_time']}\n"
                
                if order['delivery_address']:
                    status_text += f"Delivery Address: {order['delivery_address']}\n"
                
                return status_text
        
        return f"Order #{order_id} not found."
        
    except Exception as e:
        return f"Error checking order status: {str(e)}"

@mcp.tool()
async def list_orders() -> str:
    """
    List all pizza orders.
    
    Returns:
        List of all orders
    """
    try:
        if not orders_db:
            return "No pizza orders found."
        
        orders_text = f"🍕 All Pizza Orders ({len(orders_db)} total):\n\n"
        
        for order in orders_db:
            orders_text += f"Order #{order['order_id']}: {order['pizza_name']} - ${order['total']:.2f} - {order['status']}\n"
        
        return orders_text
        
    except Exception as e:
        return f"Error listing orders: {str(e)}"

if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
