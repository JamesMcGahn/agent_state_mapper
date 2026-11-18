import questionary
from questionary import Choice


class CLI:

    def print_progress(self, message: str) -> None:
        width = max(len(message), getattr(self, "_progress_width", 0))
        print(f"\r{message:<{width}}", end="", flush=True)
        self._progress_width = width

    def end_progress(self) -> None:
        if getattr(self, "_progress_width", 0):
            print(flush=True)
            self._progress_width = 0

    def print_error(self, message: str) -> None:
        self.end_progress()
        questionary.print(f"ERROR: {message}", style="bold fg:red")

    def print_info(self, message: str) -> None:
        self.end_progress()
        questionary.print(message)

    def print_warn(self, message: str) -> None:
        self.end_progress()
        questionary.print(message, style="bold fg:yellow")

    def print_status(self, message: str) -> None:
        self.end_progress()
        questionary.print(message, style="bold fg:cyan")

    def print_color(self, message: str, color: str) -> None:
        self.end_progress()
        questionary.print(message, style=f"bold fg:{color}")

    def select(self, question: str, choices: list[Choice]) -> Choice:
        question = questionary.select(question, choices)
        return question.ask()

    def text_input(self, question: str) -> str:
        question = questionary.text("Enter the Client ID: ")
        return question.ask()

    def password_input(self, question: str) -> str:
        question = questionary.password(question)
        return question.ask()

    def checkbox(self, question: str, choices: list[Choice]) -> Choice:
        question = questionary.checkbox(question, choices=choices)
        return question.ask()
