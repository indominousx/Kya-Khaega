import pandas as pd 
df=pd.read_csv('Zomato_Menu_Classified_with_Area.csv')
print(df['URL'].nunique())
print(df['Area'].unique())