"""Environment configuration and validation."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Validated environment configuration."""

    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: str
    database_url: str = ""
    server_port: int = 8080

    @classmethod
    def from_env(cls) -> "Settings":
        """Load and validate settings from environment variables."""
        required = {
            "SUPABASE_URL": os.getenv("SUPABASE_URL"),
            "SUPABASE_ANON_KEY": os.getenv("SUPABASE_ANON_KEY"),
            "SUPABASE_SERVICE_ROLE_KEY": os.getenv("SUPABASE_SERVICE_ROLE_KEY"),
        }

        missing = [k for k, v in required.items() if not v]
        if missing:
            raise EnvironmentError(
                f"Missing required environment variables: {', '.join(missing)}"
            )

        return cls(
            supabase_url=required["SUPABASE_URL"],
            supabase_anon_key=required["SUPABASE_ANON_KEY"],
            supabase_service_role_key=required["SUPABASE_SERVICE_ROLE_KEY"],
            database_url=os.getenv("DATABASE_URL", ""),
            server_port=int(os.getenv("SERVER_PORT", "8080")),
        )


settings = Settings.from_env()
