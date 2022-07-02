import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


w_brand = 2
w_cat = 5
w_name = 1

def concatenate_features(df_row):
    return ' '.join([df_row['category']]*w_cat)+' '+' '.join([df_row['brand']]*w_brand)+''.join(df_row['name']*w_name)

def process_text(text):
    text = ' '.join(text.split())
    text=text.lower()
    return text
 
def index_from_id(df,id):
    return df[df['id']==id].index.values[0]

def recommend(df,id):
    return featureMatrix(df,id)

def featureMatrix(df,id):
    df['features'] = df.apply(concatenate_features,axis=1)
    df['features'] = df.apply(lambda x: process_text(x.features),axis=1)
    vect = CountVectorizer(stop_words='english')
    vect_matrix = vect.fit_transform(df['features'])
    recommends = []
    for i in id:
        prod_index = index_from_id(df,i)
        prod_vect_matrix = vect_matrix[prod_index]
        similarity_matrix = cosine_similarity(prod_vect_matrix, vect_matrix)
        for j in recommendations(df,similarity_matrix,3):
            recommends.append(j)
    return list(np.unique(np.array(recommends)))

def recommendations( df,similarity_matrix,number_of_recommendations):
  similarity_scores = list(enumerate(similarity_matrix[0]))
  similarity_scores_sorted = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
  recommendations_indices = []
  for t in similarity_scores_sorted[1:(number_of_recommendations+1)]:
    if t[1]>=0.70:
        recommendations_indices.append(t[0])
  
  return df[['id']].iloc[recommendations_indices].values.ravel()




    

