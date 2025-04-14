from torchvision import models, transforms
from PIL import Image
import torch
import requests

class MultiModelClassifier:
    def __init__(self, model_name="resnet50", weights="DEFAULT", device=None, class_file=None):
        """
        初始化多模型分类器

        Args:
            model_name (str): 模型名称 (默认: resnet50)
            weights (str/Weights): 权重版本 ('DEFAULT' 或具体版本如 'IMAGENET1K_V2')
            device (str): 设备类型 ('cuda' 或 'cpu')
            class_file (str): 类别文件路径
        """
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model_name = model_name

        # 加载模型和权重
        self.model, self.weights = self._load_model_and_weights(model_name, weights)
        self.model = self.model.to(self.device).eval()

        # 预处理函数
        self.preprocess = self.weights.transforms()

        # 加载类别标签（需确保与模型输出一致）
        self.categories = self._load_classes(class_file)

    def _load_model_and_weights(self, model_name, weights):
        """动态加载模型和权重（修复驼峰命名问题）"""
        try:
            # Step 1: 将模型名转为正确的驼峰格式（保留中间下划线）
            # 示例：mobilenet_v3_large → MobileNet_V3_Large
            parts = model_name.split('_')
            model_name_camel = ''.join([part.capitalize() if i == 0 else '_' + part.upper() if part.startswith(
                'v') else '_' + part.capitalize() for i, part in enumerate(parts)])
            model_name_camel = model_name_camel.replace('_v', '_V')  # 处理版本号（如 v3 → V3）

            # Step 2: 获取模型构造函数和权重类
            model_creator = getattr(models, model_name)
            weights_class = getattr(models, f"{model_name_camel}_Weights")  # 正确名称

            # Step 3: 选择权重版本
            if weights == "DEFAULT":
                weights = weights_class.DEFAULT
            else:
                weights = getattr(weights_class, weights)

            # Step 4: 创建模型
            model = model_creator(weights=weights)
            return model, weights

        except AttributeError:
            # 提供更清晰的错误提示
            supported_models = self._get_supported_models()
            raise ValueError(
                f"模型 '{model_name}' 不存在或不受支持。\n"
                f"支持的模型列表：{supported_models}\n"
                f"注意：模型名需全小写（如 'mobilenet_v3_large'），权重类会自动转为驼峰格式。"
            )

    def _get_supported_models(self):
        """获取所有支持 Weights 的模型列表"""
        supported = []
        for name in dir(models):
            # 忽略私有方法和非模型类
            if name.startswith('_') or not callable(getattr(models, name)):
                continue

            # 尝试生成对应的权重类名
            parts = name.split('_')
            camel_name = ''.join([part.capitalize() if i == 0 else '_' + part.upper() if part.startswith(
                'v') else '_' + part.capitalize() for i, part in enumerate(parts)])
            camel_name = camel_name.replace('_v', '_V')
            weights_class_name = f"{camel_name}_Weights"

            if hasattr(models, weights_class_name):
                supported.append(name)
        return supported

    def _load_classes(self, class_file):
        """
        加载类别标签（支持本地文件或在线 ImageNet 标签）

        Args:
            class_file (str): 本地类别文件路径（如为 None，使用默认在线标签）

        Returns:
            list: 类别名称列表（长度应与模型输出维度一致）
        """
        if class_file:
            # 从本地文件加载
            try:
                with open(class_file, "r", encoding="utf-8") as f:
                    categories = [line.strip() for line in f.readlines()]
            except FileNotFoundError:
                raise FileNotFoundError(f"类别文件 {class_file} 未找到")
        else:
            # 从 GitHub 加载默认 ImageNet 标签（1000 类）
            url = "https://raw.githubusercontent.com/anishathalye/imagenet-simple-labels/master/imagenet-simple-labels.json"
            try:
                response = requests.get(url)
                response.raise_for_status()
                categories = response.json()
            except requests.exceptions.RequestException as e:
                raise ConnectionError(f"无法下载类别文件：{e}")

        # 验证类别数量
        if len(categories) != 1000:
            raise ValueError(f"类别数量应为 1000，当前为 {len(categories)}")

        return categories

    def predict(self, image_path, top_k=5):
        """执行预测"""
        image = Image.open(image_path).convert("RGB")
        input_tensor = self.preprocess(image).unsqueeze(0).to(self.device)

        with torch.no_grad():
            output = self.model(input_tensor)

        probs = torch.nn.functional.softmax(output[0], dim=0)
        top_probs, top_indices = torch.topk(probs, top_k)

        return [(self.categories[i], float(p)) for i, p in zip(top_indices, top_probs)]