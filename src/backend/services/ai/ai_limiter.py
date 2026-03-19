import asyncio
from typing import Optional
from datetime import datetime

class AILimiter:
    _semaphore: Optional[asyncio.Semaphore] = None
    _max_concurrent: int = 2
    _waiting_count: int = 0
    
    @classmethod
    def initialize(cls, max_concurrent: int = 2):
        cls._max_concurrent = max_concurrent
        cls._semaphore = asyncio.Semaphore(max_concurrent)
        print(f"AI Limiter initialized (max {max_concurrent} concurrent LLM calls)")
    
    @classmethod
    async def execute(cls, coro):
        if cls._semaphore is None:
            cls.initialize()
        
        if cls._semaphore.locked():
            cls._waiting_count += 1
            print(f"LLM call queued (waiting: {cls._waiting_count})")
        
        await cls._semaphore.acquire()
        
        if cls._waiting_count > 0:
            cls._waiting_count -= 1
            print(f"LLM call started (waiting: {cls._waiting_count})")
        
        try:
            result = await coro
            return result
        finally:
            cls._semaphore.release()