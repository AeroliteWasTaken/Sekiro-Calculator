import pandas as pd
pd.set_option('display.max_rows', None)
data = pd.read_csv('python/projects/sekiro stat calc/ItemLotParam.csv', index_col=False)
out = []

with open('python/projects/sekiro stat calc/out.txt', 'w', encoding='utf-8') as file:
    ids = list(map(str, data['ID'].values))
    val = list(map(str, data['Name'].values))
    val1 = list(map(str, data['atkStam'].values))
    val2 = list(map(str, data['atkPhysCorrection'].values))
    val3 = list(map(str, data['atkSuperArmorCorrection'].values))
    val4 = list(map(str, data['repelLostStamDamage'].values))
    val5 = list(map(str, data['dmgLevel'].values))

    for i in range(len(ids)):
        tval = val[i].split(' -- ')[0]
        out.append(f'{int(ids[i])}: ["{tval}", {val1[i]}, {val2[i]}, {val3[i]}, {val4[i]}, {val5[i]}],\n')
    file.write("".join(out))
