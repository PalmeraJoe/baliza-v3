"""Phase 5: canonical links, published indicator immutability."""

from alembic import op
import sqlalchemy as sa

revision = "0004_phase5"
down_revision = "0003_phase4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "indicator_value_observations",
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "rule_evaluation_inputs",
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_foreign_key(
        "fk_indicator_values_version",
        "indicator_values",
        "indicator_versions",
        ["indicator_version_id"],
        ["id"],
    )
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute(
            """
            INSERT INTO indicator_value_observations (indicator_value_id, observation_id, position)
            SELECT iv.id, elem::uuid, ord - 1
            FROM indicator_values iv
            CROSS JOIN LATERAL jsonb_array_elements_text(iv.source_observation_ids::jsonb)
              WITH ORDINALITY AS t(elem, ord)
            ON CONFLICT DO NOTHING;
            INSERT INTO rule_evaluation_inputs (rule_evaluation_id, indicator_value_id, position)
            SELECT re.id, elem::uuid, ord - 1
            FROM rule_evaluations re
            CROSS JOIN LATERAL jsonb_array_elements_text(re.input_indicator_value_ids::jsonb)
              WITH ORDINALITY AS t(elem, ord)
            ON CONFLICT DO NOTHING;
            INSERT INTO evidence_package_items (package_id, item_id, position)
            SELECT ep.id, elem::uuid, ord - 1
            FROM evidence_packages ep
            CROSS JOIN LATERAL jsonb_array_elements_text(ep.item_ids::jsonb)
              WITH ORDINALITY AS t(elem, ord)
            ON CONFLICT DO NOTHING;
            """
        )
    else:
        op.execute(
            """
            INSERT OR IGNORE INTO indicator_value_observations (indicator_value_id, observation_id, position)
            SELECT indicator_values.id, json_each.value, json_each.key
            FROM indicator_values, json_each(indicator_values.source_observation_ids);
            INSERT OR IGNORE INTO rule_evaluation_inputs (rule_evaluation_id, indicator_value_id, position)
            SELECT rule_evaluations.id, json_each.value, json_each.key
            FROM rule_evaluations, json_each(rule_evaluations.input_indicator_value_ids);
            INSERT OR IGNORE INTO evidence_package_items (package_id, item_id, position)
            SELECT evidence_packages.id, json_each.value, json_each.key
            FROM evidence_packages, json_each(evidence_packages.item_ids);
            """
        )
    op.create_table(
        "alert_evaluations",
        sa.Column("alert_id", sa.Uuid(as_uuid=True), sa.ForeignKey("alerts.id"), primary_key=True),
        sa.Column(
            "rule_evaluation_id",
            sa.Uuid(as_uuid=True),
            sa.ForeignKey("rule_evaluations.id"),
            primary_key=True,
        ),
        sa.Column("position", sa.Integer(), nullable=False),
    )
    if bind.dialect.name == "postgresql":
        op.execute(
            """
            INSERT INTO alert_evaluations (alert_id, rule_evaluation_id, position)
            SELECT a.id, elem::uuid, ord - 1
            FROM alerts a
            CROSS JOIN LATERAL jsonb_array_elements_text(a.rule_evaluation_ids::jsonb)
              WITH ORDINALITY AS t(elem, ord)
            ON CONFLICT DO NOTHING;
            """
        )
    else:
        op.execute(
            """
            INSERT OR IGNORE INTO alert_evaluations (alert_id, rule_evaluation_id, position)
            SELECT alerts.id, json_each.value, json_each.key
            FROM alerts, json_each(alerts.rule_evaluation_ids);
            """
        )
    op.drop_column("indicator_values", "source_observation_ids")
    op.drop_column("rule_evaluations", "input_indicator_value_ids")
    op.drop_column("evidence_packages", "item_ids")
    op.drop_column("alerts", "rule_evaluation_ids")
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute(
            """
            CREATE OR REPLACE FUNCTION baliza_reject_published_indicator_write()
            RETURNS trigger LANGUAGE plpgsql AS $$
            BEGIN
              IF TG_OP = 'DELETE' AND OLD.status = 'published' THEN
                RAISE EXCEPTION 'published IndicatorVersion cannot be deleted';
              END IF;
              IF TG_OP = 'UPDATE' AND OLD.status = 'published' THEN
                RAISE EXCEPTION 'published IndicatorVersion cannot be updated';
              END IF;
              RETURN COALESCE(NEW, OLD);
            END;
            $$;
            CREATE TRIGGER indicator_versions_published_immutable
            BEFORE UPDATE OR DELETE ON indicator_versions
            FOR EACH ROW EXECUTE FUNCTION baliza_reject_published_indicator_write();
            """
        )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("DROP TRIGGER IF EXISTS indicator_versions_published_immutable ON indicator_versions")
        op.execute("DROP FUNCTION IF EXISTS baliza_reject_published_indicator_write()")
    op.add_column("alerts", sa.Column("rule_evaluation_ids", sa.JSON(), nullable=False, server_default="[]"))
    op.add_column("evidence_packages", sa.Column("item_ids", sa.JSON(), nullable=False, server_default="[]"))
    op.add_column("rule_evaluations", sa.Column("input_indicator_value_ids", sa.JSON(), nullable=False, server_default="[]"))
    op.add_column("indicator_values", sa.Column("source_observation_ids", sa.JSON(), nullable=False, server_default="[]"))
    op.drop_table("alert_evaluations")
    op.drop_constraint("fk_indicator_values_version", "indicator_values", type_="foreignkey")
    op.drop_column("rule_evaluation_inputs", "position")
    op.drop_column("indicator_value_observations", "position")
