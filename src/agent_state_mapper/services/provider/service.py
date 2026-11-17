from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...db import SQLConnectionManager
    from ...models.intra import TenantSelection
    from .query_worker import ProviderQueryWorker
    from ...cli import CLI
    from ...models.intra import Provider

from ...models.intra import ProviderResult, StateResult
from ...enums.db_name import DB_NAME


class ProviderService:

    def __init__(self, cli: CLI, db: SQLConnectionManager, worker: ProviderQueryWorker):
        self.cli = cli
        self.db = db
        self.worker = worker

    def fetch_call_providers(self, tenant_selection: TenantSelection) -> ProviderResult:
        tenant = tenant_selection.tenant
        node = tenant_selection.node
        self.db.connect(node, DB_NAME.MT)
        try:
            self.cli.print_status(f"Querying {tenant.name} for ACDs Providers.")
            acd_providers = self.worker.acd_providers(self.db, tenant_selection)
            self.cli.print_status(f"Receieved {len(acd_providers)} ACDs.")

            self.cli.print_status(f"Querying {tenant.name} for IntraCall Provider.")
            intra_call_provider = self.worker.intra_call_provider(
                self.db, tenant_selection
            )

            self.cli.print_status(
                f"Receieved {"1" if intra_call_provider is not None else "0"} IntraCall Provider."
            )

            return ProviderResult(
                acd_providers=acd_providers, intra_call_provider=intra_call_provider
            )
        finally:
            self.db.disconnect()

    def fetch_intra_call_states(
        self,
        tenant_selection: TenantSelection,
        intra_call_provider: Provider,
    ) -> StateResult:
        tenant = tenant_selection.tenant
        node = tenant_selection.node
        self.db.connect(node, DB_NAME.MT)
        try:

            self.cli.print_status(
                f"Querying {tenant.name} for IntraCall Provider Mapped States. "
            )
            mapped_states = self.worker.fetch_intra_call_provider_state_config(
                self.db, tenant_selection, intra_call_provider
            )

            self.cli.print_status(
                f"Receieved {len(mapped_states)} States from IntraCall Provider."
            )

            return StateResult(provider=intra_call_provider, states=mapped_states)
        finally:
            self.db.disconnect()
