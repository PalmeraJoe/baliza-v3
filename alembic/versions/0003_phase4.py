"""Phase 4: observation metadata, action type, lookup indexes."""

from alembic import op
import sqlalchemy as sa

revision = "0003_phase4"
down_revision = "0002_phase36"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "indicator_versions",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("indicator_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("version", sa.String(32), nullable=False),
        sa.Column("unit", sa.String(32), nullable=False),
        sa.Column("formula_kind", sa.String(64), nullable=False),
        sa.Column("baseline", sa.Float(), nullable=True),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("input_variable", sa.String(128), nullable=True),
        sa.UniqueConstraint("indicator_id", "version", name="uq_indicator_version_identity"),
    )
    op.add_column("observations", sa.Column("metadata", sa.JSON(), nullable=False, server_default="{}"))
    op.add_column(
        "actions",
        sa.Column("action_type", sa.String(64), nullable=False, server_default="recorded_step"),
    )
    op.add_column("actions", sa.Column("metadata", sa.JSON(), nullable=False, server_default="{}"))
    op.create_index("ix_observations_observed_at", "observations", ["observed_at"])
    op.create_index("ix_alerts_status", "alerts", ["status"])


def downgrade() -> None:
    op.drop_table("indicator_versions")
    op.drop_index("ix_alerts_status", table_name="alerts")
    op.drop_index("ix_observations_observed_at", table_name="observations")
    op.drop_column("actions", "metadata")
    op.drop_column("actions", "action_type")
    op.drop_column("observations", "metadata")
