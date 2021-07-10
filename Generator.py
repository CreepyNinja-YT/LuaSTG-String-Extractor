from Configuration import Configuration

"""
Small script replacing strings in LuaSTG auto-generated script file.
It replaces strings from script with files containing spells, dialogues and music,
and makes a new file with substituted strings. Naive algorithm, theoretically can be
enhanced with line checking when working in "numbered" mode. Something to work on I guess.

Sibling algorithm - Extractor.py - generates needed files, containing extracted strings.

Created in 4 hours, so the code might still be difficult to read.
Made by CreepyNinja_. Have fun~
"""


class Generator:
    def __init__(self, filename: str = None, configfile: str = 'config.ini'):
        self.configuration = Configuration(configfile)
        self.in_filename = self.configuration.get_if_null('file.script', filename)
        self.out_filename = self.configuration.get('file.script.output')
        self.strings = [
            ('_tmp_sc=boss.card.New(', self.parse_spell),
            ('table.insert(_sc_table', self.parse_spell_alt),
            ('boss.dialog.sentence(', self.parse_dialog),
            ('MusicRecord("', self.parse_music),
            ('].name=', self.parse_boss),
            ('boss.init"', self.parse_boss),
            ('', self.parse_line)
        ]
        self.file = None
        self.line = ""
        self.line_no = 0

        in_suffix = self.configuration.get('input.suffix') + self.configuration.get('input.ext')
        in_spell = self.configuration.get('file.spell') + in_suffix
        in_dialogue = self.configuration.get('file.dialogue') + in_suffix
        in_music = self.configuration.get('file.music') + in_suffix
        self.in_file_spell = open(in_spell, encoding="utf-8")
        self.in_file_dialogue = open(in_dialogue, encoding="utf-8")
        self.in_file_music = open(in_music, encoding="utf-8")
        self.out_file = open(self.out_filename, mode='w', encoding="utf-8")
        self.get_line = self.get_input_function()

    def __del__(self):
        self.in_file_spell.close()
        self.in_file_dialogue.close()
        self.in_file_music.close()

    def get_input_function(self):
        modifier = self.configuration.get('output.modifier')
        if modifier == 'simple':
            return lambda file: file.readline()[:-1]
        elif modifier == 'numbered':
            return self.get_line_numbered  # out_file.write(f'{self.line_no} - "{line}"\n')
        else:
            raise AssertionError('Invalid config option:', modifier)

    def next_line(self):
        self.line = self.file.readline()
        self.line_no = self.line_no + 1
        return self.line

    def get_line_numbered(self, file):
        line = file.readline()
        if line == "":
            return ""
        start = line.find('"')
        end = line.find('"', start + 1)
        if end == -1:
            if line[-2] == '\\':
                return line[start+1:-1]
            else:
                return line[:start]
        return line[start+1:end]

    def output_to_file(self, line):
        self.out_file.write(f'{line}')

    def generate_file(self):
        self.line_no = 0
        with open(self.in_filename, encoding="utf-8") as self.file:
            while self.next_line():
                for string in self.strings:
                    if self.line.find(string[0]) != -1:
                        string[1]()
                        break

    def parse_spell(self):
        line = self.get_line(self.in_file_spell)
        self.replace_quoted_string(line)

    def parse_spell_alt(self):
        line = self.get_line(self.in_file_spell)
        self.replace_quoted_string(line, 2)

    def parse_dialog(self):
        line = self.get_line(self.in_file_dialogue)
        self.replace_quoted_string(line, 3)

    def parse_boss(self):
        print(f'{self.line_no} - Boss string found')
        pass

    def parse_music(self):
        line = self.get_line(self.in_file_music)
        self.replace_quoted_string(line, out=True)

    def parse_line(self):
        self.output_to_file(self.line)

    def replace_quoted_string(self, line, which_string: int = 1, cont: str = '\\', out: bool = False):
        if out:
            print(line)
        start = -1
        end = -1
        for i in range(0, which_string):
            start = self.line.find('"', end + 1)
            end = self.line.find('"', start + 1)
            if start == -1:
                print("WARNING: Quoted string not found in line.")
            elif end == -1:
                if self.line[-2] == cont:
                    if i == which_string - 1:
                        new_line = self.line[:start+1] + line + '\n'
                        self.output_to_file(new_line)
                    self.next_line()
                    line = self.get_line(self.in_file_dialogue)
                    start = 0
                    end = self.line.find('"')
                    if end != -1:
                        continue

                print("WARNING: Quoted string improperly ended.")
        new_line = self.line[:start+1] + line + self.line[end:]
        if out:
            print(new_line)
        self.output_to_file(new_line)


if __name__ == '__main__':
    generator = Generator()
    generator.generate_file()
