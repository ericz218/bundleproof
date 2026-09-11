import plistlib
import tempfile
import unittest
from pathlib import Path

from bundleproof.audit import audit


class AuditTests(unittest.TestCase):
    def test_missing_artifact_is_error(self):
        findings = audit(Path("does-not-exist"))
        self.assertEqual(["BP000"], [item.rule for item in findings])

    def test_required_glob(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "public_key.pem").write_text("key")
            self.assertFalse(audit(root, ["*.pem"]))
            self.assertEqual("BP001", audit(root, ["schema.sql"])[0].rule)

    def test_macos_app_executable(self):
        with tempfile.TemporaryDirectory(suffix=".app") as directory:
            app = Path(directory)
            contents = app / "Contents"
            contents.mkdir()
            with (contents / "Info.plist").open("wb") as stream:
                plistlib.dump({"CFBundleExecutable": "Demo"}, stream)
            rules = {item.rule for item in audit(app)}
            self.assertIn("BP104", rules)


if __name__ == "__main__":
    unittest.main()

