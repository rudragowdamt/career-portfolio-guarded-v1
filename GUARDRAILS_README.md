# Guarded V1 — deployment notes

**Default: Bedrock disabled** (`AI_ENABLED=false`). This is intentional. The API returns retrieved excerpts instead. Do not enable until you have configured and tested the quota controls.

## Steps (PowerShell in this folder)

1. `sam build --use-container`
2. `sam deploy --guided --stack-name career-portfolio-rag-api --region ap-south-1 --capabilities CAPABILITY_IAM`
3. `$api = aws cloudformation describe-stacks --stack-name career-portfolio-rag-api --region ap-south-1 --query "Stacks[0].Outputs[?OutputKey=='ApiBaseUrl'].OutputValue" --output text`
4. `Invoke-RestMethod "$api/health"`
5. `Invoke-RestMethod -Uri "$api/chat" -Method POST -ContentType application/json -Body '{"question":"What AWS projects have you built?"}' | ConvertTo-Json -Depth 8`

**Do not enable public AI until reviewed.** Set AI_ENABLED=true only after testing the DynamoDB table, quotas, and AWS budgets. Update the visitor hash salt with a secret random value before enabling. The current per-visitor key uses the apparent request IP; API Gateway proxies can make this inaccurate, and clients behind NAT can share an IP. For strict identity enforcement, use verified sessions/identity and a trusted gateway-derived client address. This package does NOT implement that yet.

**Limits and caveats:** DynamoDB transaction reservations are atomic and fail closed; cache misses are not deduplicated; curated responses are a no-LLM fallback, not a full shared cache. AWS Budget alerts are not instantaneous hard caps. Configure AWS Budgets manually and keep AI disabled until additional controls are validated. Lambda concurrency=1 and API Gateway throttling limit rate, not total AWS spend. DynamoDB and API Gateway still incur small charges when AI is off. For truly zero AWS cost, leave this stack undeployed and use the static Vercel assistant.

**Emergency stop:** `aws lambda put-function-concurrency --function-name FUNCTION_NAME --reserved-concurrent-executions 0 --region ap-south-1` (retrieve function name from CloudFormation resources first). This stops new Lambda invocations but not other AWS costs.

**Cleanup:** `sam delete --stack-name career-portfolio-rag-api --region ap-south-1`.
