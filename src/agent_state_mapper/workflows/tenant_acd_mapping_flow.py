from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..cli import CLI
    from ..models.intra import Provider
    from ..services.provider import ProviderResolver
    from ..models.intra import StateResult
    from ..services.mapping import StateMappingAnalyzer


from ..models.intra import TenantSelection
from ..errors import TenantSelectionError


from ..services.provider import ProviderService
from ..services.elk import ELKService
from ..models.states import ProviderAnalysis
from ..errors import UnresolvedProviderError


class TenantACDMappingFlow:

    def __init__(
        self,
        cli: CLI,
        provider_service: ProviderService,
        tenant_selection: TenantSelection,
        elk_service: ELKService,
        provider_resolver: ProviderResolver,
        state_mapping_analyzer: StateMappingAnalyzer,
    ):

        self._cli = cli
        self._provider_service = provider_service
        self._tenant_selection = tenant_selection
        self._elk_service = elk_service
        self._provider_resolver = provider_resolver
        self._state_mapping_analyzer = state_mapping_analyzer

    def run(self) -> None:
        if self._tenant_selection is None:
            raise TenantSelectionError("Select a tenant first.")

        call_providers = self._provider_service.fetch_call_providers(
            tenant_selection=self._tenant_selection
        )
        print(call_providers)

        intra_call_mappings = None
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
            call_providers.acd_providers, intra_call_mappings
        )

        providers_state_mapping = self._get_state_mapping_analyses(providers_analysis)

    def _get_state_mapping_analyses(self, providers_analysis: list[ProviderAnalysis]):
        return [
            self._state_mapping_analyzer.analyze(provider_analysis)
            for provider_analysis in providers_analysis
        ]

    def _get_distinct_states_call_providers(
        self, call_providers: list[Provider], intra_call_mappings: StateResult
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
            try:
                provider_resolution = self._provider_resolver.resolve(
                    provider=provider, observed_states=observed_states
                )
            except UnresolvedProviderError:
                msg = f"Skipping {provider.name} - {provider.guid} no matching provider configuration could be resolved from states or name."
                self._cli.print_error(msg)
                continue

            providers_result.append(
                ProviderAnalysis(
                    provider=provider,
                    intra_call_provider=intra_call_mappings,
                    observed_states=observed_states,
                    resolution=provider_resolution,
                )
            )
        return providers_result
