from image_classifier import ImageClassifier
from torchvision import models
from MultiModelClassifier import MultiModelClassifier

# 通用类别映射（全局常量）
GENERIC_CATEGORIES = {
    '动物': ['bird', 'cat', 'dog', 'fish', 'shark', 'tiger', 'lion', 'bear', 'elephant', 'horse', 'zebra', 'whale',
             'dolphin'],
    '人物': ['person', 'groom', 'diver', 'player', 'baby'],
    '风景': ['mountain', 'beach', 'valley', 'volcano', 'cliff', 'coral', 'geyser', 'lake', 'coast', 'lakeside',
             'lakeshore'],
    '交通工具': ['car', 'bicycle', 'airplane', 'bus', 'train', 'ship', 'motorcycle', 'truck'],
    '植物': ['tree', 'flower', 'palm', 'cactus', 'mushroom', 'broccoli', 'cabbage', 'corn', 'apple', 'orange'],
    '电子设备': ['computer', 'laptop', 'monitor', 'keyboard', 'mouse', 'printer', 'scanner', 'camera'],
    '食物': ['pizza', 'burger', 'sushi', 'bread', 'cake', 'ice cream', 'coffee', 'wine', 'soup']
}


def get_generic_category(label):
    """将具体标签映射到通用类别"""
    label = label.lower()
    for category, keywords in GENERIC_CATEGORIES.items():
        if any(keyword in label for keyword in keywords):
            return category
    return '其他'


def ai_image(image_path, model_type="resnet50"):
    """
    对图片进行分类并返回标签列表和通用类别
    :param image_path: 图片路径
    :param model_type: 模型类型（可选："resnet50" 或 "inception_v3"）
    :return: (tags, category) 元组
    """
    # 初始化分类器
    if model_type == "inception_v3":
        classifier = MultiModelClassifier(model_name="inception_v3", weights="DEFAULT")
    else:
        classifier = ImageClassifier()  # 默认使用 resnet50

    # 预测结果
    results = classifier.predict(image_path)

    # 提取标签列表和类别
    tags = [label for label, _ in results]
    category = get_generic_category(tags[0]) if tags else '其他'

    return tags, category


# 使用示例
if __name__ == "__main__":
    tags, category = ai_image("t2.jpg")
    print("标签列表:", tags)
    print("通用类别:", category)


