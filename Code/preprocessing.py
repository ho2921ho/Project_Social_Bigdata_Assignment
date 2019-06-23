# -*- coding: utf-8 -*-
"""
Created on Thu Jun 20 16:42:26 2019

@author: dongkeon
"""

#%% 사용자 함수 및 모듈
from hanja import hangul
import pandas as pd
import pickle
import numpy as np
from tqdm import tqdm
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

with open(r'C:\Github\Project_Social_Bigdata_Assignment\Data\all_dict.pickle', 'wb') as f:
    pickle.dump(all_dict , f, pickle.HIGHEST_PROTOCOL)

