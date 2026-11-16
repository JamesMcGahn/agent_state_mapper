from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...models.intra import (
        TaskFilter,
        UserFilter,
        CustomAttribute,
        PausedRule,
        AssignmentFilter,
    )
    from ...cli import CLI
    from ...models.intra import TenantCleanupAuditResult


from ..file.sheet_service import SheetService
from ...models.file import SheetData

from pathlib import Path
from datetime import datetime


class TenantCleanupAuditSheetService(SheetService):

    def __init__(self, cli: CLI):
        super().__init__(cli)

    def write_analyze(
        self,
        audit_result: TenantCleanupAuditResult,
        output_path: Path | str,
    ) -> Path:
        pass

        sheets = [
            self._build_name_sheets(
                "User Filters", ["User Filters"], audit_result.user_filters
            ),
            self._build_name_sheets(
                "Task Filters", ["Task Filters"], audit_result.task_filters
            ),
            self._build_name_sheets(
                "Attributes", ["Attributes"], audit_result.custom_attributes
            ),
            self._build_paused_rule_sheet(
                "Paused Rules", ["Rule", "Paused Time"], audit_result.paused_rules
            ),
            self._build_assignment_filter_sheet(
                "Assignment Filter",
                [
                    "First Name",
                    "Last Name",
                    "Login",
                    "Filter Name",
                    "Filter Type",
                    "Public or Private",
                ],
                audit_result.assignment_filters,
            ),
        ]

        return self.write(output_path, sheets)

    def _build_name_sheets(
        self,
        title: str,
        headers: list[str],
        records: list[TaskFilter | UserFilter | CustomAttribute],
    ):
        headers = headers

        row_data = [
            [
                record.name,
            ]
            for record in sorted(
                records,
                key=lambda record: record.name,
            )
        ]

        return SheetData(
            name=title,
            headers=headers,
            rows=row_data,
        )

    def _build_paused_rule_sheet(
        self,
        title: str,
        headers: list[str],
        records: list[PausedRule],
    ):
        headers = headers

        row_data = [
            [
                record.name,
                self.convert_time_to_str(record.paused_date),
            ]
            for record in sorted(
                records,
                key=lambda record: record.name,
            )
        ]

        return SheetData(
            name=title,
            headers=headers,
            rows=row_data,
        )

    def _build_assignment_filter_sheet(
        self,
        title: str,
        headers: list[str],
        records: list[AssignmentFilter],
    ):
        headers = headers

        row_data = [
            [
                record.first_name,
                record.last_name,
                record.login,
                record.filter_name,
                record.filter_type,
                "public" if record.is_public else "private",
            ]
            for record in sorted(
                records,
                key=lambda record: record.filter_name,
            )
        ]

        return SheetData(
            name=title,
            headers=headers,
            rows=row_data,
        )

    def convert_time_to_str(self, time: datetime) -> str:
        try:
            return time.strftime("%Y-%m-%d %H:%M:%S")
        except AttributeError:
            return time
