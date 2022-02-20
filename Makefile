deploy:
	sam validate
	sam build
	sam deploy

local-invoke:
	sam local invoke -e events/event.json ServiceAFunction

invoke:
	aws lambda invoke --cli-binary-format raw-in-base64-out --function-name resilience-app-ServiceAFunction-xxxxxxxxxxx --invocation-type Event --payload '{"simulate_error_code":400}' response.json

