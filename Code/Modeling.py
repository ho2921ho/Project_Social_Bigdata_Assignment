#%% 함수.
import os
os.chdir(r'C:\Github\Project_Social_Bigdata_Assignment')
import pandas as pd
import pickle
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import font_manager, rc

import scipy.spatial
from sklearn.cluster import AgglomerativeClustering
from sklearn.manifold import MDS
from scipy.cluster.hierarchy import linkage, dendrogram 

font_name = font_manager.FontProperties(fname="c:/Windows/Fonts/malgun.ttf").get_name()
rc('font', family=font_name)


def find_similar(search_name,matrix,num):
    name = [name for name, hangle_party in all_dict.items() if hangle_party[0] == search_name][0]
    tmp = matrix.loc[name]
    close = tmp.sort_values()[:num]
    unclose = tmp.sort_values()[-num:]
    close = list(map(lambda x : all_dict[x], close.index))
    unclose = list(map(lambda x : all_dict[x], unclose.index))

    return close, unclose

#%% 비유사도 측정 및 거리행렬 
with open(r'C:\Github\Project_Social_Bigdata_Assignment\Data\matrix.pickle', 'rb') as f:
    matrix = pickle.load(f)


a = matrix <= 3
b = a.sum().sum()
c = 298*298
b/c*100

with open(r'C:\Github\Project_Social_Bigdata_Assignment\Data\all_dict.pickle', 'rb') as f:
    all_dict = pickle.load(f)
## 발의 법안의 수로 의원이 구분 될 수 있기 때문에 상관관계 기반 거리 사용. 

distanceMatrix  = scipy.spatial.distance.pdist(matrix ,metric = 'cosine')
distanceMatrix  = scipy.spatial.distance.squareform(distanceMatrix)

distanceMatrix = pd.DataFrame(distanceMatrix)
distanceMatrix.columns = matrix.columns
distanceMatrix.index = matrix.index


#%% 상관계수 기반 거리로 본 개별 의원의 거리. 
close, unclose = find_similar('이상돈',distanceMatrix,40)

#%% 클러스터링. 

with open(r'C:\Github\Project_Social_Bigdata_Assignment\Data\Status.pickle', 'rb') as f:
    status = pickle.load(f)

with open(r'C:\Github\Project_Social_Bigdata_Assignment\Data\status2.pickle', 'rb') as f:
    status2 = pickle.load(f)
    
ac = AgglomerativeClustering(n_clusters = 10,  linkage='average')
labels = ac.fit_predict(distanceMatrix)
party = list(map(lambda x : all_dict[x][1], matrix.columns))
name = list(map(lambda x : all_dict[x][0], matrix.columns))

df = pd.DataFrame({'cluster': labels, 'party':party, 'name':name, 'hanja': matrix.columns})
df = pd.merge(df, status, how = 'left', on = ['name','hanja'])
df =  pd.merge(df, status2, how = 'left', on = ['name','hanja'])
colors = {'자유한국당':'red', '더불어민주당':'blue','바른미래당':'skyblue',
          '정의당':'yellow','무소속':'gray','민주평화당':'green','민중당':'orange','대한애국당':'purple'}
df['color'] = [ colors[x] for x in df.party]

#%% K-elbow
plt.rcParams["figure.figsize"] = (10,10)
Z = linkage(distanceMatrix, 'average')

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
## mds
matrix_embedded = MDS(n_components=2,random_state=1, eps = 0).fit_transform(distanceMatrix)
matrix_embedded = pd.DataFrame(matrix_embedded, columns = ['x1','x2'])
matrix_embedded['party'] = df['party']
matrix_embedded['cluster'] = df['cluster']

plt.rcParams["figure.figsize"] = (10,10)
sns.scatterplot(x = 'x1' , y = 'x2', data = matrix_embedded, hue = 'party', palette = colors)
sns.scatterplot(x = 'x1' , y = 'x2', data = matrix_embedded, hue = 'cluster',palette="Set1")

## 덴도 그램

leaf_colors = dict(zip(df.name,df.color))

plt.rcParams["figure.figsize"] = (50,30)
dend = dendrogram(linkage(distanceMatrix, method='average'), 
     color_threshold=4, 
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



#%% describe cluster 

df.groupby('cluster')['party'].describe()


name = [name for name, hangle_party in all_dict.items() if hangle_party[0] == '문희상'][0]

row = matrix.loc[name]
row.index = map(lambda x : all_dict[x][1], row.index)
all_dict
