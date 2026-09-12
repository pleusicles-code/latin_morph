import streamlit as st

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

    for word in adjective_vocab.keys():
        if adjective_vocab[word].get("cardinal") or adjective_vocab[word].get("pronominal"):
            adjective_vocab[word]["comp"] = None
            adjective_vocab[word]["super"] = None
        if adjective_vocab[word].get("pronominal") and word != "ūnus":
            adjective_vocab[word].setdefault("irreg",{}).setdefault("forms",{}).setdefault("sg",{})["voc"] = None

    return adjective_vocab