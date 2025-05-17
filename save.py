from qiniu import Auth, put_file, BucketManager, urlsafe_base64_encode
import requests
import time
import hmac
import hashlib
from urllib.parse import quote
import base64
from sympy.integrals.meijerint_doc import category
from color import extract_colors_with_colorthief
from ai_classify import image_classification


def hmac_sha1(signing_str: str, secret_key: str) -> str:
    """
    生成 HMAC-SHA1 签名
    :param signing_str: 待签名的字符串
    :param secret_key: 密钥（需与API要求一致，如七牛云的SecretKey）
    :return: Base64编码的签名结果
    """
    # 将密钥和字符串转换为字节（UTF-8编码）
    key_bytes = secret_key.encode('utf-8')
    msg_bytes = signing_str.encode('utf-8')

    # 计算 HMAC-SHA1 摘要
    digest = hmac.new(key_bytes, msg_bytes, hashlib.sha1).digest()

    # 将摘要转换为 Base64 字符串
    return base64.b64encode(digest).decode('utf-8')

def upload_and_set_metadata(access_key, secret_key, bucket_name, file_path, key,category_id,colors):
    q = Auth(access_key, secret_key)

    # 第一步：上传文件
    token = q.upload_token(bucket_name, key, 3600)
    ret, info = put_file(token, key, file_path)

    if not ret or ret.get('key') != key:
        print("文件上传失败:", info.text_body)
        return None

    # 第二步：构造双重URL编码的路径参数
    entry = f"{bucket_name}:{key}"
    encodedEntryURI = urlsafe_base64_encode(entry) # 双重编码

    # 构造MIME占位参数
    encoded_mime =urlsafe_base64_encode("")  # 空字符串双重编码

    stat_url = f"https://rs.qiniuapi.com/stat/{encodedEntryURI}"
    stat_token = q.token_of_request(stat_url)
    print(stat_url)
    response = requests.post(stat_url, headers={"Authorization": f"QBox {stat_token}"})
    print(response.text)  # 应返回文件信息，而非 401

    # 构造元数据参数
    meta_parts = []
    metadata = {
        "x-qn-meta-user": "user01",
        "x-qn-meta-category": str(category_id),
        "x-qn-meta-color": ",".join([f"({r},{g},{b})" for r, g, b in colors])
    }
    request_path = (
        f"/chgm/{encodedEntryURI}/mime/{urlsafe_base64_encode('image/jpeg')}/"
        f"x-qn-meta-user/{urlsafe_base64_encode(metadata['x-qn-meta-user'])}/"
        f"x-qn-meta-category/{urlsafe_base64_encode(metadata['x-qn-meta-category'])}/"
        f"x-qn-meta-color/{urlsafe_base64_encode(metadata['x-qn-meta-color'])}"  # 新增颜色字段
    )
    full_url = f"https://rs.qiniuapi.com{request_path}"

    # 4. 使用SDK生成签名（推荐）
    token = q.token_of_request(request_path)
    headers = {"Authorization":f"QBox {token}"}

    # 5. 发送请求
    response = requests.post(full_url, headers=headers)
    print(response.text)
    print("Request Path:", request_path)
    print("Full URL:", full_url)
    print("Token:", token)
    print("Status Code:", response.status_code)
    if response.status_code != 200:
        print("元数据设置失败:", response.text)
        return None

    base_url = 'http://sv1luzogb.hd-bkt.clouddn.com'
    return f'{base_url}/{key}'


if __name__ == "__main__":
    access_key = "NT8GPMLylWq3_WIl9aNk1zAUWTJtoWrGGVqbvKxh"
    secret_key = "uNj2QCpEElzFF4ZkFkvjrBrDITB9ZpO_0ixDbfXD"
    api_key = "sk-ff8f03a8cfbc03d7df75b7ddb6b1fb7f0bfc8116e02986306865aa9149741301"
    bucket_name = "photoxw"
    local_file = "test.jpg"
    file_key = f"images/{local_file}"
    category_map = {
        0: "风景", 1: "人物肖像", 2: "动物", 3: "交通工具", 4: "食品",
        5: "建筑", 6: "电子产品", 7: "运动器材", 8: "植物花卉", 9: "医疗用品",
        10: "办公用品", 11: "服装鞋帽", 12: "家具家居", 13: "书籍文档", 14: "艺术创作",
        15: "工业设备", 16: "体育赛事", 17: "天文地理", 18: "儿童玩具", 19: "美妆个护",
        20: "军事装备", 21: "宠物用品", 22: "健身器材", 23: "厨房用品", 24: "实验室器材",
        25: "音乐器材", 26: "户外装备", 27: "珠宝首饰", 28: "虚拟场景", 29: "其他"
    }
    colors = extract_colors_with_colorthief(local_file, num_colors=2)
    result=image_classification(local_file,api_key)
    category_id=result['category_id']
    url = upload_and_set_metadata(access_key, secret_key, bucket_name, local_file, file_key, category_id,colors)
    if url:
        print("文件外链:", url)