# scaffold.py
class Tag:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return repr(self.name)


class Character:
    def __init__(self, *args):
        self.tags = tuple([Character.TAGS[tag] for tag in args])

    def __repr__(self):
        return repr(self.tags)

    def has_tag(self, tag):
        return tag in self.tags
    TAGS_DEF = 'Yan', 'Sargon', 'Victoria', 'Kjerag', 'Laterano', 'Aegir', 'Siracusa', 'Kazimierz', \
               'Bastion', 'Tenacity', 'Assault', 'Swift', 'Precision', 'Arcane', \
               'Agility', 'Support', 'Cover', 'Solitary', 'Harmony', \
               'Foresight', 'Miracle', 'Investor', 'Skill'
    TAGS = {tag: Tag(tag) for tag in TAGS_DEF}


class Protocol:
    def __init__(self, chara_pool):
        self.chara_pool = chara_pool

    def __repr__(self):
        return str(len(self.chara_pool)) + ' Characters Registered.'

    def count_tag(self, tag):
        return len(self.get_tag(tag))

    def get_tag(self, tag):
        pawns = []
        for k, v in self.chara_pool.items():
            if v.has_tag(tag):
                pawns.append(k)
        return pawns


Chara = Character
