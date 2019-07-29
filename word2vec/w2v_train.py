import MeCab
import pickle
import pandas as pd
from pathlib import Path
from gensim.models import Word2Vec
import multiprocessing

corpus_path = Path("./corpus/narou_corpus.pkl")
if corpus_path.exists():
    with corpus_path.open(mode="rb") as f:
        corpus = pickle.load(f)
        print("corpus loaded")
else:
    def get_text_from_csv(path):
        df = pd.read_csv(path)
        text = "".join(df["Text"])
        return text
    print("Start corpus creating")

    csv_root = Path("./corpus/narou")
    csv_list = csv_root.glob("*")

    tagger = MeCab.Tagger("-d /usr/lib/x86_64-linux-gnu/mecab/dic/mecab-ipadic-neologd")
    white_list = ["名詞","形容詞","動詞"]
    corpus = []
    #for csv_path in itertools.islice(csv_list,1):
    for csv_path in csv_list:
        print("Now processing: ",csv_path.stem)
        text = get_text_from_csv(csv_path)
        if len(text)==0:continue
        result = tagger.parse(text.replace("　","")).strip().split("\n")
        sent = []
        for line in result[:-2]:
            w,detail = line.strip().split("\t")
            hinsi = detail.split(",")[0]
            if hinsi in white_list:
                sent.append(w)
        corpus.append(sent)
    with corpus_path.open(mode="wb") as f:
        pickle.dump(corpus,f)
    print("Done, corpus created")

print("-"*50)
print("Training Word2vec")
cores = multiprocessing.cpu_count()
w2v_model = Word2Vec(min_count=20, window=3, size=100, sample=6e-5, alpha=0.03, min_alpha=0.0007, negative=20, workers=cores-1)
w2v_model.build_vocab(corpus, progress_per=10000)
w2v_model.train(corpus, total_examples=w2v_model.corpus_count, epochs=30, report_delay=1)
w2v_model.init_sims(replace=True)

w2v_model_path = Path("./w2v.model")
with w2v_model_path.open(mode="wb") as f:
    pickle.dump(w2v_model,f)

