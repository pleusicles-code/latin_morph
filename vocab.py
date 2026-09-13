import streamlit as st
import copy
import unicodedata


def _repo_match_key(value):
    value = unicodedata.normalize("NFD", str(value)).lower()
    return "".join(ch for ch in value if unicodedata.category(ch) != "Mn")

def _repo_values(value):
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        return list(value)
    return [value]

def filter_vocab_by_repo(vocab, repo_name):
    return {
        key: value for key, value in vocab.items()
        if repo_name in _repo_values(value.get("repo"))
    }


def filter_vocab_by_repos(vocab, repo_names):
    repo_names = set(repo_names)
    return {
        key: value for key, value in vocab.items()
        if repo_names.intersection(_repo_values(value.get("repo")))
    }

def _merge_repo_entries(vocab, additions, repo_name, preserve_core=None):
    preserve_core = {_repo_match_key(item) for item in (preserve_core or set())}
    for lemma, incoming in additions.items():
        incoming = copy.deepcopy(incoming)
        incoming.pop("repo", None)
        exact = next((key for key in vocab if unicodedata.normalize("NFC", key) == unicodedata.normalize("NFC", lemma)), None)
        canonical = _repo_match_key(lemma)
        existing_key = exact or next((key for key in vocab if _repo_match_key(key) == canonical), None)
        if existing_key is None:
            incoming["repo"] = repo_name
            vocab[lemma] = incoming
            continue

        existing = copy.deepcopy(vocab.pop(existing_key))
        repos = []
        for repo in _repo_values(existing.get("repo")) + [repo_name]:
            if repo not in repos:
                repos.append(repo)

        if canonical in preserve_core:
            merged = existing
            for field in ("meaning", "lemma_lexical", "number"):
                if field in incoming:
                    merged[field] = incoming[field]
        else:
            merged = existing
            merged.update(incoming)

        merged["repo"] = repos
        vocab[lemma] = merged

def _prefix_morphology(value, prefix):
    if isinstance(value, str):
        return prefix + value
    if isinstance(value, list):
        return [_prefix_morphology(item, prefix) for item in value]
    if isinstance(value, tuple):
        return tuple(_prefix_morphology(item, prefix) for item in value)
    if isinstance(value, dict):
        return {key: _prefix_morphology(item, prefix) for key, item in value.items()}
    return value

def _compound_verb_from_base(base_data, prefix, overrides):
    result = copy.deepcopy(base_data)
    result["repo"] = "alap1"
    for field in ("pres", "perf", "ppp", "fap", "gdv", "pap"):
        if field in result and result[field] is not None:
            result[field] = _prefix_morphology(result[field], prefix)
    if "irreg" in result:
        result["irreg"] = _prefix_morphology(result["irreg"], prefix)
    result.update(copy.deepcopy(overrides))
    result["repo"] = "alap1"
    return result


#@st.cache_data
def import_verbs():
    verb_vocab = {
        "sum": {
                   "repo": "core",
            "voice": "act",
            "no_pass": True,
            "conj": None,
            "irreg": {
                "irreg": True,
                "forms": {
                    "pres": {
                        "act": {
                            "ind": {
                                "sg": {1: "sum",
                                        2: "es",
                                        3: "est"},
                                "pl": {1: "sumus",
                                        2: "estis",
                                        3: "sunt"}},
                            "subj": {"sg": {1: "sim",
                                            2: "sīs",
                                            3: "sit"},
                                    "pl": {1: "sīmus",
                                            2: "sītis",
                                            3: "sint"}},
                            "impv": {"sg": {2: "es"},
                                    "pl": {2: "este"}},
                            "inf": "esse"}
                            },
                    "impf": {
                        "act": {
                            "ind": {
                                "sg": {1: "eram",
                                    2: "erās",
                                    3: "erat"},
                                "pl": {1: "erāmus",
                                        2: "erātis",
                                        3: "erant"}
                                },
                            }
                        },
                    "fut": {
                        "act": {
                            "ind": {
                                "sg": {1: "erō",
                                        2: "eris",
                                        3: "erit"},
                                "pl": {1: "erimus",
                                        2: "eritis",
                                        3: "erunt"}
                            },
                            "impv": {
                                "sg": {
                                    2: "estō",
                                    3: "estō"
                                },
                                "pl": {
                                    2: "estōte",
                                    3: "suntō"
                                }
                            },
                            # "inf": ["futūrum esse", "fore"]
                        }
                    },                
                }
            },
            # regular information
            "perf": "fu",
            "fap": "futūr",
            "pap": None,
            "gdv": None
            },
        "possum": {
                      "repo": "core",
            "voice": "act",
            "conj": None,
            "no_impv": True,
            "no_pass": True,
            "irreg": {
                "irreg": True,
                "forms": {
                    "pres": {
                        "act": {
                            "ind": {
                                "sg": {1: "possum",
                                        2: "potes",
                                        3: "potest"},
                                "pl": {1: "possumus",
                                        2: "potestis",
                                        3: "possunt"}},
                            "subj": {"sg": {1: "possim",
                                            2: "possīs",
                                            3: "possit"},
                                    "pl": {1: "possīmus",
                                            2: "possītis",
                                            3: "possint"}},
                            "inf": "posse"}
                            },
                    "impf": {
                        "act": {
                            "ind": {
                                "sg": {1: "poteram",
                                    2: "poterās",
                                    3: "poterat"},
                                "pl": {1: "poterāmus",
                                        2: "poterātis",
                                        3: "poterant"}
                                }
                            }
                        },
                    "fut": {
                        "act": {
                            "ind": {
                                "sg": {1: "poterō",
                                        2: "poteris",
                                        3: "poterit"},
                                "pl": {1: "poterimus",
                                        2: "poteritis",
                                        3: "poterunt"}
                            },
                        }
                    },                
                }
            },
            # regular information
            "perf": "potu",
            "pap": ("potēns", "potent"),
            "gdv": None
            },
        "ferō": {
                     "repo": "core",
            "voice": "act",
            "conj": 3,
            "irreg": {
                "irreg": True,
                "forms": {
                    "pres": {
                        "act": {
                            "ind": {
                                "sg": {
                                    1: "ferō",
                                    2: "fers",
                                    3: "fert"
                                    },
                                "pl": {
                                    1: "ferimus",
                                    2: "fertis",
                                    3: "ferunt"
                                    }
                                },
                            "inf": "ferre",
                            "impv": {
                                "sg": {2: "fer"},
                                "pl": {2: "ferte"}
                            }
                        },
                        "pass": {
                            "ind": {
                                "sg": {
                                    1: "feror",
                                    2: ["ferris", "ferre"],
                                    3: "fertur"
                                    },
                                "pl": {
                                    1: "ferimur",
                                    2: "feriminī",
                                    3: "feruntur"
                                }
                            },
                            "inf": "ferrī",
                            "impv": {
                                "sg": {2: "ferre"},
                                "pl": {2: "feriminī"}
                            }
                        }
                    },
                    "fut": {
                        "act": {
                            "impv": {
                                "sg": {
                                    2: "fertō",
                                    3: "fertō"
                                },
                                "pl": {
                                    2: "fertōte",
                                    3: "feruntō"
                                }
                            }
                        },
                        "pass": {
                            "impv": {
                                "sg": {
                                    2: "fertor",
                                    3: "fertor"
                                },
                                "pl": {
                                    3: "feruntor"
                                }
                            }
                        }
                    }
                }
            },
            "pres": "fer",
            "perf": "tul",
            "ppp": "lāt"
        },
        "eō": {
                   "repo": "core",
            "voice": "act",
            "impers_pass_only": True,
            "conj": 3,
            "irreg": {
                "irreg": True,
                "forms": {
                    "pres": {
                        "act": {
                            "ind": {
                                "sg": {
                                    1: "eō",
                                    2: "īs",
                                    3: "it"
                                },
                                "pl": {
                                    1: "īmus",
                                    2: "ītis",
                                    3: "eunt"
                                }
                            },
                            "inf": "īre",
                            "impv": {
                                "sg": {2: "ī"},
                                "pl": {2: "īte"}
                            }
                        },
                        "pass": {
                            "ind": {
                                "sg": {
                                    3: "ītur"
                                }
                            }
                        }
                    },
                    "fut": {
                        "act": {
                            "ind": {
                                "sg": {1: "ībō",
                                    2: "ībis",
                                    3: "ībit"},
                                "pl": {1: "ībimus",
                                    2: "ībitis",
                                    3: "ībunt"}
                            },
                            "impv": {
                                "sg": {
                                    2: "ītō",
                                    3: "ītō"
                                },
                                "pl": {
                                    2: "ītōte",
                                    3: "euntō"
                                }
                            }
                        },
                        "pass": {
                            "ind": {
                                "sg": {
                                    3: "ībitur"
                                }
                            }
                        }
                    },
                },
                "stems": {
                    "pres": {
                        "subj": "e"
                    }
                }
            },
            "pres": "ī",
            "perf": "īv", # need to figure out how to do alternative forms of perfect
            "ppp": "it",
            "pap": ("iēns", "eunt"),
            "gdv": "eund"
        },
        "volō": {
                     "repo": "core",
            "voice": "act",
            "no_pass": True,
            "conj": 3,
            "no_impv": True,
            "irreg": {
                "irreg": True,
                "forms": {
                    "pres": {
                        "act": {
                            "ind": {
                                "sg": {
                                    1: "volō",
                                    2: "vīs",
                                    3: "vult"
                                },
                                "pl": {
                                    1: "volumus",
                                    2: "vultis",
                                    3: "volunt"
                                }
                            },
                            "subj": {
                                "sg": {
                                    1: "velim",
                                    2: "velīs",
                                    3: "velit"
                                },
                                "pl": {
                                    1: "velīmus",
                                    2: "velītis",
                                    3: "velint"
                                }
                            },
                            "inf": "velle"
                        }
                    }
                }
            },
            "pres": "vol",
            "perf": "volu",
#            "pap": ("volēns", "volent"),
            "gdv": None
        },
        "nōlō": {
                      "repo": "core",
            "voice": "act",
            "no_pass": True,
            "conj": 3,
            "irreg": {
                "irreg": True,
                "forms": {
                    "pres": {
                        "act": {
                            "ind": {
                                "sg": {
                                    1: "nōlō",
                                    2: "nōn vīs",
                                    3: "nōn vult"
                                },
                                "pl": {
                                    1: "nōlumus",
                                    2: "nōn vultis",
                                    3: "nōlunt"
                                }
                            },
                            "subj": {
                                "sg": {
                                    1: "nōlim",
                                    2: "nōlīs",
                                    3: "nōlit"
                                },
                                "pl": {
                                    1: "nōlīmus",
                                    2: "nōlītis",
                                    3: "nōlint"
                                }
                            },
                            "inf": "nōlle",
                            "impv": {
                                "sg": {2: "nōlī"},
                                "pl": {2: "nōlīte"}
                            }
                        }
                    },
                    "fut": {
                        "act": {
                            "impv": {
                                "sg": {
                                    2: "nōlītō",
                                    3: "nōlītō"
                                },
                                "pl": {
                                    2: "nōlītōte",
                                    3: "nōluntō"
                                }
                            }
                        }
                    }
                }
            },
            "pres": "nōl",
            "perf": "nōlu",
#            "pap": ("nōlēns", "nōlent"),
            "gdv": None
        },
        "mālō": {
                      "repo": "core",
            "voice": "act",
            "no_pass": True,
            "conj": 3,
            "no_impv": True,
            "irreg": {
                "irreg": True,
                "forms": {
                    "pres": {
                        "act": {
                            "ind": {
                                "sg": {
                                    1: "mālō",
                                    2: "māvīs",
                                    3: "māvult"
                                },
                                "pl": {
                                    1: "mālumus",
                                    2: "māvultis",
                                    3: "mālunt"
                                }
                            },
                            "subj": {
                                "sg": {
                                    1: "mālim",
                                    2: "mālīs",
                                    3: "mālit"
                                },
                                "pl": {
                                    1: "mālīmus",
                                    2: "mālītis",
                                    3: "mālint"
                                }
                            },
                            "inf": "mālle"
                        }
                    }
                }
            },
            "pres": "māl",
            "perf": "mālu",
            "pap": None,
            "gdv": None
        },
    "fīō": {
                 "repo": "core",
            "voice": "semidep",
            "conj": 3,
            "pres": "fī",
            "ppp": "fact",
            "pap": None,
            "gdv": "faciend",
            "fap": None,
            "irreg": {
                "irreg": True,
                "forms": {
                    "pres": {
                        "act": {
                            "ind": {
                                "sg": {
                                    1: "fīō",
                                    2: "fīs",
                                    3: "fit"
                                },
                                "pl": {
                                    1: "fīmus",
                                    2: "fītis",
                                    3: "fīunt"
                                }
                            },
                            "impv": {
                                "sg": {2: "fī"},
                                "pl": {2: "fīte"}
                            },
                        },
                        "dep": {
                            "inf": "fierī"
                        }
                    }
                }
            }
        },

        ## REGULAR VERBS

        # when adding duco, dico, and facio, don't forget the irregular singular imperative

        ## ACTIVE
        ### 1st conj
        "amō": {"repo": "core", "voice": "act",
                "conj": 1,
                "pres": "am",
                "perf": "amāv",
                "ppp": "amāt"},
        "portō": {"repo": "core", "voice": "act",
                  "conj": 1,
                  "pres": "port",
                  "perf": "portāv",
                  "ppp": "portāt"},
        "parō": {"repo": "core", "voice": "act",
                  "conj": 1,
                  "pres": "par",
                  "perf": "parāv",
                  "ppp": "parāt"},
        "optō": {"repo": "core", "voice": "act",
                  "conj": 1,
                  "pres": "opt",
                  "perf": "optāv",
                  "ppp": "optāt"},
        "vocō": {"repo": "core", "voice": "act",
                 "conj": 1,
                 "pres": "voc",
                 "perf": "vocāv",
                 "ppp": "vocāt"},

        ### 2nd conj
        "habeō": {"repo": "core", "voice": "act",
                "conj": 2,
                "pres": "hab",
                "perf": "habu",
                "ppp": "habit"},
        "dēleō": {"repo": "core", "voice": "act",
                  "conj": 2,
                  "pres": "dēl",
                  "perf": "dēlēv",
                  "ppp": "dēlēt"},
        "spondeō": {"repo": "core", "voice": "act",
                    "conj": 2,
                    "pres": "spond",
                    "perf": "spopond",
                    "ppp": "spons"},
        "moneō": {"repo": "core", "voice": "act",
                  "conj": 2,
                  "pres": "mon",
                  "perf": "monu",
                  "ppp": "monit"},
        "impleō": {"repo": "core", "voice": "act",
                  "conj": 2,
                  "pres": "impl",
                  "perf": "implēv",
                  "ppp": "implēt"},
        "teneō": {"repo": "core", "voice": "act",
                  "conj": 2,
                  "pres": "ten",
                  "perf": "tenu",
                  "ppp": "tent"},

        ### 3rd conj
        "regō": {"repo": "core", "voice": "act",
                "conj": 3,
                "pres": "reg",
                "perf": "rēx",
                "ppp": "rect"},
        "fallō": {"repo": "core", "voice": "act",
                  "conj": 3,
                  "pres": "fall",
                  "perf": "fefell",
                  "ppp": "fals"},
        "legō": {"repo": "core", "voice": "act",
                 "conj": 3,
                 "pres": "leg",
                 "perf": "lēg",
                 "ppp": "lect"},
        "mittō": {"repo": "core", "voice": "act",
                 "conj": 3,
                 "pres": "mitt",
                 "perf": "mīs",
                 "ppp": "miss"},
        "dīcō": {"repo": "core", "voice": "act",
                 "conj": 3,
                 "pres": "dīc",
                 "perf": "dīx",
                 "ppp": "dict",
                 "irreg": {
                     "forms": {
                         "pres": {
                             "act": {
                                 "impv": {
                                     "sg": {
                                         2: "dīc"
                                     }
                                 }
                             }
                         }
                     }
                 }},
        "dūcō": {"repo": "core", "voice": "act",
                 "conj": 3,
                 "pres": "dūc",
                 "perf": "dūx",
                 "ppp": "duct",
                 "irreg": {
                     "forms": {
                         "pres": {
                             "act": {
                                 "impv": {
                                     "sg": {
                                         2: "dūc"
                                     }
                                 }
                             }
                         }
                     }
                 }},

        ### 3rd io conj
        "capiō": {"repo": "core", "voice": "act",
                "conj": "3io",
                "pres": "cap",
                "perf": "cēp",
                "ppp": "capt"},
        "fugiō": {"repo": "core", "voice": "act",
                  "conj": "3io",
                  "pres": "fug",
                  "perf": "fūg",
                  "ppp": "fugit"},
        "cupiō": {"repo": "core", "voice": "act",
                  "conj": "3io",
                  "pres": "cup",
                  "perf": "cupīv",
                  "ppp": "cupīt"},
        "incipiō": {"repo": "core", "voice": "act",
                "conj": "3io",
                "pres": "incip",
                "perf": "incēp",
                "ppp": "incept"},

        ### 4th conj
        "audiō": {"repo": "core", "voice": "act",
                "conj": 4,
                "pres": "aud",
                "perf": "audīv",
                "ppp": "audīt"},
        "sentiō": {"repo": "core", "voice": "act",
                "conj": 4,
                "pres": "sent",
                "perf": "sēns",
                "ppp": "sēns"},
        "veniō": {"repo": "core", "voice": "act",
                  "impers_pass_only": True,
                  "conj": 4,
                  "pres": "ven",
                  "perf": "vēn",
                  "ppp": "vent"},

        ## DEPONENT
        ### 1st conj
        "cōnor": {"repo": "core", "voice": "dep",
                "conj": 1,
                "pres": "cōn",
                "ppp": "cōnāt"},
        "precor": {"repo": "core", "voice": "dep",
                "conj": 1,
                "pres": "prec",
                "ppp": "precāt"},
        "mīror": {"repo": "core", "voice": "dep",
                "conj": 1,
                "pres": "mīr",
                "ppp": "mīrāt"},
        "vēnor": {"repo": "core", "voice": "dep",
                "conj": 1,
                "pres": "vēn",
                "ppp": "vēnāt"},
        "minor": {"repo": "core", "voice": "dep",
                "conj": 1,
                "pres": "min",
                "ppp": "mināt"},
        ### 2nd conj
        "fateor": {"repo": "core", "voice": "dep",
                "conj": 2,
                "pres": "fat",
                "ppp": "fass"},
        "reor": {"repo": "core", "voice": "dep",
                "conj": 2,
                "pres": "r",
                "ppp": "rat"},
        "vereor": {"repo": "core", "voice": "dep",
                "conj": 2,
                "pres": "ver",
                "ppp": "verit"},
        "polliceor": {"repo": "core", "voice": "dep",
                "conj": 2,
                "pres": "pollic",
                "ppp": "pollicit"},
        ### 3rd conj
        "sequor": {"repo": "core", "voice": "dep",
                "conj": 3,
                "pres": "sequ",
                "ppp": "secūt"},
        "nāscor": {"repo": "core", "voice": "dep",
                "conj": 3,
                "pres": "nāsc",
                "ppp": "nāt",},
        "ūtor": {"repo": "core", "voice": "dep",
                "conj": 3,
                "pres": "ūt",
                "ppp": "ūs",},
        "loquor": {"repo": "core", "voice": "dep",
                "conj": 3,
                "pres": "loqu",
                "ppp": "locūt",},
        ### 3rd io conj
        "morior": {"repo": "core", "voice": "dep",
                "conj": "3io",
                "pres": "mor",
                "ppp": "mortu",
                "fap": "moritūr"},
        "patior": {"repo": "core", "voice": "dep",
                "conj": "3io",
                "pres": "pat",
                "ppp": "pass"},
        "progredior": {"repo": "core", "voice": "dep",
                "conj": "3io",
                "pres": "progred",
                "ppp": "progress"},
        "ingredior": {"repo": "core", "voice": "dep",
                "conj": "3io",
                "pres": "ingred",
                "ppp": "ingress"},
        ### 4th conj
        "experior": {"repo": "core", "voice": "dep",
                "conj": 4,
                "pres": "exper",
                "ppp": "expert"},
        "mōlior": {"repo": "core", "voice": "dep",
                "conj": 4,
                "pres": "mōl",
                "ppp": "mōlīt"},
        "partior": {"repo": "core", "voice": "dep",
                "conj": 4,
                "pres": "part",
                "ppp": "partīt"},
        "mentior": {"repo": "core", "voice": "dep",
                "conj": 4,
                "pres": "ment",
                "ppp": "mentīt"},
        # orior has a number of 3rd conj. forms, so maybe best to omit
        # "orior": {"voice": "dep",
        #         "conj": 4,
        #         "pres": "or",
        #         "ppp": "ort",
        #         "fap": "oritūr",
        #         "gdv": "oriund"},
        ## SEMIDEPONENT
        "audeō": {"repo": "core", "voice": "semidep",
                "conj": 2,
                "pres": "aud",
                "ppp": "aus"},
        "gaudeō": {"repo": "core", "voice": "semidep",
                "conj": 2,
                "pres": "gaud",
                "ppp": "gāvīs"},
    }

    # BEGIN ALAP1 VERBS
    alap1_verbs = {'agō': {'repo': 'alap1',
         'meaning': 'hajt, űz, vezet, megindít, tesz, csinál, tárgyal',
         'voice': 'act',
         'conj': 3,
         'pres': 'ag',
         'perf': 'ēg',
         'ppp': 'act'},
 'cadō': {'repo': 'alap1',
          'meaning': 'leesik, lehull, meghal, kerül vhová, bekövetkezik',
          'voice': 'act',
          'conj': 3,
          'pres': 'cad',
          'perf': 'cecid',
          'fap': 'cāsūr'},
 'dō': {'repo': 'alap1',
        'meaning': 'ad, ajándékoz, adományoz, átenged',
        'voice': 'act',
        'conj': 1,
        'pres': 'd',
        'perf': 'ded',
        'ppp': 'dat',
        'irreg': {'irreg': True,
                  'forms': {'pres': {'act': {'ind': {'sg': {1: 'dō', 2: 'dās', 3: 'dat'},
                                                     'pl': {1: 'damus', 2: 'datis', 3: 'dant'}},
                                             'subj': {'sg': {1: 'dem', 2: 'dēs', 3: 'det'},
                                                      'pl': {1: 'dēmus', 2: 'dētis', 3: 'dent'}},
                                             'impv': {'sg': {2: 'dā'}, 'pl': {2: 'date'}},
                                             'inf': 'dare'},
                                     'pass': {'ind': {'sg': {1: 'dor', 2: ['daris', 'dare'], 3: 'datur'},
                                                      'pl': {1: 'damur', 2: 'daminī', 3: 'dantur'}},
                                              'subj': {'sg': {1: 'der', 2: ['dēris', 'dēre'], 3: 'dētur'},
                                                       'pl': {1: 'dēmur', 2: 'dēminī', 3: 'dentur'}},
                                              'impv': {'sg': {2: 'dare'}, 'pl': {2: 'daminī'}},
                                              'inf': 'darī'}},
                            'impf': {'act': {'ind': {'sg': {1: 'dabam', 2: 'dabās', 3: 'dabat'},
                                                     'pl': {1: 'dabāmus', 2: 'dabātis', 3: 'dabant'}},
                                             'subj': {'sg': {1: 'darem', 2: 'darēs', 3: 'daret'},
                                                      'pl': {1: 'darēmus', 2: 'darētis', 3: 'darent'}}},
                                     'pass': {'ind': {'sg': {1: 'dabar', 2: ['dabāris', 'dabāre'], 3: 'dabātur'},
                                                      'pl': {1: 'dabāmur', 2: 'dabāminī', 3: 'dabantur'}},
                                              'subj': {'sg': {1: 'darer', 2: ['darēris', 'darēre'], 3: 'darētur'},
                                                       'pl': {1: 'darēmur', 2: 'darēminī', 3: 'darentur'}}}},
                            'fut': {'act': {'ind': {'sg': {1: 'dabō', 2: 'dabis', 3: 'dabit'},
                                                    'pl': {1: 'dabimus', 2: 'dabitis', 3: 'dabunt'}},
                                            'impv': {'sg': {2: 'datō', 3: 'datō'}, 'pl': {2: 'datōte', 3: 'dantō'}}},
                                    'pass': {'ind': {'sg': {1: 'dabor', 2: ['daberis', 'dabere'], 3: 'dabitur'},
                                                     'pl': {1: 'dabimur', 2: 'dabiminī', 3: 'dabuntur'}},
                                             'impv': {'sg': {2: 'dator', 3: 'dator'}, 'pl': {3: 'dantor'}}}}}}},
 'faciō': {'repo': 'alap1',
           'meaning': 'tesz, csinál, alkot, okoz',
           'voice': 'act',
           'conj': '3io',
           'pres': 'fac',
           'perf': 'fēc',
           'ppp': 'fact'},
 'ferō': {'repo': 'alap1',
          'meaning': 'hord, visel, hoz, elvisz, eltűr, hírül hoz',
          'voice': 'act',
          'conj': None,
          'pres': 'fer',
          'perf': 'tul',
          'ppp': 'lāt'},
 'habeō': {'repo': 'alap1',
           'meaning': 'tart, birtokában van, visel, gondol (akit aminek kettős acc.)',
           'voice': 'act',
           'conj': 2,
           'pres': 'hab',
           'perf': 'habu',
           'ppp': 'habit'},
 'maneō': {'repo': 'alap1',
           'meaning': 'marad valahol, tartózkodik, megmarad, vár',
           'voice': 'act',
           'conj': 2,
           'pres': 'man',
           'perf': 'māns',
           'ppp': 'māns'},
 'mittō': {'repo': 'alap1',
           'meaning': 'küld, dob, vet, kiad, elenged',
           'voice': 'act',
           'conj': 3,
           'pres': 'mitt',
           'perf': 'mīs',
           'ppp': 'miss'},
 'pōnō': {'repo': 'alap1',
          'meaning': 'elhelyez, odatesz, alapít, felépít, áthelyez',
          'voice': 'act',
          'conj': 3,
          'pres': 'pōn',
          'perf': 'posu',
          'ppp': 'posit'},
 'respondeō': {'repo': 'alap1',
               'meaning': 'felel, válaszol, viszonoz',
               'voice': 'act',
               'conj': 2,
               'pres': 'respond',
               'perf': 'respond',
               'ppp': 'respōns'},
 'servō': {'repo': 'alap1',
           'meaning': 'megőriz, megment',
           'voice': 'act',
           'conj': 1,
           'pres': 'serv',
           'perf': 'servāv',
           'ppp': 'servāt'},
 'stō': {'repo': 'alap1',
         'meaning': 'áll, vesztegel, szilárdan áll',
         'voice': 'act',
         'conj': 1,
         'pres': 'st',
         'perf': 'stet',
         'fap': 'statūr'},
 'sum': {'repo': 'alap1', 'meaning': 'van, létezik, megtörténik', 'voice': 'act', 'conj': None, 'perf': 'fu'},
 'teneō': {'repo': 'alap1',
           'meaning': 'tart, fog, irányít, birtokol, úgy vél',
           'voice': 'act',
           'conj': 2,
           'pres': 'ten',
           'perf': 'tenu',
           'ppp': 'tent'},
 'trahō': {'repo': 'alap1',
           'meaning': 'húz, vonszol, elhurcol, zilál',
           'voice': 'act',
           'conj': 3,
           'pres': 'trah',
           'perf': 'trāx',
           'ppp': 'tract'},
 'veniō': {'repo': 'alap1',
           'meaning': 'jön, megy, érkezik, közeleg',
           'voice': 'act',
           'conj': 4,
           'pres': 'ven',
           'perf': 'vēn',
           'ppp': 'vent'},
 'videō': {'repo': 'alap1',
           'meaning': 'lát, észrevesz, belát, megért',
           'voice': 'act',
           'conj': 2,
           'pres': 'vid',
           'perf': 'vīd',
           'ppp': 'vīs'},
 'vincō': {'repo': 'alap1',
           'meaning': 'győz, nyer, legyőz, meggyőz, uralkodik vkin',
           'voice': 'act',
           'conj': 3,
           'pres': 'vinc',
           'perf': 'vīc',
           'ppp': 'vict'},
 'vīvō': {'repo': 'alap1',
          'meaning': 'él, életben van, vmiből él',
          'voice': 'act',
          'conj': 3,
          'pres': 'vīv',
          'perf': 'vīx',
          'fap': 'vīctūr'},
 'volō': {'repo': 'alap1',
          'meaning': 'akar, óhajt',
          'voice': 'act',
          'conj': None,
          'lemma_lexical': 'volō [akar]',
          'pres': 'vol',
          'perf': 'volu'},
 'abeō': {'repo': 'alap1',
          'meaning': 'elmegy, elvonul,elmenekül',
          'voice': 'act',
          'conj': 3,
          'pres': 'abī',
          'perf': 'abi',
          'ppp': 'abit'},
 'absum': {'repo': 'alap1',
           'meaning': 'távol van, nincs jelen,hiányzik',
           'voice': 'act',
           'conj': None,
           'pres': 'abs',
           'perf': 'āfu'},
 'accipiō': {'repo': 'alap1',
             'meaning': 'kap, fogad, befogad, elfogad, megért',
             'voice': 'act',
             'conj': '3io',
             'pres': 'accip',
             'perf': 'accēp',
             'ppp': 'accept'},
 'adeō': {'repo': 'alap1',
          'meaning': 'odamegy, közeledik, kér, hozzáfog',
          'voice': 'act',
          'conj': 3,
          'pres': 'adī',
          'perf': 'adi',
          'ppp': 'adit'},
 'adsum': {'repo': 'alap1',
           'meaning': 'itt van, jelen van, megjelenik, + dat. segít',
           'voice': 'act',
           'conj': None,
           'pres': 'ads',
           'perf': 'adfu'},
 'amō': {'repo': 'alap1',
         'meaning': 'szeret, kedvel, kedvét leli',
         'voice': 'act',
         'conj': 1,
         'pres': 'am',
         'perf': 'amāv',
         'ppp': 'amāt'},
 'audiō': {'repo': 'alap1',
           'meaning': 'hall, hallgat, megtud',
           'voice': 'act',
           'conj': 4,
           'pres': 'aud',
           'perf': 'audīv',
           'ppp': 'audīt'},
 'capiō': {'repo': 'alap1',
           'meaning': 'fog, megfog, felfog, elfoglal',
           'voice': 'act',
           'conj': '3io',
           'pres': 'cap',
           'perf': 'cēp',
           'ppp': 'capt'},
 'consulō': {'repo': 'alap1',
             'meaning': 'meggondol, tanácskozik, határoz, tanácsot kér (akitől acc)',
             'voice': 'act',
             'conj': 3,
             'pres': 'consul',
             'perf': 'consulu',
             'ppp': 'consult'},
 'dēserō': {'repo': 'alap1',
            'meaning': 'elhagy, otthagy',
            'voice': 'act',
            'conj': 3,
            'pres': 'dēser',
            'perf': 'dēseru',
            'ppp': 'dēsert'},
 'dīcō': {'repo': 'alap1',
          'meaning': 'mond, beszél, előad, mutat, megszab',
          'voice': 'act',
          'conj': 3,
          'pres': 'dīc',
          'perf': 'dīx',
          'ppp': 'dict'},
 'dōnō': {'repo': 'alap1',
          'meaning': 'ajándékoz, ad',
          'voice': 'act',
          'conj': 1,
          'pres': 'dōn',
          'perf': 'dōnāv',
          'ppp': 'dōnāt'},
 'dūcō': {'repo': 'alap1',
          'meaning': 'húz, von, alakít, vonz, vezet, gondol vmit',
          'voice': 'act',
          'conj': 3,
          'pres': 'dūc',
          'perf': 'dūx',
          'ppp': 'duct'},
 'eō': {'repo': 'alap1',
        'meaning': 'megy, ,jár, indul, nekifog, elmúlik',
        'voice': 'act',
        'conj': 3,
        'lemma_lexical': 'eō [ige]',
        'pres': 'ī',
        'perf': 'īv',
        'ppp': 'it'},
 'frangō': {'repo': 'alap1',
            'meaning': 'tör, eltör, megfékez, megrendít, megaláz',
            'voice': 'act',
            'conj': 3,
            'pres': 'frang',
            'perf': 'frēg',
            'ppp': 'fract'},
 'gerō': {'repo': 'alap1',
          'meaning': 'hord, visz, visel, mutat, végez',
          'voice': 'act',
          'conj': 3,
          'pres': 'ger',
          'perf': 'gess',
          'ppp': 'gest'},
 'habitō': {'repo': 'alap1',
            'meaning': 'lakik, tartózkodik, időzik',
            'voice': 'act',
            'conj': 1,
            'pres': 'habit',
            'perf': 'habitāv',
            'ppp': 'habitāt'},
 'intrō': {'repo': 'alap1',
           'meaning': 'belép, behatol, bemegy',
           'voice': 'act',
           'conj': 1,
           'pres': 'intr',
           'perf': 'intrāv',
           'ppp': 'intrāt'},
 'inveniō': {'repo': 'alap1',
             'meaning': 'rájön, rátalál, elnyer',
             'voice': 'act',
             'conj': 4,
             'pres': 'inven',
             'perf': 'invēn',
             'ppp': 'invent'},
 'lateō': {'repo': 'alap1',
           'meaning': 'rejtőzik, bújik, lappang',
           'voice': 'act',
           'conj': 2,
           'pres': 'lat',
           'perf': 'latu'},
 'līberō': {'repo': 'alap1',
            'meaning': 'megszabadít, felszabadít',
            'voice': 'act',
            'conj': 1,
            'pres': 'līber',
            'perf': 'līberāv',
            'ppp': 'līberāt'},
 'loquor': {'repo': 'alap1', 'meaning': 'beszél', 'voice': 'dep', 'conj': 3, 'pres': 'loqu', 'ppp': 'locūt'},
 'morior': {'repo': 'alap1', 'meaning': 'meghal', 'voice': 'dep', 'conj': '3io', 'pres': 'mor', 'ppp': 'mortu'},
 'moveō': {'repo': 'alap1',
           'meaning': 'mozgat, felkavar, indít, okoz',
           'voice': 'act',
           'conj': 2,
           'pres': 'mov',
           'perf': 'mōv',
           'ppp': 'mōt'},
 'nāscor': {'repo': 'alap1',
            'meaning': 'születik, származik, ered',
            'voice': 'dep',
            'conj': 3,
            'pres': 'nāsc',
            'ppp': 'nāt'},
 'nōminō': {'repo': 'alap1',
            'meaning': 'nevez, elnevez, néven szólít',
            'voice': 'act',
            'conj': 1,
            'pres': 'nōmin',
            'perf': 'nōmināv',
            'ppp': 'nōmināt'},
 'ostendō': {'repo': 'alap1',
             'meaning': 'mutat, elébe nyújt, kijelent',
             'voice': 'act',
             'conj': 3,
             'pres': 'ostend',
             'perf': 'ostend',
             'ppp': 'ostent'},
 'possum': {'repo': 'alap1',
            'meaning': 'képes, tud, bír, -hat/het',
            'voice': 'act',
            'conj': None,
            'pres': 'poss',
            'perf': 'potu'},
 'praebeō': {'repo': 'alap1',
             'meaning': 'odanyújt, ad, átad',
             'voice': 'act',
             'conj': 2,
             'pres': 'praeb',
             'perf': 'praebu',
             'ppp': 'praebit'},
 'pugnō': {'repo': 'alap1',
           'meaning': 'harcol, küzd',
           'voice': 'act',
           'conj': 1,
           'pres': 'pugn',
           'perf': 'pugnāv',
           'ppp': 'pugnāt'},
 'putō': {'repo': 'alap1',
          'meaning': 'gondol, hisz, becsül, rendez',
          'voice': 'act',
          'conj': 1,
          'pres': 'put',
          'perf': 'putāv',
          'ppp': 'putāt'},
 'quaerō': {'repo': 'alap1',
            'meaning': 'keres, kér, kutat, kérdez',
            'voice': 'act',
            'conj': 3,
            'pres': 'quaer',
            'perf': 'quaesīv',
            'ppp': 'quaesīt'},
 'rēgnō': {'repo': 'alap1',
           'meaning': 'uralkodik, parancsol',
           'voice': 'act',
           'conj': 1,
           'pres': 'rēgn',
           'perf': 'rēgnāv',
           'ppp': 'rēgnāt'},
 'regō': {'repo': 'alap1',
          'meaning': 'irányít, igazgat, uralkodik, vezérel',
          'voice': 'act',
          'conj': 3,
          'pres': 'reg',
          'perf': 'rēx',
          'ppp': 'rēct'},
 'rogō': {'repo': 'alap1',
          'meaning': 'kérdez, kér, kíván',
          'voice': 'act',
          'conj': 1,
          'pres': 'rog',
          'perf': 'rogāv',
          'ppp': 'rogāt'},
 'spectō': {'repo': 'alap1',
            'meaning': 'néz, szemlél',
            'voice': 'act',
            'conj': 1,
            'pres': 'spect',
            'perf': 'spectāv',
            'ppp': 'spectāt'},
 'spernō': {'repo': 'alap1',
            'meaning': 'elutasít, megvet',
            'voice': 'act',
            'conj': 3,
            'pres': 'spern',
            'perf': 'sprēv',
            'ppp': 'sprēt'},
 'trānseō': {'repo': 'alap1',
             'meaning': 'átmegy, -hatol, elmúlik, eltölt',
             'voice': 'act',
             'conj': 3,
             'pres': 'trānsī',
             'perf': 'trānsi',
             'ppp': 'trānsit'},
 'triumphō': {'repo': 'alap1',
              'meaning': 'diadalmenetet tart, ujjong, diadalmaskodik',
              'voice': 'act',
              'conj': 1,
              'pres': 'triumph',
              'perf': 'triumphāv',
              'ppp': 'triumphāt'},
 'ūtor': {'repo': 'alap1',
          'meaning': 'hasznát veszi vminek, használ, alkalmaz',
          'voice': 'dep',
          'conj': 3,
          'pres': 'ūt',
          'ppp': 'ūs'},
 'vocō': {'repo': 'alap1',
          'meaning': 'kiált, hív, szólít, nevez',
          'voice': 'act',
          'conj': 1,
          'pres': 'voc',
          'perf': 'vocāv',
          'ppp': 'vocāt'},
 'vulnerō': {'repo': 'alap1',
             'meaning': 'megsebesít, megsért, bánt, bosszant',
             'voice': 'act',
             'conj': 1,
             'pres': 'vulner',
             'perf': 'vulnerāv',
             'ppp': 'vulnerāt'}}

    for _lemma, _base, _prefix in (
        ("abeō", "eō", "ab"),
        ("adeō", "eō", "ad"),
        ("trānseō", "eō", "trāns"),
        ("absum", "sum", "ab"),
        ("adsum", "sum", "ad"),
    ):
        _reviewed = alap1_verbs[_lemma]
        _compound = _compound_verb_from_base(verb_vocab[_base], _prefix, _reviewed)
        if _base == "sum":
            _compound["fap"] = "āfutūr" if _lemma == "absum" else "adfutūr"
        alap1_verbs[_lemma] = _compound

    _merge_repo_entries(
        verb_vocab,
        alap1_verbs,
        "alap1",
        preserve_core=['eō', 'ferō', 'possum', 'sum', 'volō'],
    )
    # END ALAP1 VERBS

    # BEGIN ALAP2 VERBS
    alap2_verbs = {'accēdō': {'voice': 'act', 'conj': 3, 'meaning': 'odamegy, járul, közeledik', 'pres': 'accēd', 'perf': 'access', 'ppp': 'access'},
     'aestimō': {'voice': 'act', 'conj': 1, 'meaning': 'felbecsül, értékel, vél, gondol', 'pres': 'aestim'},
     'appellō': {'voice': 'act', 'conj': 1, 'meaning': 'megszólít, szól, megnevez, nevez vminek', 'pres': 'appell'},
     'arbitror': {'voice': 'dep', 'conj': 1, 'meaning': 'kikémlel, vél, gondol', 'pres': 'arbitr', 'ppp': 'arbitrāt'},
     'ārdeō': {'voice': 'act', 'conj': 2, 'meaning': 'ég, lángol', 'pres': 'ārd', 'perf': 'ārs', 'fap': 'ārsūr'},
     'armō': {'voice': 'act', 'conj': 1, 'meaning': 'fölszerel, fölfegyverez', 'pres': 'arm'},
     'cēdō': {'voice': 'act', 'conj': 3, 'meaning': 'megy vhová, enged, hátrál', 'pres': 'cēd', 'perf': 'cess', 'ppp': 'cess'},
     'cēnseō': {'voice': 'act', 'conj': 2, 'meaning': 'számba vesz, felbecsül, gondol, indítványoz', 'pres': 'cēns', 'perf': 'cēnsu', 'ppp': 'cēns'},
     'clāmō': {'voice': 'act', 'conj': 1, 'meaning': 'kiabál, szólít, nevez, előhív', 'pres': 'clām'},
     'compleō': {'voice': 'act', 'conj': 2, 'meaning': 'megtölt, megrak, letölt, befejez', 'pres': 'compl', 'perf': 'complēv', 'ppp': 'complēt'},
     'concurrō': {'voice': 'act', 'conj': 3, 'meaning': 'összefut, összecsap, egybeesik', 'pres': 'concurr', 'perf': 'concurs', 'ppp': 'concurs'},
     'conveniō': {'voice': 'act', 'conj': 4, 'meaning': 'összejön, gyülekezik, egyetért', 'pres': 'conven', 'perf': 'convēn', 'ppp': 'convent'},
     'currō': {'voice': 'act', 'conj': 3, 'meaning': 'fut, szalad', 'pres': 'curr', 'perf': 'cucurr', 'ppp': 'curs'},
     'doceō': {'voice': 'act', 'conj': 2, 'meaning': 'tanít, oktat, értesít, kifejt', 'pres': 'doc', 'perf': 'docu', 'ppp': 'doct'},
     'ēveniō': {'voice': 'act', 'conj': 4, 'meaning': 'kijön, megtörténik, sikerül', 'pres': 'ēven', 'perf': 'ēvēn', 'ppp': 'ēvent'},
     'fallō': {'voice': 'act', 'conj': 3, 'meaning': 'megtéveszt, megcsal, elbuktat', 'pres': 'fall', 'perf': 'fefell', 'ppp': 'fals'},
     'fīō': {'voice': 'act', 'conj': None, 'meaning': 'lesz, keletkezik, lesz vmivé', 'ppp': 'fact'},
     'fugiō': {'voice': 'act', 'conj': '3io', 'meaning': 'elfut, -menekül, megfutamodik, elsiet', 'pres': 'fug', 'perf': 'fūg', 'fap': 'fugitūr'},
     'ignōrō': {'voice': 'act', 'conj': 1, 'meaning': 'nem tud, nem ismer', 'pres': 'ignōr'},
     'imperō': {'voice': 'act', 'conj': 1, 'meaning': 'parancsol, követel, uralkodik', 'pres': 'imper'},
     'īnstituō': {'voice': 'act', 'conj': 3, 'meaning': 'felállít, elrendel, bevezet', 'pres': 'īnstitu', 'perf': 'īnstitu', 'ppp': 'īnstitūt'},
     'interficiō': {'voice': 'act', 'conj': '3io', 'meaning': 'meggyilkol, megöl, tönkretesz', 'pres': 'interfic', 'perf': 'interfēc', 'ppp': 'interfect'},
     'interrogō': {'voice': 'act', 'conj': 1, 'meaning': 'kérdez,megkérdez,bevádol', 'pres': 'interrog'},
     'iubeō': {'voice': 'act', 'conj': 2, 'meaning': 'megparancsol, felszólít, utasít, elrendel', 'pres': 'iub', 'perf': 'iuss', 'ppp': 'iuss'},
     'legō': {'voice': 'act', 'conj': 3, 'meaning': 'kiválaszt, összegyűjt, olvas', 'pres': 'leg', 'perf': 'lēg', 'ppp': 'lēct'},
     'mūniō': {'voice': 'act', 'conj': 4, 'meaning': 'megerősít, megvéd, épít', 'pres': 'mūn', 'perf': 'mūnīv', 'ppp': 'mūnīt'},
     'narrō': {'voice': 'act', 'conj': 1, 'meaning': 'elmesél, beszél, mond, előad, említ', 'pres': 'narr'},
     'nesciō': {'voice': 'act', 'conj': 4, 'meaning': 'nem tud, nem ismer', 'pres': 'nesc', 'perf': 'nescīv', 'ppp': 'nescīt'},
     'nōscō': {'voice': 'act', 'conj': 3, 'meaning': 'megismer, tud, észrevesz, megszemlél', 'pres': 'nōsc', 'perf': 'nōv', 'ppp': 'nōt'},
     'numerō': {'voice': 'act', 'conj': 1, 'meaning': 'számlál, olvas, kifizet, valahová sorol', 'pres': 'numer'},
     'patior': {'voice': 'dep', 'conj': '3io', 'meaning': 'elvisel, eltűr, elszenved, enged', 'pres': 'pat', 'ppp': 'pass'},
     'petō': {'voice': 'act', 'conj': 3, 'meaning': 'megy (ahová acc.), törekszik vmire, kér, követel, rátör, siet', 'pres': 'pet', 'perf': 'petīv', 'ppp': 'petīt'},
     'placeō': {'voice': 'act', 'conj': 2, 'meaning': 'tetszik, ,jónak lát, jónak tűnik, vél, elhatároz', 'pres': 'plac', 'perf': 'placu', 'ppp': 'placit'},
     'relinquō': {'voice': 'act', 'conj': 3, 'meaning': 'hátrahagy, életben hagy, átenged, elhagy', 'pres': 'relinqu', 'perf': 'relīqu', 'ppp': 'relict'},
     'repetō': {'voice': 'act', 'conj': 3, 'meaning': 'megismétel, visszamegy, követel', 'pres': 'repet', 'perf': 'repetīv', 'ppp': 'repetīt'},
     'restituō': {'voice': 'act', 'conj': 3, 'meaning': 'visszahelyez, helyére állít, újra felépít, rendbe hoz', 'pres': 'restitu', 'perf': 'restitu', 'ppp': 'restitūt'},
     'rīdeō': {'voice': 'act', 'conj': 2, 'meaning': 'nevet, mosolyog', 'pres': 'rīd', 'perf': 'rīs', 'ppp': 'rīs'},
     'sapiō': {'voice': 'act', 'conj': '3io', 'meaning': 'ízlel, észlel, bölcs, eszes', 'pres': 'sap', 'perf': 'sapi'},
     'sciō': {'voice': 'act', 'conj': 4, 'meaning': 'tud, ismer, ért vmihez', 'pres': 'sc', 'perf': 'scīv', 'ppp': 'scīt'},
     'scrībō': {'voice': 'act', 'conj': 3, 'meaning': 'ír, megír, előad, rajzol', 'pres': 'scrīb', 'perf': 'scrīps', 'ppp': 'scrīpt'},
     'sedeō': {'voice': 'act', 'conj': 2, 'meaning': 'ül, ülésezik, tartózkodik', 'pres': 'sed', 'perf': 'sēd', 'ppp': 'sess'},
     'sentiō': {'voice': 'act', 'conj': 4, 'meaning': 'érez, észrevesz, észlel, vél, gondol', 'pres': 'sent', 'perf': 'sēns', 'ppp': 'sēns'},
     'serviō': {'voice': 'act', 'conj': 4, 'meaning': 'szolgál, kedvében jár, alkalmazkodik', 'pres': 'serv', 'perf': 'servīv', 'ppp': 'servīt'},
     'spērō': {'voice': 'act', 'conj': 1, 'meaning': 'remél', 'pres': 'spēr'},
     'studeō': {'voice': 'act', 'conj': 2, 'meaning': 'fáradozik, igyekszik, törekszik, tanul', 'pres': 'stud', 'perf': 'studu'},
     'taceō': {'voice': 'act', 'conj': 2, 'meaning': 'hallgat, elhallgat vmit, csendben van', 'pres': 'tac', 'perf': 'tacu', 'ppp': 'tacit'},
     'tangō': {'voice': 'act', 'conj': 3, 'meaning': 'érint, elér, bánt, sért', 'pres': 'tang', 'perf': 'tetig', 'ppp': 'tāct'},
     'tendō': {'voice': 'act', 'conj': 3, 'meaning': 'feszít, törekszik, tart vhová', 'pres': 'tend', 'perf': 'tetend', 'ppp': 'tent'},
     'tollō': {'voice': 'act', 'conj': 3, 'meaning': 'felemel, magasba emel, kiemel, megsemmisít', 'pres': 'toll', 'perf': 'sustul', 'ppp': 'sublāt'},
     'valeō': {'voice': 'act', 'conj': 2, 'meaning': 'erős, egészséges, érvényben van', 'pres': 'val', 'perf': 'valu', 'fap': 'valitūr'},
     'volō [repül]': {'voice': 'act', 'conj': 1, 'meaning': 'repül, siet, rohan', 'lemma_lexical': 'volō [repül]', 'pres': 'vol'}}
    _merge_repo_entries(
        verb_vocab,
        alap2_verbs,
        "alap2",
        preserve_core={'legō', 'fugiō', 'fallō', 'fīō', 'sentiō', 'patior'},
    )
    # END ALAP2 VERBS

    # BEGIN ALAP3 VERBS
    alap3_verbs = {'accūsō': {'meaning': 'vádol, bepanaszol, panaszkodik', 'voice': 'act', 'conj': 1, 'pres': 'accūs'},
 'advertō': {'meaning': 'odafordít, irányít, magára von',
             'voice': 'act',
             'conj': 3,
             'pres': 'advert',
             'perf': 'advert',
             'ppp': 'advers'},
 'agitō': {'meaning': 'mozgat, hajt, mozgásba hoz, tárgyal', 'voice': 'act', 'conj': 1, 'pres': 'agit'},
 'aperiō': {'meaning': 'feltár, kinyit, felfed, előad',
            'voice': 'act',
            'conj': 4,
            'pres': 'aper',
            'perf': 'aperu',
            'ppp': 'apert'},
 'appāreō': {'meaning': 'megjelenik',
             'voice': 'act',
             'conj': 2,
             'pres': 'appār',
             'perf': 'appāru',
             'ppp': 'appārit',
             'no_pass': True},
 'appetō': {'meaning': 'megy vhová, törekszik valamire, megkíván, rátör',
            'voice': 'act',
            'conj': 3,
            'pres': 'appet',
            'perf': 'appetīv',
            'ppp': 'appetīt'},
 'arceō': {'meaning': 'távol tart, eltávolít, visszatart, megóv',
           'voice': 'act',
           'conj': 2,
           'pres': 'arc',
           'perf': 'arcu'},
 'audeō': {'meaning': 'kedve van vmihez, rászánja magát, mer, merészel',
           'voice': 'semidep',
           'conj': 2,
           'pres': 'aud',
           'ppp': 'aus'},
 'augeō': {'meaning': 'gyarapít, növel, fokoz, megtermékenyít',
           'voice': 'act',
           'conj': 2,
           'pres': 'aug',
           'perf': 'aux',
           'ppp': 'auct'},
 'careō': {'meaning': 'nélkülöz vmit, híján van vminek (+abl.)',
           'voice': 'act',
           'conj': 2,
           'pres': 'car',
           'perf': 'caru',
           'no_pass': True},
 'caveō': {'meaning': 'óvakodik vkitől, vmitől /acc./',
           'voice': 'act',
           'conj': 2,
           'pres': 'cav',
           'perf': 'cāv',
           'ppp': 'caut'},
 'circumdō': {'meaning': 'körülvesz vmit (dat.) vmivel (acc.)',
              'voice': 'act',
              'conj': 1,
              'pres': 'circumd',
              'perf': 'circumded',
              'ppp': 'circumdat'},
 'claudō': {'meaning': 'bezár, lezár, bevégez',
            'voice': 'act',
            'conj': 3,
            'pres': 'claud',
            'perf': 'claus',
            'ppp': 'claus'},
 'colligō': {'meaning': 'összeszed, összegyűjt, következtet, végiggondol',
             'voice': 'act',
             'conj': 3,
             'pres': 'collig',
             'perf': 'collēg',
             'ppp': 'collect'},
 'commūnicō': {'meaning': 'egyesít, közössé tesz, megoszt, megbeszél', 'voice': 'act', 'conj': 1, 'pres': 'commūnic'},
 'coniūrō': {'meaning': 'együtt esküszik, felesküszik, összeesküszik', 'voice': 'act', 'conj': 1, 'pres': 'coniūr'},
 'cōnstō': {'meaning': 'áll vmiből, helytáll, megáll, ismeretes(+ acc. c. inf.)',
            'voice': 'act',
            'conj': 1,
            'pres': 'cōnst',
            'perf': 'constit',
            'fap': 'constāt',
            'no_pass': True},
 'creō': {'meaning': 'alkot, teremt, csinál, nemz, szül', 'voice': 'act', 'conj': 1, 'pres': 'cre'},
 'crēscō': {'meaning': 'nő, terem, növekszik',
            'voice': 'act',
            'conj': 3,
            'pres': 'crēsc',
            'perf': 'crēv',
            'ppp': 'crēt',
            'no_pass': True},
 'cupiō': {'meaning': 'vágyódik, kíván, érdeklődik',
           'voice': 'act',
           'conj': '3io',
           'pres': 'cup',
           'perf': 'cupīv',
           'ppp': 'cupīt'},
 'damnō': {'meaning': 'elítél, kárhoztat, rosszall', 'voice': 'act', 'conj': 1, 'pres': 'damn'},
 'dēbeō': {'meaning': 'tartozik, kénytelen, kell, adós vmivel',
           'voice': 'act',
           'conj': 2,
           'pres': 'dēb',
           'perf': 'dēbu',
           'ppp': 'dēbit'},
 'dēcrēscō': {'meaning': 'csökken, fogy, apad, gyengül',
              'voice': 'act',
              'conj': 3,
              'pres': 'dēcrēsc',
              'perf': 'dēcrēv',
              'ppp': 'dēcrēt',
              'no_pass': True},
 'dīligō': {'meaning': 'kedvel, szeret, becsül',
            'voice': 'act',
            'conj': 3,
            'pres': 'dīlig',
            'perf': 'dīlēx',
            'ppp': 'dīlect'},
 'doleō': {'meaning': 'fájlal, fáj, szenved, szomorkodik',
           'voice': 'act',
           'conj': 2,
           'pres': 'dol',
           'perf': 'dolu',
           'fap': 'dolit'},
 'dormiō': {'meaning': 'alszik, vesztegel, tétlenkedik',
            'voice': 'act',
            'conj': 4,
            'pres': 'dorm',
            'perf': 'dormīv',
            'ppp': 'dormīt',
            'no_pass': True},
 'dubitō': {'meaning': 'kételkedik', 'voice': 'act', 'conj': 1, 'pres': 'dubit'},
 'egeō': {'meaning': 'szükséget szenved', 'voice': 'act', 'conj': 2, 'pres': 'eg', 'perf': 'egu', 'no_pass': True},
 'ēligō': {'meaning': 'kiszed, kiválaszt, válogat',
           'voice': 'act',
           'conj': 3,
           'pres': 'ēlig',
           'perf': 'ēlēg',
           'ppp': 'ēlect'},
 'ēripiō': {'meaning': 'kiragad, elragad',
            'voice': 'act',
            'conj': '3io',
            'pres': 'ērip',
            'perf': 'ēripu',
            'ppp': 'ērept'},
 'exerceō': {'meaning': 'gyakorol, edz',
             'voice': 'act',
             'conj': 2,
             'pres': 'exerc',
             'perf': 'exercu',
             'ppp': 'exercit'},
 'expediō': {'meaning': 'elold, kiszabadít, lebonyolít, előteremt',
             'voice': 'act',
             'conj': 4,
             'pres': 'exped',
             'perf': 'expedīv',
             'ppp': 'expedīt'},
 'exspectō': {'meaning': 'vár, várakozik, elvár, megvár', 'voice': 'act', 'conj': 1, 'pres': 'exspect'},
 'fundō': {'meaning': 'önt, ont', 'voice': 'act', 'conj': 3, 'pres': 'fund', 'perf': 'fūd', 'ppp': 'fūs'},
 'horreō': {'meaning': 'elborzad, mered, megrémül',
            'voice': 'act',
            'conj': 2,
            'pres': 'horr',
            'perf': 'horru',
            'no_pass': True},
 'hortor': {'meaning': 'bátorít, buzdít, indít', 'voice': 'dep', 'conj': 1, 'pres': 'hort', 'ppp': 'hortāt'},
 'imitor': {'meaning': 'utánoz, színlel, ábrázol, hasonlít',
            'voice': 'dep',
            'conj': 1,
            'pres': 'imit',
            'ppp': 'imitāt'},
 'impellō': {'meaning': 'megüt, űz, mozgásba hoz, leterít, kényszerít vmire',
             'voice': 'act',
             'conj': 3,
             'pres': 'impell',
             'perf': 'impul',
             'ppp': 'impuls'},
 'impōnō': {'meaning': 'bele-, oda-, rátesz, ráhelyez, létesít',
            'voice': 'act',
            'conj': 3,
            'pres': 'impōn',
            'perf': 'imposu',
            'ppp': 'imposit'},
 'invideō': {'meaning': 'irigyel, gyűlöl, sajnál, féltékeny, rossz szemmel néz',
             'voice': 'act',
             'conj': 2,
             'pres': 'invid',
             'perf': 'invīd',
             'ppp': 'invīs',
             'no_pass': True},
 'mandō': {'meaning': 'rábíz, átad, megbíz valakit', 'voice': 'act', 'conj': 1, 'pres': 'mand'},
 'ministrō': {'meaning': 'felhord, szolgál, nyújt, segít vmiben', 'voice': 'act', 'conj': 1, 'pres': 'ministr'},
 'misceō': {'meaning': 'kever, vegyít, egyesít',
            'voice': 'act',
            'conj': 2,
            'pres': 'misc',
            'perf': 'miscu',
            'ppp': 'mixt'},
 'moneō': {'meaning': 'figyelmeztet', 'voice': 'act', 'conj': 2, 'pres': 'mon', 'perf': 'monu', 'ppp': 'monit'},
 'notō': {'meaning': 'fel-, megjegyez, jelöl, ír', 'voice': 'act', 'conj': 1, 'pres': 'not'},
 'observō': {'meaning': '(meg)figyel, ügyel vmire, tekintetbe vesz', 'voice': 'act', 'conj': 1, 'pres': 'observ'},
 'obstō': {'meaning': 'vki, vmi előtt áll, szembenáll, ellenáll, akadályoz',
           'voice': 'act',
           'conj': 1,
           'pres': 'obst',
           'perf': 'obstit',
           'fap': 'obstāt',
           'no_pass': True},
 'occidō': {'meaning': 'leesik, lemegy, lenyugszik, elpusztul',
            'voice': 'act',
            'conj': 3,
            'pres': 'occid',
            'perf': 'occid',
            'ppp': 'occās',
            'lemma_lexical': 'occidō [leesik]',
            'no_pass': True},
 'occīdō': {'meaning': 'megöl, gyilkol, gyötör',
            'voice': 'act',
            'conj': 3,
            'pres': 'occīd',
            'perf': 'occīd',
            'ppp': 'occīs',
            'lemma_lexical': 'occīdō [megöl]'},
 'occupō': {'meaning': 'elfoglal, bevesz, megtámad', 'voice': 'act', 'conj': 1, 'pres': 'occup'},
 'optō': {'meaning': 'kíván, óhajt, kiszemel, kiválaszt', 'voice': 'act', 'conj': 1, 'pres': 'opt'},
 'ōrō': {'meaning': 'kér, könyörög, beszél, szónokol, imádkozik', 'voice': 'act', 'conj': 1, 'pres': 'ōr'},
 'parcō': {'meaning': 'megkímél (akit dat.), abbahagy, takarékoskodik',
           'voice': 'act',
           'conj': 3,
           'pres': 'parc',
           'perf': 'peperc',
           'fap': 'pars'},
 'pāreō': {'meaning': 'engedelmeskedik, enged, megjelenik',
           'voice': 'act',
           'conj': 2,
           'pres': 'pār',
           'perf': 'pāru',
           'fap': 'pārit',
           'no_pass': True},
 'parō': {'meaning': 'előkészít, felszerel, készülődik vmire', 'voice': 'act', 'conj': 1, 'pres': 'par'},
 'pateō': {'meaning': 'nyitva áll, nyilvánvaló, kiderül, kiterjed',
           'voice': 'act',
           'conj': 2,
           'pres': 'pat',
           'perf': 'patu',
           'no_pass': True},
 'perdō': {'meaning': 'tönkretesz, elpusztít, megront',
           'voice': 'act',
           'conj': 3,
           'pres': 'perd',
           'perf': 'perdid',
           'ppp': 'perdit'},
 'portō': {'meaning': 'szállít, visz, hord', 'voice': 'act', 'conj': 1, 'pres': 'port'},
 'praedicō': {'meaning': 'kijelent, előír',
              'voice': 'act',
              'conj': 1,
              'pres': 'praedic',
              'lemma_lexical': 'praedicō [előír]'},
 'praedīcō': {'meaning': 'előre megmond, jósol, említ',
              'voice': 'act',
              'conj': 3,
              'pres': 'praedīc',
              'perf': 'praedīx',
              'ppp': 'praedict',
              'lemma_lexical': 'praedīcō [előre megmond]'},
 'proficīscor': {'meaning': 'elutazik, elindul, tovább megy',
                 'voice': 'dep',
                 'conj': 3,
                 'pres': 'proficīsc',
                 'ppp': 'profect'},
 'pulsō': {'meaning': 'üt, ütöget, penget, kopogtat', 'voice': 'act', 'conj': 1, 'pres': 'puls'},
 'pūrgō': {'meaning': 'tisztít, takarít, menteget', 'voice': 'act', 'conj': 1, 'pres': 'pūrg'},
 'queror': {'meaning': 'panaszkodik, sérelmez, veszekedik', 'voice': 'dep', 'conj': 3, 'pres': 'quer', 'ppp': 'quest'},
 'rapiō': {'meaning': 'magához ragad, felkap, elragad, összeszed, elrabol',
           'voice': 'act',
           'conj': '3io',
           'pres': 'rap',
           'perf': 'rapu',
           'ppp': 'rapt'},
 'reperiō': {'meaning': 'feltalál, megtalál, szerez, észrevesz',
             'voice': 'act',
             'conj': 4,
             'pres': 'reper',
             'perf': 'repper',
             'ppp': 'repert'},
 'requīrō': {'meaning': 'keres, kutat, újra felkeres, kérdez, nyomoz',
             'voice': 'act',
             'conj': 3,
             'pres': 'requīr',
             'perf': 'requīsīv',
             'ppp': 'requīsīt'},
 'ruō': {'meaning': 'siet, rohan, özönlik, ledől, összeomlik',
         'voice': 'act',
         'conj': 3,
         'pres': 'ru',
         'perf': 'ru',
         'ppp': 'rut',
         'no_pass': True},
 'saliō': {'meaning': 'ugrik, ugrál, dobog', 'voice': 'act', 'conj': 4, 'pres': 'sal', 'perf': 'salu', 'no_pass': True},
 'sēcēdō': {'meaning': 'eltávozik, félreáll, visszavonul',
            'voice': 'act',
            'conj': 3,
            'pres': 'sēcēd',
            'perf': 'sēcess',
            'ppp': 'sēcess',
            'no_pass': True},
 'secō': {'meaning': 'vág, levág', 'voice': 'act', 'conj': 1, 'pres': 'sec', 'perf': 'secu', 'ppp': 'sect'},
 'simulō': {'meaning': 'színlel, utánoz, tettet, hasonlóvá tesz', 'voice': 'act', 'conj': 1, 'pres': 'simul'},
 'sinō': {'meaning': 'enged, hagy, eltűr', 'voice': 'act', 'conj': 3, 'pres': 'sin', 'perf': 'sīv', 'ppp': 'sit'},
 'spīrō': {'meaning': 'lélegzik, él, lehel, fúj', 'voice': 'act', 'conj': 1, 'pres': 'spīr', 'no_pass': True},
 'statuō': {'meaning': 'odaállít, alapít, elrendel',
            'voice': 'act',
            'conj': 3,
            'pres': 'statu',
            'perf': 'statu',
            'ppp': 'statūt',
            'no_pass': True},
 'stupeō': {'meaning': 'álmélkodik, bámul, mozdulatlan',
            'voice': 'act',
            'conj': 2,
            'pres': 'stup',
            'perf': 'stupu',
            'no_pass': True},
 'sūmō': {'meaning': 'kézbe vesz, fog, felvesz, vásárol, elfogyaszt, elpusztít',
          'voice': 'act',
          'conj': 3,
          'pres': 'sūm',
          'perf': 'sūmps',
          'ppp': 'sūmpt'},
 'superō': {'meaning': 'fölülmúl, legyőz, kiemelkedik', 'voice': 'act', 'conj': 1, 'pres': 'super'},
 'tegō': {'meaning': 'befed, takar, beborít, elrejt',
          'voice': 'act',
          'conj': 3,
          'pres': 'teg',
          'perf': 'tēx',
          'ppp': 'tect'},
 'tremō': {'meaning': 'reszket, remeg, fél',
           'voice': 'act',
           'conj': 3,
           'pres': 'trem',
           'perf': 'tremu',
           'no_pass': True},
 'tueor': {'meaning': 'néz, figyel vmire, megvéd', 'voice': 'dep', 'conj': 2, 'pres': 'tu', 'ppp': 'tuit'},
 'vagor': {'meaning': 'kóborol, kószál, bolyong, elterjed', 'voice': 'dep', 'conj': 1, 'pres': 'vag', 'ppp': 'vagāt'}}
    _merge_repo_entries(
        verb_vocab,
        alap3_verbs,
        "alap3",
        preserve_core={'audeō', 'cupiō', 'moneō', 'optō', 'parō', 'portō'},
    )
    # END ALAP3 VERBS


    # Verbs for which BevLat deliberately suppresses ordinary passive practice.
    # Impersonal/passive edge cases are outside the intended exercise scope.
    active_only_verbs = {
        "fugiō", "veniō",
        "abeō", "cadō", "eō", "faciō", "intrō", "lateō", "maneō", "pugnō",
        "respondeō", "stō", "triumphō", "vīvō",
        "accēdō", "ārdeō", "cēdō", "concurrō", "conveniō", "currō", "ēveniō",
        "placeō", "sapiō", "sedeō", "taceō", "valeō", "volō [repül]",
    }
    for verb in active_only_verbs:
        if verb in verb_vocab:
            verb_vocab[verb]["no_pass"] = True

    return verb_vocab


#@st.cache_data
def import_nouns():
    noun_vocab = {
        ## Regular Nouns

        # 1st declension
        "puella": {"repo": "core", "gender": "f", "decl": 1,
                    "stem": "puell"},
        "hōra": {"repo": "core", "gender": "f", "decl": 1,
                    "stem": "hōr"},
        "agricola": {"repo": "core", "gender": "m", "decl": 1,
                        "stem": "agricol"},
        "mēnsa": {"repo": "core", "gender": "f", "decl": 1,
                  "stem": "mēns"},
        "poena": {"repo": "core", "gender": "f", "decl": 1,
                  "stem": "poen"},
        "silva": {"repo": "core", "gender": "f", "decl": 1,
                  "stem": "silv"},
        "umbra": {"repo": "core", "gender": "f", "decl": 1,
                  "stem": "umbr"},
        "aqua": {"repo": "core", "gender": "f", "decl": 1,
                  "stem": "aqu"},
        "causa": {"repo": "core", "gender": "f", "decl": 1,
                  "stem": "caus"},
        "anima": {"repo": "core", "gender": "f", "decl": 1,
                  "stem": "anim"},
        "pecūnia": {"repo": "core", "gender": "f", "decl": 1,
                  "stem": "pecūni"},
        "stēlla": {"repo": "core", "gender": "f", "decl": 1,
                  "stem": "stēll"},
        "fēmina": {"repo": "core", "gender": "f", "decl": 1,
                  "stem": "fēmin"},
        "fīlia": {"repo": "core", "gender": "f", "decl": 1,
                    "stem": "fīli",
                    "irreg": {
                        "pl": {
                            "dat": ["fīliīs", "fīliābus"],
                            "abl": ["fīliīs", "fīliābus"]
                        }
                    }},
        "dea": {"repo": "core", "gender": "f", "decl": 1,
                    "stem": "de",
                    "irreg": {
                        "pl": {
                            "dat": ["deīs", "deābus"],
                            "abl": ["deīs", "deābus"]
                        }
                    }},

        # 2nd declension
        "servus": {"repo": "core", "gender": "m", "decl": "2_us",
                    "stem": "serv"},
        "equus": {"repo": "core", "gender": "m", "decl": "2_us",
                    "stem": "equ"},
        "fīlius": {"repo": "core", "gender": "m", "decl": "2_us",
                    "stem": "fīli"},
        "lupus": {"repo": "core", "gender": "m", "decl": "2_us",
                  "stem": "lup"},
        "animus": {"repo": "core", "gender": "m", "decl": "2_us",
                  "stem": "anim"},
        "annus": {"repo": "core", "gender": "m", "decl": "2_us",
                  "stem": "ann"},
        "gladius": {"repo": "core", "gender": "m", "decl": "2_us",
                  "stem": "gladi"},
        "dolus": {"repo": "core", "gender": "m", "decl": "2_us",
                  "stem": "dol"},
        "colōnus": {"repo": "core", "gender": "m", "decl": "2_us",
                  "stem": "colōn"},
        "dominus": {"repo": "core", "gender": "m", "decl": "2_us",
                  "stem": "domin"},
        "nātus": {"repo": "core", "gender": "m", "decl": "2_us",
                  "stem": "nāt"},
        "amīcus": {"repo": "core", "gender": "m", "decl": "2_us",
                  "stem": "amīc"},
        ## -er
        "puer": {"repo": "core", "gender": "m", "decl": "2_er",
                    "stem": "puer"},
        "vir": {"repo": "core", "gender": "m", "decl": "2_er",
                "stem": "vir",
                "irreg": {
                    "pl": {"gen": ["virōrum", "virum"]}
                }},
        "ager": {"repo": "core", "gender": "m", "decl": "2_er",
                    "stem": "agr"},
        "liber": {"repo": "core", "gender": "m", "decl": "2_er",
                    "stem": "libr"},
        "magister": {"repo": "core", "gender": "m", "decl": "2_er",
                    "stem": "magistr"},
        "culter": {"repo": "core", "gender": "m", "decl": "2_er",
                    "stem": "cultr"},
        ## neuter
        "templum": {"repo": "core", "gender": "n", "decl": "2_neut",
                    "stem": "templ"},
        "verbum": {"repo": "core", "gender": "n", "decl": "2_neut",
                    "stem": "verb"},
        "iugum": {"repo": "core", "gender": "n", "decl": "2_neut",
                  "stem": "iug"},
        "beneficium": {"repo": "core", "gender": "n", "decl": "2_neut",
                  "stem": "benefici"},
        "signum": {"repo": "core", "gender": "n", "decl": "2_neut",
                  "stem": "sign"},
        "bellum": {"repo": "core", "gender": "n", "decl": "2_neut",
                  "stem": "bell"},
        "regnum": {"repo": "core", "gender": "n", "decl": "2_neut",
                  "stem": "regn"},
        "saxum": {"repo": "core", "gender": "n", "decl": "2_neut",
                  "stem": "sax"},
        "somnium": {"repo": "core", "gender": "n", "decl": "2_neut",
                  "stem": "somni"},
        "dōnum": {"repo": "core", "gender": "n", "decl": "2_neut",
                  "stem": "dōn"},
        # 3rd declension
        "leo": {"repo": "core", "gender": "m", "decl": 3,
                "stem": "leōn"},
        "mīles": {"repo": "core", "gender": "m", "decl": 3,
                    "stem": "mīlit"},
        "sōl": {"repo": "core", "gender": "m", "decl": 3,
                "stem": "sōl"},
        "vōx": {"repo": "core", "gender": "f", "decl": 3,
                 "stem": "vōc"},
        "rēx": {"repo": "core", "gender": "m", "decl": 3,
                "stem": "rēg"},
        "flōs": {"repo": "core", "gender": "m", "decl": 3,
                "stem": "flōr"},
        "fūr": {"repo": "core", "gender": "m/f", "decl": 3,
                "stem": "fūr"},
        "rūmor": {"repo": "core", "gender": "m", "decl": 3,
                "stem": "rūmōr"},
        "homō": {"repo": "core", "gender": "m/f", "decl": 3,
                "stem": "homin"},
        "servitūs": {"repo": "core", "gender": "f", "decl": 3,
                "stem": "servitūt"},
        ## i-stem
        "cīvis": {"repo": "core", "gender": "m/f", "decl": "3_istem",
                    "stem": "cīv"},
        "nāvis": {"repo": "core", "gender": "f", "decl": "3_istem",
                  "stem": "nāv"},
        "urbs": {"repo": "core", "gender": "f", "decl": "3_istem",
                    "stem": "urb"},
        "mōns": {"repo": "core", "gender": "m", "decl": "3_istem",
                  "stem": "mont"},
        "aedes": {"repo": "core", "gender": "f", "decl": "3_istem",
                  "stem": "aed"},
        "ignis": {"repo": "core", "gender": "m", "decl": "3_istem",
                  "stem": "ign"},
        "nox": {"repo": "core", "gender": "f", "decl": "3_istem",
                  "stem": "noct"},
        ## true i-stem (maybe add possibility of excluding these?)
        "turris": {"repo": "core", "gender": "f", "decl": "3_istem",
                   "stem": "turr",
                   "true_i_stem": True},
        ## neuter
        "nōmen": {"repo": "core", "gender": "n", "decl": "3_neut",
                    "stem": "nōmin"},
        "carmen": {"repo": "core", "gender": "n", "decl": "3_neut",
                    "stem": "carmin"},
        "genus": {"repo": "core", "gender": "n", "decl": "3_neut",
                  "stem": "gener"},
        "lītus": {"repo": "core", "gender": "n", "decl": "3_neut",
                  "stem": "lītor"},
        "onus": {"repo": "core", "gender": "n", "decl": "3_neut",
                  "stem": "oner"},
        "sīdus": {"repo": "core", "gender": "n", "decl": "3_neut",
                  "stem": "sīder"},
        "caput": {"repo": "core", "gender": "n", "decl": "3_neut",
                  "stem": "capit"},
        ## i-stem neuter
        "animal": {"repo": "core", "gender": "n", "decl": "3_istem_neut",
                    "stem": "animāl"},
        "mare": {"repo": "core", "gender": "n", "decl": "3_istem_neut",
                 "stem": "mar",
                 "irreg": {
                     "pl": {"gen": ["marium","marum"]}
                 }},
        "rēte": {"repo": "core", "gender": "n", "decl": "3_istem_neut",
                 "stem": "rēt"},
        "exemplar": {"repo": "core", "gender": "n", "decl": "3_istem_neut",
                 "stem": "exemplār"},

        # 4th declension
        "manus": {"repo": "core", "gender": "f", "decl": 4,
                    "stem": "man"},
        "senātus": {"repo": "core", "gender": "m", "decl": 4,
                    "stem": "senāt"},
        "cāsus": {"repo": "core", "gender": "m", "decl": 4,
                  "stem": "cās"},
        "ictus": {"repo": "core", "gender": "m", "decl": 4,
             "stem": "ict"},
        "gradus": {"repo": "core", "gender": "m", "decl": 4,
             "stem": "grad"},
        "exercitus": {"repo": "core", "gender": "m", "decl": 4,
             "stem": "exercit"},
        "vultus": {"repo": "core", "gender": "m", "decl": 4,
             "stem": "vult"},
        "impetus": {"repo": "core", "gender": "m", "decl": 4,
             "stem": "impet"},
        "currus": {"repo": "core", "gender": "m", "decl": 4,
             "stem": "curr"},
        "sinus": {"repo": "core", "gender": "m", "decl": 4,
             "stem": "sin"},
        "metus": {"repo": "core", "gender": "m", "decl": 4,
             "stem": "met"},
        "portus": {"repo": "core", "gender": "m", "decl": 4,
             "stem": "port"},
        "frūctus": {"repo": "core", "gender": "m", "decl": 4,
             "stem": "frūct"},
        ## neuter
        "cornū": {"repo": "core", "gender": "n", "decl": "4_neut",
                    "stem": "corn"},
        "genū": {"repo": "core", "gender": "n", "decl": "4_neut",
                 "stem": "gen"},
                    
        # 5th declension
        "rēs": {"repo": "core", "gender": "f", "decl": "5_consonant",
                "stem": "r"},
        "diēs": {"repo": "core", "gender": "m/f", "decl": "5_vowel",
                "stem": "di"},
        "faciēs": {"repo": "core", "gender": "f", "decl": "5_vowel",
                "stem": "faci"},
        "fidēs": {"repo": "core", "gender": "f", "decl": "5_consonant",
             "stem": "fid"},
        "spēs": {"repo": "core", "gender": "f", "decl": "5_consonant",
             "stem": "sp"},
        "aciēs": {"repo": "core", "gender": "f", "decl": "5_vowel",
             "stem": "aci"},
        "speciēs": {"repo": "core", "gender": "f", "decl": "5_vowel",
             "stem": "speci"},

        ## Irregular nouns

        # 2nd declension
        "deus": {"repo": "core", "gender": "m", 
            "decl": "2_us",
            "stem": "de",
            "irreg": {
                "sg": {
                    "voc": ["deus", "dīve"]
                },
                "pl": {
                    "nom": ["dī", "deī", "diī"],
                    "gen": ["deum", "deōrum"],
                    "dat": ["dīs", "deīs", "diīs"],
                    "abl": ["dīs", "deīs", "diīs"],
                    "voc": "dī"
                }
            }
        },

        # 3rd declension
        "vīs": {"repo": "core", "gender": "f", 
            "decl": "3_istem",
            "stem": "vī(r)",
            "irreg": {
                "irreg": True,
                "sg": {
                    "gen": None,
                    "dat": None,
                    "acc": "vim",
                    "abl": "vī",
                    "voc": None
                },
                "pl": {
                    "nom": "vīrēs",
                    "gen": "vīrium",
                    "dat": "vīribus",
                    "acc": ["vīrēs","vīrīs"],
                    "abl": "vīribus",
                    "voc": None
                }
            }
        },
        "bōs": {"repo": "core", "gender": "m/f", 
            "decl": 3,
            "stem": "bov",
            "irreg": {
                "irreg": True,
                "pl": {
                    "gen": ["bovum","boum"],
                    "dat": ["bōbus","būbus"],
                    "abl": ["bōbus","būbus"],
                }
            }
        }
    }

    # BEGIN ALAP1 NOUNS
    alap1_nouns = {'aedēs': {'repo': 'alap1', 'meaning': 'épület, templom', 'gender': 'f', 'decl': '3_istem', 'stem': 'aed'},
 'caedēs': {'repo': 'alap1', 'meaning': 'ölés, gyilkosság, vérontás', 'gender': 'f', 'decl': '3_istem', 'stem': 'caed'},
 'caput': {'repo': 'alap1',
           'meaning': 'fej, fő, ember, vezető, kezdet, fejezet',
           'gender': 'n',
           'decl': '3_neut',
           'stem': 'capit'},
 'corpus': {'repo': 'alap1',
            'meaning': 'test, holttest, egyén, összesség',
            'gender': 'n',
            'decl': '3_neut',
            'stem': 'corpor'},
 'currus': {'repo': 'alap1', 'meaning': 'szekér, kocsi, diadalszekér', 'gender': 'm', 'decl': 4, 'stem': 'curr'},
 'diēs': {'repo': 'alap1',
          'meaning': 'a nappal, nap, világosság, idő',
          'gender': 'm/f',
          'decl': '5_vowel',
          'stem': 'di'},
 'domus': {'repo': 'alap1',
           'meaning': 'ház, lakás, haza',
           'gender': 'f',
           'decl': 4,
           'stem': 'dom',
           'irreg': {'irreg': True,
                     'sg': {'abl': 'domō'},
                     'pl': {'acc': ['domūs', 'domōs'], 'gen': ['domuum', 'domōrum']}}},
 'exercitus': {'repo': 'alap1', 'meaning': 'hadsereg, csapat, gyakorlás', 'gender': 'm', 'decl': 4, 'stem': 'exercit'},
 'homō': {'repo': 'alap1', 'meaning': 'ember', 'gender': 'm', 'decl': 3, 'stem': 'homin'},
 'imperium': {'repo': 'alap1',
              'meaning': 'parancs, hatalom, uralom, birodalom',
              'gender': 'n',
              'decl': '2_neut',
              'stem': 'imperi'},
 'labor': {'repo': 'alap1',
           'meaning': 'gyötrelem, erőfeszítés, munka, szenvedés',
           'gender': 'm',
           'decl': 3,
           'stem': 'labōr',
           'lemma_lexical': 'labor [főnév]'},
 'lībertās': {'repo': 'alap1', 'meaning': 'szabadság', 'gender': 'f', 'decl': 3, 'stem': 'lībertāt'},
 'magister': {'repo': 'alap1', 'meaning': 'tanító, vezető, vezér', 'gender': 'm', 'decl': '2_er', 'stem': 'magistr'},
 'mors': {'repo': 'alap1', 'meaning': 'halál', 'gender': 'f', 'decl': '3_istem', 'stem': 'mort'},
 'mūnus': {'repo': 'alap1', 'meaning': 'munka, kötelesség, ajándék', 'gender': 'n', 'decl': '3_neut', 'stem': 'mūner'},
 'nōmen': {'repo': 'alap1', 'meaning': 'név, cím, elnevezés', 'gender': 'n', 'decl': '3_neut', 'stem': 'nōmin'},
 'officium': {'repo': 'alap1',
              'meaning': 'kötelesség, kötelezettség, szolgálat, hivatal',
              'gender': 'n',
              'decl': '2_neut',
              'stem': 'offici'},
 'orīgō': {'repo': 'alap1',
           'meaning': 'eredet, származás, kezdet, nemzetség',
           'gender': 'f',
           'decl': 3,
           'stem': 'orīgin'},
 'puer': {'repo': 'alap1',
          'meaning': 'fiúgyermek, puer alicuius: szolgája valakinek',
          'gender': 'm',
          'decl': '2_er',
          'stem': 'puer'},
 'rēs': {'repo': 'alap1',
         'meaning': 'ügy, dolog, birtok, jószág, vagyon',
         'gender': 'f',
         'decl': '5_consonant',
         'stem': 'r'},
 'rēx': {'repo': 'alap1', 'meaning': 'király, uralkodó, vezető', 'gender': 'm', 'decl': 3, 'stem': 'rēg'},
 'sacerdōs': {'repo': 'alap1', 'meaning': 'pap, papnő', 'gender': 'm/f', 'decl': 3, 'stem': 'sacerdōt'},
 'silva': {'repo': 'alap1', 'meaning': 'erdő, vadon, fa, park', 'gender': 'f', 'decl': 1, 'stem': 'silv'},
 'tempus': {'repo': 'alap1',
            'meaning': 'idő, időszak, időpont, kellő idő',
            'gender': 'n',
            'decl': '3_neut',
            'stem': 'tempor'},
 'urbs': {'repo': 'alap1', 'meaning': 'város, főváros (Róma)', 'gender': 'f', 'decl': '3_istem', 'stem': 'urb'},
 'uxor': {'repo': 'alap1', 'meaning': 'feleség, hitves', 'gender': 'f', 'decl': 3, 'stem': 'uxōr'},
 'verbum': {'repo': 'alap1', 'meaning': 'szó, kifejezés, mondás, ige', 'gender': 'n', 'decl': '2_neut', 'stem': 'verb'},
 'vir': {'repo': 'alap1', 'meaning': 'férfi, férj', 'gender': 'm', 'decl': '2_er', 'stem': 'vir'},
 'virtūs': {'repo': 'alap1',
            'meaning': 'férfiasság, erő, vitézség, erény, erkölcsösség',
            'gender': 'f',
            'decl': 3,
            'stem': 'virtūt'},
 'vultus': {'repo': 'alap1', 'meaning': 'arc, ábrázat, tekintet, kép, alak', 'gender': 'm', 'decl': 4, 'stem': 'vult'},
 'aes': {'repo': 'alap1', 'meaning': 'bronz', 'gender': 'n', 'decl': '3_neut', 'stem': 'aer'},
 'amor': {'repo': 'alap1', 'meaning': 'szeretet, szerelem, kedv, vágy', 'gender': 'm', 'decl': 3, 'stem': 'amōr'},
 'animus': {'repo': 'alap1',
            'meaning': 'lélek, jellem, szellemi képesség',
            'gender': 'm',
            'decl': '2_us',
            'stem': 'anim'},
 'annus': {'repo': 'alap1', 'meaning': 'év, idő, hivatali év, évszak', 'gender': 'm', 'decl': '2_us', 'stem': 'ann'},
 'aqua': {'repo': 'alap1', 'meaning': 'víz, eső, tenger, folyó', 'gender': 'f', 'decl': 1, 'stem': 'aqu'},
 'arma': {'repo': 'alap1',
          'meaning': 'fegyver, eszköz, felszerelés',
          'gender': 'n',
          'decl': '2_neut',
          'stem': 'arm',
          'number': 'plural'},
 'ars': {'repo': 'alap1', 'meaning': 'művészet, mesterség', 'gender': 'f', 'decl': '3_istem', 'stem': 'art'},
 'bellum': {'repo': 'alap1', 'meaning': 'háború, hadjárat, csata', 'gender': 'n', 'decl': '2_neut', 'stem': 'bell'},
 'campus': {'repo': 'alap1', 'meaning': 'síkság, tér, mező', 'gender': 'm', 'decl': '2_us', 'stem': 'camp'},
 'canis': {'repo': 'alap1', 'meaning': 'kutya, szemtelen ember', 'gender': 'm/f', 'decl': '3_istem', 'stem': 'can'},
 'carō': {'repo': 'alap1', 'meaning': 'hús', 'gender': 'f', 'decl': 3, 'stem': 'carn'},
 'causa': {'repo': 'alap1', 'meaning': 'ok, alkalom, mentség, ürügy', 'gender': 'f', 'decl': 1, 'stem': 'caus'},
 'cīvis': {'repo': 'alap1', 'meaning': 'polgár, alattvaló', 'gender': 'm/f', 'decl': '3_istem', 'stem': 'cīv'},
 'cīvitās': {'repo': 'alap1',
             'meaning': 'polgárjog, polgárság, város, nép, állam, törzs',
             'gender': 'f',
             'decl': 3,
             'stem': 'cīvitāt'},
 'condiciō': {'repo': 'alap1',
              'meaning': 'feltétel, helyzet, körülmény, egyezség',
              'gender': 'f',
              'decl': 3,
              'stem': 'condiciōn'},
 'consilium': {'repo': 'alap1',
               'meaning': 'tanácskozás, elhatározás, terv, tanácskozó testület',
               'gender': 'n',
               'decl': '2_neut',
               'stem': 'consili'},
 'cōnsul': {'repo': 'alap1', 'meaning': 'konzul (legfőbb tisztviselő)', 'gender': 'm', 'decl': 3, 'stem': 'cōnsul'},
 'deus': {'repo': 'alap1', 'meaning': 'isten, védőszellem', 'gender': 'm', 'decl': '2_us', 'stem': 'de'},
 'dominus': {'repo': 'alap1', 'meaning': 'úr, gazda, tulajdonos', 'gender': 'm', 'decl': '2_us', 'stem': 'domin'},
 'dōnum': {'repo': 'alap1', 'meaning': 'ajándék, adomány, áldozat', 'gender': 'n', 'decl': '2_neut', 'stem': 'dōn'},
 'dux': {'repo': 'alap1', 'meaning': 'vezér, vezető, herceg', 'gender': 'm', 'decl': 3, 'stem': 'duc'},
 'equus': {'repo': 'alap1', 'meaning': 'ló', 'gender': 'm', 'decl': '2_us', 'stem': 'equ'},
 'fābula': {'repo': 'alap1',
            'meaning': 'költemény, mese, mendemonda, szóbeszéd, dráma',
            'gender': 'f',
            'decl': 1,
            'stem': 'fābul'},
 'familia': {'repo': 'alap1', 'meaning': 'háznép, család, háztartás', 'gender': 'f', 'decl': 1, 'stem': 'famili'},
 'fīlia': {'repo': 'alap1', 'meaning': 'valakinek a lánya', 'gender': 'f', 'decl': 1, 'stem': 'fīli'},
 'fīlius': {'repo': 'alap1', 'meaning': 'valakinek a fia', 'gender': 'm', 'decl': '2_us', 'stem': 'fīli'},
 'forum': {'repo': 'alap1', 'meaning': 'piac, tér, vásártér, forum', 'gender': 'n', 'decl': '2_neut', 'stem': 'for'},
 'frāter': {'repo': 'alap1',
            'meaning': 'fivér, báty, öccs, vérrokon, unokaöccs',
            'gender': 'm',
            'decl': 3,
            'stem': 'frātr'},
 'frūctus': {'repo': 'alap1', 'meaning': 'gyümölcs, termés, haszon', 'gender': 'm', 'decl': 4, 'stem': 'frūct'},
 'frūmentum': {'repo': 'alap1', 'meaning': 'gabona', 'gender': 'n', 'decl': '2_neut', 'stem': 'frūment'},
 'glōria': {'repo': 'alap1', 'meaning': 'dicsőség, hírnév, becsvágy', 'gender': 'f', 'decl': 1, 'stem': 'glōri'},
 'hostis': {'repo': 'alap1',
            'meaning': 'idegen, ellenség, ellenfél',
            'gender': 'm/f',
            'decl': '3_istem',
            'stem': 'host'},
 'hūmānitās': {'repo': 'alap1',
               'meaning': 'emberi természet, emberi érzés, műveltség',
               'gender': 'f',
               'decl': 3,
               'stem': 'hūmānitāt'},
 'īnsula': {'repo': 'alap1', 'meaning': 'sziget, bérház, háztömb', 'gender': 'f', 'decl': 1, 'stem': 'īnsul'},
 'liber': {'repo': 'alap1',
           'meaning': 'könyv',
           'gender': 'm',
           'decl': '2_er',
           'stem': 'libr',
           'lemma_lexical': 'liber [főnév]'},
 'līberī': {'repo': 'alap1',
            'meaning': 'valakinek a gyermekei',
            'gender': 'm',
            'decl': '2_us',
            'stem': 'līber',
            'lemma_lexical': 'līberī [főnév]',
            'number': 'plural',
            'irreg': {'pl': {'gen': ['līberōrum', 'līberum']}}},
 'lītus': {'repo': 'alap1', 'meaning': 'tengerpart, partvidék', 'gender': 'n', 'decl': '3_neut', 'stem': 'lītor'},
 'locus': {'repo': 'alap1', 'meaning': 'hely, tér, szállás', 'gender': 'm', 'decl': '2_us', 'stem': 'loc'},
 'lūna': {'repo': 'alap1', 'meaning': 'hold(világ)', 'gender': 'f', 'decl': 1, 'stem': 'lūn'},
 'lupa': {'repo': 'alap1', 'meaning': 'anyafarkas', 'gender': 'f', 'decl': 1, 'stem': 'lup'},
 'lupus': {'repo': 'alap1', 'meaning': 'farkas', 'gender': 'm', 'decl': '2_us', 'stem': 'lup'},
 'mare': {'repo': 'alap1', 'meaning': 'tenger, tengervíz', 'gender': 'n', 'decl': '3_istem_neut', 'stem': 'mar'},
 'māter': {'repo': 'alap1', 'meaning': 'anya, úrnő', 'gender': 'f', 'decl': 3, 'stem': 'mātr'},
 'mīles': {'repo': 'alap1', 'meaning': 'katona, harcos, sereg, gyalogos', 'gender': 'm', 'decl': 3, 'stem': 'mīlit'},
 'monumentum': {'repo': 'alap1',
                'meaning': 'emlékmű, emlékeztető jel, írott emlék, okirat',
                'gender': 'n',
                'decl': '2_neut',
                'stem': 'monument'},
 'multitūdō': {'repo': 'alap1', 'meaning': 'sokaság, nagy szám, tömeg', 'gender': 'f', 'decl': 3, 'stem': 'multitūdin'},
 'mūrus': {'repo': 'alap1', 'meaning': 'fal, sánc, védelem', 'gender': 'm', 'decl': '2_us', 'stem': 'mūr'},
 'nāvis': {'repo': 'alap1', 'meaning': 'hajó', 'gender': 'f', 'decl': '3_istem', 'stem': 'nāv'},
 'nox': {'repo': 'alap1', 'meaning': 'éj(szaka), homály, sötétség', 'gender': 'f', 'decl': '3_istem', 'stem': 'noct'},
 'ōmen': {'repo': 'alap1', 'meaning': 'jósjel, intő jel, előjel', 'gender': 'n', 'decl': '3_neut', 'stem': 'ōmin'},
 'oppidum': {'repo': 'alap1',
             'meaning': 'város (Rómán kívül), megerősített hely',
             'gender': 'n',
             'decl': '2_neut',
             'stem': 'oppid'},
 'parēns': {'repo': 'alap1', 'meaning': 'szülő, apa, anya', 'gender': 'm/f', 'decl': 3, 'stem': 'parent'},
 'pars': {'repo': 'alap1', 'meaning': 'rész, darab', 'gender': 'f', 'decl': '3_istem', 'stem': 'part'},
 'pater': {'repo': 'alap1', 'meaning': 'atya, alapító, szerző, szenátor', 'gender': 'm', 'decl': 3, 'stem': 'patr'},
 'patria': {'repo': 'alap1', 'meaning': 'haza, szülőföld, szülőváros', 'gender': 'f', 'decl': 1, 'stem': 'patri'},
 'pāx': {'repo': 'alap1', 'meaning': 'béke, békekötés, nyugalom, kegyelem', 'gender': 'f', 'decl': 3, 'stem': 'pāc'},
 'pecūnia': {'repo': 'alap1', 'meaning': 'pénz, vagyon', 'gender': 'f', 'decl': 1, 'stem': 'pecūni'},
 'populus': {'repo': 'alap1', 'meaning': 'nép, lakosság, sokaság', 'gender': 'm', 'decl': '2_us', 'stem': 'popul'},
 'porta': {'repo': 'alap1', 'meaning': 'kapu', 'gender': 'f', 'decl': 1, 'stem': 'port'},
 'pugna': {'repo': 'alap1', 'meaning': 'harc, csata, vita, csatasor', 'gender': 'f', 'decl': 1, 'stem': 'pugn'},
 'rēgnum': {'repo': 'alap1',
            'meaning': 'királyság, uralom, kormányzás, ország',
            'gender': 'n',
            'decl': '2_neut',
            'stem': 'rēgn'},
 'Rōma': {'repo': 'alap1', 'meaning': 'Róma', 'gender': 'f', 'decl': 1, 'stem': 'Rōm', 'number': 'singular'},
 'sapientia': {'repo': 'alap1', 'meaning': 'bölcsesség', 'gender': 'f', 'decl': 1, 'stem': 'sapienti'},
 'senātus': {'repo': 'alap1',
             'meaning': 'szenátus, az állam legfőbb tanácsadó szerve',
             'gender': 'm',
             'decl': 4,
             'stem': 'senāt'},
 'simulācrum': {'repo': 'alap1',
                'meaning': 'képmás, kép, szobor, holtak árnya',
                'gender': 'n',
                'decl': '2_neut',
                'stem': 'simulācr'},
 'sōl': {'repo': 'alap1', 'meaning': 'nap, napvilág', 'gender': 'm', 'decl': 3, 'stem': 'sōl'},
 'spectāculum': {'repo': 'alap1', 'meaning': 'látványosság', 'gender': 'n', 'decl': '2_neut', 'stem': 'spectācul'},
 'templum': {'repo': 'alap1', 'meaning': 'templom, szentély', 'gender': 'n', 'decl': '2_neut', 'stem': 'templ'},
 'terra': {'repo': 'alap1', 'meaning': 'föld, vidék, ország', 'gender': 'f', 'decl': 1, 'stem': 'terr'},
 'triumphus': {'repo': 'alap1', 'meaning': 'diadalmenet', 'gender': 'm', 'decl': '2_us', 'stem': 'triumph'},
 'via': {'repo': 'alap1', 'meaning': 'út, országút', 'gender': 'f', 'decl': 1, 'stem': 'vi'},
 'virgō': {'repo': 'alap1', 'meaning': 'szűz, hajadon, lány, fiatal nő', 'gender': 'f', 'decl': 3, 'stem': 'virgin'},
 'vīs': {'repo': 'alap1', 'meaning': 'erő, erőszak, támadás', 'gender': 'f', 'decl': 3, 'stem': 'vīr'},
 'vīta': {'repo': 'alap1', 'meaning': 'élet, életmód', 'gender': 'f', 'decl': 1, 'stem': 'vīt'}}
    _merge_repo_entries(
        noun_vocab,
        alap1_nouns,
        "alap1",
        preserve_core=['deus', 'vīs'],
    )
    # END ALAP1 NOUNS

    # BEGIN ALAP2 NOUNS
    alap2_nouns = {'aciēs': {'decl': '5_vowel', 'gender': 'f', 'stem': 'aci', 'meaning': 'hegye, éle vminek, csatasor, -rend'},
     'adventus': {'decl': 4, 'gender': 'm', 'stem': 'advent', 'meaning': 'érkezés, jövetel, bekövetkezés'},
     'aetās': {'decl': 3, 'gender': 'f', 'stem': 'aetāt', 'meaning': 'élet, kor, korosztály, korszak'},
     'ager': {'decl': '2_er', 'gender': 'm', 'stem': 'agr', 'meaning': 'szántóföld, föld'},
     'agricola': {'decl': 1, 'gender': 'm', 'stem': 'agricol', 'meaning': 'földművelő, szántóvető'},
     'amīcus': {'decl': '2_us', 'gender': 'm', 'stem': 'amīc', 'meaning': 'barát'},
     'animal': {'decl': '3_istem_neut', 'gender': 'n', 'stem': 'animāl', 'meaning': 'élőlény, állat'},
     'arx': {'decl': '3_istem', 'gender': 'f', 'stem': 'arc', 'meaning': 'fellegvár, védőfal'},
     'auxilium': {'decl': '2_neut', 'gender': 'n', 'stem': 'auxili', 'meaning': 'segítség, segítő csapatok,haderő'},
     'caelum': {'decl': '2_neut', 'gender': 'n', 'stem': 'cael', 'meaning': 'égbolt, légkör, felvilág, égtáj'},
     'clāmor': {'decl': 3, 'gender': 'm', 'stem': 'clāmōr', 'meaning': 'hangos kiáltás, lárma, moraj'},
     'comes': {'decl': 3, 'gender': 'm/f', 'stem': 'comit', 'meaning': 'kísérő, résztvevő, nevelő'},
     'custōdia': {'decl': 1, 'gender': 'f', 'stem': 'custōdi', 'meaning': 'őrzés, őrizet, felügyelet, őrség, fogság'},
     'dea': {'decl': 1, 'gender': 'f', 'stem': 'de', 'meaning': 'istennő'},
     'exitium': {'decl': '2_neut', 'gender': 'n', 'stem': 'exiti', 'meaning': 'kijárat, szabadulás, romlás, pusztulás'},
     'fāma': {'decl': 1, 'gender': 'f', 'stem': 'fām', 'meaning': 'szóbeszéd, hír, közvélemény, hírnév, pletyka'},
     'fēmina': {'decl': 1, 'gender': 'f', 'stem': 'fēmin', 'meaning': 'nő'},
     'ferrum': {'decl': '2_neut', 'gender': 'n', 'stem': 'ferr', 'meaning': 'vas, vasszerszám, fegyver, kard'},
     'fidēs': {'decl': '5_consonant', 'gender': 'f', 'stem': 'fid', 'meaning': 'hit, bizalom, hitelesség, hűség, őszinteség, hihetőség'},
     'fōrma': {'decl': 1, 'gender': 'f', 'stem': 'fōrm', 'meaning': 'alak, forma, szépség'},
     'fuga': {'decl': 1, 'gender': 'f', 'stem': 'fug', 'meaning': 'futás, menekülés'},
     'furor': {'decl': 3, 'gender': 'm', 'stem': 'furōr', 'meaning': 'tombolás, düh, őrültség, rajongás'},
     'geminī': {'decl': '2_us', 'gender': 'm', 'stem': 'gemin', 'meaning': 'ikrek', 'number': 'plural'},
     'gēns': {'decl': '3_istem', 'gender': 'f', 'stem': 'gent', 'meaning': 'nemzetség, rokonság, nép, néptörzs'},
     'ignis': {'decl': '3_istem', 'gender': 'm', 'stem': 'ign', 'meaning': 'tűz, tűzvész, indulat, hév'},
     'imperātor': {'decl': 3, 'gender': 'm', 'stem': 'imperātōr', 'meaning': 'hadvezér, főparancsnok, császár'},
     'īra': {'decl': 1, 'gender': 'f', 'stem': 'īr', 'meaning': 'harag, elkeseredés, düh'},
     'iter': {'decl': '3_neut', 'gender': 'n', 'stem': 'itiner', 'meaning': 'út, ösvény'},
     'iūdex': {'decl': 3, 'gender': 'm', 'stem': 'iūdic', 'meaning': 'bíró'},
     'iūdicium': {'decl': '2_neut', 'gender': 'n', 'stem': 'iūdici', 'meaning': 'ítélet, döntés, vélemény, vizsgálat'},
     'iūs': {'decl': '3_neut', 'gender': 'n', 'stem': 'iūr', 'meaning': 'jog(szabály), törvény, ,jogrend'},
     'iussus': {'decl': 4, 'gender': 'm', 'stem': 'iuss', 'meaning': 'parancs'},
     'lacrima': {'decl': 1, 'gender': 'f', 'stem': 'lacrim', 'meaning': 'könny'},
     'latus': {'decl': '3_neut', 'gender': 'n', 'stem': 'later', 'meaning': 'oldal', 'lemma_lexical': 'latus [főnév]'},
     'lēx': {'decl': 3, 'gender': 'f', 'stem': 'lēg', 'meaning': 'törvény, rendeltetés, végzet, rend'},
     'littera': {'decl': 1, 'gender': 'f', 'stem': 'litter', 'meaning': 'betű; (pl.) írás, levél irodalom, könyvek'},
     'lūx': {'decl': 3, 'gender': 'f', 'stem': 'lūc', 'meaning': 'világ, napvilág, világosság, élet'},
     'magistrātus': {'decl': 4, 'gender': 'm', 'stem': 'magistrāt', 'meaning': 'tisztség, hivatal, tisztségviselő'},
     'maiōrēs': {'decl': 3, 'gender': 'm', 'stem': 'maiōr', 'meaning': 'az idősebbek, az ősök, az öregek', 'number': 'plural'},
     'malum': {'decl': '2_neut', 'gender': 'n', 'stem': 'mal', 'meaning': 'rossz dolog, hiba, gyarlóság, baj, kár'},
     'manus': {'decl': 4, 'gender': 'f', 'stem': 'man', 'meaning': 'kéz, csapat, családfői hatalom'},
     'moenia': {'decl': '3_istem_neut', 'gender': 'n', 'stem': 'moen', 'meaning': 'városfal, védőbástya', 'number': 'plural'},
     'mōs': {'decl': 3, 'gender': 'm', 'stem': 'mōr', 'meaning': 'szokás, akarat, szabály, törvény'},
     'mulier': {'decl': 3, 'gender': 'f', 'stem': 'mulier', 'meaning': 'asszony, nő'},
     'numerus': {'decl': '2_us', 'gender': 'm', 'stem': 'numer', 'meaning': 'szám'},
     'nūntius': {'decl': '2_us', 'gender': 'm', 'stem': 'nūnti', 'meaning': 'hírvivő, követ, küldött, üzenet, hír'},
     'oculus': {'decl': '2_us', 'gender': 'm', 'stem': 'ocul', 'meaning': 'szem'},
     'odium': {'decl': '2_neut', 'gender': 'n', 'stem': 'odi', 'meaning': 'gyűlölet'},
     'opera': {'decl': 1, 'gender': 'f', 'stem': 'oper', 'meaning': 'munka, mű, tevékenység'},
     'poēta': {'decl': 1, 'gender': 'm/f', 'stem': 'poēt', 'meaning': 'költő'},
     'potestās': {'decl': 3, 'gender': 'f', 'stem': 'potestāt', 'meaning': 'erő, hatalom, uralom, hivatal, képesség'},
     'praeda': {'decl': 1, 'gender': 'f', 'stem': 'praed', 'meaning': 'zsákmány, nyereség, haszon'},
     'proelium': {'decl': '2_neut', 'gender': 'n', 'stem': 'proeli', 'meaning': 'csata, harc'},
     'prōvincia': {'decl': 1, 'gender': 'f', 'stem': 'prōvinci', 'meaning': 'tartomány'},
     'rēgīna': {'decl': 1, 'gender': 'f', 'stem': 'rēgīn', 'meaning': 'királynő, királyné, úrnő'},
     'regiō': {'decl': 3, 'gender': 'f', 'stem': 'regiōn', 'meaning': 'vidék, táj'},
     'religiō': {'decl': 3, 'gender': 'f', 'stem': 'religiōn', 'meaning': 'vallás(osság), szertartás, eskü'},
     'repetītiō': {'decl': 3, 'gender': 'f', 'stem': 'repetītiōn', 'meaning': 'ismétlés'},
     'Rōmulus': {'decl': '2_us', 'gender': 'm', 'stem': 'Rōmul', 'meaning': 'Romulus, Róma alapítója', 'number': 'singular'},
     'saeculum': {'decl': '2_neut', 'gender': 'n', 'stem': 'saecul', 'meaning': 'emberöltő, kor, idő, század'},
     'scelus': {'decl': '3_neut', 'gender': 'n', 'stem': 'sceler', 'meaning': 'bűn, gaztett, gonoszság, álnokság'},
     'scientia': {'decl': 1, 'gender': 'f', 'stem': 'scienti', 'meaning': 'ismeret, tudás, szakértelem, tudomány'},
     'sēdēs': {'decl': '3_istem', 'gender': 'f', 'stem': 'sēd', 'meaning': 'ülőhely, szék, lakás, színhely, székhely'},
     'senātor': {'decl': 3, 'gender': 'm', 'stem': 'senātōr', 'meaning': 'szenátor, a szenátus tagja, szenátori rangú ember'},
     'sententia': {'decl': 1, 'gender': 'f', 'stem': 'sententi', 'meaning': 'mondat, nézet, vélemény, ítélet, gondolat'},
     'servus': {'decl': '2_us', 'gender': 'm', 'stem': 'serv', 'meaning': 'szolga, rabszolga'},
     'socius': {'decl': '2_us', 'gender': 'm', 'stem': 'soci', 'meaning': 'társ, részes, szövetséges'},
     'speciēs': {'decl': '5_vowel', 'gender': 'f', 'stem': 'speci', 'meaning': 'külalak, megjelenés, kép, látszat, fajta'},
     'spēs': {'decl': '5_consonant', 'gender': 'f', 'stem': 'sp', 'meaning': 'remény, várakozás'},
     'studium': {'decl': '2_neut', 'gender': 'n', 'stem': 'studi', 'meaning': 'törekvés, igyekezet, érdeklődés, vmivel való foglalkozás'},
     'taurus': {'decl': '2_us', 'gender': 'm', 'stem': 'taur', 'meaning': 'bika'},
     'tēlum': {'decl': '2_neut', 'gender': 'n', 'stem': 'tēl', 'meaning': 'fegyver, dárda, nyíl, támadófegyver'},
     'Tiberis': {'decl': '3_istem', 'gender': 'm', 'stem': 'Tiber', 'meaning': 'Tiberis folyó', 'number': 'singular', 'true_i_stem': True, 'irreg': {'sg': {'acc': 'Tiberim', 'abl': 'Tiberī'}}},
     'vēritās': {'decl': 3, 'gender': 'f', 'stem': 'vēritāt', 'meaning': 'valóság, igazság, őszinteség'},
     'victor': {'decl': 3, 'gender': 'm', 'stem': 'victōr', 'meaning': 'győztes, győző'},
     'victōria': {'decl': 1, 'gender': 'f', 'stem': 'victōri', 'meaning': 'győzelem, siker'},
     'voluntās': {'decl': 3, 'gender': 'f', 'stem': 'voluntāt', 'meaning': 'akarat'},
     'vōx': {'decl': 3, 'gender': 'f', 'stem': 'vōc', 'meaning': 'hangzás, hang'},
     'vulgus': {'decl': '2_neut', 'gender': 'n', 'stem': 'vulg', 'meaning': 'tömeg, sokaság, köznép, csőcselék', 'number': 'singular', 'irreg': {'sg': {'acc': 'vulgus', 'voc': None}}}}
    _merge_repo_entries(
        noun_vocab,
        alap2_nouns,
        "alap2",
        preserve_core={'fēmina', 'spēs', 'aciēs', 'vōx', 'dea', 'agricola', 'manus', 'animal', 'speciēs', 'amīcus', 'servus', 'ager', 'ignis', 'fidēs'},
    )
    # END ALAP2 NOUNS

    # BEGIN ALAP3 NOUNS
    alap3_nouns = {'agnus': {'meaning': 'bárány', 'gender': 'm', 'stem': 'agn', 'decl': '2_us'},
 'Athēnae': {'meaning': 'Athén', 'gender': 'f', 'stem': 'Athēn', 'decl': 1, 'number': 'plural'},
 'auris': {'meaning': 'fül', 'gender': 'f', 'stem': 'aur', 'decl': '3_istem'},
 'avis': {'meaning': 'madár, szárnyas, jósjel', 'gender': 'f', 'stem': 'av', 'decl': '3_istem'},
 'bōs': {'meaning': 'szarvasmarha, tehén, ökör', 'gender': 'm/f', 'stem': 'bov', 'decl': 3},
 'cibus': {'meaning': 'étel, élelem, táplálék', 'gender': 'm', 'stem': 'cib', 'decl': '2_us'},
 'collis': {'meaning': 'domb', 'gender': 'm', 'stem': 'coll', 'decl': '3_istem'},
 'color': {'meaning': 'szín, arcszín, látszat, ,jelleg', 'gender': 'm', 'stem': 'colōr', 'decl': 3},
 'coniūrātiō': {'meaning': 'szövetkezés, összeesküvés', 'gender': 'f', 'stem': 'coniūrātiōn', 'decl': 3},
 'cor': {'meaning': 'szív, lélek, bátorság', 'gender': 'n', 'stem': 'cord', 'decl': '3_neut'},
 'cornū': {'meaning': 'szarv, hegye vminek, szaru', 'gender': 'n', 'stem': 'corn', 'decl': '4_neut'},
 'corōna': {'meaning': 'koszorú', 'gender': 'f', 'stem': 'corōn', 'decl': 1},
 'culpa': {'meaning': 'hiba, bűn', 'gender': 'f', 'stem': 'culp', 'decl': 1},
 'cupīdō': {'meaning': 'vágy, szerelmi vágy', 'gender': 'f', 'stem': 'cupīdin', 'decl': 3},
 'decus': {'meaning': 'dísz, ékesség, báj, szépség, hírnév', 'gender': 'n', 'stem': 'decor', 'decl': '3_neut'},
 'dictātor': {'meaning': 'diktátor (legfőbb rendkívüli tisztviselő)', 'gender': 'm', 'stem': 'dictātōr', 'decl': 3},
 'dolor': {'meaning': 'kín, szenvedés, bánat, harag', 'gender': 'm', 'stem': 'dolōr', 'decl': 3},
 'epistola': {'meaning': 'levél, írásbeli közlemény', 'gender': 'f', 'stem': 'epistol', 'decl': 1},
 'famēs': {'meaning': 'éhség, éhínség, mohó vágy', 'gender': 'f', 'stem': 'fam', 'decl': 3, 'number': 'singular'},
 'flōs': {'meaning': 'virág, ifjúság', 'gender': 'm', 'stem': 'flōr', 'decl': 3},
 'foedus': {'meaning': 'szövetség, egyezmény, rendelkezés', 'gender': 'n', 'stem': 'foeder', 'decl': '3_neut'},
 'fōns': {'meaning': 'forrás, kezdete vminek', 'gender': 'm', 'stem': 'font', 'decl': 3},
 'frīgus': {'meaning': 'hűvösség, fagy, hideg', 'gender': 'n', 'stem': 'frīgor', 'decl': '3_neut'},
 'grex': {'meaning': 'nyáj, csapat, csorda', 'gender': 'm', 'stem': 'greg', 'decl': 3},
 'haruspex': {'meaning': 'béljós, áldozatmagyarázó', 'gender': 'm', 'stem': 'haruspic', 'decl': 3},
 'ingenium': {'meaning': 'tehetség, jellem, veleszületett tulajdonság',
              'gender': 'n',
              'stem': 'ingeni',
              'decl': '2_neut'},
 'invidia': {'meaning': 'irigység', 'gender': 'f', 'stem': 'invidi', 'decl': 1},
 'lapis': {'meaning': 'kő, határkő, mérföldkő, drágakő', 'gender': 'm', 'stem': 'lapid', 'decl': 3},
 'legiō': {'meaning': 'legio, harci egység, hadtest', 'gender': 'f', 'stem': 'legiōn', 'decl': 3},
 'līmen': {'meaning': 'küszöb, ház, lakás, bejárat', 'gender': 'n', 'stem': 'līmin', 'decl': '3_neut'},
 'lūmen': {'meaning': 'fény, ékesség, világosság, szem', 'gender': 'n', 'stem': 'lūmin', 'decl': '3_neut'},
 'lyra': {'meaning': 'lant, líra, lírai vers', 'gender': 'f', 'stem': 'lyr', 'decl': 1},
 'marītus': {'meaning': 'férj, vőlegény', 'gender': 'm', 'stem': 'marīt', 'decl': '2_us'},
 'mēnsa': {'meaning': 'asztal, étkezés, ebéd', 'gender': 'f', 'stem': 'mēns', 'decl': 1},
 'mēnsis': {'meaning': 'hónap', 'gender': 'm', 'stem': 'mēns', 'decl': '3_istem'},
 'mercātor': {'meaning': 'kereskedő, felvásárló', 'gender': 'm', 'stem': 'mercātōr', 'decl': 3},
 'mīrāculum': {'meaning': 'csoda, csodás dolog', 'gender': 'n', 'stem': 'mīrācul', 'decl': '2_neut'},
 'negōtium': {'meaning': 'tevékenység, munka, kereső foglalkozás', 'gender': 'n', 'stem': 'negōti', 'decl': '2_neut'},
 'nūmen': {'meaning': 'bólintás, parancs, akarat, isteni erő, istenség',
           'gender': 'n',
           'stem': 'nūmin',
           'decl': '3_neut'},
 'onus': {'meaning': 'teher, súly', 'gender': 'n', 'stem': 'oner', 'decl': '3_neut'},
 'opīniō': {'meaning': 'vélemény, nézet, hiedelem', 'gender': 'f', 'stem': 'opīniōn', 'decl': 3},
 'ops': {'meaning': 'segítség, (pl.) vagyon', 'gender': 'f', 'stem': 'op', 'decl': 3},
 'opus': {'meaning': 'mű, munka, fáradság, dolog', 'gender': 'n', 'stem': 'oper', 'decl': '3_neut'},
 'ōra': {'meaning': 'part', 'gender': 'f', 'stem': 'ōr', 'decl': 1},
 'ōtium': {'meaning': 'nyugalom, szabad idő, dologtalanság, nem cselekvés',
           'gender': 'n',
           'stem': 'ōti',
           'decl': '2_neut'},
 'pectus': {'meaning': 'mell, mellkas, kebel, szív, lélek', 'gender': 'n', 'stem': 'pector', 'decl': '3_neut'},
 'perīculum': {'meaning': 'veszély, próba', 'gender': 'n', 'stem': 'perīcul', 'decl': '2_neut'},
 'pēs': {'meaning': 'láb, versláb', 'gender': 'm', 'stem': 'ped', 'decl': 3},
 'pōns': {'meaning': 'híd', 'gender': 'm', 'stem': 'pont', 'decl': 3},
 'praetor': {'meaning': 'praetor, igazságügyi tisztviselő', 'gender': 'm', 'stem': 'praetōr', 'decl': 3},
 'prōdigium': {'meaning': 'csodajel, jósjel', 'gender': 'n', 'stem': 'prōdigi', 'decl': '2_neut'},
 'prōverbium': {'meaning': 'közmondás', 'gender': 'n', 'stem': 'prōverbi', 'decl': '2_neut'},
 'prūdentia': {'meaning': 'előrelátás, bölcsesség, ismeret, tudás, okosság',
               'gender': 'f',
               'stem': 'prūdenti',
               'decl': 1},
 'radius': {'meaning': 'sugár, pálcika, vessző', 'gender': 'm', 'stem': 'radi', 'decl': '2_us'},
 'requiēs': {'meaning': 'pihenés, nyugalom', 'gender': 'f', 'stem': 'requiēt', 'decl': 3},
 'rūs': {'meaning': 'mező, falu, szántóföld', 'gender': 'n', 'stem': 'rūr', 'decl': '3_neut'},
 'sīdus': {'meaning': 'csillag(kép), égtáj', 'gender': 'n', 'stem': 'sīder', 'decl': '3_neut'},
 'silentium': {'meaning': 'csönd, hallgatás, nyugalom', 'gender': 'n', 'stem': 'silenti', 'decl': '2_neut'},
 'societās': {'meaning': 'közösség, részesség, szövetség, társaság', 'gender': 'f', 'stem': 'societāt', 'decl': 3},
 'soror': {'meaning': 'nőtestvér, nővér, húg', 'gender': 'f', 'stem': 'sorōr', 'decl': 3},
 'sors': {'meaning': 'sors, sorsvetés, végzet', 'gender': 'f', 'stem': 'sort', 'decl': 3},
 'spatium': {'meaning': 'tér, terjedelem, távolság, köz', 'gender': 'n', 'stem': 'spati', 'decl': '2_neut'},
 'spīritus': {'meaning': 'levegő, lélegzet, élet, lélek', 'gender': 'm', 'stem': 'spīrit', 'decl': 4},
 'supplicium': {'meaning': 'könyörgés, halálbüntetés', 'gender': 'n', 'stem': 'supplici', 'decl': '2_neut'},
 'unda': {'meaning': 'hullám', 'gender': 'f', 'stem': 'und', 'decl': 1},
 'ūsus': {'meaning': 'alkalmazás, használat, gyakorlat, szokás', 'gender': 'm', 'stem': 'ūs', 'decl': 4},
 'vātēs': {'meaning': 'jövendőmondó, jós, próféta, költő',
           'gender': 'm/f',
           'stem': 'vāt',
           'decl': '3_istem',
           'irreg': {'pl': {'gen': ['vātium', 'vātum']}}},
 'versus': {'meaning': 'vers, vonal, sor', 'gender': 'm', 'stem': 'vers', 'decl': 4},
 'vigilia': {'meaning': 'virrasztás, ébrenlét', 'gender': 'f', 'stem': 'vigili', 'decl': 1},
 'voluptās': {'meaning': 'gyönyörűség', 'gender': 'f', 'stem': 'voluptāt', 'decl': 3},
 'vōtum': {'meaning': 'fogadalom, kívánság, fogadalmi ajándék', 'gender': 'n', 'stem': 'vōt', 'decl': '2_neut'}}
    _merge_repo_entries(
        noun_vocab,
        alap3_nouns,
        "alap3",
        preserve_core={'bōs', 'flōs', 'mēnsa', 'onus', 'sīdus'},
    )
    # END ALAP3 NOUNS


    missing_gender = [noun for noun, data in noun_vocab.items() if not data.get("gender")]
    if missing_gender:
        raise ValueError(f"Noun entries missing gender metadata: {missing_gender}")

    return noun_vocab

#@st.cache_data
def import_pronouns():
    pronoun_vocab = {
        "hic": {
                   "repo": "core",
            "genders": True,
            "type": "demonstrative",
            "sg": {
                "nom": ("hic", "haec", "hoc"),
                "gen": ("huius",),
                "dat": ("huic",),
                "acc": ("hunc", "hanc", "hoc"),
                "abl": ("hōc", "hāc", "hōc")
            },
            "pl": {
                "nom": ("hī", "hae", "haec"),
                "gen": ("hōrum", "hārum", "hōrum"),
                "dat": ("hīs",),
                "acc": ("hōs", "hās", "haec"),
                "abl": ("hīs",)
            }
        },
        "ille": {
                    "repo": "core",
            "genders": True,
            "type": "demonstrative",
            "sg": {
                "nom": ("ille", "illa", "illud"),
                "gen": ("illīus",),
                "dat": ("illī",),
                "acc": ("illum", "illam", "illud"),
                "abl": ("illō", "illā", "illō")
            },
            "pl": {
                "nom": ("illī", "illae", "illa"),
                "gen": ("illōrum", "illārum", "illōrum"),
                "dat": ("illīs",),
                "acc": ("illōs", "illās", "illa"),
                "abl": ("illīs",)
            }
        },
        "iste": {
                    "repo": "core",
            "genders": True,
            "type": "demonstrative",
            "sg": {
                "nom": ("iste", "ista", "istud"),
                "gen": ("istīus",),
                "dat": ("istī",),
                "acc": ("istum", "istam", "istud"),
                "abl": ("istō", "istā", "istō")
            },
            "pl": {
                "nom": ("istī", "istae", "ista"),
                "gen": ("istōrum", "istārum", "istōrum"),
                "dat": ("istīs",),
                "acc": ("istōs", "istās", "ista"),
                "abl": ("istīs",)
            }
        },
        "quī": {
                    "repo": "core",
            "genders": True,
            "type": "rel_interrog",
            "sg": {
                "nom": ("quī", "quae", "quod"),
                "gen": ("cuius",),
                "dat": ("cui",),
                "acc": ("quem", "quam", "quod"),
                "abl": ("quō", "quā", "quō")
            },
            "pl": {
                "nom": ("quī", "quae", "quae"),
                "gen": ("quōrum", "quārum", "quōrum"),
                "dat": ("quibus",),
                "acc": ("quōs", "quās", "quae"),
                "abl": ("quibus",)
            }
        },
        "is": {
                  "repo": "core",
            "genders": True,
            "type": "demonstrative",
            "sg": {
                "nom": ("is", "ea", "id"),
                "gen": ("eius",),
                "dat": ("eī",),
                "acc": ("eum", "eam", "id"),
                "abl": ("eō", "eā", "eō")
            },
            "pl": {
                "nom": (["iī","eī"], "eae", "ea"),
                "gen": ("eōrum", "eārum", "eōrum"),
                "dat": (["iīs","eīs"],),
                "acc": ("eōs", "eās", "ea"),
                "abl": (["iīs","eīs"],)
            }
        },
        "īdem": {
                     "repo": "core",
            "genders": True,
            "type": "demonstrative",
            "sg": {
                "nom": ("īdem", "eadem", "idem"),
                "gen": ("eiusdem",),
                "dat": ("eīdem",),
                "acc": ("eundem", "eandem", "idem"),
                "abl": ("eōdem", "eādem", "eōdem")
            },
            "pl": {
                "nom": ("īdem", "eaedem", "eadem"),
                "gen": ("eōrundem", "eārundem", "eōrundem"),
                "dat": (["īsdem","eīsdem"],),
                "acc": ("eōsdem", "eāsdem", "eadem"),
                "abl": (["īsdem","eīsdem"],)
            }
        },
        "ipse": {
                    "repo": "core",
            "genders": True,
            "type": "demonstrative",
            "sg": {
                "nom": ("ipse", "ipsa", "ipsum"),
                "gen": ("ipsīus",),
                "dat": ("ipsī",),
                "acc": ("ipsum", "ipsam", "ipsum"),
                "abl": ("ipsō", "ipsā", "ipsō")
            },
            "pl": {
                "nom": ("ipsī", "ipsae", "ipsa"),
                "gen": ("ipsōrum", "ipsārum", "ipsōrum"),
                "dat": ("ipsīs",),
                "acc": ("ipsōs", "ipsās", "ipsa"),
                "abl": ("ipsīs",)
            }
        },
        "quis": {
                    "repo": "core",
            "genders": True,
            "type": "rel_interrog",
            "sg": {
                "nom": ("quis", "quid"),
                "gen": ("cuius",),
                "dat": ("cui",),
                "acc": ("quem", "quid"),
                "abl": ("quō",)
            },
            "pl": {
                "nom": ("quī", "quae", "quae"),
                "gen": ("quōrum", "quārum", "quōrum"),
                "dat": ("quibus",),
                "acc": ("quōs", "quās", "quae"),
                "abl": ("quibus",)
            }
        },
        "ego": {
                   "repo": "core",
            "type": "pers_pron",
            "forms": {
                "nom": "ego",
                "gen": "meī",
                "dat": ["mihi", "mī"],
                "acc": "mē",
                "abl": "mē"
            },
        },
        "tū": {
                   "repo": "core",
            "type": "pers_pron",
            "forms": {
                "nom": "tū",
                "gen": "tuī",
                "dat": "tibi",
                "acc": "tē",
                "abl": "tē"
            },
        },
        "sē": {
                   "repo": "core",
            "type": "pers_pron",
            "forms": {
                "nom": None,
                "gen": "suī",
                "dat": "sibi",
                "acc": ["sē","sēsē"],
                "abl": ["sē","sēsē"]
            },
        },
        "nōs": {
                    "repo": "core",
            "type": "pers_pron",
            "forms": {
                "nom": "nōs",
                "gen": {"partitive": "nostrum", 
                        "non_part": "nostrī"},
                "dat": "nōbīs",
                "acc": "nōs",
                "abl": "nōbīs"
            },
        },
        "vōs": {
                    "repo": "core",
            "type": "pers_pron",
            "forms": {
                "nom": "vōs",
                "gen": {"partitive": "vestrum", 
                        "non_part": "vestrī"},
                "dat": "vōbīs",
                "acc": "vōs",
                "abl": "vōbīs"
            },
        },
        "nēmō": {
                      "repo": "core",
            "type": "indefinite",
            "forms": {
                "nom": "nēmō",
                "gen": ["nēminis","nūllīus"],
                "dat": "nēminī",
                "acc": "nēminem",
                "abl": "nūllō"
            }
        },
        "quīdam": {
                       "repo": "core",
            "genders": True,
            "type": "indefinite",
            "sg": {
                "nom": ("quīdam", "quaedam", "quiddam"),
                "gen": ("cuiusdam",),
                "dat": ("cuidam",),
                "acc": ("quendam", "quandam", "quiddam"),
                "abl": ("quōdam", "quādam", "quōdam")
            },
            "pl": {
                "nom": ("quīdam", "quaedam", "quaedam"),
                "gen": ("quōrundam", "quārundam", "quōrundam"),
                "dat": ("quibusdam",),
                "acc": ("quōsdam", "quāsdam", "quaedam"),
                "abl": ("quibusdam",)
            }
        }

    }
    return pronoun_vocab

#@st.cache_data
def import_adjectives():
    adjective_vocab = {
        # "": {
        #     "stem": "",
        #     "decl": (),
        #     # "noms": (),
        #     # "irreg": {
        #     #     
        #     # },
        #     "no_adv": False,
        # },
        ## 1st/2nd declension
        ### -r, -ra, -rum
        "pulcher": {
                       "repo": "core",
            "stem": "pulchr",
            "decl": (1,2)
        },
        "pauper": {
                      "repo": "core",
            "stem": "pauper",
            "decl": (1,2)
        },
        "niger": {
                     "repo": "core",
            "stem": "nigr",
            "decl": (1,2)
        },
        "tener": {
                     "repo": "core",
            "stem": "tener",
            "decl": (1,2)
        },
        "miser": {
                     "repo": "core",
            "stem": "miser",
            "decl": (1,2),
            "irreg": {
                "forms": {
                    "adv": {"pos": ["miserē", "miseriter"]}
                }
            }
        },
        "dexter": {
                      "repo": "core",
            "stem": "dextr",
            "decl": (1,2),
            "irreg": {
                "stems": {
                    "comp": "dexter",
                    "super": "dextim"
                },
                "forms": {
                    "adv": {
                        "pos": "dexterē",
                        "comp": None,
                        "super": None
                    }
                }
            }
        },
        # -us, -a, -um
        "laetus": {
                      "repo": "core",
            "stem": "laet",
            "decl": (1,2)
        },
        "cautus": {
                      "repo": "core",
            "stem": "caut",
            "decl": (1,2)
        },
        "sānus": {
                      "repo": "core",
            "stem": "sān",
            "decl": (1,2)
        },
        "vacuus": {
                      "repo": "core",
            "stem": "vacu",
            "decl": (1,2)
        },
        "longus": {
                      "repo": "core",
            "stem": "long",
            "decl": (1,2)
        },
        "cārus": {
                      "repo": "core",
            "stem": "cār",
            "decl": (1,2)
        },
        ### irregular
        "bonus": {
                     "repo": "core",
            "stem": "bon",
            "decl": (1,2),
            "irreg": {
                "stems": {
                    "comp": "mel",
                    "super": "optim"
                },
                "forms": {
                    "adv": {"pos": "bene"}
                }
            }
        },
        "malus": {
                     "repo": "core",
            "stem": "mal",
            "decl": (1,2),
            "irreg": {
                "stems": {
                    "comp": "pē",
                    "super": "pessim"
                },
                "forms": {
                    "adv": {
                        "pos": "male"
                    }
                }
            }
        },
        "magnus": {
                      "repo": "core",
            "stem": "magn",
            "decl": (1,2),
            "irreg": {
                "stems": {
                    "comp": "mā",
                    "super": "maxim"
                },
                "forms": {
                    "adv": {
                        "pos": ["magnoperē","magnopere","magnum"],
                        "comp": "magis"
                    }
                }
            }
        },
        "multus": {
                      "repo": "core",
            "stem": "mult",
            "decl": (1,2),
            "irreg": {
                "stems": {
                    "super": "plūrim"
                },
                "forms": {
                    "adv": {
                        "pos": "multum",
                        "comp": "plūs",
                        "super": "plūrimum"
                    },
                    "comp": {
                        "sg": {
                            "nom": (None,"plūs"),
                            # "acc": (None,"plūs"),
                        },
                        "pl": {
                            "gen": ("plūrium",)
                        },
                        "stem_no_infix": "plūr"
                    }
                },
            }
        },
        "parvus": {
                      "repo": "core",
            "stem": "parv",
            "decl": (1,2),
            "irreg": {
                "stems": {
                    "super": "minim"
                },
                "forms": {
                    "adv": {
                        "pos": ["parum","paulum"],
                        "comp": "minus",
                    },
                    "comp": {
                        "sg": {
                            "nom": ("minor","minus")
                        },
                        "stem_no_infix": "minōr"
                    }
                },
            }
        },
        ## 3rd declension
        "facilis": {
                       "repo": "core",
            "noms": ("facilis", "facile"),
            "stem": "facil",
            "decl": 3,
            "irreg": {
                "forms":{
                    "adv": {"pos": "facile"}
                }
            }
        },
        "difficilis": {
                          "repo": "core",
            "noms": ("difficilis", "difficile"),
            "stem": "difficil",
            "decl": 3,
            "irreg": {
                "forms":{
                    "adv": {"pos": ["difficulter", "difficiliter", "difficilē"]}
                }
            }
        },
        "fortis": {
                      "repo": "core",
            "noms": ("fortis", "forte"),
            "stem": "fort",
            "decl": 3,
        },
        "dulcis": {
                      "repo": "core",
            "noms": ("dulcis", "dulce"),
            "stem": "dulc",
            "decl": 3,
        },
        "trīstis": {
                        "repo": "core",
            "noms": ("trīstis", "trīste"),
            "stem": "trīst",
            "decl": 3,
            "irreg": {
                "forms":{
                    "adv": {"pos": "trīste"}
                }
            }
        },
        "audax": {
                     "repo": "core",
            "noms": ("audax",),
            "stem": "audāc",
            "decl": 3,
        },
        "ācer": {
                     "repo": "core",
            "noms": ("ācer", "ācris", "ācre"),
            "stem": ("ācr"),
            "decl": 3
        },
        "celer": {
                     "repo": "core",
            "noms": ("celer", "celeris", "celere"),
            "stem": ("celer"),
            "decl": 3,
            "irreg": {
                "forms": {
                    "pl": {
                        "gen": ("celerum",)
                    }
                }
            }
        },
        "ingēns": {
                       "repo": "core",
            "noms": ("ingēns",),
            "stem": ("ingent"),
            "decl": 3,
            "no_adv": True
        },
        "innocēns": {
                         "repo": "core",
            "noms": ("innocēns",),
            "stem": ("innocent"),
            "decl": 3,
        },
        "omnis": {
                     "repo": "core",
            "noms": ("omnis", "omne"),
            "stem": "omn",
            "decl": 3,
            "comp": None,
            "super": None,
            "irreg": {
                "forms": {
                    "adv": {
                        "pos": "omnīnō"
                    }
                }
            }
        },        
        "sōlus": {
                      "repo": "core",
            "pronominal": True,
            "decl": (1,2),
            "stem": "sōl",
            "irreg": {
                "forms": {
                    "adv": {
                        "pos": "sōlum"
                    }
                }
            }
        },
        "alius": {
                     "repo": "core",
            "pronominal": True,
            "decl": (1,2),
            "stem": "ali",
            "noms": ("alius", "alia", "aliud"),
            "irreg": {
                "forms": {
                    "sg": {
                        # "nom": ("alius", "alia", "aliud"),
                        "gen": ("alterīus",),
                        "dat": (["alterī","aliī"],),
                        # "acc": ("alium", "aliam", "aliud"),
                        "voc": None
                    },
                    "adv": {
                        "pos": "aliter"
                    }
                }
            }
        },
        "ūnus": {
                     "repo": "core",
            "cardinal": True,
            "pronominal": True,
            "decl": (1,2),
            "no_pl": True,
            "stem": "ūn"
        },
        "duo": {
                   "repo": "core",
            "cardinal": True,
            "decl": (1,2),
            "no_sg": True,
            "stem": "du",
            "irreg": {
                "forms":{
                    "pl": {
                        "nom": ("duo", "duae", "duo"),
                        "gen": ("duōrum", "duārum", "duōrum"),
                        "dat": ("duōbus", "duābus", "duōbus"),
                        "acc": (["duo","duōs"], "duās", "duo"),
                        "abl": ("duōbus", "duābus", "duōbus"),
                        "voc": ("duo", "duae", "duo")
                    }
                }
            }
        },
        "trēs": {
                     "repo": "core",
            "cardinal": True,
            "decl": 3,
            "no_sg": True,
            "stem": "tr",
            "noms": ("trēs", "tria")
        },

        ## 3rd decl. consonant stems
        "vetus": {
                     "repo": "core",
            "cons_stem": True,
            "decl": 3,
            "stem": "veter",
            "noms": ("vetus",),
            "no_adv": True,
            "irreg": {
                "stems": {
                    "comp": "vetust"
                }
            }
        },
        ## need to account for None forms in adjectives.py code
        # "dīves": {
        #     "cons_stem": True,
        #     "decl": 3,
        #     "stem": "dīvit",
        #     "noms": ("dīves",),
        #     "no_adv": True,
        #     "irreg": {
        #         "forms": {
        #             "pl": {
        #                 "nom": ("dīvitēs", None),
        #                 "acc": ("dīvitēs", None),
        #             }
        #         }
        #     }
        # }
    }


    # BEGIN ALAP1 ADJECTIVES
    alap1_adjectives = {'bonus': {'repo': 'alap1', 'meaning': 'jó, szép, derék, csinos, helyes', 'decl': (1, 2), 'stem': 'bon'},
 'līber': {'repo': 'alap1',
           'meaning': 'szabad, független, akadálytalan',
           'decl': (1, 2),
           'stem': 'līber',
           'lemma_lexical': 'līber [melléknév]'},
 'omnis': {'repo': 'alap1',
           'meaning': 'minden, mindegyik, egész, teljes',
           'decl': 3,
           'stem': 'omn',
           'noms': ('omnis', 'omne')},
 'similis': {'repo': 'alap1',
             'meaning': 'hasonló, egyenlő, éppolyan',
             'decl': 3,
             'stem': 'simil',
             'noms': ('similis', 'simile')},
 'ācer': {'repo': 'alap1',
          'meaning': 'éles, kemény, ádáz',
          'decl': 3,
          'stem': 'ācr',
          'noms': ('ācer', 'ācris', 'ācre')},
 'brevis': {'repo': 'alap1',
            'meaning': 'rövid, kicsiny, csekély, tömör',
            'decl': 3,
            'stem': 'brev',
            'noms': ('brevis', 'breve')},
 'cīvīlis': {'repo': 'alap1',
             'meaning': 'polgári, közösségi, állami, udvarias',
             'decl': 3,
             'stem': 'cīvīl',
             'noms': ('cīvīlis', 'cīvīle')},
 'commūnis': {'repo': 'alap1',
              'meaning': 'közös, általános, nyilvános, közönséges',
              'decl': 3,
              'stem': 'commūn',
              'noms': ('commūnis', 'commūne')},
 'difficilis': {'repo': 'alap1',
                'meaning': 'nehéz, súlyos, fárasztó, mogorva',
                'decl': 3,
                'stem': 'difficil',
                'noms': ('difficilis', 'difficile')},
 'dissimilis': {'repo': 'alap1',
                'meaning': 'különböző, eltérő',
                'decl': 3,
                'stem': 'dissimil',
                'noms': ('dissimilis', 'dissimile')},
 'facilis': {'repo': 'alap1',
             'meaning': 'könnyű, élénk, könnyelmű',
             'decl': 3,
             'stem': 'facil',
             'noms': ('facilis', 'facile')},
 'fēstus': {'repo': 'alap1', 'meaning': 'ünnepi, ünneplő, vidám', 'decl': (1, 2), 'stem': 'fēst'},
 'gravis': {'repo': 'alap1',
            'meaning': 'súlyos, hatalmas, tekintélyes',
            'decl': 3,
            'stem': 'grav',
            'noms': ('gravis', 'grave')},
 'horribilis': {'repo': 'alap1',
                'meaning': 'borzasztó, irtózatos, rendkívüli',
                'decl': 3,
                'stem': 'horribil',
                'noms': ('horribilis', 'horribile')},
 'hūmānus': {'repo': 'alap1', 'meaning': 'emberi(es), emberszerető, művelt', 'decl': (1, 2), 'stem': 'hūmān'},
 'humilis': {'repo': 'alap1',
             'meaning': 'alacsony, kicsi, mindennapi, alacsonyrendű',
             'decl': 3,
             'stem': 'humil',
             'noms': ('humilis', 'humile')},
 'ingēns': {'repo': 'alap1',
            'meaning': 'hatalmas, rendkívüli, nagyszerű',
            'decl': 3,
            'stem': 'ingent',
            'noms': ('ingēns',)},
 'iuvenis': {'repo': 'alap1', 'meaning': 'fiatal', 'decl': 3, 'stem': 'iuven', 'noms': ('iuvenis', 'iuvene')},
 'longus': {'repo': 'alap1', 'meaning': 'hosszú, hosszadalmas', 'decl': (1, 2), 'stem': 'long'},
 'magnus': {'repo': 'alap1', 'meaning': 'nagy, tágas, idős', 'decl': (1, 2), 'stem': 'magn'},
 'malus': {'repo': 'alap1', 'meaning': 'rossz, ártalmas, veszedelmes', 'decl': (1, 2), 'stem': 'mal'},
 'meus': {'repo': 'alap1',
          'meaning': 'enyém, az én…',
          'decl': (1, 2),
          'stem': 'me',
          'comp': None,
          'super': None,
          'no_adv': True,
          'irreg': {'forms': {'sg': {'voc': ('mī', 'mea', 'meum')}}}},
 'mortālis': {'repo': 'alap1',
              'meaning': 'halandó, múló, emberi',
              'decl': 3,
              'stem': 'mortāl',
              'noms': ('mortālis', 'mortāle')},
 'mortuus': {'repo': 'alap1', 'meaning': 'halott', 'decl': (1, 2), 'stem': 'mortu'},
 'multus': {'repo': 'alap1', 'meaning': 'sok, számos,j elentékeny', 'decl': (1, 2), 'stem': 'mult'},
 'noster': {'repo': 'alap1',
            'meaning': 'mienk, a mi …',
            'decl': (1, 2),
            'stem': 'nostr',
            'comp': None,
            'super': None,
            'no_adv': True},
 'novus': {'repo': 'alap1', 'meaning': 'új, friss, szokatlan, ,járatlan', 'decl': (1, 2), 'stem': 'nov'},
 'parvus': {'repo': 'alap1', 'meaning': 'kis, kicsiny, csekély, jelentéktelen', 'decl': (1, 2), 'stem': 'parv'},
 'pulcher': {'repo': 'alap1', 'meaning': 'szép, gyönyörű, derék', 'decl': (1, 2), 'stem': 'pulchr'},
 'Rōmānus': {'repo': 'alap1', 'meaning': 'római', 'decl': (1, 2), 'stem': 'Rōmān'},
 'sapiēns': {'repo': 'alap1', 'meaning': 'bölcs', 'decl': 3, 'stem': 'sapient', 'noms': ('sapiēns',)},
 'stultus': {'repo': 'alap1', 'meaning': 'ostoba, oktalan, együgyű', 'decl': (1, 2), 'stem': 'stult'},
 'superbus': {'repo': 'alap1', 'meaning': 'gőgös, büszke, kimagasló', 'decl': (1, 2), 'stem': 'superb'},
 'suus': {'repo': 'alap1',
          'meaning': 'saját, övé, magáé',
          'decl': (1, 2),
          'stem': 'su',
          'comp': None,
          'super': None,
          'no_adv': True},
 'tūtus': {'repo': 'alap1', 'meaning': 'biztonságos, biztos', 'decl': (1, 2), 'stem': 'tūt'},
 'tuus': {'repo': 'alap1',
          'meaning': 'tied, a te …',
          'decl': (1, 2),
          'stem': 'tu',
          'comp': None,
          'super': None,
          'no_adv': True},
 'vester': {'repo': 'alap1',
            'meaning': 'tiétek, a ti …',
            'decl': (1, 2),
            'stem': 'vestr',
            'comp': None,
            'super': None,
            'no_adv': True}}
    _merge_repo_entries(
        adjective_vocab,
        alap1_adjectives,
        "alap1",
    )
    # END ALAP1 ADJECTIVES

    # BEGIN ALAP2 ADJECTIVES
    alap2_adjectives = {'aeternus': {'meaning': 'örök, elmúlhatatlan', 'decl': (1, 2), 'stem': 'aetern'},
     'antīquus': {'meaning': 'régi, ősi', 'decl': (1, 2), 'stem': 'antīqu'},
     'barbarus': {'meaning': 'barbár, külföldi, műveletlen, durva, vad', 'decl': (1, 2), 'stem': 'barbar'},
     'beātus': {'meaning': 'gazdag, vagyonos, boldog', 'decl': (1, 2), 'stem': 'beāt'},
     'doctus': {'meaning': 'iskolázott, tanult, művelt, ,jártas', 'decl': (1, 2), 'stem': 'doct'},
     'duo': {'meaning': 'két, kettő', 'decl': 3, 'stem': 'du'},
     'extrēmus': {'meaning': 'legvégső, legutolsó, legnagyobb, szélső', 'decl': (1, 2), 'stem': 'extrēm'},
     'falsus': {'meaning': 'téves, álnok, csalárd, hazug, megtévesztett', 'decl': (1, 2), 'stem': 'fals'},
     'fortis': {'meaning': 'bátor, vitéz, erős', 'decl': 3, 'stem': 'fort', 'noms': ('fortis', 'forte')},
     'gracilis': {'meaning': 'karcsú, nyulánk, vékony, szűkös, dísztelen', 'decl': 3, 'stem': 'gracil', 'noms': ('gracilis', 'gracile')},
     'illūstris': {'meaning': 'világos, ragyogó, híres, kiváló', 'decl': 3, 'stem': 'illūstr', 'noms': ('illūstris', 'illūstre')},
     'immortālis': {'meaning': 'halhatatlan, örökkévaló, boldog', 'decl': 3, 'stem': 'immortāl', 'noms': ('immortālis', 'immortāle')},
     'inimīcus': {'meaning': 'ellenséges, barátságtalan', 'decl': (1, 2), 'stem': 'inimīc'},
     'lātus': {'meaning': 'széles, tágas, nagyképű, hosszadalmas', 'lemma_lexical': 'lātus [melléknév]', 'decl': (1, 2), 'stem': 'lāt'},
     'medius': {'meaning': 'középső, középen levő', 'decl': (1, 2), 'stem': 'medi'},
     'prīmus': {'meaning': 'első, kezdő, legkiválóbb', 'decl': (1, 2), 'stem': 'prīm'},
     'prīvātus': {'meaning': 'vmitől megfosztott, magán, magános, mindennapi', 'decl': (1, 2), 'stem': 'prīvāt'},
     'pūblicus': {'meaning': 'állami, hivatalos, nyilvános, közös', 'decl': (1, 2), 'stem': 'pūblic'},
     'quālis': {'meaning': 'milyen, miféle,melyik, amilyen, amelyik', 'decl': 3, 'stem': 'quāl', 'noms': ('quālis', 'quāle')},
     'quantus': {'meaning': 'mennyi, mekkora, amennyi, amekkora', 'decl': (1, 2), 'stem': 'quant'},
     'rēctus': {'meaning': 'egyenes, helyes, becsületes', 'decl': (1, 2), 'stem': 'rēct'},
     'reliquus': {'meaning': 'többi, maradék, hátrahagyott+E248 ', 'decl': (1, 2), 'stem': 'reliqu'},
     'secundus': {'meaning': 'következő, második, másodrendű, kedvező', 'decl': (1, 2), 'stem': 'secund'},
     'sōlus': {'meaning': 'egyedüli, egyetlen, magányos', 'decl': (1, 2), 'stem': 'sōl', 'pronominal': True},
     'summus': {'meaning': 'legfelső, teljes', 'decl': (1, 2), 'stem': 'summ'},
     'tacitus': {'meaning': 'hallgatag, szótlan, csendes, titkos', 'decl': (1, 2), 'stem': 'tacit'},
     'tālis': {'meaning': 'ilyen, olyan', 'decl': 3, 'stem': 'tāl', 'noms': ('tālis', 'tāle')},
     'tantus': {'meaning': 'akkora, annyi', 'decl': (1, 2), 'stem': 'tant'},
     'tertius': {'meaning': 'harmadik', 'decl': (1, 2), 'stem': 'terti'},
     'tōtus': {'meaning': 'egész, teljes, minden, összes', 'decl': (1, 2), 'stem': 'tōt', 'pronominal': True},
     'trēs': {'meaning': 'három', 'decl': 3, 'stem': 'tr'},
     'ūnus': {'meaning': 'egy, egyik', 'decl': (1, 2), 'stem': 'ūn', 'pronominal': True},
     'ūtilis': {'meaning': 'használható, alkalmas vmire', 'decl': 3, 'stem': 'ūtil', 'noms': ('ūtilis', 'ūtile')},
     'validus': {'meaning': 'erős, érvényes', 'decl': (1, 2), 'stem': 'valid'},
     'vērus': {'meaning': 'igaz, igazi, valódi', 'decl': (1, 2), 'stem': 'vēr'},
     'senex': {'decl': 3,
               'stem': 'sen',
               'noms': ('senex',),
               'meaning': 'agg, öreg, vén',
               'comp': None,
               'super': None,
               'no_adv': True,
               'irreg': {'forms': {'sg': {'nom': ('senex', 'senex', 'senex'),
                                          'voc': ('senex', 'senex', 'senex'),
                                          'gen': ('senis', 'senis', 'senis'),
                                          'dat': ('senī', 'senī', 'senī'),
                                          'acc': ('senem', 'senem', 'senex'),
                                          'abl': ('sene', 'sene', 'sene')},
                                    'pl': {'nom': ('senēs', 'senēs', 'senēs'),
                                           'voc': ('senēs', 'senēs', 'senēs'),
                                           'gen': ('senum', 'senum', 'senum'),
                                           'dat': ('senibus', 'senibus', 'senibus'),
                                           'acc': ('senēs', 'senēs', 'senēs'),
                                           'abl': ('senibus', 'senibus', 'senibus')}}}}}
    _merge_repo_entries(
        adjective_vocab,
        alap2_adjectives,
        "alap2",
        preserve_core={'sōlus', 'fortis', 'trēs', 'duo', 'ūnus'},
    )
    # END ALAP2 ADJECTIVES

    # BEGIN ALAP3 ADJECTIVES
    alap3_adjectives = {'aeger': {'meaning': 'beteg, gyengélkedő, szomorú, fájdalmas', 'decl': (1, 2), 'stem': 'aegr'},
 'almus': {'meaning': 'tápláló, éltető, ,jóságos, áldásos', 'decl': (1, 2), 'stem': 'alm'},
 'audāx': {'meaning': 'merész, vakmerő, elbizakodott', 'decl': 3, 'stem': 'audāc', 'noms': ('audāx',)},
 'avidus': {'meaning': 'vágyakozó, mohó, fösvény', 'decl': (1, 2), 'stem': 'avid'},
 'benignus': {'meaning': 'jóindulatú, bőkezű', 'decl': (1, 2), 'stem': 'benign'},
 'candidus': {'meaning': 'ragyogó, fehér, becsületes, őszinte', 'decl': (1, 2), 'stem': 'candid'},
 'citus': {'meaning': 'gyors, sebes, korai, idő előtti', 'decl': (1, 2), 'stem': 'cit'},
 'cupidus': {'meaning': 'vágyódó (amire gen.), szerelmes, kapzsi', 'decl': (1, 2), 'stem': 'cupid'},
 'dīversus': {'meaning': 'különböző, eltérő', 'decl': (1, 2), 'stem': 'dīvers'},
 'dīves': {'meaning': 'gazdag, dús, becses, hasznos',
           'decl': 3,
           'stem': 'dīvit',
           'noms': ('dīves',),
           'irreg': {'forms': {'sg': {'abl': ('dīvite',)},
                               'pl': {'nom': ('dīvitēs', 'dīvitēs', None),
                                      'gen': ('dīvitum',),
                                      'acc': ('dīvitēs', 'dīvitēs', None),
                                      'voc': ('dīvitēs', 'dīvitēs', None)}}}},
 'dubius': {'meaning': 'kétséges, kétes, bizonytalan', 'decl': (1, 2), 'stem': 'dubi'},
 'dūrus': {'meaning': 'kemény, merev, érdes, darabos', 'decl': (1, 2), 'stem': 'dūr'},
 'frequēns': {'meaning': 'gyakori, sűrűn látogatott', 'decl': 3, 'stem': 'frequent', 'noms': ('frequēns',)},
 'grātus': {'meaning': 'kedves, kellemes, kedvelt, hálás', 'decl': (1, 2), 'stem': 'grāt'},
 'impius': {'meaning': 'kegyetlen, gonosz, istentelen', 'decl': (1, 2), 'stem': 'impi'},
 'integer': {'meaning': 'érintetlen, sértetlen, ép, teljes', 'decl': (1, 2), 'stem': 'integr'},
 'levis': {'meaning': 'könnyű, gyenge, fürge, ,jelentéktelen', 'decl': 3, 'stem': 'lev', 'noms': ('levis', 'leve')},
 'miser': {'meaning': 'nyomorult, szerencsétlen, gyötrő', 'decl': (1, 2), 'stem': 'miser'},
 'nūdus': {'meaning': 'meztelen, vmitől megfosztott', 'decl': (1, 2), 'stem': 'nūd'},
 'obscūrus': {'meaning': 'homályos, sötét, érthetetlen', 'decl': (1, 2), 'stem': 'obscūr'},
 'pār': {'meaning': 'egyenlő, egyforma', 'decl': 3, 'stem': 'par', 'noms': ('pār',)},
 'paucus': {'meaning': 'kevés', 'decl': (1, 2), 'stem': 'pauc'},
 'pauper': {'meaning': 'szegény',
            'decl': 3,
            'stem': 'pauper',
            'noms': ('pauper',),
            'irreg': {'forms': {'sg': {'abl': ('paupere',)},
                                'pl': {'nom': ('pauperēs', 'pauperēs', 'paupera'),
                                       'gen': ('pauperum',),
                                       'acc': ('pauperēs', 'pauperēs', 'paupera'),
                                       'voc': ('pauperēs', 'pauperēs', 'paupera')}}}},
 'perpetuus': {'meaning': 'állandó, örökös', 'decl': (1, 2), 'stem': 'perpetu'},
 'proprius': {'meaning': 'saját, övé, az ő tulajdona', 'decl': (1, 2), 'stem': 'propri'},
 'pūrus': {'meaning': 'tiszta, derült, feddhetetlen, egyszerű', 'decl': (1, 2), 'stem': 'pūr'},
 'rārus': {'meaning': 'ritka, gyér, laza, szétszórt', 'decl': (1, 2), 'stem': 'rār'},
 'sollemnis': {'meaning': 'ünnepi, ünnepélyes, szokásos',
               'decl': 3,
               'stem': 'sollemn',
               'noms': ('sollemnis', 'sollemne')},
 'superus': {'meaning': 'felső, égi', 'decl': (1, 2), 'stem': 'super'},
 'varius': {'meaning': 'különböző, váltakozó, tarka, sokszínű', 'decl': (1, 2), 'stem': 'vari'},
 'vetus': {'meaning': 'régi, öreg, tapasztalt, hajdani',
           'decl': 3,
           'stem': 'veter',
           'noms': ('vetus',),
           'irreg': {'forms': {'sg': {'abl': ('vetere',)},
                               'pl': {'nom': ('veterēs', 'veterēs', 'vetera'),
                                      'gen': ('veterum',),
                                      'acc': ('veterēs', 'veterēs', 'vetera'),
                                      'voc': ('veterēs', 'veterēs', 'vetera')}}}},
 'vīcīnus': {'meaning': 'szomszédos, közeli', 'decl': (1, 2), 'stem': 'vīcīn'},
 'virēns': {'meaning': 'zöld, zöldellő, viruló, friss erőben levő', 'decl': 3, 'stem': 'virent', 'noms': ('virēns',)}}
    _merge_repo_entries(
        adjective_vocab,
        alap3_adjectives,
        "alap3",
        preserve_core={'miser', 'pauper', 'vetus'},
    )
    # The reviewed alap3 list treats these as pedagogical irregulars:
    # ordinary 3rd-declension adjectives otherwise follow the strong i-stem pattern.
    for word in ('dīves', 'pauper', 'vetus'):
        adjective_vocab[word]['irreg'] = copy.deepcopy(alap3_adjectives[word]['irreg'])
    # pauper is a one-ending 3rd-declension adjective; the legacy core entry
    # incorrectly classified it with 1st/2nd-declension -er adjectives.
    adjective_vocab['pauper']['decl'] = 3
    adjective_vocab['pauper']['stem'] = 'pauper'
    adjective_vocab['pauper']['noms'] = ('pauper',)
    # END ALAP3 ADJECTIVES


    for word in adjective_vocab.keys():
        if adjective_vocab[word].get("cardinal") or adjective_vocab[word].get("pronominal"):
            adjective_vocab[word]["comp"] = None
            adjective_vocab[word]["super"] = None
        if adjective_vocab[word].get("pronominal") and word != "ūnus":
            adjective_vocab[word].setdefault("irreg",{}).setdefault("forms",{}).setdefault("sg",{})["voc"] = None

    return adjective_vocab

# BEGIN ALAP2 MISC
def import_misc():
    misc_vocab = {'aiō': {'meaning': 'igent mond, így szól, állít, azt mondja', 'lexical_only': True, 'source_pos': 'verb', 'dictionary_entry': 'aiō, ait', 'lemma_lexical': 'aiō'},
     'coepī': {'meaning': 'kezdett, megkezdődött, kezd', 'lexical_only': True, 'source_pos': 'verb', 'dictionary_entry': 'coepī, coepisse, coeptum'},
     'ōdī': {'meaning': 'gyűlöl, utál, megvet', 'lexical_only': True, 'source_pos': 'verb', 'dictionary_entry': 'ōdī, ōdisse, ōsus sum'},
     'oportet': {'meaning': 'kell, illik, célszerű', 'lexical_only': True, 'source_pos': 'verb', 'dictionary_entry': 'oportet 2 oportuit'},
     'rēs pūblica': {'meaning': 'közügy, köztársaság, állam, államhatalom, államvagyon', 'lexical_only': True, 'source_pos': 'noun', 'dictionary_entry': 'rēs pūblica, reī pūblicae f.'}}
    for data in misc_vocab.values():
        data["repo"] = "alap2"
    # BEGIN ALAP3 MISC
    alap3_misc = {'alō': {'meaning': 'táplál, nevel, éltet',
         'lexical_only': True,
         'source_pos': 'verb',
         'dictionary_entry': 'alō 3 aluī, al(i)tum',
         'lemma_lexical': 'alō'},
 'decet': {'meaning': 'illik (személytelen ige)',
           'lexical_only': True,
           'source_pos': 'verb',
           'dictionary_entry': 'decet 2 -uit',
           'lemma_lexical': 'decet'},
 'lavō': {'meaning': 'mos, locsol, megnedvesít',
          'lexical_only': True,
          'source_pos': 'verb',
          'dictionary_entry': 'lavō 1',
          'lemma_lexical': 'lavō'},
 'pereō': {'meaning': 'elmúlik, elpusztul, elvész, tönkremegy',
           'lexical_only': True,
           'source_pos': 'verb',
           'dictionary_entry': 'pereō 4 periī, peritūrus',
           'lemma_lexical': 'pereō'},
 'praesum': {'meaning': 'jelen van, élén áll (dat.)',
             'lexical_only': True,
             'source_pos': 'verb',
             'dictionary_entry': 'praesum, -esse, -fuī',
             'lemma_lexical': 'praesum'},
 'supersum': {'meaning': 'fennmarad, hátra van, életben marad',
              'lexical_only': True,
              'source_pos': 'verb',
              'dictionary_entry': 'supersum, -esse, -fuī',
              'lemma_lexical': 'supersum'}}
    for data in alap3_misc.values():
        data["repo"] = "alap3"
    misc_vocab.update(alap3_misc)
    # END ALAP3 MISC

    return misc_vocab
# END ALAP2 MISC
