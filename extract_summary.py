from gensim.models import word2vec
from sklearn import mixture
from collections import defaultdict
import numpy as np
import jieba
import re

model = word2vec.Word2VecKeyedVectors.load_word2vec_format('D:/datas/model/hanlp-wiki-vec-zh.txt', binary=False)
# model = word2vec.Word2VecKeyedVectors.load_word2vec_format('D:/datas/model/sgns.baidubaike.bigram-char', binary=False)
stop_words = [line.strip() for line in open('D:/datas/stopwords.txt', 'r', encoding='utf-8').readlines()]


def get_sentence_vec(sentence):
    words = jieba.cut(sentence)
    words = [w for w in words if not w in stop_words]
    vec = []
    for word in words:
        if word in model.vocab:
            vec.append(model[word])
        else:
            for w in word:
                if w in model.vocab:
                    vec.append(model[w])
                else:
                    vec.append(np.zeros(model.vector_size))
    mean_vec = None
    if len(vec) < 1:
        print("有空向量：%s" % sentence)
        mean_vec = np.zeros(model.vector_size)
    else:
        mean_vec = np.mean(np.array(vec), axis=0)
    return sentence, mean_vec


# 调用谱聚类函数
def spectral_cluster(k, X):
    from sklearn.cluster import SpectralClustering
    y_pred = SpectralClustering(n_clusters=k, gamma=0.1).fit_predict(X)
    return y_pred


# 调用密度聚类
def dbscan_cluster(X, eps=0.3, min_samples=1):
    from sklearn.cluster import DBSCAN
    db = DBSCAN(eps=eps, min_samples=min_samples).fit(X)
    labels = db.labels_
    return labels


# 调用高斯混合聚类
def gmm_cluster(k, X):
    gmm = mixture.gaussian_mixture.GaussianMixture(n_components=k, covariance_type='full').fit(X)
    y_pred = gmm.predict(X)  # 预测数据簇类
    return y_pred


def get_cluster_summary(doc):
    clusters_summary = ""
    sentences = []
    # sentences = [i for i in re.split('[。.?？！!；]', doc) if len(i) > 2]
    for i in re.split('[。.?？！!]', doc):
        str_length = len(i)
        if 2 < str_length <= 200:
            sentences.append(i)
        if str_length > 200:
            for j in re.split('[;；():：]', i):
                sentences.append(j)

    if len(sentences) > 2:
        sen, vectors = [], []
        for s in sentences:
            se, vec = get_sentence_vec(s)  # 获取句子对应向量
            sen.append(se.strip(' '))
            vectors.append(vec)
        sen_vectors = dict(zip(sen, vectors))  # 将句子和对应的向量转化为映射，方便后期调用查询单句向量
        np_matrix = np.array(vectors)  # 向量转化为numpy数据类型用以训练
        # 调用sklearn库中的（密度）聚类算法，对句子进行聚类
        # n_components = len(sen_vectors) / 3
        y_pred = dbscan_cluster(X=np_matrix, eps=0.5, min_samples=1)
        # 对同簇数据（句子集合）做处理
        d = defaultdict(set)
        for k, v in zip(y_pred, sen):
            if len(v) > 10:
                d[k].add(v)
        # 对每簇数据的数据量做倒排序(类似于TextRank投票机制)
        sen_label_map = dict(sorted(d.items(), key=lambda x: len(x[1]), reverse=True))
        summary_sens = []
        for k, v in sen_label_map.items():
            # print(k, len(v), v)
            sens = [sen_vectors[w] for w in v]
            center_vec = np.mean(np.array(sens))  # 获取簇内中心向量
            dis_jv = {}
            for w in v:  # 获取距离簇中心向量最近的句子，作为簇中心句
                jv = sen_vectors[w]
                dis = np.linalg.norm(center_vec - jv)
                dis_jv[w] = dis
            centens_sen = sorted(dis_jv.items(), key=lambda x: x[1], reverse=True)[0][0]
            summary_sens.append(centens_sen)
        # 合并簇中心句，得到事件摘要
        clusters_summary = "。".join(summary_sens[0:2]).strip(' ')
    # print(clusters_summary)
    else:
        if len(doc) > 200:
            clusters_summary = doc[0:200].strip(' ')
        else:
            clusters_summary = doc.strip(' ')
    clusters_summary = clusters_summary.strip(',，。.?？！!……:：～$') + "。"
    return re.sub("[！!，。?？：；]{2,}", "，", clusters_summary).lstrip('”『:：』」》】）)]')


if __name__ == '__main__':
    import time
    start = time.time()
    doc = '12月20日，河南省高级人民法院依法对被告人赵志勇、李娜、刘洪羊、周合鑫强奸、组织、强迫卖淫、协助组织卖淫一案二审当庭宣判。' \
          '以强奸罪判处被告人赵志勇死刑，剥夺政治权利终身，并依法报请最高人民法院核准；以强奸罪、组织、强迫卖淫罪判处被告人李娜死刑，缓期两年执行，' \
          '剥夺政治权利终身，限制减刑；其他两名被告人分别被判处十八年到十二年有期徒刑。' \
          '发生在河南省尉氏县的这起性侵幼女案，动机特别卑劣，情节极其恶劣，作案手段十分残忍，案发后受到社会各界高度关注。' \
          '司法机关依法严厉惩治侵害未成年人犯罪，为被害未成年人及其家庭主持正义与公道，彰显了司法体系对侵害未成年人权益犯罪行为“零容忍”的态度。' \
          '保护未成年人身心健康不受侵犯，是人类现代文明的底线与准则。未成年人是社会的未来，他们身心发育不成熟，抵御和防范外部侵害的能力弱。' \
          '对未成年人实施特殊的保护，是维护社会正义的题中应有之义。尉氏性侵幼女案被曝光后，引发民众的极大愤慨。对于社会热点案件的审判执行工作，要高度关注社情民意，更要坚守法律正义和社会正义，努力实现法、理、情的有机结合。' \
          '河南省高院判处此案主犯死刑，并依法报请最高人民法院核准，既坚持以法律为准绳，又充分考虑社情民意，显示了司法机关坚决维护未成年人权益的决心。' \
          '近年来，侵害未成年人犯罪呈上升趋势，性侵害和伤害案件占据较大比例。' \
          '根据最高检公开发布的信息，侵害未成年人的重大恶性案件时有发生，不少案件犯罪次数多、被害人多、时间跨度长。' \
          '针对未成年人的性侵案件屡屡引发社会热议。打击性侵未成年人犯罪，需要国家、社会、学校、家庭的共同努力，开展全方位的综合治理，而司法是不容缺席的关键一环。' \
          '我国法律对性侵未成年人犯罪早已有明确态度，构筑了不容逾越的高压线年，' \
          '最高人民法院、最高人民检察院、公安部、司法部出台《关于依法惩治性侵害未成年人犯罪的意见》，强调针对未成年人实施强奸、猥亵犯罪的，' \
          '应当从重处罚年8月，刑法修正案（九）废除了嫖宿幼女罪，有关嫖宿幼女的违法犯罪行为依据强奸罪的对应条款处理，而强奸幼女属强奸罪从重处罚情节，' \
          '最高可判死刑。近日，最高人民检察院还发布指导性案例，对性侵未成年人犯罪案件证据审查判断标准提出明确指导意见。对于未成年人性侵案件，' \
          '不仅要从重处罚犯罪分子，还要特别注意保护受害者隐私信息，避免造成二次伤害。法院依法不公开开庭审理尉氏性侵幼女案，体现了对受害者特殊的保护。' \
          '社会舆论在关注性侵未成年人案件时，也要避免公开有可能暴露当事人身份的信息，在正常舆论监督和保护未成年人权益之间严守合理的尺度。' \
          '司法机关依法顶格论处此案，判处主犯极刑，将给侵害未成年人犯罪极大的震慑，释放法律绝不姑息纵容此类案件的信号。' \
          '未成年人是含苞待放的花朵，不让这些美丽的花朵受到玷污，是国家的责任，也是全社会任何有良知者义不容辞的责任。'
    # print(get_cluster_summary(doc))

    import pandas as pd
    from pandas.core.frame import DataFrame

    df = pd.read_csv("E:/gitpython/my_seq2seq_stu/data/labels.csv")
    data = zip(df['event'], df['content'])
    d = defaultdict(set)
    march_re = '注：[\u4e00-\u9fa5，,]+|[\u4e00-\u9fa5，-]*网页链接|原标题：|导读：|发布了头条文章|' \
               '转：|[\u4e00-\u9fa5@ /]*[微博网易秒拍]视频|[关注]*@[\u4e00-\u9fa5]+|/+|' \
               '[\u4e00-\u9fa5\\，, ]*编辑：[\u4e00-\u9fa5]*|[\u4e00-\u9fa5]*源：[\u4e00-\u9fa5\\w]+|' \
               '免责声明.+。|[#【][\u4e00-\u9fa5\\w]+[#】]'
    for k, v in data:
        con = re.sub(march_re, "", v)
        d[k].add(con)

    dic = {}
    for k in d.keys():
        # print(len(d[k]))
        dic[k] = "。".join(d[k])
    event_summary = {}
    for k, v in dic.items():
        event_summary[k] = get_cluster_summary(v)

    for ev, es in event_summary.items():
        print(ev + "==================" + es)

    # summary_data = event_summary.items()
    summary_df = pd.DataFrame({'event': list(event_summary.keys()), 'summary': list(event_summary.values())})
    # print(summary_df['summary'])
    result = pd.merge(df, summary_df, on=['event'])
    print(result.columns.values)
    result.to_csv(r'E:/gitpython/my_seq2seq_stu/data/event_summary.csv', encoding='utf-8')
    print(time.time() - start)
