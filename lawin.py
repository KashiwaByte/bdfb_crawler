#该文件用于匹配法律名称然后插入法条内容


import pandas as pd

# 读取文件
laws_a_df = pd.read_csv('laws_A.csv', encoding='utf-8')
laws_b_df = pd.read_csv('laws_B.csv', encoding='utf-8')

# 创建一个字典来映射A文件中的法律名称到法条内容
law_to_content_map = pd.Series(laws_a_df['法条内容'].values, index=laws_a_df['法律名称']).to_dict()

# 遍历B文件，查找匹配的法律名称并更新法条内容
for index, row in laws_b_df.iterrows():
    law_name = row['法律名称']
    if law_name in law_to_content_map:
        # 如果找到匹配的法律名称，更新法条内容
        laws_b_df.at[index, '法条内容'] = law_to_content_map[law_name]

# 将更新后的B文件保存到新的CSV文件中
laws_b_df.to_csv('updated_laws_B.csv', index=False, encoding='utf-8')

print('B文件已更新并保存为 "updated_laws_B.csv"')
