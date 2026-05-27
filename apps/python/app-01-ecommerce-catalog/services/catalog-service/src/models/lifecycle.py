from enum import Enum


class LifecycleState(Enum):
    DRAFT = "draft"
    REVIEW = "review"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class LifecycleTransition:
    ALLOWED_TRANSITIONS = {
        LifecycleState.DRAFT: [LifecycleState.REVIEW],
        LifecycleState.REVIEW: [LifecycleState.PUBLISHED, LifecycleState.DRAFT],
        LifecycleState.PUBLISHED: [LifecycleState.ARCHIVED, LifecycleState.REVIEW],
        LifecycleState.ARCHIVED: [],
    }

    @staticmethod
    def can_transition(current: LifecycleState, target: LifecycleState) -> bool:
        return target in LifecycleTransition.ALLOWED_TRANSITIONS.get(current, [])


class ProductLifecycle:
    def __init__(self, product_id: int, state: LifecycleState):
        self.product_id = product_id
        self.state = state
        self.history: list[dict] = []