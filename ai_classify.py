import requests
import base64
from PIL import Image
import io


def process_image(image_path, max_size=2048, quality=85):
    """图片预处理核心函数"""
    try:
        # 读取并转换图片格式
        img = Image.open(image_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # 保持比例的尺寸调整
        width, height = img.size
        if max(width, height) > max_size:
            ratio = max_size / max(width, height)
            new_size = (int(width * ratio), int(height * ratio))
            img = img.resize(new_size, Image.Resampling.LANCZOS)

        # 优化存储体积
        byte_arr = io.BytesIO()
        img.save(byte_arr, format='JPEG', quality=quality, optimize=True)
        return byte_arr.getvalue()

    except Exception as e:
        print(f"图片预处理失败: {str(e)}")
        return None


def image_classification(image_path, api_key):
    # 1. 预处理图片
    image_bytes = process_image(image_path)
    if not image_bytes:
        return None

    # 2. 构建符合规范的Data URL
    encoded_image = base64.b64encode(image_bytes).decode("utf-8")
    image_data_url = f"data:image/jpeg;base64,{encoded_image}"

    # 3. 构建请求载荷（保持分类提示不变）
    payload = {
        "model": "qwen2.5-vl-7b-instruct",
        "messages": [
            {
                "role": "system",
                "content": [{
                    "type": "text",
                    "text": "你是一个专业的图像分类助手，需要准确分析图片内容并匹配预定义分类。"
                }]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """请从以下30个类别中选择最合适的数字编号：
0:风景 1:人物肖像 2:动物 3:交通工具 4:食品
5:建筑 6:电子产品 7:运动器材 8:植物花卉 9:医疗用品
10:办公用品 11:服装鞋帽 12:家具家居 13:书籍文档 14:艺术创作
15:工业设备 16:体育赛事 17:天文地理 18:儿童玩具 19:美妆个护
20:军事装备 21:宠物用品 22:健身器材 23:厨房用品 24:实验室器材
25:音乐器材 26:户外装备 27:珠宝首饰 28:虚拟场景 29:其他
只需返回数字，不要解释"""
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_data_url,
                            "detail": "auto"
                        }
                    }
                ]
            }
        ]
    }

    # 4. 发送请求（保持不变）
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            "https://api.qnaigc.com/v1/chat/completions",
            json=payload,
            headers=headers,
            timeout=15
        )

        if response.status_code == 200:
            # 5. 解析响应
            result = response.json()
            class_id = int(result['choices'][0]['message']['content'].strip())

            # 类别映射表（与之前定义一致）
            category_map = {
                0: "风景", 1: "人物肖像", 2: "动物", 3: "交通工具", 4: "食品",
                5: "建筑", 6: "电子产品", 7: "运动器材", 8: "植物花卉", 9: "医疗用品",
                10: "办公用品", 11: "服装鞋帽", 12: "家具家居", 13: "书籍文档", 14: "艺术创作",
                15: "工业设备", 16: "体育赛事", 17: "天文地理", 18: "儿童玩具", 19: "美妆个护",
                20: "军事装备", 21: "宠物用品", 22: "健身器材", 23: "厨房用品", 24: "实验室器材",
                25: "音乐器材", 26: "户外装备", 27: "珠宝首饰", 28: "虚拟场景", 29: "其他"
            }

            return {
                "category_id": class_id,
                "category_name": category_map.get(class_id, "未知类别"),
                "raw_response": result  # 保留原始响应用于调试
            }

        else:
            print(f"API Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Request failed: {str(e)}")
        return None


# 使用示例
if __name__ == "__main__":
    api_key = "sk-ff8f03a8cfbc03d7df75b7ddb6b1fb7f0bfc8116e02986306865aa9149741301"
    image_path = "shi2.jpg"  # 必须使用本地文件路径
    result = image_classification(image_path, api_key)
    if result:
        print(f"分类结果：{result['category_name']} (ID: {result['category_id']})")