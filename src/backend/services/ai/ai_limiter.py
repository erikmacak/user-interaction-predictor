import asyncio

class AILimiter:
    _semaphore: asyncio.Semaphore | None = None
    _max_concurrent: int = 2
    _waiting_count: int = 0
    
    @classmethod
    def initialize(cls, max_concurrent: int = 2) -> None:
        cls._max_concurrent = max_concurrent
        cls._semaphore = asyncio.Semaphore(max_concurrent)
        print(f"AI Limiter initialized (max {max_concurrent} concurrent LLM calls)")
    
    @classmethod
    async def execute(cls, coro):
        if cls._semaphore is None:
            cls.initialize()
        
        cls._log_queue_status()
        
        await cls._semaphore.acquire()
        
        cls._log_execution_start()
        
        try:
            result = await coro
            return result
        finally:
            cls._semaphore.release()
    
    @classmethod
    def _log_queue_status(cls) -> None:
        if cls._semaphore.locked():
            cls._waiting_count += 1
            print(f"LLM call queued (waiting: {cls._waiting_count})")
    
    @classmethod
    def _log_execution_start(cls) -> None:
        if cls._waiting_count > 0:
            cls._waiting_count -= 1
            print(f"LLM call started (waiting: {cls._waiting_count})")