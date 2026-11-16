from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models.network import AccessToken

from .app_config import AppConfig
from .cli import CLI


from requests import Session
from .network import NetworkClient, NetworkThrottle
from .enums import RUN_MENU
import sys
from .workflows import Workflow, TenantSelectionFlow, TenantCleanUpAuditFlow
from .prompts import Prompts
from .errors.network import NetworkResponseException, RetryableNetworkException
from .services.tenant import TenantService, TenantQueryWorker, TenantDAL
from .services.tenant_cleanup_audit import (
    TenantCleanUpAuditService,
    TenantCleanupAuditQueryWorker,
    TenantCleanupAuditDAL,
)
from .db import SQLConnectionManager
from .models.intra import TenantSelection
from .errors import TenantSelectionError
from .errors.db import DBConnectionError


class App:

    def __init__(
        self,
    ):
        self.cli = CLI()
        self._app_config = AppConfig(self.cli)
        self._config = None
        self._http_session = Session()
        self._network_throttle = NetworkThrottle()
        self._network_client = NetworkClient(self._http_session)
        # self._gen_api = GenesysAPI(
        #     self._network_client, self._network_throttle, self.cli
        # )
        self.prompts = Prompts(self.cli)
        # self.activity_code_analyzer = ActivityCodeAnalyze(self.cli)
        # self.activity_code_reports = AnalyzeSheetService(self.cli)
        # self.raw_payload_writer = RawPlayloadService(self.cli)

        self._gen_token: AccessToken | None = None
        # self._region: Region | None = None
        # self._client_creds: ClientCredentials | None = None
        self._sql_conn_manager = SQLConnectionManager(self.cli)
        self._tenant_dal = TenantDAL()
        self._tenant_query_worker = TenantQueryWorker(
            cli=self.cli, dal=self._tenant_dal
        )
        self._tenant_service = TenantService(
            cli=self.cli, db=self._sql_conn_manager, worker=self._tenant_query_worker
        )

        self._tenant_cleanup_dal = TenantCleanupAuditDAL()
        self._tenant_cleanup_query_worker = TenantCleanupAuditQueryWorker(
            cli=self.cli, dal=self._tenant_cleanup_dal
        )

        self._tenant_cua_service = TenantCleanUpAuditService(
            cli=self.cli,
            db=self._sql_conn_manager,
            worker=self._tenant_cleanup_query_worker,
        )

        self._tenant_selection = TenantSelectionFlow(
            cli=self.cli,
            prompts=self.prompts,
            config=self._app_config,
            tenant_service=self._tenant_service,
        )

        self._user_tenant_selection: TenantSelection | None = None

    @property
    def user_tenant_selection(self):
        return self._user_tenant_selection

    @user_tenant_selection.setter
    def user_tenant_selection(self, tenant_selection: TenantSelection):
        self._user_tenant_selection = tenant_selection

    def prompt_user_for_tenant(self):
        while True:
            try:
                self.user_tenant_selection = self._tenant_selection.run()
                return
            except TenantSelectionError:
                self.cli.print_error(
                    "Please select a tenant before running one of the actions."
                )
                self.cli.print_warn("Remember to run the application on the VPN!")
            except DBConnectionError:
                self.cli.print_warn("Remember to run the application on the VPN!")

    def run(self):
        self.start_up()
        while True:
            choice = self.prompts.welcome_menu()
            if choice == RUN_MENU.QUIT:
                sys.exit(0)
            elif choice == RUN_MENU.CHANGE_TENANT:
                self.prompt_user_for_tenant()
            else:
                self.run_choice(choice)

    def run_choice(self, choice: RUN_MENU):
        workflows: dict[RUN_MENU, Workflow] = {
            RUN_MENU.CLEANUP_QUERIES: TenantCleanUpAuditFlow(
                self.cli,
                prompts=self.prompts,
                config=self._app_config,
                tenant_audit_service=self._tenant_cua_service,
                tenant_selection=self.user_tenant_selection,
            )
        }
        try:
            workflows[choice].run()
        except RetryableNetworkException:
            self.cli.print_error(
                "Genesys is temporarily unavailable or rate limiting requests. "
                "Wait before trying again."
            )
        except NetworkResponseException as error:
            if error.status == 0:
                self.cli.print_error("Cannot reach Genesys. Check your connection.")
            elif error.status == 403:
                self.cli.print_error("Access denied. Check the client's permissions.")
            else:
                self.cli.print_error(f"Genesys request failed: {error}")
        except PermissionError:
            self.cli.print_error(
                "Cannot write the report. Close it in Excel "
                "and check the output folder's permissions."
            )
        except OSError as error:
            self.cli.print_error(f"Cannot save the report: {error}")
        except TenantSelectionError:
            self.cli.print_error(
                "Please select a tenant before running one of the actions."
            )
            self.cli.print_warn("Remember to run the application on the VPN!")
        except DBConnectionError:
            self.cli.print_warn("Remember to run the application on the VPN!")

    def start_up(self):
        self._app_config.load_config()
        self.prompts.welcome_message()
        self.prompt_user_for_tenant()
