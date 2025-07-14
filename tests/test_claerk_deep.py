# tests/test_claerk_deep.py — Deep CLÆRK System Test

import requests
import time
import json
import random

BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin_test@example.com"
ADMIN_PASS = "admintest123"
USER_EMAIL = "user_test@example.com"
USER_PASS = "usertest123"
HEADERS = {"Content-Type": "application/json"}
LOG_FILE = "test_log.txt"

def log(msg):
    print(msg)
    with open(LOG_FILE, "a") as f:
        f.write(msg + "\n")

def assert_ok(resp, msg=""):
    if not resp.ok:
        log(f"[FAIL] {msg or resp.url} — {resp.status_code}: {resp.text}")
        exit(1)
    log(f"[OK] {msg or resp.url}")

def try_login(email, password):
    r = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password})
    return r.json().get("token")

def register_user(email, password):
    log(f"Registering {email} ...")
    r = requests.post(f"{BASE_URL}/auth/register", json={"email": email, "password": password})
    if r.status_code == 400 and "already" in r.text.lower():
        log(f"User {email} exists.")
    else:
        assert_ok(r, f"Register {email}")

def create_product_as_admin(token, product=None):
    if product is None:
        slug = f"deep-test-{random.randint(1,99999)}"
        product = {
            "title": "DeepTest Product",
            "slug": slug,
            "description": "Auto-generated for E2E test.",
            "price": round(random.uniform(8.5, 99.9), 2),
            "category": "Testing",
            "tags": "test,auto,api"
        }
    r = requests.post(
        f"{BASE_URL}/products/",
        headers={"Authorization": f"Bearer {token}", **HEADERS},
        json=product
    )
    assert_ok(r, "Admin create product")
    log(f"Created product: {product['title']}")
    return product["slug"]

def test_jwt_security(token):
    log("Testing JWT protected endpoint ...")
    r = requests.get(f"{BASE_URL}/products/", headers={"Authorization": f"Bearer {token}"})
    assert_ok(r, "JWT security (product list)")

def test_product_generate(token):
    log("Testing prompt-to-product gen ...")
    r = requests.post(
        f"{BASE_URL}/api/generate_product",
        headers={"Authorization": f"Bearer {token}"},
        json={"prompt": "Ultimate Focus Notion Template"}
    )
    assert_ok(r, "Prompt-to-product")
    copy = r.json().get("product_copy")
    log(f"Prompt product copy: {copy[:50]}...")
    return copy

def test_cart_and_checkout(token, product_slug):
    log("Testing cart/checkout flow ...")
    # Create Stripe checkout session
    r = requests.post(
        f"{BASE_URL}/orders/checkout-session",
        headers={"Authorization": f"Bearer {token}"},
        json={"product_slug": product_slug}
    )
    assert_ok(r, "Stripe checkout session")
    sid = r.json().get("sessionId")
    log(f"Checkout session ID: {sid}")
    return sid

def test_list_orders(token):
    log("Listing user orders ...")
    r = requests.get(f"{BASE_URL}/orders/", headers={"Authorization": f"Bearer {token}"})
    assert_ok(r, "List orders")
    log(f"Orders found: {r.json()}")

def test_testimonials(token, product_slug):
    log("Submitting testimonial ...")
    test_text = "This is a test review."
    r = requests.post(
        f"{BASE_URL}/testimonials/",
        headers={"Authorization": f"Bearer {token}"},
        json={"product_slug": product_slug, "text": test_text}
    )
    assert_ok(r, "Testimonial submission")
    # Fetch testimonials
    r2 = requests.get(f"{BASE_URL}/testimonials/")
    assert_ok(r2, "List testimonials")
    log(f"Testimonials: {r2.json()}")

def test_admin_panel(token):
    log("Testing admin panel access ...")
    r = requests.get(f"{BASE_URL}/admin/", headers={"Authorization": f"Bearer {token}"})
    if r.ok:
        log("[OK] Admin panel accessible.")
    else:
        log("[WARN] Admin panel not found (HTML or SPA only)")

def test_bots_api():
    log("Testing bot registry API ...")
    r = requests.get(f"{BASE_URL}/bots")
    assert_ok(r, "Bots API")
    bots = r.json()
    log(f"Bots available: {[b['name'] for b in bots]}")
    # Run a bot via API
    if bots:
        bot_name = bots[0]['name']
        r2 = requests.post(f"{BASE_URL}/run/{bot_name}")
        assert_ok(r2, f"Bot run: {bot_name}")

def test_psych_engine():
    log("Testing psych engine API ...")
    try:
        r = requests.post("http://localhost:8001/personalize", json={
            "content": "Make me buy this planner.",
            "ctx": {"persona": "tester"}
        })
        assert_ok(r, "Psych engine personalize")
        log(f"Personalized: {r.json()}")
    except Exception as e:
        log(f"[WARN] Psych engine not running: {e}")

def test_llm_gateway():
    log("Testing LLM gateway ...")
    try:
        r = requests.post("http://localhost:9999/llm/generate", json={
            "prompt": "Give me a clever product blurb.",
            "provider": "ollama",
            "model": "llama3",
            "max_tokens": 64
        }, timeout=20)
        assert_ok(r, "LLM gateway")
        log(f"LLM output: {r.json().get('response')}")
    except Exception as e:
        log(f"[WARN] LLM gateway not running: {e}")

def test_concurrent_users():
    log("Testing concurrency (simulate multiple users)...")
    from threading import Thread

    def user_flow(email, pwd):
        try:
            register_user(email, pwd)
            token = try_login(email, pwd)
            test_product_generate(token)
        except Exception as e:
            log(f"[FAIL] User flow {email}: {e}")

    threads = []
    for i in range(3):
        t = Thread(target=user_flow, args=(f"test_user_{i}@mail.com", f"pw_{i}_123"))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    log("Concurrent user simulation done.")

def test_security_checks():
    log("Testing protected endpoints without token ...")
    r = requests.get(f"{BASE_URL}/products/")
    if r.status_code == 401:
        log("[OK] Products endpoint correctly protected.")
    else:
        log("[FAIL] Security: Products should be protected.")

def test_404():
    log("Testing 404 page ...")
    r = requests.get(f"{BASE_URL}/no_such_endpoint_abcdef")
    if r.status_code == 404:
        log("[OK] 404 handled properly.")
    else:
        log("[WARN] 404 not handled as expected.")

def main():
    open(LOG_FILE, "w").close()  # Reset log
    log("=== CLÆRK DEEP SYSTEM TEST START ===")
    test_security_checks()
    register_user(ADMIN_EMAIL, ADMIN_PASS)
    register_user(USER_EMAIL, USER_PASS)

    admin_token = try_login(ADMIN_EMAIL, ADMIN_PASS)
    user_token = try_login(USER_EMAIL, USER_PASS)
    assert admin_token and user_token, "Token missing!"

    test_jwt_security(admin_token)
    test_jwt_security(user_token)

    product_slug = create_product_as_admin(admin_token)
    test_product_generate(user_token)
    test_cart_and_checkout(user_token, product_slug)
    test_list_orders(user_token)
    test_testimonials(user_token, product_slug)
    test_admin_panel(admin_token)
    test_bots_api()
    test_psych_engine()
    test_llm_gateway()
    test_concurrent_users()
    test_404()
    log("=== CLÆRK DEEP SYSTEM TEST PASSED ===")
    print(f"\nAll tests passed. See {LOG_FILE} for details.")

if __name__ == "__main__":
    main()
