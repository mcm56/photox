
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

results = classifier.predict("aaa.png")

for label, confidence in results:
    print(f"{label}: {confidence:.2%}")

