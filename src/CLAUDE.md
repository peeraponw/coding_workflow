
# AGENTS.md — Python 3.13+ Development Standards

  

This document defines the authoritative rules for Python development in this repository.

All MUST/NEVER statements are binding. This file contains only enforceable rules, no opinions.

  

If you feel unsure about any implementations, use **Context7 MCP** to check the documentation.

  

---

  

# 1. Core Development Philosophy

  

## 1.1 KISS and YAGNI

  

- Code MUST use the simplest correct solution that satisfies requirements.

- Abstractions MUST be introduced only when they remove real duplication or complexity.

- Speculative features, unused extension points, or “maybe future” parameters MUST NOT be added.

  

```python

# ❌ Forbidden: speculative abstraction

def process_items(items, strategy: Callable | None = None) -> None:

...

  

# ✅ Required: implement only what is needed now

def process_items(items: Sequence[Item]) -> None:

...

```

  

## 1.2 Fail Fast

  

* Code MUST detect invalid state early and raise explicit exceptions.

* Silent fallbacks and dummy defaults MUST NOT be used unless explicitly documented for a specific use case.

  

```python

# ❌ Forbidden: hides real error behind magic fallback

def parse_count(raw: str) -> int:

try:

return int(raw)

except ValueError:

return 0 # silently wrong

  
  

# ✅ Required: fail fast with explicit error

def parse_count(raw: str) -> int:

try:

return int(raw)

except ValueError as exc:

raise ValueError(f"Invalid count {raw!r}") from exc

```

  

## 1.3 No Guessing

  

* Code MUST NOT guess at types, formats, or paths.

* All external input MUST be validated.

* AI-assisted code MUST NOT invent paths or modules that do not exist.

  

---

  

# 2. Architecture & Project Structure

  

## 2.1 Vertical Slice Architecture — MANDATORY

  

The project MUST follow a vertical-slice layout, with code and tests co-located by feature:

  

```text

src/project/

__init__.py

main.py

  

core/

__init__.py

db/

__init__.py

connection.py

models.py

tests/

test_connection.py

test_models.py

auth/

__init__.py

authentication.py

authorization.py

tests/

test_authentication.py

test_authorization.py

  

features/

user_management/

__init__.py

handlers.py

validators.py

services.py

tests/

test_handlers.py

test_validators.py

test_services.py

  

payment_processing/

__init__.py

processor.py

gateway.py

tests/

test_processor.py

test_gateway.py

  

shared/

__init__.py

consts.py

types.py

utils/

__init__.py

string_utils.py

date_utils.py

tests/

test_string_utils.py

test_date_utils.py

```

  

## 2.2 File, Function, and Class Limits

  

* Files MUST NOT exceed **500 lines**.

* Functions MUST NOT exceed **50 lines**.

* Classes MUST NOT exceed **100 lines**.

* Maximum line length MUST be **100 characters**.

  

When nearing these limits, code MUST be split into smaller modules, functions, or classes.

  

## 2.3 Import Rules (No Relative Imports)

  

* Relative imports (`from ..module import X`) MUST NOT be used.

* All imports MUST be absolute, from the top-level package.

  

```python

# ❌ Forbidden

from ..shared.utils import string_utils

  

# ✅ Required

from project.shared.utils import string_utils

```

  

## 2.4 Constants and “Magic” Values

  

* Magic strings/numbers MUST NOT be hard-coded in multiple places.

* Shared constants MUST live in `project/shared/consts.py`.

  

```python

# project/shared/consts.py

DEFAULT_PAGE_SIZE = 50

SYSTEM_USER_NAME = "system"

EVENT_USER_CREATED = "user_created"

```

  

```python

# ❌ Forbidden: inline magic string

audit.log("user_created", user_id=user.id)

  

# ✅ Required

from project.shared.consts import EVENT_USER_CREATED

  

audit.log(EVENT_USER_CREATED, user_id=user.id)

```

  

## 2.5 Dependency Injection for Complex Components

  

* Complex components (DB connections, repositories, external API clients, service classes) MUST be provided via dependency injection, not constructed deep inside business logic.

  

```python

# ❌ Forbidden: hard-coding dependency

def process_user(user_id: UUID) -> None:

repo = UserRepository(create_db_connection())

repo.process(user_id)

  
  

# ✅ Required: inject dependency

def process_user(user_id: UUID, repo: UserRepositoryProtocol) -> None:

repo.process(user_id)

```

  

---

  

# 3. Tooling, Packaging, and Environment

  

## 3.1 Build System — Hatchling (Required)

  

`pyproject.toml` MUST use `hatchling`:

  

```toml

[build-system]

requires = ["hatchling"]

build-backend = "hatchling.build"

```

  

## 3.2 Environment and Dependency Management — uv (Required)

  

* uv MUST be used for environments and dependencies.

  

```bash

curl -LsSf https://astral.sh/uv/install.sh | sh

  

uv venv

uv sync

  

uv add fastapi pydantic

uv add --dev pytest ruff pyright

uv remove some-package

```

  

* Dependencies MUST NOT be edited manually in `pyproject.toml`; use `uv add` / `uv remove`.

  

## 3.3 Code Quality Tools

  

The following tools are mandatory:

  

* Formatting: `ruff format`

* Linting: `ruff check`

* Type checking: `pyright`

* Testing: `pytest`

* Coverage: `pytest --cov=src --cov-report=html`

  

Example commands:

  

```bash

uv run ruff format .

uv run ruff check .

uv run pyright src/

uv run pytest

uv run pytest --cov=src --cov-report=html

```

  

---

  

# 4. Python Style and Conventions

  

## 4.1 PEP 8 with Project-Specific Rules

  

* Code MUST follow PEP 8.

* Line length MUST be 100 characters.

* Strings MUST use double quotes by default.

* Trailing commas MUST be used in multiline collections and argument lists.

* Type hints MUST be present on all public functions and methods.

  

```python

def create_user(

email: str,

name: str,

is_admin: bool = False,

) -> User:

...

```

  

## 4.2 Type Hints and `TYPE_CHECKING`

  

* All public function arguments and return values MUST have type hints.

* Class attributes MUST be annotated.

* `from typing import TYPE_CHECKING` MUST NOT be used. Type issues MUST be solved at their root (correct imports, stubs, or architecture), not hidden behind type-check-only imports.

  

```python

# ❌ Forbidden

from typing import TYPE_CHECKING

  

if TYPE_CHECKING:

from project.core.models import User

  
  

# ✅ Required

from project.core.models import User

```

  

---

  

# 5. Data Models and Validation (Pydantic v2)

  

## 5.1 Pydantic Models

  

* Pydantic v2 MUST be used for data validation and serialization where structured validation is needed (e.g. API payloads, configuration, external data).

  

```python

from datetime import datetime

from decimal import Decimal

  

from pydantic import BaseModel, Field, EmailStr

  
  

class Product(BaseModel):

id: int

name: str = Field(min_length=1, max_length=255)

price: Decimal = Field(gt=0, decimal_places=2)

created_at: datetime

is_active: bool = True

email: EmailStr | None = None

```

  

## 5.2 External Data Validation

  

* All external inputs (HTTP bodies, query params, environment variables, message payloads) MUST be validated.

* Plain dicts from untrusted sources MUST NOT be used directly without validation.

  

---

  

# 6. Configuration Management

  

## 6.1 Centralized Settings

  

* Configuration MUST be loaded via a single settings module using `pydantic_settings`.

  

```python

from functools import lru_cache

  

from pydantic_settings import BaseSettings

  
  

class Settings(BaseSettings):

app_name: str = "MyApp"

debug: bool = False

database_url: str

redis_url: str = "redis://localhost:6379"

max_connections: int = 100

  

model_config = {

"env_file": ".env",

"env_file_encoding": "utf-8",

}

  
  

@lru_cache

def get_settings() -> Settings:

return Settings()

```

  

* Code MUST NOT read `os.environ` directly across the codebase; environment access MUST go through the settings module.

  

```python

# ❌ Forbidden

os.getenv("DATABASE_URL")

  

# ✅ Required

from project.config import get_settings

  

settings = get_settings()

settings.database_url

```

  

---

  

# 7. Error Handling

  

## 7.1 Custom Exceptions

  

* Domain-specific exceptions MUST be defined instead of using bare `Exception`.

  

```python

class ProjectError(Exception):

"""Base exception for project-level errors."""

  
  

class UserNotFoundError(ProjectError):

"""Raised when a user cannot be found."""

  
  

class PaymentError(ProjectError):

"""Raised when a payment fails."""

```

  

## 7.2 No Blanket `except Exception` Without Re-raise

  

* Blanket `except Exception` MUST NOT swallow errors.

* When catching, code MUST log and either:

  

* transform to a domain error, or

* re-raise.

  

```python

# ❌ Forbidden: swallow and hide error

try:

process_payment(data)

except Exception:

return {"status": "ok"} # hides real problem

  
  

# ✅ Required: log and expose controlled status

try:

process_payment(data)

except PaymentError as exc:

logger.warning("Payment failed", extra={"error": str(exc)})

return {"status": "payment_failed", "error": str(exc)}

```

  

## 7.3 Fail Fast Logic

  

* Branches that silently substitute dummy defaults in error conditions MUST NOT be used unless explicitly documented as “graceful degradation” behavior.

  

---

  

# 8. Logging and Observability

  

## 8.1 Logging

  

* Structured logging MUST be used (e.g. `structlog` or structured `logging`).

* Log MUST use the following: `format="%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s"`

* `print` MUST NOT be used for logging in production code.

  

```python

import logging

  

logger = logging.getLogger(__name__)

  
  

def process_user(user_id: str) -> None:

logger.info("Processing user", extra={"user_id": user_id})

```

  

## 8.2 Error Logging

  

* All errors that reach top-level handlers (API endpoints, CLI commands, background workers) MUST be logged with error level and include relevant context (but no secrets).

  

---

  

# 9. Testing Strategy

  

## 9.1 Coverage and Requirements

  

* Minimum test coverage MUST be **80%**.

* New code MUST NOT be merged if it reduces coverage below 80%.

  

## 9.2 TDD Preference

  

* Tests SHOULD be written before implementation, especially for core business logic.

* At minimum, tests MUST be added with new features or bug fixes.

  

## 9.3 Test Layout

  

* Tests MUST be co-located with the code they test, inside `tests/` directories as shown in the architecture section.

* `conftest.py` MUST be used for shared fixtures.

  

```python

# src/project/features/user_management/tests/test_handlers.py

def test_user_can_update_email(user_factory) -> None:

user = user_factory(email="old@example.com")

update_user_email(user, "new@example.com")

assert user.email == "new@example.com"

```

  

## 9.4 Test Rules

  

* `pytest` MUST be used.

* `unittest` style MUST NOT be introduced for new tests.

* Tests MUST NOT rely on external services; external dependencies MUST be mocked.

  

---

  

# 10. Security Requirements

  

## 10.1 Secrets and Credentials

  

* Secrets MUST NOT be committed to the repository.

* Secrets MUST come from environment variables, secret stores, or configuration services.

  

## 10.2 Database and External Services

  

* All database access MUST use parameterized queries or ORM methods that generate such queries.

* User input MUST NOT be concatenated into SQL strings.

  

```python

# ❌ Forbidden

cursor.execute(f"SELECT * FROM users WHERE email = '{email}'")

  
  

# ✅ Required

cursor.execute("SELECT * FROM users WHERE email = %s", (email,))

```

  

## 10.3 Input Validation

  

* All inbound data from clients MUST be validated with Pydantic models or explicit validators before use.

  

---

  

# 11. Performance Guidelines

  

## 11.1 Measurement Before Optimization

  

* Performance optimizations MUST be based on measurement (profiling) rather than speculation.

* Tools such as `cProfile`, `py-spy`, or equivalent MUST be used before significant optimization work.

  

## 11.2 Caching and Resource Use

  

* Expensive pure functions MAY use `functools.lru_cache`.

* For large datasets, iterators and generators MUST be preferred over loading everything into memory.

  

---

  

# 12. Containers and CI

  

## 12.1 `.dockerignore` and `.containerignore`

  

* Both `.dockerignore` and `.containerignore` MUST exist and MUST exclude tests and development artifacts from production images.

  

Example:

  

```text

**/tests/

**/test_*.py

__pycache__/

.pytest_cache/

.coverage

htmlcov/

*.log

*.tmp

.git

```

  

## 12.2 Container Build Rules

  

* Images MUST NOT `COPY . .` blindly.

* Only required code, configuration, and assets MUST be copied.

  

```dockerfile

WORKDIR /app

  

COPY pyproject.toml uv.lock ./

COPY src ./src

  

RUN uv sync --no-dev

  

CMD ["uv", "run", "python", "-m", "project.main"]

```

  

## 12.3 CI Pipeline

  

A CI job for Python MUST at least:

  

1. Install dependencies with `uv sync`.

2. Run `ruff format --check` (or equivalent).

3. Run `ruff check`.

4. Run `pyright`.

5. Run `pytest` with coverage and enforce ≥80%.

  

---

  

# 13. Git Workflow and Search Commands

  

## 13.1 Branching

  

* Branch names MUST follow:

  

* `main` — production-ready

* `dev` — integration

* `feat/*` — features

* `fix/*` — bug fixes

* `docs/*` — documentation

* `refactor/*` — refactors

* `test/*` — test-specific changes

  

## 13.2 Commit Messages

  

* Commits MUST follow a semantic style:

  

```text

feat(auth): add jwt-based login

fix(api): handle invalid pagination params

docs(readme): update setup instructions

```

  

## 13.3 Search Commands

  

* `rg` (ripgrep) MUST be used for searching.

* `grep` and `find` MUST NOT be used in scripts or documented workflows.

  

```bash

rg "pattern"

rg --files -g "*.py"

```

  

---

  

# 14. AI Assistant Rules

  

The AI assistant MUST:

  

* Obey all rules in this document.

* Inspect existing modules and patterns before generating new code.

* Prefer extending existing functions, classes, and patterns over introducing parallel ones.

* Always add or update tests when adding or changing behavior.

* Avoid new dependencies if equivalent functionality exists in the project or standard library.

  

The AI assistant MUST NOT:

  

* Introduce relative imports.

* Use `from typing import TYPE_CHECKING`.

* Add magic strings instead of using constants.

* Add uncovered (untested) critical-path code.

* Reduce type or linting strictness.

  

---

  

# 15. Pre-Commit Checklist

  

Before committing, ALL of the following MUST be true:

  

* [ ] `uv sync` has been run and `pyproject.toml` / lockfile are up to date

* [ ] `uv run ruff format .` has been run (and/or `ruff format --check` passes)

* [ ] `uv run ruff check .` passes with no errors

* [ ] `uv run pyright src/` passes with no errors

* [ ] `uv run pytest` passes

* [ ] Coverage is ≥80% and new code is covered

* [ ] No `print` statements in production code

* [ ] No relative imports

* [ ] No magic strings where constants exist

* [ ] No secrets added to the repository

* [ ] New public functions/classes have docstrings

* [ ] New external data flows use validation (Pydantic or equivalent)

  

---

  

This document is the single source of truth for Python development standards in this repository.

All generated and handwritten code MUST comply with these rules.