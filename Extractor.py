from Configuration import Configuration

"""
Small script extracting LuaSTG auto-generated strings.
It splits results into separate files containing spells, dialogues and music.

Sibling algorithm - Generator.py - assembles these files and replaces found strings appropriately.

Created in 4 hours, so the code might still be difficult to read.
Made by CreepyNinja_. Have fun~
"""


class Extractor:
    def __init__(self, filename: str = None, configfile: str = 'config.ini'):
        self.configuration = Configuration(configfile)
        self.filename = self.configuration.get_if_null('file.script', filename)
        self.strings = [
            ('_tmp_sc=boss.card.New(', self.parse_spell),
            ('table.insert(_sc_table', self.parse_spell_alt),
            ('boss.dialog.sentence(', self.parse_dialog),
            ('MusicRecord(', self.parse_music),
            ('].name=', self.parse_boss),
            ('boss.init"', self.parse_boss),
        ]
        self.file = None
        self.line = ""
        self.line_no = 0

        out_suffix = self.configuration.get('output.suffix') + self.configuration.get('output.ext')
        out_spell = self.configuration.get('file.spell') + out_suffix
        out_dialogue = self.configuration.get('file.dialogue') + out_suffix
        out_music = self.configuration.get('file.music') + out_suffix
        self.out_file_spell = open(out_spell, mode='w', encoding="utf-8")
        self.out_file_dialogue = open(out_dialogue, mode='w', encoding="utf-8")
        self.out_file_music = open(out_music, mode='w', encoding="utf-8")
        self.output_to_file = self.get_output_function()

    def __del__(self):
        self.out_file_spell.close()
        self.out_file_dialogue.close()
        self.out_file_music.close()

    def get_output_function(self):
        modifier = self.configuration.get('output.modifier')
        if modifier == 'simple':
            return lambda out_file, line: out_file.write(f'{line}\n')
        elif modifier == 'numbered':
            return lambda out_file, line: out_file.write(f'{self.line_no} - "{line}"\n')
        else:
            raise AssertionError('Invalid config option:', modifier)

    def next_line(self):
        self.line = self.file.readline()
        self.line_no = self.line_no + 1
        return self.line

    def parse_file(self):
        self.line_no = 0
        with open(self.filename, encoding="utf-8") as self.file:
            while self.next_line():
                for string in self.strings:
                    if self.line.find(string[0]) != -1:
                        string[1]()
                        break

    def parse_spell(self):
        line = self.get_quoted_string()
        self.output_to_file(self.out_file_spell, line)

    def parse_spell_alt(self):
        line = self.get_quoted_string(2)
        self.output_to_file(self.out_file_spell, line)

    def parse_dialog(self):
        line = self.get_quoted_string(3)
        self.output_to_file(self.out_file_dialogue, line)

    def parse_boss(self):
        print(f'{self.line_no} - Boss string found')
        pass

    def parse_music(self):
        line = self.get_quoted_string()
        self.output_to_file(self.out_file_music, line)

    def get_quoted_string(self, which_string: int = 1, cont: str = '\\'):
        start = -1
        end = -1
        continuation = ""
        for i in range(0, which_string):
            continuation = ""
            start = self.line.find('"', end + 1)
            end = self.line.find('"', start + 1)
            if start == -1:
                print("WARNING: Quoted string not found in line", self.line_no)
            elif end == -1:
                if self.line[-2] == cont:
                    continuation = self.line[start+1:end] + '\n'
                    self.next_line()
                    start = 0
                    end = self.line.find('"')
                    if end != -1:
                        continue

                print("WARNING: Quoted string improperly ended in line", self.line_no)
        return continuation + self.line[start+1:end]


if __name__ == '__main__':
    extractor = Extractor()
    extractor.parse_file()
