variable "ecr_repo_name" {
  type        = string
  description = "ECR repo name"
}

variable "lambda_function_local_path" {
  type        = string
  description = "local path to the python lambda function/ lambda file"
}

variable "docker_image_local_path" {
  type        = string
  description = "local path to the docker file"
}

variable "region" {
  type        = string
  default     = "eu-north-1"
  description = "region"
}

variable "ecr_image_tag" {
  type        = string
  default     = "latest"
  description = "ECR VERSION"
}

variable "account_id" {}