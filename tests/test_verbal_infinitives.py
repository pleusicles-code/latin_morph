"""Regression tests for the six-form infinitive selection."""
import unittest

from verbal_infinitives import (
    ALL_INFINITIVE_TYPES, infinitive_paradigm, expand_selected_form_types,
)


class InfinitiveParadigmTests(unittest.TestCase):
    def setUp(self):
        self.dico = {"conj": 3, "voice": "act", "pres": "dīc", "perf": "dīx", "ppp": "dict"}

    def test_all_option_independent_of_imperfect_active_checkbox(self):
        self.assertEqual(
            expand_selected_form_types(["inf_all"]), list(ALL_INFINITIVE_TYPES)
        )
        self.assertEqual(
            expand_selected_form_types(["inf_impf_act", "inf_all"]),
            list(ALL_INFINITIVE_TYPES)
        )
        self.assertEqual(
            expand_selected_form_types(["pap", "inf_all"]),
            ["pap", *ALL_INFINITIVE_TYPES]
        )
        self.assertEqual(
            expand_selected_form_types(["pap", "inf_impf_act"]),
            ["pap", "inf_impf_act"]
        )

    def test_regular_six_types(self):
        forms = infinitive_paradigm("dīcō", self.dico)
        self.assertEqual(set(forms), set(ALL_INFINITIVE_TYPES))
        self.assertEqual(forms["inf_impf_act"][0], "dīcere")
        self.assertEqual(forms["inf_impf_pass"][0], "dīcī")
        self.assertEqual(forms["inf_perf_act"][0], "dīxisse")
        self.assertEqual(forms["inf_perf_pass"][0], "dictum esse")
        self.assertEqual(forms["inf_inst_act"][0], "dictūrum esse")
        self.assertEqual(forms["inf_inst_pass"][0], "dictum īrī")

    def test_first_and_fourth_conjugations(self):
        amo = {"voice": "act", "conj": 1, "pres": "am", "perf": "amāv", "ppp": "amāt"}
        venio = {"voice": "act", "conj": 4, "pres": "ven", "perf": "vēn", "ppp": "vent"}
        self.assertEqual(infinitive_paradigm("amō", amo)["inf_impf_pass"], ["amārī"])
        self.assertEqual(infinitive_paradigm("veniō", venio)["inf_impf_pass"], ["venīrī"])

    def test_third_io_and_facio(self):
        facio = {"voice": "act", "conj": "3io", "pres": "fac", "perf": "fēc", "ppp": "fact"}
        forms = infinitive_paradigm("faciō", facio)
        self.assertEqual(forms["inf_impf_act"], ["facere"])
        self.assertEqual(forms["inf_impf_pass"], ["fierī"])

    def test_deponent(self):
        loquor = {"voice": "dep", "conj": 3, "pres": "loqu", "ppp": "locūt"}
        forms = infinitive_paradigm("loquor", loquor)
        self.assertEqual(set(forms), {"inf_impf_pass", "inf_perf_pass", "inf_inst_act"})
        self.assertEqual(forms["inf_impf_pass"], ["loquī"])
        self.assertEqual(forms["inf_perf_pass"][0], "locūtum esse")
        self.assertEqual(forms["inf_inst_act"][0], "locūtūrum esse")

    def test_semideponent(self):
        audeo = {"voice": "semidep", "conj": 2, "pres": "aud", "ppp": "aus"}
        forms = infinitive_paradigm("audeō", audeo)
        self.assertEqual(set(forms), {"inf_impf_act", "inf_perf_pass", "inf_inst_act"})
        self.assertEqual(forms["inf_impf_act"], ["audēre"])
        self.assertEqual(forms["inf_perf_pass"][0], "ausum esse")

    def test_fio_special_infinitives(self):
        fio = {
            "voice": "semidep", "conj": 3, "pres": "fī", "ppp": "fact", "fap": None,
            "irreg": {"forms": {"pres": {"dep": {"inf": "fierī"}}}},
        }
        forms = infinitive_paradigm("fīō", fio)
        self.assertEqual(forms["inf_impf_pass"], ["fierī"])
        self.assertEqual(forms["inf_inst_pass"], ["factum īrī"])
        self.assertNotIn("inf_impf_act", forms)

    def test_future_only_part_and_no_perfect(self):
        cado = {"voice": "act", "conj": 3, "pres": "cad", "perf": "cecid", "fap": "cāsūr"}
        forms = infinitive_paradigm("cadō", cado)
        self.assertEqual(forms["inf_inst_act"], ["cāsūrum esse", "cāsūrus esse", "cāsūra esse"])
        self.assertNotIn("inf_perf_pass", forms)
        self.assertNotIn("inf_inst_pass", forms)

    def test_irregular_present_infinitives(self):
        fero = {
            "voice": "act", "conj": 3, "pres": "fer", "perf": "tul", "ppp": "lāt",
            "irreg": {"forms": {"pres": {
                "act": {"inf": "ferre"}, "pass": {"inf": "ferrī"}
            }}},
        }
        forms = infinitive_paradigm("ferō", fero)
        self.assertEqual(forms["inf_impf_act"], ["ferre"])
        self.assertEqual(forms["inf_impf_pass"], ["ferrī"])

    def test_no_passive_and_alternative_perfect(self):
        nescio = {"voice": "act", "conj": 4, "pres": "nesc", "perf": "nescīv", "ppp": "nescīt", "no_pass": True}
        forms = infinitive_paradigm("nesciō", nescio)
        self.assertNotIn("inf_impf_pass", forms)
        self.assertNotIn("inf_perf_pass", forms)
        self.assertNotIn("inf_inst_pass", forms)
        self.assertIn("nescīvisse", forms["inf_perf_act"])
        self.assertIn("nesciisse", forms["inf_perf_act"])

    def test_sum_fore(self):
        sum_data = {"voice": "act", "conj": None, "perf": "fu", "fap": "futūr",
                    "no_pass": True,
                    "irreg": {"forms": {"pres": {"act": {"inf": "esse"}}}}}
        forms = infinitive_paradigm("sum", sum_data)
        self.assertEqual(forms["inf_impf_act"], ["esse"])
        self.assertIn("fore", forms["inf_inst_act"])
        self.assertFalse(any(kind.endswith("_pass") for kind in forms))

    def test_missing_stems_do_not_fabricate(self):
        invalid = {"voice": "act", "conj": 3, "pres": "cad"}
        forms = infinitive_paradigm("cadō", invalid)
        self.assertEqual(set(forms), {"inf_impf_act", "inf_impf_pass"})


if __name__ == "__main__":
    unittest.main()
