import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import prism  # noqa: E402


class PrismKernelTest(unittest.TestCase):
    def test_all_fixtures_compile(self) -> None:
        self.assertEqual(prism.cmd_check(None), 0)

    def test_missing_field_rejected(self) -> None:
        seed = json.loads((ROOT / "evals/fixtures/poster.json").read_text())
        seed["fields"].pop("dynamic_negative_constraints")
        with self.assertRaises(prism.PrismError):
            prism.validate_seed(seed)

    def test_banned_soup_rejected(self) -> None:
        with self.assertRaises(prism.PrismError):
            prism.compile_fields(
                {
                    "core_style_contract": "masterpiece best quality",
                    "dynamic_negative_constraints": "避免卡通",
                }
            )

    def test_harvest_axes(self) -> None:
        seed = prism.validate_seed(json.loads((ROOT / "evals/fixtures/portrait.json").read_text()))
        cards = prism.harvest_cards(seed["fields"])
        axes = {card["axis"] for card in cards}
        self.assertTrue({"style", "subject", "motion"} <= axes)

    def test_poster_prompt_keeps_failure(self) -> None:
        seed = prism.validate_seed(json.loads((ROOT / "evals/fixtures/poster.json").read_text()))
        prompt = prism.compile_fields(seed["fields"])
        self.assertIn("避免", prompt)
        self.assertNotIn("{", prompt)

    def test_compile_restates_locks_before_negatives(self) -> None:
        seed = prism.validate_seed(json.loads((ROOT / "evals/hard-set/H7-cloud-water.json").read_text()))
        prompt = prism.compile_fields(seed["fields"])
        self.assertIn("必须守住", prompt)
        self.assertIn("CLOUD WATER", prompt)
        self.assertGreater(prompt.find("避免"), prompt.find("必须守住"))

    def test_h5_compile_locks_paint_not_photo(self) -> None:
        seed = prism.validate_seed(json.loads((ROOT / "evals/hard-set/H5-mist-palace.json").read_text()))
        prompt = prism.compile_fields(seed["fields"])
        self.assertIn("数字绘画", prompt)
        self.assertIn("可见湿边", prompt)
        self.assertIn("禁止实景摄影", prompt)
        self.assertIn("必须守住", prompt)
        self.assertTrue(prompt.startswith("数字绘画"))

    def test_extract_json_object_from_fence(self) -> None:
        obj = prism.extract_json_object('前言\n```json\n{"type":"product","fields":{"a":"b"}}\n```\n')
        self.assertEqual(obj["type"], "product")
        self.assertEqual(obj["fields"]["a"], "b")

    def test_normalize_type_aliases(self) -> None:
        self.assertEqual(prism.normalize_type_id("portrait"), "portrait")
        self.assertEqual(prism.normalize_type_id("二次元插画"), "illustration")
        self.assertEqual(prism.normalize_type_id("秋日宫苑山水"), "scene")
        self.assertEqual(prism.normalize_type_id("??"), "generic")

    def test_coerce_seed_flattens_and_validates(self) -> None:
        raw = {
            "type": "产品图",
            "core_style_contract": "瓶身即天空",
            "dynamic_negative_constraints": "避免改成可乐",
            "notes": "ignore",
        }
        seed = prism.coerce_seed(raw, "generic")
        self.assertEqual(seed["type"], "product")
        self.assertIn("core_style_contract", seed["fields"])
        self.assertNotIn("notes", seed["fields"])

    def test_fill_prompt_lists_type_fields(self) -> None:
        text = prism.fill_prompt("product")
        self.assertIn("subject_identity", text)
        self.assertIn("避免", text)

    def test_classify_prompt_keeps_anime_as_illustration(self) -> None:
        text = prism.classify_prompt()
        self.assertIn("赛璐璐", text)
        self.assertIn("不是动画", text)

    def test_infer_size_reads_landscape_words(self) -> None:
        self.assertEqual(prism.infer_size({"type": "scene", "fields": {"image_type": "横向宽画幅"}}), "1536x1024")
        self.assertEqual(prism.infer_size({"type": "illustration", "fields": {"image_type": "横向矩形"}}), "1536x1024")
        self.assertEqual(prism.infer_size({"type": "portrait", "fields": {"image_type": "竖版 9:16"}}), "1024x1536")


if __name__ == "__main__":
    unittest.main()
