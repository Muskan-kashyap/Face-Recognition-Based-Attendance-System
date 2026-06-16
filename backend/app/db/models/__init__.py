from app.db.models.base import Base, NVARCHAR

# Load all model definitions so Base.metadata is populated.
# IMPORTANT: import must use a single, consistent module path
# (app.*) to avoid SQLAlchemy MetaData re-definition errors.
import app.db.models.all_models  # noqa: F401

__all__ = ["Base", "NVARCHAR"]

