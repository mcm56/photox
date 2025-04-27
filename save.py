from qiniu import Auth, put_file, BucketManager, urlsafe_base64_encode
import requests
import time
import hmac
import hashlib
from urllib.parse import quote

from ai_image import ai_image


def upload_and_set_metadata(access_key, secret_key, bucket_name, file_path, key, tags, category):
    q = Auth(access_key, secret_key)

    # 第一步：上传文件
    token = q.upload_token(bucket_name, key, 3600)
    ret, info = put_file(token, key, file_path)

    if not ret or ret.get('key') != key:
        print("文件上传失败:", info.text_body)
        return None

    # 第二步：构造双重URL编码的路径参数
    entry = f"{bucket_name}:{key}"
    encoded_entry = quote(quote(entry, safe=""))  # 双重编码

    # 构造MIME占位参数
    encoded_mime = quote(quote("", safe=""))  # 空字符串双重编码

    # 构造元数据参数
    meta_parts = []
    metadata = {
        "user": "1",
        "tags": ",".join(tags),
        "category": category
    }
    for meta_key, value in metadata.items():
        encoded_key = quote(quote(f"x-qn-meta-{meta_key}", safe=""))
        encoded_value = quote(quote(str(value), safe=""))
        meta_parts.append(f"{encoded_key}/{encoded_value}")

    # 构造完整请求路径
    request_path = f"/chgm/{encoded_entry}/mime/{encoded_mime}/{'/'.join(meta_parts)}"

    # 手动生成签名
    signing_str = f"POST {request_path}\nHost: rs.qiniuapi.com\nContent-Type: application/x-www-form-urlencoded\n\n"
    secret_key = q.get_secret_key()  
    sign = hmac.new(
        secret_key,
        signing_str.encode(),
        hashlib.sha1
    ).digest()
    encoded_sign = urlsafe_base64_encode(sign)
    token = f"{access_key}:{encoded_sign}".replace("=","")

    # 设置请求头
    timestamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    headers = {
        "Authorization": f"Qiniu {token}",
        "X-Qiniu-Date": timestamp,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    # 发送请求
    full_url = f"https://rs.qiniuapi.com{request_path}"
    response = requests.post(full_url, headers=headers, data=None)
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
    access_key = "zzdIIpWEZBJYyoLbJkY3OqkfjPu9hsXSUucflboK"
    secret_key = "p-4gx6LYzySYoxSmnl86JQKUKsQU6gUjnrIKEdOk"
    bucket_name = "photoxw"
    local_file = "shi2.jpg"
    file_key = f"images/{local_file}"
    tags,category=ai_image(local_file)
    url = upload_and_set_metadata(access_key, secret_key, bucket_name, local_file, file_key, tags, category)
    if url:
        print("文件外链:", url)

        # 验证元数据
        q = Auth(access_key, secret_key)
        bucket_manager = BucketManager(q)
        ret, info = bucket_manager.stat(bucket_name, file_key)

        if ret:
            print("元数据:", {
                "user": ret.get("x-qn-meta-user"),
                "tags": ret.get("x-qn-meta-tags", "").split(","),
                "category": ret.get("x-qn-meta-category", "未设置")
            })
        else:
            print("元数据获取失败:", info.text_body)
