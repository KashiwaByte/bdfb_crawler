# 该文件用于插入新列 发行类别
import pandas as pd

# 读取CSV文件
laws_df = pd.read_csv('updated_laws_B.csv', encoding='utf-8')

# 在'发文字号'和'公布日期'之间插入新的列'发行类别'，并填充值为'中央'
# 首先找到'发文字号'列的位置
issue_num_index = laws_df.columns.get_loc('发文字号')

# 使用insert方法在指定位置插入新列
#laws_df.insert(issue_num_index + 1, '发行类别', '中央')

laws_df.insert(issue_num_index + 1, '发行类别', '地方')
# 保存更新后的数据到新的CSV文件

#laws_df.to_csv('central_laws.csv', index=False, encoding='utf-8')

laws_df.to_csv('local_laws.csv', index=False, encoding='utf-8')

print('文件已更新并保存为 "local_laws.csv"')
