import functools
import json
import logging
import os

from pydash import _
from requests import Session

from pydex_lib.upstash_redis_client import (
    RedisEnvironmentInfo,
    RedisUpstashRestAPIClient,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class RateLimiter:
    def __init__(
        self,
        redis: RedisUpstashRestAPIClient,
        number_of_requests_limit: int,
        reset_period_in_seconds: int,
    ):
        self.period = reset_period_in_seconds
        self.limit = number_of_requests_limit
        self.redis = redis

    def should_allow(self, key) -> bool:
        current_requests = self.redis.get(key)
        if current_requests is None:
            self.redis.set(key, 1)
            self.redis.expire(key, self.period)
            return True
        if current_requests <= self.limit:
            self.redis.incr(key)
            return True
        return False


limiter = None


def get_limiter(api_url, token, prefix, limit, period):
    global limiter
    if limiter:
        return limiter
    redis_env = RedisEnvironmentInfo(api_url=api_url, prefix=prefix, token=token)
    redis_http_session = Session()
    limiter = RateLimiter(
        redis=RedisUpstashRestAPIClient(
            environment=redis_env, http_session=redis_http_session
        ),
        number_of_requests_limit=limit,
        reset_period_in_seconds=period,
    )
    return limiter


def rate_limited(event_key, prefix, limit, period):
    def decorator_func(func):
        @functools.wraps(func)
        def wrapped_function(*args, **kwargs):
            logger.info("Entering rate_limited with args: %s", args)
            event = args[0]
            rate_limiter_key = _.get(event, event_key)
            logger.info("Extracted rate limiter key: %s", rate_limiter_key)

            rate_limiter = get_limiter(
                api_url=os.environ["REDIS_URL"],
                token=os.environ["REDIS_TOKEN"],
                prefix=prefix,
                limit=limit,
                period=period,
            )

            logger.info("Instantied rate limiter: %s", rate_limiter)

            if rate_limiter.should_allow(rate_limiter_key):
                logger.info("Rate limit - OK")
                response = func(*args, **kwargs)
                logger.info("Func response: %s", response)
                return response
            else:
                logger.info("Rate limit - exceeded")
                return {
                    "statusCode": 429,
                    "body": json.dumps({"message": "Rate limit exceeded"}),
                }

        return wrapped_function

    return decorator_func
