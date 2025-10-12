import pandas as pd 
df=pd.read_csv("Zomato_Menu_Classified_with_Area.csv")
df1=df['URL'].unique()
print(df1)
with open('new_data.csv', 'w') as f:
    for item in df1:
        f.write("%s\n" % item)

