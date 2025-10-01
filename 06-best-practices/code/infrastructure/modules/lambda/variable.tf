variable "source_stream_name" {
  type =  string
  description = "Name of the stream which will receive the events"
}

variable "source_stream_arn" {
  type =  string
  description = "Name of the stream which will receive the events"
}
variable "output_stream_name" {
  type        = string
  description = "Name of the stream in which all the output will be passed"
}

variable "output_stream_arn" {
  type        = string
  description = "ARN of the stream in which all the output will be passed"
}

variable "model_bucket" {
  type        = string
  description = "description"
}

variable "lambda_function_name" {
  type        = string
  description = "description"
}

variable "image_uri" {
  type        = string
  description = "description"
}

variable "aws_ecr_arn" {
  type = string
  description = "arn of the ecr repo"
}