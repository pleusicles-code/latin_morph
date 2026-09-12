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
                                    2: "fertis",
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
        }
    }
    return verb_vocab
