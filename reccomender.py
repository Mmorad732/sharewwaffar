from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


w_brand = 2
w_cat = 5
w_name = 1
global similarity_matrix

def concatenate_features(df_row): 
  return ' '.join([df_row['category']]*w_cat)+' '+' '.join([df_row['brand']]*w_brand)+' '.join(df_row['name']*w_name)

def process_text(text):
  text = ' '.join(text.split())
  text=text.lower()
  return text
 
def index_from_title(df,name):
  return df[df['name']==name].index.values[0]

def title_from_index(df,index):
  return df[df.index==index].name.values[0]

def index_from_id(df,id):
    return df[df['id']==id].index.values[0]


def featureMatrix(df):
    df['features'] = df.apply(concatenate_features,axis=1)
    df['features'] = df.apply(lambda x: process_text(x.features),axis=1)
    vect = CountVectorizer(stop_words='english')
    vect_matrix = vect.fit_transform(df['features'])
    global similarity_matrix
    similarity_matrix = cosine_similarity(vect_matrix, vect_matrix)
    

def recommendations( id, df,number_of_recommendations):
  global similarity_matrix
  index = index_from_id(df,id)
  similarity_scores = list(enumerate(similarity_matrix[index]))
  similarity_scores_sorted = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
  recommendations_indices = []
  for t in similarity_scores_sorted[1:(number_of_recommendations+1)]:
    if t[1]>=0.80:
        recommendations_indices.append(t[0])
  
  return df[['id','name']].iloc[recommendations_indices]


    

