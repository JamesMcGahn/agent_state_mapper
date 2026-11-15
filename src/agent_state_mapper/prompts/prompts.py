from ..cli import CLI
from ..enums import RUN_MENU

from ..models.intra import Node, Tenant
from questionary import Choice
from ..__version__ import __version__


class Prompts:
    def __init__(self, cli: CLI):
        self.cli = cli

    def welcome_message(self) -> None:
        self.cli.print_color(
            f"\nWelcome to the V11 Migration Tools (v{__version__})",
            "green",
        )
        self.cli.print_color("-----------------------------------------------", "green")

    def welcome_menu(self) -> RUN_MENU:
        choice = self.cli.select("Select : ", [code.value for code in RUN_MENU])
        if choice is None:
            raise KeyboardInterrupt
        return RUN_MENU(choice)

    def enter_client_id(self) -> str:
        return self.cli.text_input("Enter the Client ID: ")

    def enter_client_secret(self) -> str:
        return self.cli.password_input("Enter the Client Secret: ")

    # def enter_client_credentials(self) -> ClientCredentials:
    #     client_id = ""
    #     client_secret = ""

    #     while not client_id:
    #         client_id = self.enter_client_id()
    #         if client_id is None:
    #             raise KeyboardInterrupt
    #         client_id = client_id.strip()

    #     while not client_secret:
    #         client_secret = self.enter_client_secret()
    #         if client_secret is None:
    #             raise KeyboardInterrupt
    #         client_secret = client_secret.strip()

    #     return ClientCredentials(client_id=client_id, client_secret=client_secret)

    def prompt_user_for_node_selection(self, config: list[Node]) -> Node:
        node_list = [Choice(title=node.name, value=node.name) for node in config]
        node_name = self.cli.select("Select Node: ", node_list)
        if node_name is None:
            raise KeyboardInterrupt

        for node in config:
            if node.name == node_name:
                return node

        raise RuntimeError(f"Selected node was not found: {node_name}")

    def prompt_user_for_tenant_selection(self, node_tenants: list[Tenant]) -> Tenant:
        tenant_list = sorted(
            [
                Choice(title=tenant.name, value=tenant.tenant_id)
                for tenant in node_tenants
            ],
            key=lambda b: b.title,
        )
        tenant_selection = self.cli.select("Select Tenant:", tenant_list)
        if tenant_selection is None:
            raise KeyboardInterrupt

        for tenant in node_tenants:
            if tenant.tenant_id == tenant_selection:
                return tenant

        raise RuntimeError(f"Selected tenant was not found: {tenant_selection}")
