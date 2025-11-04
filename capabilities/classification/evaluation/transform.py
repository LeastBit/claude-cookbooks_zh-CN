def get_transform(output, context):
    try:
        return output.split("<category>")[1].split("</category>")[0].strip()
    except Exception as e:
        print(f"get_transform 出错: {e}")
        return output
