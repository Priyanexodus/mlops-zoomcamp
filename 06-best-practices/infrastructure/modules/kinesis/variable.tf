variable "stream_name" {
  type        = string
  default     = ""
  description = "The name of the kinesis stream"
}

variable "shard_count" {
  type        = number
  default     = 1
  description = "The shard count."
}

variable "retention_period" {
  type        = number
  default     = 24
  description = "It gives the retention period"
}

variable "shard_level_metrics" {
  type        = list(string)
  default     = [
    "IncomingBytes",
    "IncomingRecords",
    "IteratorAgeMilliseconds",
    "OutgoingBytes",
    "OutgoingRecords",
    "ReadProvisionedThroughputExceeded",
    "WriteProvisionedThroughputExceeded",
  ]
  description = "description"
}

variable "tags" {
  type        = string
  default     = ""
  description = "Tags to assign to the Kinesis stream"
}