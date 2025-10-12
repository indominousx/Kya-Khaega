import pandas as pd 
df=pd.read_csv('Zomato_Menu_Classified_with_Area.csv')
# print(df['URL'].nunique())
# print(df['Area'].unique())
# print(df[df['Area']=='Kondhwa'].nunique())
df1=df[df['Area']=='Kondhwa'].groupby('Restaurant_Name').size()
print(df1.index.tolist())