from qiniu import Auth, put_file, urlsafe_base64_encode,BucketManager
import requests
import time
import hmac
import hashlib

def upload_and_set_metadata(access_key, secret_key, bucket_name, file_path, key, tags, category):
    q = Auth(access_key, secret_key)

    # 第一步：上传文件
    token = q.upload_token(bucket_name, key, 3600)
    ret, info = put_file(token, key, file_path)

    if not ret or ret.get('key') != key:
        print("文件上传失败:", info.text_body)
        return None

    # 第二步：构造 EncodedEntryURI
    entry = f"{bucket_name}:{key}"
    encoded_entry = urlsafe_base64_encode(entry.encode()).replace("=", "")

    # 构造元数据键值对
    meta_parts = []
    metadata = {
        "user": "1",
        "tags": ",".join(tags),
        "category": category
    }
    for key_part, value in metadata.items():
        encoded_key = f"x:qn-meta-{key_part}"
        encoded_value = urlsafe_base64_encode(value.encode()).replace("=", "")
        meta_parts.append(f"{encoded_key}/{encoded_value}")

    # 构造请求URL
    url = f"chgm/{encoded_entry}/{'/'.join(meta_parts)}"

    timestamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())

    # 生成Token，指定正确方法和body
    token = q.token_of_request(
        url,
     #  method="POST",  # 根据实际情况调整
        body="",  # 明确空body
        content_type="application/x-www-form-urlencoded"
    )

    headers = {
        "Authorization": f"Qiniu {token}",
        "X-Qiniu-Date": timestamp,
        "Content-Type": "application/x-www-form-urlencoded"  # 与生成token时一致
    }


    # 发送请求
    response = requests.post(url, headers=headers)
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
    tags = ["nature", "sunset"]
    category = "landscape"

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