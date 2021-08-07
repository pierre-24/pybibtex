"""
If executed, get the translation table from "utf8enc.dfu".
Requires a working TeX environment (and probably a UNIX system).
Inspired by https://stackoverflow.com/a/4579006.
"""

import subprocess
import re


if __name__ == '__main__':

    lwich = 'kpsewhich'
    m = re.compile(r'\\DeclareUnicodeCharacter{(\w+)}{(.*)}')

    with open(subprocess.check_output([lwich, 'utf8enc.dfu']).strip()) as f:
        lines = f.readlines()

        macros = {}

        print('TRANSLATION_TABLE = {')
        for line in lines:
            result = m.match(line)
            if result:
                unic, ltx = result.groups()
                if ltx[0] != '\\':  # skip the last few lines
                    continue

                codepoint = int(unic, 16)
                if codepoint == 65279:  # skip \0
                    continue

                ltx = ltx.replace('@tabacckludge', '')

                # extract macros
                if not ltx[1].isalpha():
                    name = ltx[1]
                    if name not in macros:
                        macros[name] = {}
                    macros[name][ltx[2:]] = codepoint
                else:
                    backslh = ltx[1:].find('\\')
                    if backslh < 0:
                        cmd = ltx[1:].split(' ')
                    else:
                        cmd = ltx[1:backslh + 1], ltx[backslh + 1:]
                    name = cmd[0]
                    if len(cmd) == 1:  # no args
                        macros[name] = codepoint
                    elif len(cmd) == 2:
                        if name not in macros:
                            macros[name] = {}
                        macros[name][cmd[1]] = codepoint
                    else:
                        raise Exception('more than one arg {}?!?'.format(ltx))

                print("    {}: '{}',".format(codepoint, ltx.replace('\\', '\\\\').replace("'", "\\'")))

        print('}')

        print('REVERSE_TRANSLATION_TABLE = {')
        for key, value in macros.items():
            key = key.replace('\\', '\\\\').replace("'", "\\'")
            if type(value) is int:
                print("   '{}': {},".format(key, value))
            else:
                print("   '{}': {{".format(key))
                for subkey, subvalue in value.items():
                    print("        '{}': {},".format(subkey.replace('\\', '\\\\'), subvalue))
                print('    },')
        print('}')
