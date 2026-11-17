from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .dal import ProviderDAL
    from ...db import SQLConnectionManager
    from ...cli import CLI
    from ...models.intra import TenantSelection

from ...models.intra import Provider, State
from ...enums import PROVIDER_CATEGORY


class ProviderQueryWorker:

    def __init__(self, cli: CLI, dal: ProviderDAL):
        self.cli = cli
        self.dal = dal

    def acd_providers(
        self, db: SQLConnectionManager, tenant_selection: TenantSelection
    ) -> list[Provider]:
        acd_providers = []
        tenant = tenant_selection.tenant

        for guid, name, underscored_guid, provider_type in self.dal.fetch_acd_providers(
            db, tenant.tenant_id
        ):

            acd_providers.append(
                Provider(
                    name=name,
                    guid=guid,
                    guid_underscored=underscored_guid,
                    provider_category=PROVIDER_CATEGORY.ACD,
                    provider_type=provider_type,
                )
            )
        return acd_providers

    def intra_call_provider(
        self, db: SQLConnectionManager, tenant_selection: TenantSelection
    ) -> Provider | None:
        intra_call_provider = None
        tenant = tenant_selection.tenant
        row = self.dal.fetch_intra_call_provider(db, tenant.tenant_id)
        if not row:
            return None

        guid, name, underscored_guid, provider_type = row

        intra_call_provider = Provider(
            name=name,
            guid=guid,
            guid_underscored=underscored_guid,
            provider_category=PROVIDER_CATEGORY.INTRA_CALL,
            provider_type=provider_type,
        )

        return intra_call_provider

    def fetch_intra_call_provider_state_config(
        self,
        db: SQLConnectionManager,
        tenant_selection: TenantSelection,
        intra_call_provider: Provider,
    ) -> list[State]:
        tenant = tenant_selection.tenant
        row = self.dal.fetch_intra_call_state_config(
            db, tenant.tenant_id, intra_call_provider.guid
        )
        if not row:
            return []

        state_mappings = row

        return self._parse_state_mappings(state_mappings)

    def _parse_state_mappings(self, state_mappings: str) -> list[tuple[str, State]]:
        mappings = []

        for entry in state_mappings.split("|"):
            if not entry:
                continue

            _, acd_state, original_mapping = entry.split(":", 2)
            state, _, aux = acd_state.partition(".")

            mappings.append(
                State(
                    state=state,
                    aux=aux,
                    original_mapping=original_mapping,
                )
            )

        return mappings
