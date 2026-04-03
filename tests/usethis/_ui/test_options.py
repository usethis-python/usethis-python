import typer.models

import usethis._ui.options as options_module


class TestUniqueHelpText:
    def test_no_duplicate_help_text(self):
        # Arrange
        help_texts: dict[str, str] = {}
        for name in dir(options_module):
            obj = getattr(options_module, name)
            if not isinstance(obj, (typer.models.OptionInfo, typer.models.ArgumentInfo)):
                continue
            help_text = obj.help
            if help_text is None:
                continue

            # Assert
            assert help_text not in help_texts.values(), (
                f"Duplicate help text {help_text!r} "
                f"found on {name!r} and {next(k for k, v in help_texts.items() if v == help_text)!r}"
            )
            help_texts[name] = help_text
