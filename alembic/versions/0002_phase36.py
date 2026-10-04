"""Phase 3.6 integrity constraints: unique rule versions, evidence FKs, insert-only triggers."""

from alembic import op
import sqlalchemy as sa

revision = "0002_phase36"
down_revision = "0001_phase3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_unique_constraint("uq_rule_version_identity", "rule_versions", ["rule_id", "version"])
    op.create_foreign_key(
        "fk_rule_evaluations_rule_version",
        "rule_evaluations",
        "rule_versions",
        ["rule_version_id"],
        ["id"],
    )
    op.alter_column("alerts", "evidence_package_id", nullable=False)
    op.add_column("alerts", sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True))
    op.create_table(
        "indicator_value_observations",
        sa.Column("indicator_value_id", sa.Uuid(as_uuid=True), sa.ForeignKey("indicator_values.id"), primary_key=True),
        sa.Column("observation_id", sa.Uuid(as_uuid=True), sa.ForeignKey("observations.id"), primary_key=True),
    )
    op.create_table(
        "rule_evaluation_inputs",
        sa.Column("rule_evaluation_id", sa.Uuid(as_uuid=True), sa.ForeignKey("rule_evaluations.id"), primary_key=True),
        sa.Column("indicator_value_id", sa.Uuid(as_uuid=True), sa.ForeignKey("indicator_values.id"), primary_key=True),
    )
    op.create_table(
        "evidence_package_items",
        sa.Column("package_id", sa.Uuid(as_uuid=True), sa.ForeignKey("evidence_packages.id"), primary_key=True),
        sa.Column("item_id", sa.Uuid(as_uuid=True), sa.ForeignKey("evidence_items.id"), primary_key=True),
        sa.Column("position", sa.Integer(), nullable=False),
    )
    op.create_table(
        "actions",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("decision_id", sa.Uuid(as_uuid=True), sa.ForeignKey("decisions.id"), nullable=False),
        sa.Column("acted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("recorded_by", sa.Uuid(as_uuid=True), nullable=True),
        sa.Column("status", sa.String(32), nullable=False),
    )
    op.create_table(
        "outcomes",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("action_id", sa.Uuid(as_uuid=True), sa.ForeignKey("actions.id"), nullable=False),
        sa.Column("decision_id", sa.Uuid(as_uuid=True), sa.ForeignKey("decisions.id"), nullable=False),
        sa.Column("observed_outcome_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("notes", sa.Text(), nullable=False),
    )
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute(
            """
            CREATE OR REPLACE FUNCTION baliza_reject_snapshot_write()
            RETURNS trigger LANGUAGE plpgsql AS $$
            BEGIN
              RAISE EXCEPTION 'dss_context_snapshots are insert-only';
            END;
            $$;
            CREATE TRIGGER dss_context_snapshots_insert_only
            BEFORE UPDATE OR DELETE ON dss_context_snapshots
            FOR EACH ROW EXECUTE FUNCTION baliza_reject_snapshot_write();

            CREATE OR REPLACE FUNCTION baliza_reject_published_rule_write()
            RETURNS trigger LANGUAGE plpgsql AS $$
            BEGIN
              IF TG_OP = 'DELETE' AND OLD.status = 'published' THEN
                RAISE EXCEPTION 'published RuleVersion cannot be deleted';
              END IF;
              IF TG_OP = 'UPDATE' AND OLD.status = 'published' THEN
                RAISE EXCEPTION 'published RuleVersion cannot be updated';
              END IF;
              RETURN COALESCE(NEW, OLD);
            END;
            $$;
            CREATE TRIGGER rule_versions_published_immutable
            BEFORE UPDATE OR DELETE ON rule_versions
            FOR EACH ROW EXECUTE FUNCTION baliza_reject_published_rule_write();
            """
        )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("DROP TRIGGER IF EXISTS rule_versions_published_immutable ON rule_versions")
        op.execute("DROP TRIGGER IF EXISTS dss_context_snapshots_insert_only ON dss_context_snapshots")
        op.execute("DROP FUNCTION IF EXISTS baliza_reject_published_rule_write()")
        op.execute("DROP FUNCTION IF EXISTS baliza_reject_snapshot_write()")
    op.drop_table("outcomes")
    op.drop_table("actions")
    op.drop_table("evidence_package_items")
    op.drop_table("rule_evaluation_inputs")
    op.drop_table("indicator_value_observations")
    op.drop_column("alerts", "reviewed_at")
    op.alter_column("alerts", "evidence_package_id", nullable=True)
    op.drop_constraint("fk_rule_evaluations_rule_version", "rule_evaluations", type_="foreignkey")
    op.drop_constraint("uq_rule_version_identity", "rule_versions", type_="unique")
