lugat = {'А': 'A', 'Б': 'B', 'Ч': 'Ch', 'Д': 'D', 'Е': 'E', 'Ф': 'F', 'Г': 'G', "Ғ": "G'", 'Ҳ': 'H',
         'И': 'I', 'Ж': 'J', 'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N', 'О': 'O', "Ў": "O'", 'П': 'P',
         'Қ': 'Q', 'Р': 'R', 'С': 'S', 'Ш': 'Sh', 'Т': 'T', 'У': 'U', 'В': 'V', 'Х': 'X', 'Й': 'Y',
         'З': 'Z', 'Я': 'ya', 'Ц': 'ts', 'Ю': 'yu', 'Ё': 'yo', 'Ъ': '', 'Ь': '', 'Ы': 'i', 'Э': 'e'}

l = lugat.copy()
for v, k in l.items():
    lugat[k] = v


def krill_to(words):
    """ krill to latin or latin to kiril"""

    i = 0
    son = -1
    gap2 = ""
    word = ''
    text11 = words
    while i < (len(text11)):
        try:
            if (text11[i] + text11[i+1]) == "Sh":
                word = "Sh"
                son = i
            elif (text11[i] + text11[i+1]) == "sh":
                word = "sh"
                son = i
            elif (text11[i] + text11[i+1]) == "Ch":
                word = "Ch"
                son = i
            elif (text11[i] + text11[i+1]) == "ch":
                word = "ch"
                son = i
            elif (text11[i] + text11[i+1]) == "o'":
                word = "o'"
                son = i + 1
            elif (text11[i] + text11[i+1]) == "O'":
                word = "O'"
                son = i + 1
            elif (text11[i] + text11[i+1]) == "g'":
                word = "g'"
                son = i + 1
            elif (text11[i] + text11[i+1]) == "G'":
                word = "G'"
                son = i + 1
        except:
            pass
        if son == i:
            if text11[i].islower():
                word = text11[i].upper() + "h"
                gap2 = gap2 + lugat[word].lower()
            else:
                gap2 = gap2 + lugat[word]
            i += 1
        elif son == (i+1):
            if text11[i].islower():
                word = text11[i].upper() + "'"
                gap2 = gap2 + lugat[word].lower()
            else:
                gap2 = gap2 + lugat[word]
            i += 1
        else:
            try:
                lu = lugat[text11[i].upper()]
                if text11[i].islower():
                    gap2 = gap2 + lugat[text11[i].upper()].lower()
                else:
                    gap2 = gap2 + lugat[text11[i]]
            except:
                gap2 = gap2 + text11[i]
        i += 1
    return gap2


def makeWord(word):
    words = word.split(',')
    for i in range(1, len(words)):
        if not words[i].startswith(' '):
            words[i] = ' ' + words[i]
    return ','.join(words)
