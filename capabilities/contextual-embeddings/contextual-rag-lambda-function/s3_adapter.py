import json
import boto3
from botocore.exceptions import ClientError


class S3Adapter:
    def __init__(self):
        # 创建一个S3客户端
        self.s3_client = boto3.client("s3")

    def write_output_to_s3(self, bucket_name, file_name, json_data):
        """
        将JSON对象写入S3存储桶

        :param bucket_name: S3存储桶的名称
        :param file_name: 要在存储桶中创建的文件名
        :param json_data: 要写入的JSON对象
        :return: 如果文件上传成功返回True，否则返回False
        """

        try:
            # 将JSON对象转换为字符串
            json_string = json.dumps(json_data)

            # 上传文件
            response = self.s3_client.put_object(
                Bucket=bucket_name, Key=file_name, Body=json_string, ContentType="application/json"
            )

            # 检查上传是否成功
            if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
                print(f"成功将 {file_name} 上传到 {bucket_name}")
                return True
            else:
                print(f"无法将 {file_name} 上传到 {bucket_name}")
                return False

        except ClientError as e:
            print(f"发生错误: {e}")
            return False

    def read_from_s3(self, bucket_name, file_name):
        """
        从S3存储桶读取JSON对象

        :param bucket_name: S3存储桶的名称
        :param file_name: 要读取的文件名
        :return: 如果文件读取成功返回内容，否则返回None
        """
        try:
            # 从S3获取对象
            response = self.s3_client.get_object(Bucket=bucket_name, Key=file_name)

            # 读取文件内容
            return json.loads(response["Body"].read().decode("utf-8"))

        except ClientError as e:
            print(f"从S3读取文件时出错: {str(e)}")

    def parse_s3_path(self, s3_path):
        # 如果存在，移除's3://'前缀
        s3_path = s3_path.replace("s3://", "")

        # 将路径分割为存储桶和键
        parts = s3_path.split("/", 1)

        if len(parts) != 2:
            raise ValueError("无效的S3路径格式")

        bucket_name = parts[0]
        file_key = parts[1]

        return bucket_name, file_key
