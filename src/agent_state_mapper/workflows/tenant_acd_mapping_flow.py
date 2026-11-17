from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..cli import CLI

    # from ..services.tenant_cleanup_audit import (
    #     TenantCleanUpAuditService,
    #     TenantCleanupAuditSheetService,
    # )


from ..models.intra import TenantSelection
from ..errors import TenantSelectionError


from ..services.provider import ProviderService


class TenantACDMappingFlow:

    def __init__(
        self,
        cli: CLI,
        provider_service: ProviderService,
        tenant_selection: TenantSelection,
    ):

        self._cli = cli
        self._provider_service = provider_service
        self._tenant_selection = tenant_selection

    def run(self) -> None:
        if self._tenant_selection is None:
            raise TenantSelectionError("Select a tenant first.")

        call_providers = self._provider_service.fetch_call_providers(
            tenant_selection=self._tenant_selection
        )
        print(call_providers)

        if call_providers.intra_call_provider is not None:
            intra_call_mappings = self._provider_service.fetch_intra_call_states(
                tenant_selection=self._tenant_selection,
                intra_call_provider=call_providers.intra_call_provider,
            )
            print(intra_call_mappings)
        else:
            self._cli.print_info(
                "Skipping IntraCall Mappings as couldnot find IntraCall Provider."
            )
