import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools import validate_splits


class SplitValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        root = Path(self.temp_dir.name)
        config = root / "config" / "US"
        config.mkdir(parents=True)
        source = root / "src" / "Game" / "Player"
        source.mkdir(parents=True)
        (source / "PlayerInput.cpp").write_text("int placeholder;\n")
        self.symbols = config / "symbols.txt"
        self.verified = config / "verified_symbols.txt"
        self.splits = config / "splits.txt"
        self.symbols.write_text("PlayerInput::isRollingTrigOn = .text:0x022b2f50; // size:0x14\n")
        self.verified.write_text("PlayerInput_isRollingTrigOn = .text:0x022b2f50; // size:0x14\n")
        self.splits.write_text(
            "Game/Player/PlayerInput.cpp:\n"
            "    .text start:0x022b2f50 end:0x022b2f64\n"
        )
        for attr, val in (("ROOT", root), ("CONFIG", config)):
            override = patch.object(validate_splits, attr, val)
            override.start()
            self.addCleanup(override.stop)

    def test_valid(self):
        validate_splits.validate()

    def test_unverified_symbol(self):
        self.verified.write_text("")
        with self.assertRaisesRegex(ValueError, "verified PowerPC"):
            validate_splits.validate()

    def test_duplicate_symbol(self):
        self.symbols.write_text(self.symbols.read_text() * 2)
        with self.assertRaisesRegex(ValueError, "duplicate"):
            validate_splits.validate()

    def test_overlap(self):
        other = validate_splits.ROOT / "src" / "Game" / "Player" / "Other.cpp"
        other.write_text("int other;\n")
        self.splits.write_text(
            self.splits.read_text() +
            "Game/Player/Other.cpp:\n"
            "    .text start:0x022b2f5c end:0x022b2f6c\n"
        )
        with self.assertRaisesRegex(ValueError, "overlap"):
            validate_splits.validate()

    def test_outside_text(self):
        self.splits.write_text(self.splits.read_text().replace("0x022b2f50", "0x01900000"))
        with self.assertRaisesRegex(ValueError, "out-of-bounds"):
            validate_splits.validate()


if __name__ == "__main__":
    unittest.main()
