
#%% EDA ### EDA 할 때는 대표발의 테이터로 다시하기 -> 생략 문제를 최대한 단순하게 가져가자.
with open(r'C:\Github\Project_Social_Bigdata_Assignment\Data\raw2.pickle', 'rb') as f:
    raw2 = pickle.load(f)

# 국회의원 사전 만드는 함수.
    




# 원내 7당체재 기준, 바른미래당 창당. 최근 1년 동안 법안을 가장 많이/적게 만든 의원 
color_dict = {'더불어민주당':'blue','자유한국당':'red','바른미래당':'skyblue','민주평화당':'green','정의당':'yellow','무소속':'gray','대한애국당':'darkblue','민중당':'orange'}
EDA1 = pd.DataFrame({'hanja':tmpmem,'party':tmppar,'hangle':hangle})

cnt = EDA1.hanja.value_counts()[0:30]

plt.figure(figsize=(10, 10))
height = cnt.values
bars = list(map(lambda x:mem_dict[x][0],cnt.index))
y_pos = np.flip(np.arange(len(bars)))
color = list(map(lambda x:color_dict[x],list(map(lambda x:mem_dict[x][1],cnt.index))))

plt.barh(y_pos, height,color = color) ; plt.yticks(y_pos, bars) 
plt.title('발의법안 수 상위 의원')
plt.show()


cnt = EDA1.hanja.value_counts()[-31:-1]

plt.figure(figsize=(10, 10))
height = cnt.values
bars = list(map(lambda x:mem_dict[x][0],cnt.index))
y_pos = np.arange(len(bars))
color = list(map(lambda x:color_dict[x],list(map(lambda x:mem_dict[x][1],cnt.index))))


plt.barh(y_pos, height,color = color) ; plt.yticks(y_pos, bars) 
plt.axvline(x= mean_cnt, color = 'red', ls = 'dotted')
plt.title('발의법안 수 하위 의원')
plt.show()

# 최근 6개월 1인당 법안 발의 수 가장 높은/낮은 정당. 
cnt = EDA1.party.value_counts()

tmp = EDA1.groupby(['hanja','party']).count().index.get_level_values(1)
tmp = list(tmp)
b = pd.Series(tmp).value_counts()
b.values.sum()

height = cnt.values
bars = cnt.index
color = list(map(lambda x:color_dict[x],bars))
y_pos = np.flip(np.arange(len(bars)))
 
plt.barh(y_pos, height,color = color) ; plt.yticks(y_pos, bars) 
plt.axvline(x=np.mean(height), color = 'red', ls = 'dotted')
plt.title('정당별 총 발의 법안 수')
plt.show()

mean_cnt = np.mean(height/b)
plt.barh(y_pos, height/b ,color = color) ; plt.yticks(y_pos, bars) 
plt.axvline(x= mean_cnt, color = 'red', ls = 'dotted')
plt.title('정당별 1 인당 발의 법안 수')
plt.show() 

# 법률안 발의 빈도의 시계열 추이. (일주일 간격.)

EDA3 = raw2['date'].to_frame()
EDA3.set_index('date', inplace=True)
EDA3['count'] = 1
EDA3 = EDA3.resample('30D', how='sum')

y = EDA3['count'][:-1]
x = EDA3.index[:-1]
plt.plot(x,y)

# 별차이가 없다... 