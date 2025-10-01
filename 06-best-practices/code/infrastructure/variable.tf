variable "aws_region" {
  type        = string
  default     = "eu-north-1"
  description = "Give the region of the aws provider"
}

variable "project_id" {
  type        = string
  default     = "mlops-zoomcamp"
  description = "description"
}

variable "source_stream_name" {
  type        = string
  description = "Provide the name for the stream in which the input will be pushed."
}

variable "destination_stream_name" {
  type        = string
  description = "Provide the name for the stream in which the output will be thrown."
}

variable "bucket_name" {
  type        = string
  description = "description"
}

variable "ecr_repo_name" {
  type        = string
  description = "description"
}

variable "lambda_function_local_path" {
  type        = string
  description = "description"
}

variable "docker_image_local_path" {
  type        = string
  description = "description"
}

variable "lambda_function_name" {
  description = "Provide the name of the lambda function"
}