import json
import logging
from inference_adapter import InferenceAdapter
from s3_adapter import S3Adapter

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

contextual_retrieval_prompt = """
    <document>
    {doc_content}
    </document>


    这是我们想要在整个文档中定位的块
    <chunk>
    {chunk_content}
    </chunk>


    请提供一个简短简洁的上下文，以便在整体文档中定位此块，用于改进块的搜索检索。
    仅回答简洁的上下文，不要其他内容。
    """


def lambda_handler(event, context):
    logger.debug("input={}".format(json.dumps(event)))

    s3_adapter = S3Adapter()
    inference_adapter = InferenceAdapter()

    # 从输入事件中提取相关信息
    input_files = event.get("inputFiles")
    input_bucket = event.get("bucketName")

    if not all([input_files, input_bucket]):
        raise ValueError("缺少必需的输入参数")

    output_files = []
    for input_file in input_files:
        processed_batches = []
        for batch in input_file.get("contentBatches"):
            # 从S3获取块
            input_key = batch.get("key")

            if not input_key:
                raise ValueError("内容批次中缺少uri")

            # 从S3读取文件
            file_content = s3_adapter.read_from_s3(bucket_name=input_bucket, file_name=input_key)
            print(file_content.get("fileContents"))

            # 合并所有块以构建原始文件的内容
            # 另外我们也可以读取原始文件并从中提取文本
            original_document_content = "".join(
                content.get("contentBody")
                for content in file_content.get("fileContents")
                if content
            )

            # 一次处理一个块
            chunked_content = {"fileContents": []}
            for content in file_content.get("fileContents"):
                content_body = content.get("contentBody", "")
                content_type = content.get("contentType", "")
                content_metadata = content.get("contentMetadata", {})

                # 使用附加上下文更新块
                prompt = contextual_retrieval_prompt.format(
                    doc_content=original_document_content, chunk_content=content_body
                )
                response_stream = inference_adapter.invoke_model_with_response_stream(prompt)
                chunk_context = "".join(chunk for chunk in response_stream if chunk)

                # 将块附加到输出文件内容
                chunked_content["fileContents"].append(
                    {
                        "contentBody": chunk_context + "\n\n" + content_body,
                        "contentType": content_type,
                        "contentMetadata": content_metadata,
                    }
                )

            output_key = f"Output/{input_key}"

            # 将更新的块写入输出S3
            s3_adapter.write_output_to_s3(input_bucket, output_key, chunked_content)

            # 将处理过的块文件附加到文件列表
            processed_batches.append({"key": output_key})
        output_files.append(
            {
                "originalFileLocation": input_file.get("originalFileLocation"),
                "fileMetadata": {},
                "contentBatches": processed_batches,
            }
        )

    return {"outputFiles": output_files}
