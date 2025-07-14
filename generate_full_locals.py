#!/usr/bin/env python3
import os
import json

# 1) Master English strings
base_strings = {
    "welcome": "Welcome to CLÆRK",
    "login": "Login",
    "logout": "Logout",
    "register": "Register",
    "email": "Email",
    "password": "Password",
    "cart": "Cart",
    "checkout": "Checkout",
    "add_to_cart": "Add to Cart",
    "remove": "Remove",
    "your_cart": "Your Cart",
    "products": "Products",
    "price": "Price",
    "category": "Category",
    "created": "Created",
    "testimonials": "Testimonials",
    "what_users_say": "What Users Say",
    "orders": "Orders",
    "users": "Users",
    "admin": "Admin",
    "bots": "Bots",
    "analytics": "Analytics",
    "total_sales": "Total Sales",
    "unique_visitors": "Unique Visitors",
    "products_generated": "Products Generated",
    "conversion_rate": "Conversion Rate",
    "edit": "Edit",
    "delete": "Delete",
    "approve": "Approve",
    "run_now": "Run Now",
    "download": "Download",
    "close": "Close",
    "refresh": "Refresh",
    "export_csv": "Export CSV",
    "account_login": "Account Login",
    "create_account": "Create Account",
    "cancel": "Cancel",
    "error": "Error",
    "add_product": "Add Product",
    "send": "Send",
    "search": "Search",
    "describe_your_product": "Describe Your Dream Product",
    "generate": "Generate",
    "activity": "Activity",
    "lead_magnet": "Free Download",
    "terms": "Terms of Service",
    "privacy": "Privacy Policy",
    "not_found": "Page Not Found",
    "support_chat": "Support Chat",
    "ai_editor": "AI Editor"
}

# 2) Desired locale codes
language_codes = [
    "en","es","fr","de","it","pt","zh-CN","zh-TW","ja","ko","ar","ru",
    "hi","bn","ur","tr","vi","th","id","nl","sv","da","fi","no","pl",
    "uk","he","el","cs","hu","ro","bg","ms","ta","te"
]

# 3) Ensure output dir
os.makedirs("locales", exist_ok=True)

# 4) Write one JSON per locale (all seeded with English)
for code in language_codes:
    with open(f"locales/{code}.json", "w", encoding="utf-8") as f:
        json.dump(base_strings, f, ensure_ascii=False, indent=2)
    print(f"Generated locales/{code}.json")

print("✅ All English-seeded locale files written under ./locales/")
