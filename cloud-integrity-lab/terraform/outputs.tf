output "app_public_ip" {
  description = "Public IP of the Django app instance"
  value       = aws_instance.cloud_integrity_app.public_ip
}

output "db_private_ip" {
  description = "Private IP of the PostgreSQL instance"
  value       = aws_instance.cloud_integrity_db.private_ip
}

output "app_url" {
  description = "Base URL to hit the API"
  value       = "http://${aws_instance.cloud_integrity_app.public_ip}:8080"
}
