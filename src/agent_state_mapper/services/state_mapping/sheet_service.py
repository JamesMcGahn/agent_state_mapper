from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...cli import CLI
    from ...models.mapping import ProviderMappingResult
    from ...models.intra import TenantSelection


from ..file.sheet_service import SheetService
from ...models.file import SheetData
from ...models.file.sheet_data import CellValue
from pathlib import Path


class StateMappingSheetService(SheetService):

    def __init__(self, cli: CLI):
        super().__init__(cli)

    def write_analyze(
        self,
        tenant_selection: TenantSelection,
        providers_mappings: list[ProviderMappingResult],
        output_path: Path | str,
    ) -> Path:

        sheets = [
            self._build_tenant_mapping_sheet(
                f"{tenant_selection.tenant.name} state mapping v11",
                [
                    "provider_instance",
                    "IntradiemState",
                    "ProviderState",
                    "AuxCode",
                    "IsOnCallState (TRUE/FALSE)",
                    "Source",
                    "Needs Review",
                ],
                providers_mappings,
            ),
        ]

        return self.write(output_path, sheets)

    def _build_tenant_mapping_sheet(
        self,
        title: str,
        headers: list[str],
        records: list[ProviderMappingResult],
    ):
        headers = headers

        row_data = []

        for provider in records:
            provider_rows = self._build_name_provider_rows(provider)
            row_data.extend(provider_rows)

        return SheetData(
            name=title,
            headers=headers,
            rows=row_data,
        )

    def _build_name_provider_rows(
        self, result: ProviderMappingResult
    ) -> list[list[CellValue]]:

        records = result.mappings
        provider_guid = result.analysis.provider.guid_underscored
        row_data = [
            [
                provider_guid,
                record.target,
                record.state.state,
                record.state.aux,
                record.is_on_call,
                record.source,
                record.needs_review,
            ]
            for record in sorted(
                records,
                key=lambda record: record.state.state,
            )
        ]

        return row_data
