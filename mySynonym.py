import synonyms

words = "英俊;帅气;相貌堂堂;眉清目秀;婀娜;绰约;娉婷;环肥燕瘦;纤腰楚楚;不盈一握" \
        ";娇小玲珑;亭亭玉立;千娇百媚;仪态万方;仪态万千;妩媚;健美;魁梧;挺拔;强壮;健壮;可爱;甜美;楚楚动人" \
        ";长相讨喜;玉骨冰肌;吹弹即破;肤白貌美;妆容精致;光鲜亮丽;出水芙蓉;光彩照人;容光焕发;魅力四射;风华绝代;" \
        "风情万种;颜值巅峰;时尚;新潮;时髦;衣着光鲜;衣着得体;衣冠楚楚;剪裁合身;合体剪裁;剪裁合适;不修边幅;胡子拉碴;"
word_list = []
words_arr = words.split(";")
for w in words_arr:
    # print(w)
    word, distance = synonyms.nearby(w)
    word_list.append(word)
# print(len(words_arr))
for d in word_list:
    print(d)
# word, distance = synonyms.nearby("漂亮")
# # print(word)
