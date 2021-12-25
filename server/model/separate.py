import json


with open('res.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for ann in data['annotations']:
    ann['bbox'] = list(map(int, ann['bbox']))
    ann['area'] = int(ann['area'])
    
    bb = ann['bbox']
    ann['segmentation'] = [[
        bb[0],
        bb[1],
        bb[0],
        bb[3],
        bb[2],
        bb[3],
        bb[2],
        bb[1]
    ]]

with open('res-segm.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
