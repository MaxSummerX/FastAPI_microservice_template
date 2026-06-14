from app.presentation.event_dispatcher import dispatcher
from app.presentation.handlers.users import (
    handle_user_created,
    handle_user_logged_in,
    handle_user_updated,
)


def register_handlers() -> None:
    """Зарегистрировать все обработчики событий."""
    dispatcher.register("user.created", handle_user_created)
    dispatcher.register("user.logged_in", handle_user_logged_in)
    dispatcher.register("user.updated", handle_user_updated)
