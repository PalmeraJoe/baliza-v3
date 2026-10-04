from datetime import UTC, datetime

from sqlalchemy.orm import Session

from baliza.domain.enums import DataQualityFacet
from baliza.domain.ids import ObservationId
from baliza.domain.observation import Observation
from baliza.domain.quality import DataQuality
from baliza.infrastructure.persistence.models import Base, make_engine
from baliza.infrastructure.persistence.repositories import SqlObservationRepository

NOW = datetime(2026, 9, 30, 12, 0, tzinfo=UTC)


def test_observation_roundtrip_sqlite() -> None:
    engine = make_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        repo = SqlObservationRepository(session)
        obs = Observation(
            id=ObservationId(),
            variable="sst",
            unit="degC",
            observed_at=NOW,
            processed_at=NOW,
            quality=DataQuality(facet=DataQualityFacet.VALID, score=0.8),
            value=28.1,
            spatial_ref="zone-a",
        )
        repo.add(obs)
        session.commit()
        loaded = repo.get(obs.id)
        assert loaded is not None
        assert loaded.variable == "sst"
        assert loaded.value == 28.1
        assert loaded.quality.facet is DataQualityFacet.VALID
