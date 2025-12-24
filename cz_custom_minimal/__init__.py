from typing import List


class AutoDetectCz:
    """Auto-detect commit type based on keywords in the message."""

    bump_pattern: str | None = None
    bump_map: dict[str, str] | None = None
    bump_map_major_version_zero: dict[str, str] | None = None
    default_style_config: list[tuple[str, str]] = [
        ("qmark", "fg:#ff9d00 bold"),
        ("question", "bold"),
        ("answer", "fg:#ff9d00 bold"),
        ("pointer", "fg:#ff9d00 bold"),
        ("highlighted", "fg:#ff9d00 bold"),
        ("selected", "fg:#cc5454"),
        ("separator", "fg:#cc5454"),
        ("instruction", ""),
        ("text", ""),
        ("disabled", "fg:#858585 italic"),
    ]
    commit_parser: str | None = r"(?P<message>.*)"
    changelog_pattern: str | None = r".*"
    change_type_map: dict[str, str] | None = None
    change_type_order: list[str] | None = None
    changelog_message_builder_hook: object | None = None
    changelog_hook: object | None = None
    changelog_release_hook: object | None = None
    template_extras: dict[str, object] = {}

    def __init__(self, config=None):
        self.config = config
        if config and hasattr(config, "settings") and not config.settings.get("style"):
            config.settings.update({"style": []})

    @property
    def style(self):
        from prompt_toolkit.styles import Style

        style_config = self.default_style_config[:]
        if self.config and hasattr(self.config, "settings"):
            style_config = style_config + self.config.settings.get("style", [])
        return Style(style_config)

    def questions(self) -> List:
        questions = [
            {
                "type": "input",
                "name": "message",
                "message": "Write a short and imperative summary:",
                "filter": lambda s: s.strip().rstrip("."),
            },
        ]
        return questions

    def detect_type(self, message: str) -> str:
        """Auto-detect commit type based on keywords."""
        fix_keywords = [
            "fix",
            "bug",
            "error",
            "issue",
            "problem",
            "crash",
            "fail",
            "broken",
            "correction",
            "patch",
            "repair",
            "solve",
            "resolve",
        ]
        feat_keywords = [
            "add",
            "new",
            "implement",
            "create",
            "introduce",
            "support",
            "feature",
            "enable",
            "allow",
        ]
        docs_keywords = ["doc", "readme", "documentation", "update readme", "docstring"]
        test_keywords = ["test", "testing", "spec", "pytest", "unit test"]
        refactor_keywords = [
            "refactor",
            "clean",
            "simplify",
            "improve",
            "optimize",
            "restructure",
            "reorganize",
        ]
        style_keywords = ["format", "style", "lint", "indentation", "whitespace"]
        perf_keywords = ["performance", "speed", "fast", "slow", "optimize performance"]
        chore_keywords = ["chore", "dependency", "update version", "bump", "maintain"]

        msg_lower = message.lower()

        for keyword in fix_keywords:
            if keyword in msg_lower:
                return "fix"

        for keyword in feat_keywords:
            if keyword in msg_lower:
                return "feat"

        for keyword in docs_keywords:
            if keyword in msg_lower:
                return "docs"

        for keyword in test_keywords:
            if keyword in msg_lower:
                return "test"

        for keyword in refactor_keywords:
            if keyword in msg_lower:
                return "refactor"

        for keyword in style_keywords:
            if keyword in msg_lower:
                return "style"

        for keyword in perf_keywords:
            if keyword in msg_lower:
                return "perf"

        for keyword in chore_keywords:
            if keyword in msg_lower:
                return "chore"

        return "chore"

    def message_pattern(self, prefix: str = "", message: str = "") -> str:
        prefix = self.detect_type(message)
        if message:
            return f"{prefix}: {message}"
        return ""

    def message(self, answers: dict) -> str:
        message = answers.get("message", "")
        prefix = self.detect_type(message)
        return f"{prefix}: {message}"

    def example(self) -> str:
        return (
            "add new user authentication\n-> becomes: feat: add new user authentication"
        )

    def schema_pattern(self) -> str:
        return "<message> (type auto-detected)"

    def schema(self) -> str:
        return """Just write your commit message, the type will be auto-detected.

Examples:
  "add new feature"           -> feat: add new feature
  "fix login bug"             -> fix: fix login bug
  "update readme"              -> docs: update readme
  "add tests for auth"        -> test: add tests for auth
  "refactor user service"     -> refactor: refactor user service
  "fix code style"            -> style: fix code style
  "improve performance"       -> perf: improve performance
  "update dependencies"       -> chore: update dependencies
"""

    def info(self) -> str:
        return """Auto-detect commit message type.

Just write your message, and the type will be detected from keywords:
  fix      fix, bug, error, issue, problem, crash, fail, broken...
  feat     add, new, implement, create, feature...
  docs     doc, readme, documentation...
  test     test, testing, spec, pytest...
  refactor refactor, clean, simplify, improve...
  style    format, style, lint, whitespace...
  perf     performance, speed, fast, slow...
  chore    chore, dependency, update version...
"""
