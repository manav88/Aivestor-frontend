# llama_inference.py
import boto3
import json





def call_llama3(prompt):
    client = boto3.client("bedrock-runtime", region_name="us-east-1")

    response = client.invoke_model(
        modelId="meta.llama3-8b-instruct-v1:0",
        body=json.dumps({
            "prompt": prompt,
            "max_gen_len": 512,
            "temperature": 0.3,
            "top_p": 0.9
        }),
        contentType="application/json",
        accept="application/json"
    )

    result = json.loads(response['body'].read())
    return result.get('generation', '').strip()