"""Demo-эндпоинт для тестирования consumer-group."""

import asyncio
from uuid import uuid4

from fastapi import APIRouter, Depends, Query

from app.domain.events.base import BaseEvent
from app.domain.events.users import UserCreatedEvent
from app.infrastructure.message_brokers.protocols.publisher import IEventPublisher
from app.presentation.dependencies import get_event_publisher


router = APIRouter(prefix="/demo", tags=["Demo"])


@router.post("/created")
async def demo_created(
    users: int = Query(default=10, ge=1, le=100_000),
    publisher: IEventPublisher = Depends(get_event_publisher),
) -> dict[str, str]:
    """Создает пользователей и публикует события в Kafka."""
    semaphore = asyncio.Semaphore(50)

    async def publish_with_semaphore(event: BaseEvent) -> None:
        async with semaphore:
            await publisher.publish(event)

    events = [
        UserCreatedEvent(
            user_id=uuid4(),
            email=f"test_{i}@example.com",
            firstname=f"First_name_{i}",
            lastname=f"Last_name_{i}",
        )
        for i in range(users)
    ]

    results = await asyncio.gather(
        *(publish_with_semaphore(event) for event in events),
        return_exceptions=True,
    )

    failed = sum(1 for res in results if isinstance(res, Exception))

    return {"message": f"Создано {users - failed} пользователей, c ошибками: {failed}"}
