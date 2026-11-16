"""Regression tests for uninflected participle dictionary-form answers."""
import unittest

from verbal_principal_forms import (
    participle_dictionary_entry,
    accepts_participle_dictionary_answer,
    has_real_perfect_passive_stem,
    has_usable_fourth_part,
)


class ParticipleDictionaryFormsTests(unittest.TestCase):
    def setUp(self):
        self.dico = {"conj": 3, "pres": "dic", "ppp": "dict"}
        self.facio = {"conj": "3io", "pres": "fac", "ppp": "fact"}

    def test_perfect_passive_variants(self):
        entry = participle_dictionary_entry(self.dico, "ppp")
        self.assertEqual(entry["canonical"], "dictus 3")
        for answer in (
            "dictus 3", "dictus 3.", "dictus3", "dictus3.", "dictus, dicta, dictum",
            "dictus -a -um", "dictus, -a, -um",
            "dictus/-a/-um", "dictus-a-um", "DICTUS -A -UM",
        ):
            with self.subTest(answer=answer):
                self.assertTrue(accepts_participle_dictionary_answer(answer, entry))
        for wrong in ("dictus", "dicta 3", "dictus, dictam, dictum", "dictus 2"):
            with self.subTest(wrong=wrong):
                self.assertFalse(accepts_participle_dictionary_answer(wrong, entry))

    def test_present_active_variants(self):
        entry = participle_dictionary_entry(self.dico, "pap")
        self.assertEqual(entry["canonical"], "dicēns (ntis)")
        self.assertEqual(entry["genitive"], "dicentis")
        for answer in (
            "dicens (ntis)", "dicēns, dicentis", "dicens -ntis",
            "dicens, -ntis", "dicens dicentis", "DICENS/-NTIS",
        ):
            with self.subTest(answer=answer):
                self.assertTrue(accepts_participle_dictionary_answer(answer, entry))
        for wrong in ("dicens", "dicens 3", "dicens, dicentes", "dicentis"):
            with self.subTest(wrong=wrong):
                self.assertFalse(accepts_participle_dictionary_answer(wrong, entry))

    def test_macron_policy(self):
        entry = participle_dictionary_entry(self.dico, "pap")
        self.assertTrue(accepts_participle_dictionary_answer("dicēns -ntis", entry, enforce_macrons=True))
        self.assertFalse(accepts_participle_dictionary_answer("dicens -ntis", entry, enforce_macrons=True))
        self.assertTrue(accepts_participle_dictionary_answer("dicens -ntis", entry, enforce_macrons=False))

    def test_future_active_and_gerundive(self):
        future = participle_dictionary_entry(self.dico, "fap")
        gerundive = participle_dictionary_entry(self.dico, "gdv")
        self.assertEqual(future["canonical"], "dictūrus 3")
        self.assertEqual(gerundive["canonical"], "dicendus 3")
        self.assertTrue(accepts_participle_dictionary_answer("dicturus -a -um", future))
        self.assertTrue(accepts_participle_dictionary_answer("dictūrus3", future))
        self.assertTrue(accepts_participle_dictionary_answer("dicendus3", gerundive))
        self.assertTrue(accepts_participle_dictionary_answer("dicendus, dicenda, dicendum", gerundive))

    def test_third_io_forms(self):
        entry = participle_dictionary_entry(self.facio, "pap")
        self.assertEqual(entry["canonical"], "faciēns (ntis)")
        self.assertEqual(entry["genitive"], "facientis")

    def test_irregular_present_participle(self):
        entry = participle_dictionary_entry({"pap": ("iēns", "eunt"), "ppp": "it"}, "pap")
        self.assertEqual(entry["canonical"], "iēns (ntis)")
        self.assertTrue(accepts_participle_dictionary_answer("iens, euntis", entry))

    def test_fourth_part_restrictions(self):
        missing = {"conj": 3, "pres": "parc", "perf": "peperc"}
        bracketed = {**missing, "fap": "pars"}  # parcō: displayed as [parsus]
        marked = {**missing, "ppp": "[pars]"}
        no_fourth = {**missing, "ppp": None}
        for data in (missing, bracketed, marked, no_fourth):
            with self.subTest(data=data):
                self.assertFalse(has_usable_fourth_part(data))
                for kind in ("pap", "ppp", "fap", "gdv"):
                    self.assertIsNone(participle_dictionary_entry(data, kind))

    def test_future_only_fourth_part(self):
        future_only = {"conj": 3, "pres": "ard", "fap": "ārsūr"}
        self.assertTrue(has_usable_fourth_part(future_only))
        self.assertFalse(has_real_perfect_passive_stem(future_only))
        self.assertIsNone(participle_dictionary_entry(future_only, "ppp"))
        self.assertEqual(
            participle_dictionary_entry(future_only, "fap")["canonical"],
            "ārsūrus 3",
        )
        self.assertTrue(
            accepts_participle_dictionary_answer(
                "ārsūrus3", participle_dictionary_entry(future_only, "fap")
            )
        )
        future_stored_as_ppp = {"conj": 3, "pres": "fut", "ppp": "futūr"}
        self.assertIsNone(participle_dictionary_entry(future_stored_as_ppp, "ppp"))
        self.assertEqual(participle_dictionary_entry(future_stored_as_ppp, "fap")["canonical"], "futūrus 3")

    def test_wrong_joined_numerals(self):
        entry = participle_dictionary_entry(self.dico, "ppp")
        for answer in ("dictus33", "dictus4", "dicta3", "dictus3um"):
            self.assertFalse(accepts_participle_dictionary_answer(answer, entry))

    def test_missing_forms(self):
        self.assertIsNone(participle_dictionary_entry({"no_pass": True, "ppp": "dict"}, "ppp"))
        self.assertIsNone(participle_dictionary_entry({"pres": "dic", "conj": 3, "gdv": None}, "gdv"))


if __name__ == "__main__":
    unittest.main()
