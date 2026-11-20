from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models.network import AccessToken

from .services.config import AppConfig, ConfigService, StateConfig
from .cli import CLI


from requests import Session
from .services.network import NetworkClient, NetworkThrottle
from .enums import RUN_MENU
import sys
from .workflows import (
    Workflow,
    TenantSelectionFlow,
    TenantCleanUpAuditFlow,
    TenantIDEAuditFlow,
    TenantACDMappingFlow,
)
from .prompts import Prompts
from .errors.network import (
    NetworkResponseException,
    RetryableNetworkException,
    NotAuthenticatedException,
)
from .services.tenant import TenantService, TenantQueryWorker, TenantDAL
from .services.tenant_cleanup_audit import (
    TenantCleanUpAuditService,
    TenantCleanupAuditQueryWorker,
    TenantCleanupAuditDAL,
    TenantCleanupAuditSheetService,
)
from .services.ide_audit import (
    TenantIDEAuditService,
    TenantIDEAuditQueryWorker,
    TenantIDEAuditDAL,
    TenantIDEAuditSheetService,
)
from .services.elk import ELKAPI, ELKService
from .services.provider import ProviderService, ProviderQueryWorker, ProviderDAL
from .db import SQLConnectionManager
from .models.intra import TenantSelection
from .errors import TenantSelectionError
from .errors.db import DBConnectionError
from .services.file import TomlFileService


class App:

    def __init__(
        self,
    ):
        self.cli = CLI()
        self._toml_file_service = TomlFileService(self.cli)
        self._app_config = AppConfig(self.cli)
        self._state_config = StateConfig(self.cli)
        self._config_service = ConfigService(
            self.cli,
            toml_file_service=self._toml_file_service,
            app_config=self._app_config,
            state_config=self._state_config,
        )

        self._http_session = Session()
        self._network_throttle = NetworkThrottle(self.cli)
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
        self._user_tenant_selection: TenantSelection | None = None

        self._sql_conn_manager = SQLConnectionManager(self.cli)
        # -----SERVICES-----
        # -----TENANT-------
        self._tenant_dal = TenantDAL()
        self._tenant_query_worker = TenantQueryWorker(
            cli=self.cli, dal=self._tenant_dal
        )
        self._tenant_service = TenantService(
            cli=self.cli, db=self._sql_conn_manager, worker=self._tenant_query_worker
        )
        # -----TENANT CLEANUP-------
        self._tenant_cleanup_dal = TenantCleanupAuditDAL()
        self._tenant_cleanup_query_worker = TenantCleanupAuditQueryWorker(
            cli=self.cli, dal=self._tenant_cleanup_dal
        )
        self._tenant_cua_service = TenantCleanUpAuditService(
            cli=self.cli,
            db=self._sql_conn_manager,
            worker=self._tenant_cleanup_query_worker,
        )
        self._tenant_cua_sheet_service = TenantCleanupAuditSheetService(cli=self.cli)

        # -----TENANT SELECTION-------
        self._tenant_selection = TenantSelectionFlow(
            cli=self.cli,
            prompts=self.prompts,
            config_service=self._config_service,
            tenant_service=self._tenant_service,
        )
        # -----TENANT IDE-------
        self._tenant_idea_dal = TenantIDEAuditDAL()
        self._tenant_idea_query_worker = TenantIDEAuditQueryWorker(
            cli=self.cli, dal=self._tenant_idea_dal
        )
        self._tenant_idea_service = TenantIDEAuditService(
            cli=self.cli,
            db=self._sql_conn_manager,
            worker=self._tenant_idea_query_worker,
        )
        self._tenant_idea_sheet_service = TenantIDEAuditSheetService(cli=self.cli)
        # -----TENANT PROVIDERS-------
        self._provider_dal = ProviderDAL()
        self._provider_query = ProviderQueryWorker(cli=self.cli, dal=self._provider_dal)
        self._provider_service = ProviderService(
            cli=self.cli, db=self._sql_conn_manager, worker=self._provider_query
        )
        # -----ELK-------
        self._elk_api = ELKAPI(
            cli=self.cli,
            network_client=self._network_client,
            network_throttle=self._network_throttle,
        )
        self._elk_service = ELKService(cli=self.cli, elk_api=self._elk_api)

        # -----STATE MAPPING-------

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
                cli=self.cli,
                tenant_audit_service=self._tenant_cua_service,
                tenant_selection=self.user_tenant_selection,
                reports=self._tenant_cua_sheet_service,
            ),
            RUN_MENU.TENANT_IDE_VERSIONS: TenantIDEAuditFlow(
                cli=self.cli,
                tenant_ide_audit_service=self._tenant_idea_service,
                tenant_selection=self.user_tenant_selection,
                reports=self._tenant_idea_sheet_service,
            ),
            RUN_MENU.STATE_MAPPING: TenantACDMappingFlow(
                cli=self.cli,
                provider_service=self._provider_service,
                tenant_selection=self.user_tenant_selection,
                elk_service=self._elk_service,
            ),
        }
        try:
            workflows[choice].run()
        except RetryableNetworkException as error:
            self.cli.print_error(
                "Network is temporarily unavailable or rate limiting requests. "
                "Wait before trying again."
            )
            self.cli.print_error(f"{error}")
        except NetworkResponseException as error:
            if error.status == 0:
                self.cli.print_error("Cannot reach network. Check your connection.")
                self.cli.print_error(f"{error}")
                self.cli.print_warn("ELK TASKS MUST BE RAN ON AWS RDP!")
            elif error.status == 403:
                self.cli.print_error("Access denied. Check the client's permissions.")
            else:
                self.cli.print_error(f"Network request failed: {error}")
                self.cli.print_warn("ELK TASKS MUST BE RAN ON AWS RDP!")
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
        except DBConnectionError as error:
            self.cli.print_warn("Remember to run the application on the VPN!")
            self.cli.print_error(f"{error}")
        except NotAuthenticatedException as error:
            self.cli.print_error(
                "Please check the ELK API key. Make sure to Run from RDP Server and not your local Machine."
            )
            self.cli.print_error(f"{error}")

    def start_up(self):
        self._config_service.load_application_config()
        self._config_service.load_state_configs()
        self.prompts.welcome_message()
        self.cli.print_warn("STATE MAPPING MUST BE RAN ON AWS RDP!")
        self.prompt_user_for_tenant()
