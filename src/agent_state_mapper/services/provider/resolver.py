from __future__ import annotations

from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from ...cli import CLI
    from ...models.config import StateSettings
    from ...models.intra import Provider
    from ...models.elk import StatesResult
    from ...models.states import ProviderStates

from ...models.states import ProviderResolution
from ...enums import PROVIDER_MATCH_BY


class ProviderResolver:

    def __init__(self, cli: CLI, get_configs: Callable[[], StateSettings]):
        self._cli = cli
        self._get_configs = get_configs

    def resolve(
        self, provider: Provider, observed_states: StatesResult
    ) -> ProviderResolution | None:

        state_configs = self._get_configs()
        provider_configs = state_configs.providers
        match = self._find_matched_provider_by_alias(
            provider, provider_configs, observed_states
        )
        if match is not None:
            return match

        matches = self._find_matched_providers_by_state(
            provider, provider_configs, observed_states
        )

        if not matches:
            return None

        if len(matches) == 1:
            return matches[0]

        matches.sort(key=lambda candidate: candidate.match_percentage, reverse=True)

        if matches[0].match_percentage - matches[1].match_percentage > 5:
            return matches[0]

        return None

    def _find_matched_provider_by_alias(
        self,
        provider: Provider,
        provider_configs: list[ProviderStates],
        observed_states: StatesResult,
    ) -> ProviderResolution | None:

        for provider_config in provider_configs:

            if provider.provider_type in provider_config.aliases:
                match_by = PROVIDER_MATCH_BY.ALIAS
                matched_states, unexpected_states, needs_review, match_percentage = (
                    self._find_matched_states(provider_config, observed_states)
                )
                return ProviderResolution(
                    provider=provider,
                    config=provider_config,
                    matched_by=match_by,
                    matched_states=matched_states,
                    unexpected_states=unexpected_states,
                    needs_review=needs_review,
                    match_percentage=match_percentage,
                )
        return None

    def _find_matched_providers_by_state(
        self,
        provider: Provider,
        provider_configs: list[ProviderStates],
        observed_states: StatesResult,
    ) -> list[ProviderResolution]:
        provider_matches = []

        for provider_config in provider_configs:
            matched_states, unexpected_states, needs_review, match_percentage = (
                self._find_matched_states(provider_config, observed_states)
            )

            if match_percentage >= 85.0:
                match_by = PROVIDER_MATCH_BY.STATES
                provider_match = ProviderResolution(
                    provider=provider,
                    config=provider_config,
                    matched_by=match_by,
                    matched_states=matched_states,
                    unexpected_states=unexpected_states,
                    needs_review=needs_review,
                    match_percentage=match_percentage,
                )
                provider_matches.append(provider_match)
        return provider_matches

    def _find_matched_states(
        self,
        provider_config: ProviderStates,
        observed_states: StatesResult,
    ):
        observed_states_name = {state.state for state in observed_states.states}

        unexpected_states = set(observed_states_name) - set(provider_config.base_states)
        matched_states = set(provider_config.base_states) & set(observed_states_name)

        needs_review = not observed_states_name or bool(unexpected_states)
        match_percentage = (
            len(matched_states) / len(observed_states_name) * 100
            if observed_states_name
            else 0.0
        )
        return (matched_states, unexpected_states, needs_review, match_percentage)
