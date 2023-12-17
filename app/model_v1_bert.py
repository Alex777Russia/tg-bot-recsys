import pandas as pd
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel


tokenizer = AutoTokenizer.from_pretrained("cointegrated/rubert-tiny2")
model = AutoModel.from_pretrained("cointegrated/rubert-tiny2")

def embed_bert_cls(text, model=model, tokenizer=tokenizer):
    # векторизация текста
    t = tokenizer(text, padding=True, truncation=True, return_tensors='pt')
    with torch.no_grad():
        model_output = model(**{k: v.to(model.device) for k, v in t.items()})
    embeddings = model_output.last_hidden_state[:, 0, :]
    embeddings = torch.nn.functional.normalize(embeddings)
    return embeddings[0].cpu().numpy()

def cos(a, b):
    # Считает косинусную близость между двумя векторами
    return a@b/((a**2).sum() * (b**2).sum())

def load_rubrics(file_path):
    # Возвращает DataFrame рубрик
    rubrics = pd.read_csv(file_path)
    rubrics = rubrics.drop("Unnamed: 0", axis=1)
    return rubrics

def rubric_to_vector(vec_comment, rubrics, count_rubrics):
    # Получает векторизованный комментарий, dataframe рубрик и количество рубрик
    # возвращает 3 текстовые наиболее близкие категории -> list[str]
    result = []
    for i in range(count_rubrics):
        rub = rubrics.iloc[i]
        result.append([cos(vec_comment, rub.vector), rub.split_rubrics])
    result = sorted(result, reverse=False)
    
    return result[-1][1], result[-2][1], result[-3][1]

def prepare_data(file_path):
    rubrics = load_rubrics(file_path)

    result = rubrics['vector'].apply(lambda x: 
                           np.fromstring(
                               x.replace('\n','')
                                .replace('[','')
                                .replace(']','')
                                .replace('  ',' '), sep=' '))
    rubrics.vector = result
    return rubrics

def load_organisations(path_to_organizations_file):
    db = pd.read_csv(path_to_organizations_file)
    db = db.drop("Unnamed: 0", axis=1)
    return db