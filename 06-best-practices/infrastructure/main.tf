terraform {
  required_version = ">= 0.12"
  backend "s3" {
    bucket  = "tf-state-mlops-zoomcamp-priyan"
    key     = "mlops-zoomcamp-stg.tfstate"
    region  = "eu-north-1"
    encrypt = "true"
  }
}

provider "aws" {
  region = var.aws_region
}

data "aws_caller_identity" "current_identity" {}
locals {
  account_id = data.aws_caller_identity.current_identity.account_id
}

module "source_kinesis_stream" {
  source           = "./modules/kinesis"
  stream_name      = "${var.source_stream_name}-${var.project_id}"
  shard_count      = 1
  retention_period = 24
  tags             = var.project_id
}

module "destination_kinesis_stream" {
  source           = "./modules/kinesis"
  stream_name      = "${var.destination_stream_name}-${var.project_id}"
  shard_count      = 1
  retention_period = 24
  tags             = var.project_id
}

module "s3_bucket" {
  source      = "./modules/s3"
  bucket_name = "${var.bucket_name}-${var.project_id}"
}

module "ecr" {
  source                     = "./modules/ecr"
  ecr_repo_name              = "${var.ecr_repo_name}_${var.project_id}"
  account_id                 = local.account_id
  lambda_function_local_path = var.lambda_function_local_path
  docker_image_local_path    = var.docker_image_local_path
}

module "source" {
  source               = "./modules/lambda"
  image_uri            = module.ecr.image_uri
  lambda_function_name = "${var.lambda_function_name}_${var.project_id}"
  model_bucket         = module.s3_bucket.name
  output_stream_name   = "${var.destination_stream_name}-${var.project_id}"
  output_stream_arn    = module.destination_kinesis_stream.stream_arn
  source_stream_name   = "${var.source_stream_name}-${var.project_id}"
  source_stream_arn    = module.source_kinesis_stream.stream_arn
  aws_ecr_arn          = module.ecr.repo_arn
}