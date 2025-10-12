# import pandas as pd
# df1=pd.read_csv("Zomato_Menu_Classified_with_Area.csv")
# df2=pd.read_csv("zomato_dining_ratings.csv")
# newdf=pd.merge(df1,df2,on='URL',how='left')
# newdf.to_csv('NewZomatoDataset.csv',index=False)
# print(newdf)

import pandas as pd
df=pd.read_csv(r'D:\Kya-Khaega\backend\NewZomatoDataset.csv')
# print(df['Dining_Rating'].isna().sum())
df