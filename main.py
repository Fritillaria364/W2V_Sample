from flask import Flask, render_template, request, logging, Response, redirect, flash
from gensim.models import Word2Vec
from pathlib import Path
import pickle

app = Flask(__name__)

history = []

def w2v(pos,neg,model):
    output = []
    permit = True
    voc = model.wv.vocab.keys()
    pos_w = pos.strip().split()
    neg_w = neg.strip().split()
    for w in pos_w+neg_w:
        if w not in voc:
            permit = False

    if permit:
        result = model.wv.most_similar(positive=pos_w, negative=neg_w, topn=3)
        [ output.append({"word":w, "sim":s}) for w,s in result]
        return output
    else:
        return [{"word":"Failure","sim":"Words not in vocabulary"}]


@app.route('/', methods = ["GET", "POST"])
def index():
    if request.method == 'POST':
        # ポジネガ単語をテキストボックスから取得
        pos = request.form['positive']
        neg = request.form['negative']
        # 入力履歴に追加
        newhis = {"pos":pos, "neg":neg}
        if newhis not in history:
            history.append(newhis)

        # top3の単語とベクトルリストを取得
        # outputはwordとsimilarityをキーに持つdictのリスト
        # -> [{"word":"hoge","sim":"[0 1 2 3 4 5]"},{"word":"huga","sim":"[10 20 30 40 50]"...}
        output = w2v(pos,neg,w2v_model)
        # 結果を反映してレンダリング
        html = render_template('index.html', pos=pos, neg=neg, output=output, history=reversed(history))
    else:
        html = render_template('index.html')
    return html

if __name__ == "__main__":
    p = Path("./word2vec/w2v.model")
    with p.open(mode="rb") as f:
        w2v_model = pickle.load(f)

    app.debug = True
    app.run()
