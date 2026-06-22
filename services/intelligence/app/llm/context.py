from contextvars import ContextVar

auth_token_var: ContextVar[str | None] = ContextVar("auth_token", default=None)