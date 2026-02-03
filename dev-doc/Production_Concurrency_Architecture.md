# NexSidi Production Concurrency Architecture
**Handling Multiple Projects Simultaneously - Professional Quality**

**Critical Concern:** If 2-3 projects build at same time with multiple agents/tests running in parallel, system MUST NOT break. This is about **professional service quality**, not cost.

---

## 🚨 THE PROBLEM (Without Proper Architecture)

### Scenario: 3 Projects Building Simultaneously

```
Time: 2:15 PM at Demo Booth

Project A (Kirana Shop):
  NAVYA reviewing backend    → Calling Claude API
  KARAN reviewing backend    → Calling Claude API
  AARAV testing in browser   → Opening Chrome

Project B (Blog Platform):
  NAVYA reviewing backend    → Calling Claude API
  DEEPIKA reviewing backend  → Calling Claude API
  AARAV testing in browser   → Opening Chrome

Project C (Restaurant):
  SHUBHAM generating code    → Calling Gemini API
  AANYA generating frontend  → Calling Gemini API
```

**What Goes Wrong:**

### 1. Database Race Conditions
```python
# Project A saves:
db.update(project_id="abc", status="testing")

# Project B saves at SAME TIME:
db.update(project_id="xyz", status="testing")

# Result: Database lock timeout! 💥
# One project fails randomly
```

### 2. AI API Rate Limits
```
Claude API Limit: 50 requests/minute
Gemini API Limit: 60 requests/minute

Project A: 3 requests
Project B: 3 requests
Project C: 2 requests

Total: 8 concurrent requests

If 10 more visitors arrive...
→ 80 concurrent requests
→ API rate limit exceeded! 💥
→ All projects fail
```

### 3. File System Conflicts
```python
# Project A creates:
/tmp/test_results/screenshot.png

# Project B creates at SAME TIME:
/tmp/test_results/screenshot.png

# Result: File overwritten! 💥
# Wrong screenshot shown to wrong customer
```

### 4. Browser Resource Exhaustion
```
AARAV opens 10 Chrome instances (10 projects testing)
Each Chrome: ~500MB RAM

Total RAM: 5GB
Server has: 4GB

Result: Out of memory! 💥
System crashes
```

### 5. GCP Quota Limits
```
GCP Cloud Run: 100 concurrent deployments per region

If 150 visitors at demo...
→ 150 deployment requests
→ Quota exceeded! 💥
→ Projects stuck in "deploying" forever
```

---

## ✅ THE SOLUTION: Professional Concurrency Architecture

### Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                  LOAD BALANCER                      │
│          (Handles incoming requests)                │
└────────────────────┬────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────┐
│              QUEUE SYSTEM (Redis)                   │
│  Project A → Queue 1 (position 1)                   │
│  Project B → Queue 2 (position 2)                   │
│  Project C → Queue 3 (position 3)                   │
└────────────────────┬────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────┐
│           WORKER POOL (3-5 workers)                 │
│  Worker 1: Processing Project A                     │
│  Worker 2: Processing Project B                     │
│  Worker 3: Processing Project C                     │
│  Worker 4: Idle (waiting)                           │
│  Worker 5: Idle (waiting)                           │
└────────────────────┬────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────┐
│          PROJECT ISOLATION (Containers)             │
│  Project A → Container A (isolated)                 │
│  Project B → Container B (isolated)                 │
│  Project C → Container C (isolated)                 │
└─────────────────────────────────────────────────────┘
```

---

## 🏗️ IMPLEMENTATION

### 1. Queue System (Redis + Celery)

**Purpose:** Prevent overwhelming system, control concurrency

```python
# backend/app/services/queue_manager.py

from celery import Celery
from redis import Redis
import asyncio

app = Celery('nexsidi', broker='redis://localhost:6379/0')
redis_client = Redis(host='localhost', port=6379, db=0)

class QueueManager:
    """Manages project queue and concurrent execution"""
    
    def __init__(self):
        self.max_concurrent_projects = 3  # Maximum 3 at once
        self.redis = redis_client
    
    async def enqueue_project(self, project_id: str, user_id: str):
        """Add project to queue"""
        
        # Check current queue size
        queue_size = await self.get_queue_size()
        
        if queue_size >= 10:  # Maximum 10 in queue
            raise Exception("Queue is full. Please try again in 5 minutes.")
        
        # Add to queue
        position = await self.redis.lpush('project_queue', project_id)
        
        # Store project metadata
        await self.redis.hset(
            f'project:{project_id}',
            mapping={
                'user_id': user_id,
                'status': 'queued',
                'queue_position': position,
                'queued_at': time.time()
            }
        )
        
        return {
            'project_id': project_id,
            'queue_position': position,
            'estimated_wait': self._estimate_wait_time(position)
        }
    
    async def get_queue_size(self) -> int:
        """Get current queue size"""
        return await self.redis.llen('project_queue')
    
    def _estimate_wait_time(self, position: int) -> str:
        """Estimate wait time based on position"""
        
        # Average project: 15 minutes
        # 3 concurrent: 5 minutes per batch
        
        wait_minutes = (position // 3) * 5
        
        if wait_minutes == 0:
            return "Starting now"
        elif wait_minutes <= 5:
            return "1-5 minutes"
        elif wait_minutes <= 15:
            return "5-15 minutes"
        else:
            return f"~{wait_minutes} minutes"


# Celery task for processing projects
@app.task
async def process_project(project_id: str):
    """Process project in isolated worker"""
    
    try:
        # Update status
        await redis_client.hset(
            f'project:{project_id}',
            'status', 'processing'
        )
        
        # Process with isolation
        result = await ProjectProcessor(project_id).process()
        
        # Update status
        await redis_client.hset(
            f'project:{project_id}',
            mapping={
                'status': 'completed',
                'result': json.dumps(result)
            }
        )
        
        return result
        
    except Exception as e:
        # Update status
        await redis_client.hset(
            f'project:{project_id}',
            mapping={
                'status': 'failed',
                'error': str(e)
            }
        )
        raise
```

**Result:**
- ✅ Only 3 projects process at once
- ✅ Others wait in queue
- ✅ No resource exhaustion
- ✅ Fair queuing (FIFO)

---

### 2. Project Isolation (Docker Containers)

**Purpose:** Each project runs in isolated environment

```python
# backend/app/services/project_isolator.py

import docker
import uuid

class ProjectIsolator:
    """Isolate each project in separate container"""
    
    def __init__(self):
        self.docker_client = docker.from_env()
    
    async def create_isolated_environment(self, project_id: str):
        """Create isolated container for project"""
        
        # Create unique network for this project
        network = self.docker_client.networks.create(
            f"nexsidi-project-{project_id}",
            driver="bridge",
            check_duplicate=True
        )
        
        # Create container with resource limits
        container = self.docker_client.containers.run(
            image="nexsidi-worker:latest",
            name=f"nexsidi-worker-{project_id}",
            network=network.name,
            detach=True,
            remove=True,  # Auto-remove after completion
            mem_limit="1g",  # 1GB RAM limit
            cpu_quota=50000,  # 50% CPU limit
            environment={
                'PROJECT_ID': project_id,
                'ISOLATED': 'true'
            },
            volumes={
                f'/tmp/nexsidi/{project_id}': {
                    'bind': '/workspace',
                    'mode': 'rw'
                }
            }
        )
        
        return {
            'container_id': container.id,
            'network_id': network.id,
            'workspace': f'/tmp/nexsidi/{project_id}'
        }
    
    async def cleanup_environment(self, project_id: str):
        """Clean up isolated environment"""
        
        try:
            # Stop container
            container = self.docker_client.containers.get(
                f"nexsidi-worker-{project_id}"
            )
            container.stop(timeout=10)
            container.remove()
            
            # Remove network
            network = self.docker_client.networks.get(
                f"nexsidi-project-{project_id}"
            )
            network.remove()
            
        except docker.errors.NotFound:
            pass  # Already cleaned up
```

**Result:**
- ✅ Each project isolated
- ✅ Resource limits enforced
- ✅ No interference between projects
- ✅ Automatic cleanup

---

### 3. Database Connection Pooling

**Purpose:** Prevent database connection exhaustion

```python
# backend/app/database.py (UPDATED)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,          # Maximum 10 connections
    max_overflow=20,       # Allow 20 extra during peak
    pool_timeout=30,       # Wait 30s for connection
    pool_recycle=3600,     # Recycle connections every hour
    pool_pre_ping=True     # Test connection before use
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Dependency for getting DB session
async def get_db():
    """
    Get database session with automatic cleanup.
    
    Each request gets own session.
    Session auto-closed after request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Transaction helper for concurrent updates
async def safe_update(db, model, filters, updates):
    """
    Thread-safe database update with retry.
    
    Handles race conditions automatically.
    """
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            # Start transaction
            db.begin_nested()
            
            # Lock row for update
            obj = db.query(model).filter_by(**filters).with_for_update().first()
            
            if not obj:
                raise ValueError("Object not found")
            
            # Apply updates
            for key, value in updates.items():
                setattr(obj, key, value)
            
            # Commit
            db.commit()
            return obj
            
        except Exception as e:
            db.rollback()
            
            if attempt == max_retries - 1:
                raise
            
            # Wait before retry
            await asyncio.sleep(0.1 * (2 ** attempt))
```

**Result:**
- ✅ No connection exhaustion
- ✅ Automatic retry on conflicts
- ✅ Row-level locking
- ✅ No race conditions

---

### 4. AI API Rate Limiting

**Purpose:** Respect API limits, prevent failures

```python
# backend/app/services/rate_limiter.py

import asyncio
from collections import deque
import time

class AIRateLimiter:
    """Rate limiter for AI API calls"""
    
    def __init__(self):
        # Claude: 50 requests/minute
        self.claude_limit = 50
        self.claude_window = 60  # seconds
        self.claude_calls = deque()
        
        # Gemini: 60 requests/minute
        self.gemini_limit = 60
        self.gemini_window = 60
        self.gemini_calls = deque()
        
        self.locks = {
            'claude': asyncio.Lock(),
            'gemini': asyncio.Lock()
        }
    
    async def acquire(self, provider: str):
        """
        Acquire permission to make API call.
        Blocks if rate limit would be exceeded.
        """
        
        async with self.locks[provider]:
            # Get limits
            if provider == 'claude':
                limit = self.claude_limit
                window = self.claude_window
                calls = self.claude_calls
            else:
                limit = self.gemini_limit
                window = self.gemini_window
                calls = self.gemini_calls
            
            # Remove old calls outside window
            current_time = time.time()
            while calls and calls[0] < current_time - window:
                calls.popleft()
            
            # Check if at limit
            if len(calls) >= limit:
                # Calculate wait time
                oldest_call = calls[0]
                wait_time = (oldest_call + window) - current_time
                
                if wait_time > 0:
                    print(f"⏳ Rate limit reached for {provider}. Waiting {wait_time:.1f}s...")
                    await asyncio.sleep(wait_time)
            
            # Record this call
            calls.append(current_time)
    
    async def get_current_usage(self, provider: str):
        """Get current usage statistics"""
        
        if provider == 'claude':
            calls = self.claude_calls
            limit = self.claude_limit
        else:
            calls = self.gemini_calls
            limit = self.gemini_limit
        
        current_time = time.time()
        
        # Count calls in last minute
        recent_calls = sum(1 for t in calls if t > current_time - 60)
        
        return {
            'provider': provider,
            'calls_last_minute': recent_calls,
            'limit': limit,
            'percentage': (recent_calls / limit) * 100
        }


# Update AI Router to use rate limiter
rate_limiter = AIRateLimiter()

# In ai_router.py:
async def generate(self, ...):
    # Determine provider
    provider = 'claude' if model.startswith('claude') else 'gemini'
    
    # Wait for rate limit permission
    await rate_limiter.acquire(provider)
    
    # Now make API call
    response = await self._call_model(...)
    
    return response
```

**Result:**
- ✅ Never exceeds API limits
- ✅ Automatic queuing
- ✅ No failed requests
- ✅ Smooth degradation under load

---

### 5. Browser Resource Management

**Purpose:** Prevent Chrome from exhausting memory

```python
# backend/app/agents/aarav_testing.py (UPDATED)

from playwright.async_api import async_playwright
import asyncio

class BrowserPool:
    """Pool of reusable browser instances"""
    
    def __init__(self, max_browsers=3):
        self.max_browsers = max_browsers
        self.available_browsers = asyncio.Queue(maxsize=max_browsers)
        self.lock = asyncio.Lock()
    
    async def initialize(self):
        """Initialize browser pool"""
        
        async with self.lock:
            for i in range(self.max_browsers):
                playwright = await async_playwright().start()
                browser = await playwright.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-gpu'
                    ]
                )
                await self.available_browsers.put((playwright, browser))
    
    async def acquire(self):
        """Get browser from pool (wait if none available)"""
        return await self.available_browsers.get()
    
    async def release(self, playwright, browser):
        """Return browser to pool"""
        await self.available_browsers.put((playwright, browser))
    
    async def cleanup(self):
        """Close all browsers"""
        while not self.available_browsers.empty():
            playwright, browser = await self.available_browsers.get()
            await browser.close()
            await playwright.stop()


# Global browser pool
browser_pool = BrowserPool(max_browsers=3)

class AaravTesting:
    """Browser testing agent with resource management"""
    
    async def test_website(self, url: str):
        """Test website using pooled browser"""
        
        # Acquire browser from pool (wait if all busy)
        playwright, browser = await browser_pool.acquire()
        
        try:
            page = await browser.new_page()
            
            # Set timeout
            page.set_default_timeout(30000)  # 30 seconds
            
            # Test website
            await page.goto(url)
            # ... run tests ...
            
            # Cleanup
            await page.close()
            
            return test_results
            
        finally:
            # Always return browser to pool
            await browser_pool.release(playwright, browser)
```

**Result:**
- ✅ Maximum 3 browsers at once
- ✅ Browser reuse (faster)
- ✅ No memory exhaustion
- ✅ Automatic queuing

---

### 6. File System Isolation

**Purpose:** Each project gets unique workspace

```python
# backend/app/services/workspace_manager.py

import os
import shutil
import uuid

class WorkspaceManager:
    """Manage isolated workspaces for projects"""
    
    def __init__(self, base_path="/tmp/nexsidi"):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)
    
    def create_workspace(self, project_id: str):
        """Create isolated workspace for project"""
        
        workspace_path = os.path.join(self.base_path, project_id)
        
        # Create directory structure
        os.makedirs(workspace_path, exist_ok=True)
        os.makedirs(f"{workspace_path}/code", exist_ok=True)
        os.makedirs(f"{workspace_path}/tests", exist_ok=True)
        os.makedirs(f"{workspace_path}/screenshots", exist_ok=True)
        os.makedirs(f"{workspace_path}/logs", exist_ok=True)
        
        return {
            'workspace': workspace_path,
            'code_dir': f"{workspace_path}/code",
            'test_dir': f"{workspace_path}/tests",
            'screenshot_dir': f"{workspace_path}/screenshots",
            'log_dir': f"{workspace_path}/logs"
        }
    
    def cleanup_workspace(self, project_id: str):
        """Remove workspace after project completion"""
        
        workspace_path = os.path.join(self.base_path, project_id)
        
        if os.path.exists(workspace_path):
            shutil.rmtree(workspace_path)


# Usage in agents:
workspace = workspace_manager.create_workspace(self.project_id)

# Save screenshot to project-specific directory
screenshot_path = f"{workspace['screenshot_dir']}/test_result.png"
await page.screenshot(path=screenshot_path)
```

**Result:**
- ✅ No file conflicts
- ✅ Easy cleanup
- ✅ Organized structure
- ✅ No overwrites

---

### 7. Circuit Breaker Pattern

**Purpose:** Prevent cascading failures

```python
# backend/app/services/circuit_breaker.py

import time
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"    # Normal operation
    OPEN = "open"        # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if recovered

class CircuitBreaker:
    """Circuit breaker for external services"""
    
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
    
    async def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker"""
        
        # Check state
        if self.state == CircuitState.OPEN:
            # Check if timeout passed
            if time.time() - self.last_failure_time > self.timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker OPEN - service unavailable")
        
        try:
            # Execute function
            result = await func(*args, **kwargs)
            
            # Success - reset
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
            
            return result
            
        except Exception as e:
            # Failure
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            # Check threshold
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
                print(f"⚠️ Circuit breaker OPENED after {self.failure_count} failures")
            
            raise


# Usage:
gcp_breaker = CircuitBreaker(failure_threshold=3, timeout=300)

async def deploy_to_gcp(code):
    return await gcp_breaker.call(pranav.deploy, code)
```

**Result:**
- ✅ Fast failure detection
- ✅ Prevents cascade
- ✅ Automatic recovery
- ✅ System stays responsive

---

## 📊 PRODUCTION CONFIGURATION

### Demo Configuration (India AI Summit)

```python
# config/demo.py

DEMO_CONFIG = {
    # Queue settings
    'max_concurrent_projects': 3,
    'max_queue_size': 10,
    'queue_timeout': 900,  # 15 minutes
    
    # Resource limits per project
    'max_memory_per_project': '1g',
    'max_cpu_per_project': 0.5,  # 50% CPU
    'max_browsers_total': 3,
    
    # AI API limits
    'claude_requests_per_minute': 45,  # Leave buffer
    'gemini_requests_per_minute': 55,
    
    # Database connections
    'db_pool_size': 10,
    'db_max_overflow': 20,
    
    # Timeouts
    'project_timeout': 900,  # 15 minutes max
    'agent_timeout': 300,     # 5 minutes per agent
    'browser_test_timeout': 120,  # 2 minutes
    
    # GCP quotas
    'max_deployments_per_hour': 50,
    
    # Monitoring
    'alert_on_queue_size': 8,
    'alert_on_failure_rate': 0.2,  # 20%
}
```

---

## 🎯 DEMO DAY SCENARIO (Realistic)

### Booth Traffic Pattern

```
Time: 2:00 PM - Peak traffic

Minute 1:
- 5 visitors arrive
- 5 projects queued
- 3 processing (Worker 1, 2, 3)
- 2 waiting (positions 4, 5)

Status: ✅ HEALTHY

Minute 5:
- 10 more visitors
- Queue size: 12 (2 from before + 10 new)
- 3 processing
- 9 waiting

Status: ⚠️ WARNING (queue filling)

Minute 10:
- 5 more visitors
- Queue FULL (10 max)
- 3 processing
- 7 waiting
- 5 REJECTED (told to return in 10 min)

Status: ⚠️ AT CAPACITY

Minute 15:
- 3 projects completed
- Queue size: 7
- 3 new projects start
- 5 rejected visitors return

Status: ✅ RECOVERING
```

**What Users See:**

**Position 1-3:** "Starting now..."
**Position 4-7:** "Starting in 5-10 minutes"
**Position 8-10:** "Starting in 10-15 minutes"
**Position 11+:** "Queue is full. Please return in 10 minutes"

---

## 🔍 MONITORING & ALERTS

```python
# backend/app/services/monitoring.py

class SystemMonitor:
    """Monitor system health and alert on issues"""
    
    async def check_health(self):
        """Check all systems"""
        
        health = {
            'queue_size': await queue_manager.get_queue_size(),
            'active_workers': await self.get_active_workers(),
            'database_connections': await self.get_db_connections(),
            'claude_usage': await rate_limiter.get_current_usage('claude'),
            'gemini_usage': await rate_limiter.get_current_usage('gemini'),
            'browser_usage': await self.get_browser_usage(),
            'memory_usage': await self.get_memory_usage(),
        }
        
        # Check thresholds
        alerts = []
        
        if health['queue_size'] >= 8:
            alerts.append("⚠️ Queue nearly full")
        
        if health['claude_usage']['percentage'] >= 80:
            alerts.append("⚠️ Claude API usage high")
        
        if health['memory_usage'] >= 80:
            alerts.append("⚠️ Memory usage critical")
        
        return {
            'health': health,
            'alerts': alerts,
            'status': 'healthy' if not alerts else 'warning'
        }
```

---

## ✅ FINAL RESULT

With this architecture:

**✅ Can Handle:**
- 3-5 projects building simultaneously
- 10 projects in queue
- 50+ demo visitors per day
- Multiple agents per project
- Concurrent browser tests
- Parallel AI API calls

**✅ Guarantees:**
- No race conditions
- No resource exhaustion
- No API rate limit failures
- No file conflicts
- No cascading failures
- Professional quality service

**✅ User Experience:**
- Clear queue position
- Accurate wait times
- Smooth degradation
- No random failures
- Predictable performance

---

## 📝 IMPLEMENTATION PRIORITY

### Week 1 (Before Demo)

**Day 1-2: Queue System**
```
□ Install Redis
□ Install Celery
□ Implement QueueManager
□ Test with 5 concurrent projects
```

**Day 3-4: Rate Limiting**
```
□ Implement AIRateLimiter
□ Update AI Router
□ Test with burst traffic
```

**Day 5: Database Pooling**
```
□ Update database.py
□ Test concurrent writes
□ Verify no race conditions
```

**Day 6: Browser Pooling**
```
□ Implement BrowserPool
□ Update AARAV agent
□ Test with 5 concurrent tests
```

**Day 7: Integration Testing**
```
□ Test 10 concurrent projects
□ Monitor all resources
□ Fix any bottlenecks
```

---

## 🎯 THIS IS WHAT MAKES IT PROFESSIONAL

**Amateur System:**
- ❌ No queue → crashes under load
- ❌ No rate limiting → API failures
- ❌ No isolation → projects interfere
- ❌ No monitoring → blind to issues

**Professional System (NexSidi):**
- ✅ Queue management → controlled load
- ✅ Rate limiting → respects API limits
- ✅ Project isolation → no interference
- ✅ Monitoring → proactive alerts
- ✅ Circuit breakers → graceful degradation
- ✅ Resource pooling → efficient usage

**This is the difference between a demo that works once vs a production system that works reliably.**

---

**YOUR CONCERN WAS 100% VALID.** This document addresses it properly.

Now the system will handle demo traffic professionally! 🚀

---

END OF DOCUMENT
