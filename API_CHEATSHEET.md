# CLÆRK API CHEAT SHEET

## AUTH
- POST `/auth/register` `{email, password}` → `{ok}`
- POST `/auth/login` `{email, password}` → `{token}`

## PRODUCTS
- GET `/products/` → `[products]`
- POST `/products/` `{...}` [admin only]
- DELETE `/products/{slug}` [admin only]

## ORDERS
- GET `/orders/` [user token]
- POST `/orders/checkout-session` `{product_slug}` → Stripe session

## TESTIMONIALS
- GET `/testimonials/`
- POST `/testimonials/` `{product_slug, text}` [user token]
- POST `/testimonials/{id}/approve` [admin]
- DELETE `/testimonials/{id}` [admin]

## BOTS
- GET `/bots`
- POST `/run/{bot_name}`
- POST `/run_all`

## AI/GEN
- POST `/api/generate_product` `{prompt}` [token]
- POST `/ai_editor/` `{instruction, content|file}` → `{before, after, diff}`

## ANALYTICS
- GET `/analytics/`

## ADMIN DASHBOARD
- GET `/admin.html` (HTML page, JWT protected)

## HEALTH
- GET `/health`

## SITEMAP
- GET `/sitemap.xml`

**All endpoints accept/return JSON unless HTML page.**  
**Use JWT Bearer token for authenticated/admin actions.**
