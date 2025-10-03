resource "aws_iam_role" "iam_lambda"{
    name = "iam_lambda_stg"
    assume_role_policy =<<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action" : "sts:AssumeRole",
            "Principal" : {
                "Service": [
                    "lambda.amazonaws.com",
                    "kinesis.amazonaws.com"
                ]
            },
            "Effect":"Allow"
        }
    ]
}
EOF
}

resource "aws_iam_policy" "allow_kinesis_processing" {
    name = "allow_kinesis_processing_${var.lambda_function_name}"
    path = "/"
    description = "IAM policy logging lambda"

    policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "kinesis:DescribeStream",
                "kinesis:DescribeStreamSummary",
                "kinesis:GetRecords",
                "kinesis:GetShardIterator",
                "kinesis:ListShards",
                "kinesis:ListStreams",
                "kinesis:SubscribeToShard",
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "*"
        }
    ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "kinesis_processing"{
    role = aws_iam_role.iam_lambda.id
    policy_arn = aws_iam_policy.allow_kinesis_processing.arn
}

resource "aws_iam_role_policy" "inline_lambda_policy"{
    name = "LambdaInlinePolicy"
    role = aws_iam_role.iam_lambda.id
    depends_on = [aws_iam_role.iam_lambda]
    policy = <<EOF
{
	"Version": "2012-10-17",
	"Statement": [
		{
			"Sid": "VisualEditor0",
			"Effect": "Allow",
			"Action": [
				"kinesis:PutRecord",
				"kinesis:PutRecords"
			],
			"Resource": "${var.output_stream_arn}"
		}
	]
}
EOF
}

resource "aws_lambda_permission" "allow_cloudwatch_to_trigger_lambda_function" {
  statement_id = "AllowExecutionFromCloudWatch"
  action = "lambda:InvokeFunction"
  function_name = aws_lambda_function.kinesis_lambda.function_name
  principal =  "events.amazonaws.com"
  source_arn =  var.source_stream_arn
}

resource "aws_iam_policy" "allow_logging"{
    name = "allow_logging_${var.lambda_function_name}"
    path = "/"
    description = "Allows to create the log"

policy = <<EOF
{
	"Version": "2012-10-17",
	"Statement": [
		{
			"Effect": "Allow",
			"Action": [
				"logs:CreateLogStream",
				"logs:CreateLogGroup",
				"logs:PutLogEvents"
			],
			"Resource": "arn:aws:logs:*:*:*"
		}
	]
}
EOF
}

resource "aws_iam_role_policy_attachment" "lambda_logs" {
    role = aws_iam_role.iam_lambda.name
    policy_arn = aws_iam_policy.allow_logging.arn
}

resource "aws_iam_policy" "lambda_s3_role_policy"{
    name = "lambda_s3_role_policy_${var.lambda_function_name}"
    description = "IAM policy for s3"
    policy = <<EOF
{
	"Version": "2012-10-17",
	"Statement": [
		{
            "Sid": "S3ReadAccess",
			"Effect": "Allow",
			"Action": [
				"s3:Get*",
				"s3:List*"
			],
			"Resource": [
				"arn:aws:s3:::${var.model_bucket}",
				"arn:aws:s3:::${var.model_bucket}/*"
			]
		},
        {
            "Sid": "MonitoringAccess",
			"Effect": "Allow",
			"Action": [
				"sns:*",
				"cloudwatch:*",
                "logs:*",
                "autoscaling:Describe*"
			],
			"Resource":"*"
		},
        {
            "Sid": "S3ListAllBuckets",
            "Effect": "Allow",
            "Action": [
                "s3:ListAllMyBuckets",
                "s3:GetBucketLocation"
            ],
            "Resource": "*"
        }
	]
}
EOF
}

resource "aws_iam_role_policy_attachment" "s3_access_monitoring"{
    role = aws_iam_role.iam_lambda.name
    policy_arn = aws_iam_policy.lambda_s3_role_policy.arn
}

resource "aws_iam_policy" "lambda_ecr_access" {
  name =  "lambda_ecr_access_${var.lambda_function_name}"
  description = "Gives permission to use ecr."

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchGetImage",
        "ecr:BatchCheckLayerAvailability",
        "ecr:DescribeImages"
      ],
      "Resource": "${var.aws_ecr_arn}"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ecr:GetAuthorizationToken"
      ],
      "Resource": "*"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "lambda_ecr" {
  role = aws_iam_role.iam_lambda.name
  policy_arn = aws_iam_policy.lambda_ecr_access.arn
}