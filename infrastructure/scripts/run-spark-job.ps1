# This script is used to run a Spark job using spark-submit.
# It loads MinIO credentials from the project .env file,
# injects them into the Spark driver container,
# and executes the requested Spark job.

param(
    [Parameter(Mandatory = $true)]
    [string]$JobPath
)

# Path to the project root directory
$projectRoot = Resolve-Path "$PSScriptRoot\..\.."

# Load the environment variables from the .env file
$envFile = Join-Path $projectRoot ".env"

# Check if the .env file exists
if (-not (Test-Path $envFile)) {
    throw ".env file not found at $envFile"
}

# Read the .env file
$envLines = Get-Content $envFile

# Extract MinIO credentials
$minioUsername = ($envLines | Where-Object { $_ -match '^MINIO_USERNAME=' }) -replace '^MINIO_USERNAME=', ''
$minioPassword = ($envLines | Where-Object { $_ -match '^MINIO_PASSWORD=' }) -replace '^MINIO_PASSWORD=', ''

# Trim surrounding whitespace or quotes
$minioUsername = $minioUsername.Trim().Trim('"').Trim("'")
$minioPassword = $minioPassword.Trim().Trim('"').Trim("'")

# Validate that the credentials are not empty
if ([string]::IsNullOrWhiteSpace($minioUsername) -or [string]::IsNullOrWhiteSpace($minioPassword)) {
    throw "MINIO_USERNAME or MINIO_PASSWORD is missing from .env"
}

# Map MinIO credentials to the standard AWS environment variable names
# expected by the S3A credential provider.
$env:AWS_ACCESS_KEY_ID = $minioUsername
$env:AWS_SECRET_ACCESS_KEY = $minioPassword

# Check if the Spark job file exists
$jobFile = Join-Path $projectRoot $JobPath

if (-not (Test-Path $jobFile)) {
    throw "Spark job not found at $jobFile"
}

# Execute the Spark job inside the persistent Spark driver container.
# Spark configuration is loaded from spark-defaults.conf.
docker compose exec `
    -T `
    -e AWS_ACCESS_KEY_ID="$minioUsername" `
    -e AWS_SECRET_ACCESS_KEY="$minioPassword" `
    spark-driver `
    spark-submit `
    --master spark://spark-master:7077 `
    "/workspace/$JobPath"