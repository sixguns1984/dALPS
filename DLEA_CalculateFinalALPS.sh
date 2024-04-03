import pandas as pd

# 读取原始CSV文件
input_csv = '/home/lincha/tem5/ppmi/ppmi1/output.csv'
df = pd.read_csv(input_csv)
df.fillna(0, inplace=True)
# 添加'ALPS_right'和'ALPS_left'列
df['ALPS_right'] = df.apply(lambda row: (row['value1'] + row['value2']) / (row['value3'] + row['value4']) if (row['value3'] + row['value4']) != 0 and row['value1'] != 0 else 0, axis=1)
df['ALPS_left'] = df.apply(lambda row: (row['value5'] + row['value6']) / (row['value7'] + row['value8']) if (row['value7'] + row['value8']) != 0 and row['value5'] != 0 else 0, axis=1)

# 保存带有新列的CSV文件
df.to_csv(input_csv, index=False)

# 创建ALPS.csv文件
output_csv = '/home/lincha/tem5/ppmi/ppmi1/ALPS.csv'

# 用于存储id和对应的ALPS值的字典
id_to_alps = {}

# 遍历DataFrame，计算id相同的非零ALPS值的平均值
for _, row in df.iterrows():
    filename = row['filename']
    id = filename.split('_')[0]
    if id not in id_to_alps:
        id_to_alps[id] = {'ALPS_right': [], 'ALPS_left': []}
    if row['ALPS_right'] != 0:
        id_to_alps[id]['ALPS_right'].append(row['ALPS_right'])
    if row['ALPS_left'] != 0:
        id_to_alps[id]['ALPS_left'].append(row['ALPS_left'])

# 计算平均值并保存到ALPS.csv文件

with open(output_csv, 'w') as f:
    f.write('id,aver\n')
    for id, values in id_to_alps.items():
        alps_right_avg = sum(values['ALPS_right']) / len(values['ALPS_right']) if len(values['ALPS_right']) > 0 else 0
        alps_left_avg = sum(values['ALPS_left']) / len(values['ALPS_left']) if len(values['ALPS_left']) > 0 else 0
        if alps_right_avg != 0 and alps_left_avg != 0:
            f.write(f'{id},{(alps_right_avg + alps_left_avg) / 2}\n')
        elif alps_right_avg != 0 or alps_left_avg != 0:
            f.write(f'{id},{(alps_right_avg + alps_left_avg)}\n')
        else:
            f.write(f'{id},0\n')
