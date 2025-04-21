from qiniu import Auth, put_file, etag
import qiniu.config


def upload_to_qiniu(access_key, secret_key, bucket_name, file_path, key):
    """
    上传文件到七牛云存储
    :param access_key: AK
    :param secret_key: SK
    :param bucket_name: 存储空间名
    :param file_path: 本地文件路径
    :param key: 上传到七牛云后的文件名（可包含路径）
    :return: 外链URL或None
    """
    # 鉴权对象
    q = Auth(access_key, secret_key)

    # 生成上传凭证
    token = q.upload_token(bucket_name, key, 3600)

    # 上传文件
    ret, info = put_file(token, key, file_path)

    if ret and ret.get('key') == key:
        # 构建外链URL（假设使用测试域名，生产环境建议绑定自定义域名）
        base_url = 'https://portal.qiniu.com/cdn/domain/sv1luzogb.hd-bkt.clouddn.com'  # 替换为你的空间域名
        url = f'{base_url}/{key}'
        return url
    else:
        print("上传失败:", info)
        return None


# 使用示例
if __name__ == "__main__":
    access_key = "zzdIIpWEZBJYyoLbJkY3OqkfjPu9hsXSUucflboK"
    secret_key = "p-4gx6LYzySYoxSmnl86JQKUKsQU6gUjnrIKEdOk"
    bucket_name = "photoxw"
    local_file = "test.jpg"  # 本地图片路径
    file_key = "images/test.jpg"  # 七牛云中的路径+文件名

    url = upload_to_qiniu(access_key, secret_key, bucket_name, local_file, file_key)
    if url:
        print("文件外链:", url)