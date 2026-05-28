from src.models.lifecycle import LifecycleState, LifecycleTransition, ProductLifecycle
from src.config.db_sql import get_db_connection


# In-memory lifecycle store (simulates DB table)
_lifecycles: dict[int, ProductLifecycle] = {}
_history_store: list[dict] = []


def get_lifecycle(product_id: int) -> ProductLifecycle | None:
    return _lifecycles.get(product_id)


def advance_lifecycle(product_id: int, action: str) -> dict:
    valid_actions = {
        "submit": LifecycleState.REVIEW,
        "approve": LifecycleState.PUBLISHED,
        "reject": LifecycleState.DRAFT,
        "archive": LifecycleState.ARCHIVED,
        "unpublish": LifecycleState.REVIEW,
    }

    target_state = valid_actions.get(action)
    if target_state is None:
        raise ValueError(f"Invalid action: {action}")

    lifecycle = _lifecycles.get(product_id)
    if lifecycle is None:
        # Auto-create lifecycle for existing products
        lifecycle = ProductLifecycle(product_id, LifecycleState.DRAFT)
        _lifecycles[product_id] = lifecycle

    if not LifecycleTransition.can_transition(lifecycle.state, target_state):
        raise ValueError(
            f"Cannot transition from {lifecycle.state.value} to {target_state.value}"
        )

    previous = lifecycle.state
    lifecycle.state = target_state

    entry = {
        "product_id": product_id,
        "from_state": previous.value,
        "to_state": target_state.value,
        "action": action,
    }
    _history_store.append(entry)
    lifecycle.history.append(entry)

    # Persist lifecycle state in products table
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE products SET lifecycle_state = ? WHERE id = ?",
        (target_state.value, product_id),
    )
    conn.commit()

    return entry


def get_lifecycle_history(product_id: int) -> list[dict]:
    return [h for h in _history_store if h["product_id"] == product_id]


def init_lifecycle_states():
    """Seed lifecycle states for existing products."""
    conn = get_db_connection()
    cursor = conn.cursor()
    # Add lifecycle_state column if not present
    try:
        cursor.execute("ALTER TABLE products ADD COLUMN lifecycle_state TEXT DEFAULT 'published'")
    except Exception:
        pass  # Column already exists

    cursor.execute("SELECT id FROM products")
    for row in cursor.fetchall():
        pid = row["id"]
        # Published products start as published
        lifecycle = ProductLifecycle(pid, LifecycleState.PUBLISHED)
        _lifecycles[pid] = lifecycle
        cursor.execute(
            "UPDATE products SET lifecycle_state = ? WHERE id = ?",
            ("published", pid),
        )
    conn.commit()