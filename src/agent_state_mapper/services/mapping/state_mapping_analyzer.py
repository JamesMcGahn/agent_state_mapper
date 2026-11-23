from __future__ import annotations

from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from ...cli import CLI
    from ...models.states import ProviderAnalysis
    from ...models.config import StateSettings
    from ...models.states import ProviderResolution

from ...enums import V11_STATE, MAPPING_SOURCE

from ...models.mapping import StateMappingResult, ProviderMappingResult
from ...errors import UnresolvedProviderError
from ...models.intra import State


class StateMappingAnalyzer:

    def __init__(self, cli: CLI, get_configs: Callable[[], StateSettings]):
        self._cli = cli
        self._get_configs = get_configs
        self._states_mapped: dict[tuple[str, str], StateMappingResult] = {}

    def reset_mapping_cache(self):
        self._states_mapped = {}

    def analyze(self, provider_analysis: ProviderAnalysis) -> ProviderMappingResult:
        self.reset_mapping_cache()
        resolution = provider_analysis.resolution
        self._cli.print_info(
            f"Starting State Analyzation for {provider_analysis.provider.name}"
        )

        if resolution is None or resolution.config is None:
            msg = f"Cannot map states for unresolved provider: {provider_analysis.provider.name}"
            self._cli.print_error(msg)
            raise UnresolvedProviderError(msg)
        self._map_call_analysis_provider(provider_analysis, resolution)
        self._map_provider_config_state_aux_mappings(resolution)
        self._map_observed_states_on_common_aux_exact(provider_analysis)

        self._cli.print_status(
            f"Completed State Analyzation for {provider_analysis.provider.name}"
        )
        return ProviderMappingResult(
            analysis=provider_analysis,
            mappings=self._collect_states(),
        )

    def _collect_states(self) -> list[StateMappingResult]:
        return list(self._states_mapped.values())

    def _map_provider_config_state_aux_mappings(
        self, provider_resolution: ProviderResolution
    ):
        provider_config = provider_resolution.config
        for (state_name, aux), target in provider_config.state_aux_mappings.items():
            target = self.convert_state_str_to_v11_state(target)
            state_aux_pair = (state_name, aux)
            if state_aux_pair in self._states_mapped:
                continue

            state = State(state=state_name, aux=aux)
            self._states_mapped[state_aux_pair] = StateMappingResult(
                state=state,
                target=target,
                source=MAPPING_SOURCE.PROVIDER_STATE_AUX_MATCH,
                needs_review=target == V11_STATE.NOT_MAPPED,
                reason=(
                    "Cannot find V11 State" if target == V11_STATE.NOT_MAPPED else None
                ),
            )

    def _map_observed_states_on_common_aux_exact(
        self, provider_analysis: ProviderAnalysis
    ):
        state_settings = self._get_configs()
        if state_settings is None:
            raise RuntimeError("State Settings is None.")

        exact_aux = state_settings.common.exact_aux_matches
        observed_states = provider_analysis.observed_states
        for state in observed_states.states:

            if state.aux not in exact_aux:
                continue

            state_aux_pair = (state.state, state.aux)

            if state_aux_pair in self._states_mapped:
                continue

            target = self.convert_state_str_to_v11_state(exact_aux[state.aux])

            self._states_mapped[state_aux_pair] = StateMappingResult(
                state=state,
                target=target,
                source=MAPPING_SOURCE.COMMON_AUX_MATCH,
                needs_review=target == V11_STATE.NOT_MAPPED,
                reason=(
                    "Cannot find V11 State" if target == V11_STATE.NOT_MAPPED else None
                ),
            )

    def _map_call_analysis_provider(
        self,
        provider_analysis: ProviderAnalysis,
        provider_resolution: ProviderResolution,
    ):
        call_analysis_mapping = provider_analysis.intra_call_provider
        provider_config = provider_resolution.config
        self._cli.print_info("Starting Analysis Mapping...")
        if call_analysis_mapping is None:
            self._cli.print_info(
                "Skipping Call Analysis Mapping as IntraCall Provider is not available."
            )
            return

        for state in call_analysis_mapping.states:
            if state.state not in provider_config.base_states:
                continue

            target = self.convert_legacy_to_v11_state(state.original_mapping)
            state_aux_pair = (state.state, state.aux)

            if state_aux_pair not in self._states_mapped:
                self._states_mapped[state_aux_pair] = StateMappingResult(
                    state=state,
                    target=target,
                    source=MAPPING_SOURCE.CALL_ANALYSIS,
                    needs_review=target == V11_STATE.NOT_MAPPED,
                    reason=(
                        "Cannot find V11 State"
                        if target == V11_STATE.NOT_MAPPED
                        else None
                    ),
                )
        self._cli.print_status("Completed Analysis Mapping...")

    def convert_legacy_to_v11_state(self, original_mapping: str) -> V11_STATE:
        state_settings = self._get_configs()
        if state_settings is None:
            raise RuntimeError("State Settings is None.")

        legacy_states = state_settings.common.legacy_states
        try:
            new_state = legacy_states.get(original_mapping)
            return V11_STATE(new_state)
        except ValueError:
            return V11_STATE.NOT_MAPPED

    def convert_state_str_to_v11_state(self, state_str: str) -> V11_STATE:
        try:
            return V11_STATE(state_str)
        except ValueError:
            return V11_STATE.NOT_MAPPED
