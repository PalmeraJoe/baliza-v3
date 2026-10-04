"""Phase 3 initial schema — generated from SQLAlchemy metadata at revision time."""

from alembic import op
import sqlalchemy as sa

revision = "0001_phase3"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "observations",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("variable", sa.String(128), nullable=False),
        sa.Column("unit", sa.String(32), nullable=False),
        sa.Column("value", sa.Float(), nullable=True),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("quality_facet", sa.String(32), nullable=False),
        sa.Column("quality_score", sa.Float(), nullable=True),
        sa.Column("spatial_ref", sa.String(256), nullable=True),
    )
    op.create_table(
        "indicator_values",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("indicator_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("indicator_version_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("indicator_version", sa.String(32), nullable=False),
        sa.Column("computed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("unit", sa.String(32), nullable=False),
        sa.Column("value", sa.Float(), nullable=True),
        sa.Column("quality_facet", sa.String(32), nullable=False),
        sa.Column("source_observation_ids", sa.JSON(), nullable=False),
        sa.Column("notes", sa.JSON(), nullable=False),
    )
    op.create_table(
        "rule_versions",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("rule_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("version", sa.String(32), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("operator", sa.String(8), nullable=False),
        sa.Column("threshold_name", sa.String(64), nullable=False),
        sa.Column("thresholds", sa.JSON(), nullable=False),
        sa.Column("severity_if_triggered", sa.String(16), nullable=False),
        sa.Column("evaluator_engine_id", sa.String(64), nullable=False),
    )
    op.create_table(
        "rule_evaluations",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("rule_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("rule_version_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("rule_version", sa.String(32), nullable=False),
        sa.Column("evaluated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("outcome", sa.String(32), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("thresholds_applied", sa.JSON(), nullable=False),
        sa.Column("input_snapshot", sa.JSON(), nullable=False),
        sa.Column("input_indicator_value_ids", sa.JSON(), nullable=False),
        sa.Column("evaluator_engine_id", sa.String(64), nullable=False),
    )
    op.create_table(
        "evidence_items",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("kind", sa.String(32), nullable=False),
        sa.Column("epistemic_label", sa.String(32), nullable=False),
        sa.Column("referenced_type", sa.String(64), nullable=False),
        sa.Column("referenced_id", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("content_hash", sa.String(64), nullable=True),
        sa.Column("narrative", sa.Text(), nullable=True),
    )
    op.create_table(
        "evidence_packages",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("subject", sa.String(256), nullable=False),
        sa.Column("item_ids", sa.JSON(), nullable=False),
        sa.Column("assembled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("gaps", sa.JSON(), nullable=False),
        sa.Column("incomplete", sa.Boolean(), nullable=False),
    )
    op.create_table(
        "alerts",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("severity", sa.String(16), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("alerted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("evidence_package_id", sa.Uuid(as_uuid=True), sa.ForeignKey("evidence_packages.id")),
        sa.Column("rule_evaluation_ids", sa.JSON(), nullable=False),
        sa.Column("history", sa.JSON(), nullable=False),
        sa.Column("health", sa.String(32), nullable=False),
    )
    op.create_table(
        "dss_packages",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("opened_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
    )
    op.create_table(
        "dss_context_snapshots",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("dss_package_id", sa.Uuid(as_uuid=True), sa.ForeignKey("dss_packages.id")),
        sa.Column("frozen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("object_key", sa.String(256), nullable=True),
    )
    op.create_table(
        "decisions",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("actor_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column(
            "dss_context_snapshot_id",
            sa.Uuid(as_uuid=True),
            sa.ForeignKey("dss_context_snapshots.id"),
            nullable=False,
        ),
        sa.Column("dss_package_id", sa.Uuid(as_uuid=True), sa.ForeignKey("dss_packages.id")),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("justification", sa.Text(), nullable=False),
        sa.Column("selected_option", sa.String(256), nullable=False),
        sa.Column("snapshot_hash", sa.String(64), nullable=False),
    )
    op.create_table(
        "audit_events",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("action", sa.String(64), nullable=False),
        sa.Column("entity_type", sa.String(64), nullable=False),
        sa.Column("entity_id", sa.String(64), nullable=False),
        sa.Column("actor_id", sa.Uuid(as_uuid=True), nullable=True),
        sa.Column("system_component", sa.String(64), nullable=True),
        sa.Column("entity_version", sa.String(64), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("context", sa.JSON(), nullable=False),
    )


def downgrade() -> None:
    for table in [
        "audit_events",
        "decisions",
        "dss_context_snapshots",
        "dss_packages",
        "alerts",
        "evidence_packages",
        "evidence_items",
        "rule_evaluations",
        "rule_versions",
        "indicator_values",
        "observations",
    ]:
        op.drop_table(table)
