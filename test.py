
from image_classifier import ImageClassifier
from torchvision import models
from MultiModelClassifier import MultiModelClassifier



# 自定义设置
#classifier =MultiModelClassifier(
#   model_name="inception_v3",
#   weights="DEFAULT"
#)

#一般模型设置，默认为resnet50
classifier=ImageClassifier()

results = classifier.predict("t2.jpg")

# 定义通用类别映射
GENERIC_CATEGORIES = {
    '动物': [
        'bird', 'cat', 'dog', 'fish', 'shark', 'tiger', 'lion',
        'bear', 'elephant', 'horse', 'zebra', 'whale', 'dolphin'
    ],
    '人物': [
        'person', 'groom', 'diver', 'player', 'baby'
    ],
    '风景': [
        'mountain', 'beach', 'valley', 'volcano', 'cliff',
        'coral', 'geyser', 'lake', 'coast','lakeside, lakeshore'
    ],
    '交通工具': [
        'car', 'bicycle', 'airplane', 'bus', 'train',
        'ship', 'motorcycle', 'truck'
    ],
    '植物': [
        'tree', 'flower', 'palm', 'cactus', 'mushroom',
        'broccoli', 'cabbage', 'corn', 'apple', 'orange'
    ],
    '电子设备': [
        'computer', 'laptop', 'monitor', 'keyboard',
        'mouse', 'printer', 'scanner', 'camera'
    ],
    '食物': [
        'pizza', 'burger', 'sushi', 'bread', 'cake',
        'ice cream', 'coffee', 'wine', 'soup'
    ]
}

def get_generic_category(label):
    """将具体标签映射到通用类别"""
    label = label.lower()
    for category, keywords in GENERIC_CATEGORIES.items():
        for keyword in keywords:
            if keyword in label:
                return category
    return '其他'


category=''
flag=1
for label, confidence in results:
    print(f"{label}: {confidence:.2%}")
    if flag==1:
        category=get_generic_category(label)
        flag=0

print(f"类别：{category}")



