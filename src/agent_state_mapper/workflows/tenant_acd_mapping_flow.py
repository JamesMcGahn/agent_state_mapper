from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..cli import CLI
    from ..models.intra import Provider
    from ..services.provider import ProviderResolver


from ..models.intra import TenantSelection
from ..errors import TenantSelectionError


from ..services.provider import ProviderService
from ..services.elk import ELKService
from ..models.states import ProviderAnalysis


class TenantACDMappingFlow:

    def __init__(
        self,
        cli: CLI,
        provider_service: ProviderService,
        tenant_selection: TenantSelection,
        elk_service: ELKService,
        provider_resolver: ProviderResolver,
    ):

        self._cli = cli
        self._provider_service = provider_service
        self._tenant_selection = tenant_selection
        self._elk_service = elk_service
        self._provider_resolver = provider_resolver

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
                "Skipping IntraCall Mappings as could not find IntraCall Provider."
            )

        providers_analysis = self._get_distinct_states_call_providers(
            call_providers.acd_providers
        )

    def _get_distinct_states_call_providers(
        self, call_providers: list[Provider]
    ) -> list[ProviderAnalysis]:
        providers_result = []

        for index, provider in enumerate(call_providers, start=1):
            self._cli.print_status(
                f"Provider {index}/{len(call_providers)}: {provider.name}"
            )
            observed_states = self._elk_service.distinct_acd_states(
                tenant_selection=self._tenant_selection,
                provider_instance=provider,
                day_range=7,
            )

            provider_resolution = self._provider_resolver.resolve(
                provider=provider, observed_states=observed_states
            )

            providers_result.append(
                ProviderAnalysis(
                    provider=provider,
                    observed_states=observed_states,
                    resolution=provider_resolution,
                )
            )
        return providers_result
