# Phase 3 AWS SAM deployment (Windows PowerShell)

## Before deploying
- AWS CLI and SAM CLI installed; Docker Desktop running if using `--use-container`.
- AWS CLI configured with an identity authorized to deploy SAM/CloudFormation, Lambda, IAM and API Gateway.
- Model `apac.amazon.nova-lite-v1:0` verified in `ap-south-1` (already tested locally).
- **AWS usage is billable.** Set an AWS Budget alert and review service quotas before making this public.
- The API is PUBLIC. API Gateway throttling and Lambda concurrency limits reduce but do not eliminate abuse or costs. For sustained use, add WAF, stronger rate limiting, and request authorization or a managed abuse-control layer. CORS is not authentication.

## 1. Extract and change directory
```powershell
cd "C:\AI_Projects\AWSAIProject\Project3 - career-portfolio-starter\career-portfolio-phase3-deploy"
```
## 2. Build
```powershell
sam build --use-container
```
If native build on Python 3.12 succeeds and produces compatible packages, `sam build` is an alternative.

## 3. Deploy
```powershell
sam deploy --guided --stack-name career-portfolio-rag-api --region ap-south-1 --capabilities CAPABILITY_IAM
```
Use the default AllowedOrigin (`https://career-portfolio-starter.vercel.app`), and accept IAM role creation. Save arguments to `samconfig.toml` if prompted. Record the `ApiBaseUrl` output.

## 4. Verify
```powershell
$api = (aws cloudformation describe-stacks --stack-name career-portfolio-rag-api --region ap-south-1 --query "Stacks[0].Outputs[?OutputKey=='ApiBaseUrl'].OutputValue" --output text)
```
```powershell
Invoke-RestMethod -Uri "$api/health"
```
```powershell
Invoke-RestMethod -Uri "$api/chat" -Method POST -ContentType 'application/json' -Body '{"question":"What AWS and AI projects have you built?"}' | ConvertTo-Json -Depth 8
```
Expected `/health` `mode: bedrock`; `/chat` returns an answer and sources. If deployment fails, inspect CloudWatch logs for the Lambda function and CloudFormation stack events.

## 5. Connect to Vercel
Copy the `ApiBaseUrl` value into your frontend `config.js`:
```javascript
window.CAREER_API_URL = "https://YOUR_API_ID.execute-api.ap-south-1.amazonaws.com/Prod";
```
Commit `config.js` and frontend changes to the GitHub repository that Vercel actually deploys, then push via GitHub Desktop. Do not publish `.env` or credentials. Test the live website chat after deployment.

## 6. Cleanup
```powershell
sam delete --stack-name career-portfolio-rag-api --region ap-south-1
```
CloudWatch log groups or other separately created resources may need additional review. Deleting the stack disables the public AI endpoint; restore the frontend to a non-API preview or show an unavailable message.

## Known limitations
- TF-IDF retrieval, not neural vector embeddings. A useful RAG baseline, but not a vector database implementation.
- In-memory IP rate limits reset on cold starts and are not global across Lambda instances. API Gateway throttling is best-effort.
- The `/sources` endpoint exposes approved public knowledge-source metadata.
- Bedrock IAM uses `Resource: '*'` to accommodate cross-region inference; tighten to the required inference-profile and underlying model ARNs before broader use.
- API Gateway and Lambda payload/timeouts apply. Avoid storing confidential resume data in the knowledge base.
