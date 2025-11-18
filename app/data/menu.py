"""
Simple Menu Data
"""

MENU = {
    "1": {
        "id": "1",
        "name": "Margherita Pizza",
        "description": "Classic pizza with tomato sauce, mozzarella cheese, and fresh basil",
        "price": 299.00,
        "category": "pizza"
    },
    "2": {
        "id": "2",
        "name": "Chicken Burger",
        "description": "Juicy grilled chicken patty with lettuce, tomato, and special sauce",
        "price": 199.00,
        "category": "burger"
    },
    "3": {
        "id": "3",
        "name": "French Fries",
        "description": "Crispy golden french fries with seasoning",
        "price": 99.00,
        "category": "side"
    },
    "4": {
        "id": "4",
        "name": "Pasta Alfredo",
        "description": "Creamy fettuccine pasta with parmesan cheese and herbs",
        "price": 279.00,
        "category": "pasta"
    },
    "5": {
        "id": "5",
        "name": "Club Sandwich",
        "description": "Triple-decker sandwich with chicken, cheese, and veggies",
        "price": 179.00,
        "category": "sandwich"
    }
}


def search_menu(query: str):
    """Search menu items by query"""
    query = query.lower()
    results = []
    
    for item_id, item in MENU.items():
        if (query in item['name'].lower() or 
            query in item['description'].lower() or 
            query in item['category'].lower()):
            results.append(item)
    
    return results


def get_menu_text():
    """Get formatted menu text"""
    menu_text = "Our menu today:\n"
    for item in MENU.values():
        menu_text += f"- {item['name']}: {item['description']} - ₹{item['price']}\n"
    return menu_text


def get_item_by_id(item_id: str):
    """Get item by ID"""
    return MENU.get(item_id)
