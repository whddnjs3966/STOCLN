"""Redis 캐시 유틸리티

분석 결과를 캐싱하여 중복 API 호출을 방지합니다.
Redis 연결 실패 시에도 서비스가 정상 동작하도록 graceful degradation을 적용합니다.
"""

import json
import logging

import redis.asyncio as redis

from app.core.config import settings

logger = logging.getLogger(__name__)

_redis_client: redis.Redis | None = None


def _get_client() -> redis.Redis:
    """Redis 클라이언트 싱글턴을 반환합니다."""
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(
            settings.redis_url,
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2,
        )
    return _redis_client


async def get_cached(key: str) -> dict | None:
    """캐시에서 데이터를 조회합니다.

    Args:
        key: 캐시 키

    Returns:
        캐시된 딕셔너리 또는 None (캐시 미스 또는 연결 실패 시)
    """
    try:
        client = _get_client()
        value = await client.get(key)
        if value is not None:
            return json.loads(value)
        return None
    except (redis.ConnectionError, redis.TimeoutError, OSError) as e:
        logger.warning("Redis get failed for key '%s': %s", key, e)
        return None
    except (json.JSONDecodeError, TypeError) as e:
        logger.warning("Redis deserialization failed for key '%s': %s", key, e)
        return None


async def set_cached(key: str, data: dict, ttl: int = 3600) -> None:
    """데이터를 캐시에 저장합니다.

    Args:
        key: 캐시 키
        data: 저장할 딕셔너리
        ttl: 만료 시간(초). 기본 1시간.
    """
    try:
        client = _get_client()
        await client.set(key, json.dumps(data, ensure_ascii=False), ex=ttl)
    except (redis.ConnectionError, redis.TimeoutError, OSError) as e:
        logger.warning("Redis set failed for key '%s': %s", key, e)
    except (TypeError, ValueError) as e:
        logger.warning("Redis serialization failed for key '%s': %s", key, e)


async def invalidate(key: str) -> None:
    """캐시 키를 삭제합니다.

    Args:
        key: 삭제할 캐시 키
    """
    try:
        client = _get_client()
        await client.delete(key)
    except (redis.ConnectionError, redis.TimeoutError, OSError) as e:
        logger.warning("Redis delete failed for key '%s': %s", key, e)
