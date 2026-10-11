import hashlib
import os
import time

def cache_key(question):
    normalized = " ".join(question.lower().split())
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    return "cache#" + digest

def get_cached_answer(question):
    table_name = os.getenv("QUOTA_TABLE", "")
    if not table_name:
        return None

    import boto3
    table = boto3.resource("dynamodb").Table(table_name)
    result = table.get_item(Key={"pk": cache_key(question)})
    item = result.get("Item")

    if not item or int(item.get("expires", 0)) <= int(time.time()):
        return None

    return item.get("answer")

def save_cached_answer(question, answer):
    table_name = os.getenv("QUOTA_TABLE", "")
    if not table_name:
        return

    import boto3
    table = boto3.resource("dynamodb").Table(table_name)
    table.put_item(Item={
        "pk": cache_key(question),
        "answer": answer,
        "expires": int(time.time()) + 604800
    })
