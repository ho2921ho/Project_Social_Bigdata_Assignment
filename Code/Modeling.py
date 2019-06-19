#%% 함수.
import os
os.chdir(r'C:\Github\Project_Social_Bigdata_Assignment')
import pandas as pd
import pickle
from tqdm import tqdm
import numpy as np

def mem_dict(df): 
    df = df.members   
    
    tmpmem = []
    tmppar = []
    hangle = []
    for i in df:
        for j in i:
            tmpmem.append(j[2])
            tmppar.append(j[1])
            hangle.append(j[0])
    
    mem_df = pd.DataFrame({'hanja':tmpmem,'hangle':hangle,'party':tmppar})
    mem_df = mem_df.drop_duplicates(subset = ['hanja','hangle'], keep = 'first').reset_index(drop = True)
    for idx,i in enumerate(mem_df.hangle):
        if len(i)>4:
            mem_df.drop(index = idx, inplace = True)
    
    mem_df.reset_index(drop = True, inplace = True)
    
    mem_dict = {}
    for idx, i in enumerate(mem_df.hanja):
        mem_dict[i] = [mem_df.hangle[idx],mem_df.party[idx]]
    
    return mem_dict 


def make_matrix(df):
    two_mode_matrix = []
    for i in tqdm(df.members):
        where = [x[2] for x in i]
        try:
            where = [idx_dict[x] for x in where]
        except:
            pass
        law_one= []
        for i in range(len(idx_dict)):
            if i in where:
                law_one.append(1.)
            else:
                law_one.append(0.)
        two_mode_matrix.append(law_one)
    
    two_mode_matrix = np.array(two_mode_matrix)
    one_mode_matrix = np.dot(two_mode_matrix.T,two_mode_matrix)

    return one_mode_matrix

def find_similar(search_name,matrix,num):
    name = [name for name, hangle_party in all_dict.items() if hangle_party[0] == search_name][0]
    tmp = matrix.loc[name]
    close = tmp.sort_values()[:num]
    unclose = tmp.sort_values()[-num:]
    
    close = list(map(lambda x : all_dict[x], close.index))
    unclose = list(map(lambda x : all_dict[x], unclose.index))

    return close, unclose

def data_cleansing(search_name,matrix,delete = False):
    
    name = [name for name, hangle_party in all_dict.items() if hangle_party[0] == search_name]
    
    if delete == False:
        print(name)
        print('select remove name')
        remove_column = input()
        remove_column = int(remove_column)
        a = matrix.loc[name[0],]
        b = matrix.loc[name[1],]
        c = a+b
        matrix.loc[name[1],] = c
        
        matrix = matrix.drop(columns = name[remove_column], index = name[remove_column])
        all_name.remove(name[remove_column])
        all_dict.pop(name[remove_column],None)
    if delete == True:
        name = [name for name, hangle_party in all_dict.items() if hangle_party[0] == search_name][0]
        matrix = matrix.drop(columns = name, index = name)
        all_name.remove(name)
    return matrix

#%% 전처리, 최근 6개월 동안의 클러스터링. 12.28 ~ 6.14 

with open(r'C:\Github\Project_Social_Bigdata_Assignment\Data\raw2.pickle', 'rb') as f:
    raw2 = pickle.load(f)

all_dict = mem_dict(raw2)
all_name = sorted(list(set(all_dict)))

idx_dict = {} ## 벡터의 순서를 표현하기 위해 한자와 idx를 mapping
for idx, i in enumerate(all_name):
    idx_dict[i] = int(idx)


matrix = make_matrix(raw2) 
matrix = pd.DataFrame(matrix)
matrix.columns = all_name 
matrix.index = all_name 

## 데이터 클렌징. 
## 오타로 인한 추가 구분 테이터를 통합. 
from hanja import hangul

for i in matrix.columns:
    tmp = 0
    for j in i:
        tmp += hangul.is_hangul(j)
    if tmp != 0:
        print(i,all_dict[i])
        
matrix = data_cleansing('심상정',matrix)
matrix = data_cleansing('민병두',matrix)
    
## 의원직이 박탈된 사람은 제거.
with open(r'C:\Github\Project_Social_Bigdata_Assignment\Data\remove_list.pickle', 'rb') as f:
    remove_list = pickle.load(f)

for i in remove_list:
    try:
        matrix = data_cleansing(i,matrix, delete = True)
    except:
        print(i)

# 전처리된 자료 저장.    
with open(r'C:\Github\Project_Social_Bigdata_Assignment\Data\matrix.pickle', 'wb') as f:
    pickle.dump(matrix , f, pickle.HIGHEST_PROTOCOL)


#%% 비유사도 측정 및 거리행렬 
with open(r'C:\Github\Project_Social_Bigdata_Assignment\Data\matrix.pickle', 'rb') as f:
    matrix = pickle.load(f)
## 발의 법안의 수로 의원이 구분 될 수 있기 때문에 상관관계 기반 거리 사용. 


import scipy.spatial
distanceMatrix  = scipy.spatial.distance.pdist(matrix ,metric = 'cosine')
distanceMatrix  = scipy.spatial.distance.squareform(distanceMatrix)

distanceMatrix = pd.DataFrame(distanceMatrix)
distanceMatrix.columns = matrix.columns
distanceMatrix.index = matrix.index

#%% 상관계수 기반 거리로 본 개별 의원의 거리. 
unclose, close = find_similar('문희상',matrix,40)

#%% 클러스터링. 
from sklearn.cluster import AgglomerativeClustering

with open(r'C:\Github\Project_Social_Bigdata_Assignment\Data\Status.pickle', 'rb') as f:
    status = pickle.load(f)

with open(r'C:\Github\Project_Social_Bigdata_Assignment\Data\status2.pickle', 'rb') as f:
    status2 = pickle.load(f)
    
ac = AgglomerativeClustering(n_clusters = 3,  linkage='complete')
labels = ac.fit_predict(distanceMatrix)
party = list(map(lambda x : all_dict[x][1], matrix.columns))
name = list(map(lambda x : all_dict[x][0], matrix.columns))

df = pd.DataFrame({'cluster': labels, 'party':party, 'name':name, 'hanja': matrix.columns})
df = pd.merge(df, status, how = 'left', on = ['name','hanja'])
df =  pd.merge(df, status2, how = 'left', on = ['name','hanja'])


#%% K-elbow
plt.rcParams["figure.figsize"] = (10,10)
Z = linkage(distanceMatrix, 'complete')

last = Z[-10:, 2]
last_rev = last[::-1]
idxs = np.arange(1, len(last) + 1)
plt.plot(idxs, last_rev)

acceleration = np.diff(last, 2)  # 2nd derivative of the distances
acceleration_rev = acceleration[::-1]

plt.plot(idxs[:-2] + 1, acceleration_rev)
plt.show()
k = acceleration_rev.argmax() + 2  # if idx 0 is the max of this we want 2 clusters
print ("clusters:", k)

#%% 시각화. 
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import font_manager, rc
font_name = font_manager.FontProperties(fname="c:/Windows/Fonts/malgun.ttf").get_name()
rc('font', family=font_name)


colors = {'자유한국당':'red', '더불어민주당':'blue','바른미래당':'skyblue',
          '정의당':'yellow','무소속':'gray','민주평화당':'green','민중당':'orange','대한애국당':'purple'}

## mds
from sklearn.manifold import MDS
from sklearn.manifold import TSNE
matrix_embedded = MDS(n_components=2,random_state=1, eps = 0).fit_transform(distanceMatrix)
matrix_embedded = pd.DataFrame(matrix_embedded, columns = ['x1','x2'])
matrix_embedded['party'] = df['party']
matrix_embedded['cluster'] = df['cluster']

plt.rcParams["figure.figsize"] = (10,10)
sns.scatterplot(x = 'x1' , y = 'x2', data = matrix_embedded, hue = 'party', palette = colors)
sns.scatterplot(x = 'x1' , y = 'x2', data = matrix_embedded, hue = 'cluster',palette="Set1")

## 덴도 그램
df['color'] = [ colors[x] for x in df.party]
from scipy.cluster.hierarchy import linkage, dendrogram 

leaf_colors = dict(zip(df.name,df.color))

plt.rcParams["figure.figsize"] = (50,10)
dend = dendrogram(linkage(distanceMatrix, method='complete'), 
     color_threshold=15, 
     leaf_font_size=9, 
     labels = df.name.tolist())

ax = plt.gca()
xlbls = ax.get_xmajorticklabels()
for lbl in xlbls:
    lbl.set_color(leaf_colors[lbl.get_text()])

plt.show()

## barchart

bar = df.groupby(['cluster']).party.value_counts().unstack('cluster').fillna(0)
bar = bar / bar.sum(axis=0)
bar = bar.T

plt.rcParams["figure.figsize"] = (10,10)
bar.plot(kind='bar', stacked=True, color=[colors.get(x, '#333333') for x in bar.columns])



