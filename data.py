# data.py
from scaffold import Chara

chara_pool = {
    "Muelsyse": Chara(6, "Yan", "Sargon", "Victoria", "Kjerag", "Laterano", "Aegir", "Siracusa", "Kazimierz", "Harmony"),


    "Pepe": Chara(6, "Sargon", "Tenacity"), "Passenger": Chara(6, "Sargon", "Swift", "Solitary"), "Gavial the Invincible": Chara(5, "Sargon"), "Titi": Chara(5, "Sargon", "Precision"), "Beeswax": Chara(4, "Sargon", "Support"),
    "Philae": Chara(3, "Sargon"), "Minimalist": Chara(3, "Sargon", "Agility"), "Bubble": Chara(2, "Sargon", "Bastion"), "Papyrus": Chara(2, "Sargon"), "Estelle": Chara(1, "Sargon"),

    "Quibai": Chara(6, "Yan", "Assault"), "Yu": Chara(6, "Bastion", "Yan"), "Dusk": Chara(5, "Arcane", "Yan"), "Hoshiguma": Chara(4, "Yan"),
    "Record Keeper": Chara(4, "Yan", "Miracle"), "Swire": Chara(3, "Yan", "Foresight"), "Swire the Elegant Wit": Chara(3, "Yan", "Investor"), "Grain Buds": Chara(2, "Yan", "Agility"), "Leizi": Chara(1, "Yan"),
    "Blaze the Igniting Spark": Chara(5, "Yan", "Victoria"),
    "Vina Victoria": Chara(6, "Victoria", "Miracle"), "Reed The Flame Shadow": Chara(6, "Victoria", "Precision"), "Horn": Chara(5, "Victoria"), "Catherine": Chara(4, "Victoria", "Agility"),
    "Bagpipe": Chara(4, "Victoria", "Tenacity", "Foresight"), "Mint": Chara(3, "Victoria"), "Rockrock": Chara(2, "Victoria", "Arcane"), "Vendela": Chara(1, "Victoria", "Support"),
    "Harold": Chara(2, "Victoria", "Kjerag"),
    "Pramanix the Prerita": Chara(6, "Kjerag", "Arcane"), "SilverAsh the Reignfrost": Chara(5, "Kjerag", "Swift", "Investor"), "Gnosis": Chara(4, "Kjerag", "Agility"), "Kjera": Chara(4, "Kjerag", "Support"),
    "Snow Hunter": Chara(3, "Kjerag", "Precision"), "Pramanix": Chara(3, "Kjerag", "Foresight"), "Cliffheart": Chara(2, "Kjerag", "Tenacity"), "Matterhorn": Chara(1, "Kjerag", "Bastion"),
    "Degenbrecher": Chara(6, "Kjerag", "Kazimierz", "Swift"),
    "Nearl the Radiant Knight": Chara(6, "Kazimierz", "Assault"), "Mwynar": Chara(5, "Kazimierz"), "Fartooth": Chara(4, "Kazimierz", "Precision"), "Flametail": Chara(4, "Kazimierz"),
    "Meteor": Chara(3, "Kazimierz", "Solitary"), "Blemishine": Chara(3, "Kazimierz", "Assault"), "Ashlock": Chara(2, "Kazimierz", "Bastion"), "Gravel": Chara(2, "Kazimierz", "Tenacity"), "Wild Mane": Chara(1, "Kazimierz", "Swift"),

    "Lemuen": Chara(6, "Laterano", "Precision"), "Virtuosa": Chara(6, "Laterano"), "Exusiai the New Covenant": Chara(6, "Laterano"), "Executor the Ex Foedere": Chara(5, "Laterano", "Foresight"), "Sankta Miksaparato": Chara(4, "Laterano", "Bastion"),
    "Mostima": Chara(4, "Laterano", "Arcane"), "Exusiai": Chara(3, "Laterano", "Miracle"), "Enforcer": Chara(3, "Laterano"), "Executor": Chara(2, "Laterano", "Precision"), "Insider": Chara(1, "Laterano", "Swift"),

    "Skadi the Corrupting Heart": Chara(6, "Aegir"), "Ulpianus": Chara(5, "Aegir"), "Specter the Unchained": Chara(5, "Aegir", "Tenacity"), "Mizuki": Chara(4, "Aegir", "Solitary"), "Gladiia": Chara(4, "Aegir"),
    "Skadi": Chara(3, "Aegir", "Bastion", "Assault"), "Lucilla": Chara(3, "Aegir", "Arcane"), "Specter": Chara(2, "Aegir"), "Underflow": Chara(1, "Aegir"),

    "Lappland the Decadenza": Chara(6, "Siracusa"),  "Suzuran": Chara(5, "Siracusa", "Cover"), "Angelina": Chara(5, "Siracusa", "Miracle"), "Aroma": Chara(4, "Siracusa", "Arcane"), "Texas the Omertosa": Chara(4, "Siracusa", "Assault"),
    "Shamare": Chara(3, "Siracusa", "Support"), "Vulpisfoglia": Chara(3, "Siracusa", "Swift"), "Lappland": Chara(2, "Siracusa"), "Provence": Chara(1, "Siracusa"), "Texas": Chara(1, "Siracusa", "Solitary"),


    "Saria": Chara(5, "Bastion", "Solitary"), "Cuora": Chara(3, "Bastion", "Tenacity"), "Vetochki": Chara(2, "Bastion", "Solitary"), "Gum": Chara(1, "Bastion"),
    "Entelechia": Chara(5, "Tenacity", "Agility"), "Vigna": Chara(1, "Tenacity"),
    "Surtr": Chara(5, "Assault", "Arcane"), "Ines": Chara(4, "Assault", "Foresight"), "Humus": Chara(2, "Assault"), "Utage": Chara(1, "Assault"),
    "Nymph": Chara(6, "Swift"), "Thorns the Lodestar": Chara(5, "Swift", "Miracle"), "Leonhardt": Chara(4, "Swift", "Precision"), "Pinecone": Chara(3, "Swift", "Cover"), "Tippi": Chara(2, "Swift", "Agility"),
    "Rosmontis": Chara(6, "Precision", "Cover", "Foresight"), "Kroos the Keen Glint": Chara(4, "Precision"), "Indigo": Chara(1, "Arcane", "Precision"), "Caper": Chara(1, "Precision"),
    "Astgenne the Lightchaser": Chara(6, "Arcane", "Agility"), "Akkord": Chara(2, "Arcane", "Support"),
    "Ptilopsis": Chara(5, "Agility", "Support"), "Ayerscarpe": Chara(3, "Agility"), "Greyy": Chara(1, "Agility"),
    "Lumen": Chara(6, "Support"), "Eyjafjalla the Hvit Aska": Chara(6, "Support"), "Perfumer": Chara(2, "Support"), "Podenco": Chara(1, "Support"),
    "Civilight Eterna": Chara(5, "Cover", "Miracle"), "Rose Salt": Chara(4, "Cover"),
    "Mudrock": Chara(4, "Solitary"),
    "Santalla": Chara(5, "Foresight"), "Silence": Chara(2, "Foresight"), "Earthspirit": Chara(1, "Foresight", "Miracle"),
    "Warfarin": Chara(5, "Miracle"), "Kazemaru": Chara(2, "Miracle"),
    "Mountain": Chara(5, "Investor"), "Tin Man": Chara(1, "Investor")
}
