
from image_classifier import ImageClassifier
from torchvision import models
from MultiModelClassifier import MultiModelClassifier



# 自定义设置
classifier =MultiModelClassifier(
    model_name="inception_v3",
    weights="DEFAULT"
)

results = classifier.predict("aaa.png")

for label, confidence in results:
    print(f"{label}: {confidence:.2%}")

