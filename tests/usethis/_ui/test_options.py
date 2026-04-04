import importlib
import pkgutil

import typer.models

import usethis._ui as ui_module
import usethis._ui.options as options_module


class TestUniqueHelpText:
    def test_no_duplicate_help_text(self):
        # Arrange
        help_texts: dict[str, str] = {}
        for name in dir(options_module):
            obj = getattr(options_module, name)
            if not isinstance(
                obj, (typer.models.OptionInfo, typer.models.ArgumentInfo)
            ):
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


class TestNoAbbreviatedFlags:
    def test_no_abbreviated_flags(self):
        """Ensure no CLI option uses an abbreviated (short) form like -o."""
        for _importer, modname, _ispkg in pkgutil.walk_packages(
            path=ui_module.__path__,
            prefix=ui_module.__name__ + ".",
            onerror=lambda _: None,
        ):
            module = importlib.import_module(modname)
            for name in dir(module):
                obj = getattr(module, name)
                if not isinstance(obj, typer.models.OptionInfo):
                    continue
                if not obj.param_decls:
                    continue
                for decl in obj.param_decls:
                    assert not (decl.startswith("-") and not decl.startswith("--")), (
                        f"Option {name!r} in {modname!r} uses abbreviated flag {decl!r}. "
                        "Only long forms (--flag) are allowed unless explicitly requested."
                    )
