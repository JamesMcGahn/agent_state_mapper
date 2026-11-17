from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...models.intra import UserIDEVersion
    from ...cli import CLI
    from ...models.intra import TenantIDEAuditResult


from ..file.sheet_service import SheetService
from ...models.file import SheetData

from pathlib import Path


class TenantIDEAuditSheetService(SheetService):

    def __init__(self, cli: CLI):
        super().__init__(cli)

    def write_analyze(
        self,
        audit_result: TenantIDEAuditResult,
        output_path: Path | str,
    ) -> Path:
        pass

        sheets = [
            self._build_ide_sheets(
                "IDE Versions",
                [
                    "IDE Version",
                    "User Guid",
                    "Login",
                    "First Name",
                    "Last Name",
                    "Tenant Name",
                ],
                audit_result.users_ide,
            ),
        ]

        return self.write(output_path, sheets)

    def _build_ide_sheets(
        self,
        title: str,
        headers: list[str],
        records: list[UserIDEVersion],
    ):
        headers = headers

        row_data = [
            [
                record.ide_verison,
                record.user_guid,
                record.login,
                record.first_name,
                record.last_name,
                record.tenant_name,
            ]
            for record in sorted(
                records,
                key=lambda record: record.ide_verison,
            )
        ]

        return SheetData(
            name=title,
            headers=headers,
            rows=row_data,
        )
