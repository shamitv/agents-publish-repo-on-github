import sqlite3
from threading import Lock


_db_conn = None
_db_lock = Lock()


def get_db_connection():
    global _db_conn
    if _db_conn is None:
        _db_conn = sqlite3.connect(":memory:", check_same_thread=False)
        _db_conn.row_factory = sqlite3.Row
    return _db_conn


def init_db():
    with _db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if cursor.fetchone():
            return

        cursor.execute(
            """
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sku TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                description TEXT,
                category TEXT,
                price REAL NOT NULL,
                quantity INTEGER NOT NULL
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                order_number TEXT NOT NULL UNIQUE,
                total_amount REAL NOT NULL,
                status TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL
            )
            """
        )

        cursor.executemany(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            [
                ("alice", "alice123", "CUSTOMER"),
                ("bob", "bob123", "CUSTOMER"),
                ("admin", "admin123", "ADMIN"),
            ],
        )
        cursor.executemany(
            "INSERT INTO products (sku, name, description, category, price, quantity) VALUES (?, ?, ?, ?, ?, ?)",
            [
                ("SKU-CB-001", "Neural Uplink Core v4", "Direct cortical connection unit. Enables high-speed quantum cyberspace navigation.", "Hardware", 850.00, 25),
                ("SKU-CB-002", "Holographic Cyber-Visor", "Augmented reality HUD with thermal signatures, netrunner trace filters, and neon tint.", "Wearables", 320.00, 40),
                ("SKU-CB-003", "Subdermal Armor Plating", "Military-grade synthetic alloy shields that fit neatly under organic skin layers.", "Cyberware", 1250.00, 15),
                ("SKU-CB-004", "Monofilament Laser-Whip", "High-energy micro-filament line that slices through standard security gates.", "Tactical", 450.00, 10),
                ("SKU-CB-005", "Neon Mesh Trenchcoat", "Stunning waterproof active-mesh outerwear with custom LED color wave modulators.", "Apparel", 190.00, 50),
                ("SKU-CB-006", "Decrypted Netrunner Deck", "Pre-configured mainframe access terminal featuring custom payload exploit macros.", "Hardware", 950.00, 8),
                ("SKU-CB-007", "Glitch-Art Decal Sticker Pack", "High-quality reflective vinyl sticker prints featuring corrupted hardware errors.", "Apparel", 15.00, 100),
                ("SKU-CB-008", "Portable Ice-Pick Exploit", "Hardware-based decrypter capable of shattering sub-level commercial firewalls.", "Tactical", 680.00, 12),
            ],
        )

        cursor.execute("INSERT INTO orders (user_id, order_number, total_amount, status) VALUES (1, 'ORD-2026-001', 1170.00, 'DELIVERED')")
        cursor.execute("INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (1, 1, 1, 850.00)")
        cursor.execute("INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (1, 2, 1, 320.00)")
        cursor.execute("INSERT INTO orders (user_id, order_number, total_amount, status) VALUES (2, 'ORD-2026-002', 380.00, 'SHIPPED')")
        cursor.execute("INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (2, 5, 2, 190.00)")
        cursor.execute("INSERT INTO orders (user_id, order_number, total_amount, status) VALUES (1, 'ORD-2026-003', 1250.00, 'PROCESSING')")
        cursor.execute("INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (3, 3, 1, 1250.00)")
        conn.commit()
