"""List all routes"""
from app import app

with app.app_context():
    routes = []
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            routes.append(f"{rule.rule:40} -> {rule.endpoint}")
    
    print("\nAll Application Routes:")
    print("=" * 70)
    for route in sorted(routes):
        print(route)
    print("=" * 70)
