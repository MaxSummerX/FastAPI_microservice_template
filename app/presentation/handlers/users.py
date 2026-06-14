import logging

from app.domain.events.users import UserCreatedEvent, UserLoggedInEvent, UserUpdatedEvent


consumer_logger = logging.getLogger("kafka.consumer")


async def handle_user_created(event: UserCreatedEvent) -> None:
    consumer_logger.info("user created: %s | %s", event.user_id, event.email)


async def handle_user_updated(event: UserUpdatedEvent) -> None:
    consumer_logger.info("user updated: %s | %s | %s", event.user_id, event.firstname, event.lastname)


async def handle_user_logged_in(event: UserLoggedInEvent) -> None:
    consumer_logger.info("user logged in: %s", event.user_id)
