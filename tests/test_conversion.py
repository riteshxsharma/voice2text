import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from voice2text.config import AppConfig
from voice2text.conversion import convert_transcript
from voice2text.session_control import DictationSessionController


class ConversionTests(unittest.TestCase):
    def test_equation_conversion(self) -> None:
        result = convert_transcript("begin equation alpha equals pi over 2 end equation")
        self.assertEqual(result.latex_text, "\\[\n\\alpha = \\frac{\\pi}{2}\n\\]\n")
        self.assertEqual(result.emacs_text, result.latex_text)

    def test_session_import_can_be_retried_after_stop(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = AppConfig(
                desktop_project_dir=str(root),
                macwhisper_export_dir=str(root / "macwhisper"),
                recordings_dir=str(root / "recordings"),
                incoming_dir=str(root / "incoming"),
                raw_archive_dir=str(root / "raw"),
                emacs_dir=str(root / "emacs"),
                latex_dir=str(root / "latex"),
                logs_dir=str(root / "logs"),
            )
            config.ensure_directories()
            controller = DictationSessionController(config)

            controller.start_session("test")
            first_stop = controller.stop_session()
            self.assertEqual(first_stop, [])

            export = config.macwhisper_export_path / "sample.txt"
            export.write_text("alpha equals beta\n", encoding="utf-8")

            imported = controller.import_last_session_exports()
            self.assertEqual(len(imported), 1)
            self.assertTrue(imported[0].exists())

    def test_import_does_not_duplicate_same_export(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = AppConfig(
                desktop_project_dir=str(root),
                macwhisper_export_dir=str(root / "macwhisper"),
                recordings_dir=str(root / "recordings"),
                incoming_dir=str(root / "incoming"),
                raw_archive_dir=str(root / "raw"),
                emacs_dir=str(root / "emacs"),
                latex_dir=str(root / "latex"),
                logs_dir=str(root / "logs"),
            )
            config.ensure_directories()
            controller = DictationSessionController(config)

            controller.start_session("test")
            export = config.macwhisper_export_path / "sample.txt"
            export.write_text("alpha equals beta\n", encoding="utf-8")
            imported_once = controller.stop_session()
            imported_twice = controller.import_last_session_exports()

            self.assertEqual(len(imported_once), 1)
            self.assertEqual(imported_twice, [])


if __name__ == "__main__":
    unittest.main()
