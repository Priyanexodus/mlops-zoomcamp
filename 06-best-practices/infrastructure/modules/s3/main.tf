resource "aws_s3_bucket" "S3_bucket" {
    bucket = var.bucket_name
}

output "name" {
    value = aws_s3_bucket.S3_bucket.bucket
}

resource "aws_s3_bucket_public_access_block" "my_permission"{

    bucket = aws_s3_bucket.S3_bucket.id
    block_public_acls = true
    ignore_public_acls = true
    block_public_policy = true
    restrict_public_buckets = true
}