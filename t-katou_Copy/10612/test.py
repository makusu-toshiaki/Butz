import MeCab as mc

import oseti
o = oseti.Analyzer()
print(oseti.Analyzer().analyze("優勝"))

def mecab_analysis(texts):
    t = mc.Tagger("")
    t.parse('')
    output = []
    node =  t.parseToNode(texts)  
    while node:
        if node.surface != "":  # ヘッダとフッタを除外
            word_type = node.feature.split(",")[0]
            if word_type in ['名詞']:
                output.append(node.surface)
        node = node.next
        if node is None:
            break
    return output

print(mecab_analysis("加藤稔朗は巻須稔明です"))