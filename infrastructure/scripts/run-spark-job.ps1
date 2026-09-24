# This script is used to run a Spark job using spark-submit. It sets the necessary environment variables for MinIO credentials and executes the Spark job with the provided arguments.


# Param is used to define the parameters that the script accepts. In this case, it accepts a single mandatory parameter called JobPath
# which is a string representing the path to the Spark job to be executed.
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

# Load the environment variables from the .env file
$envLines = Get-Content $envFile

# Extract MINIO_USERNAME and MINIO_PASSWORD from the .env file
$minioUsername = ($envLines | Where-Object { $_ -match '^MINIO_USERNAME=' }) -replace '^MINIO_USERNAME=', ''
$minioPassword = ($envLines | Where-Object { $_ -match '^MINIO_PASSWORD=' }) -replace '^MINIO_PASSWORD=', ''

# Trim any surrounding whitespace or quotes from the values
$minioUsername = $minioUsername.Trim().Trim('"').Trim("'")
$minioPassword = $minioPassword.Trim().Trim('"').Trim("'")

# Validate that the extracted values are not empty
if ([string]::IsNullOrWhiteSpace($minioUsername) -or [string]::IsNullOrWhiteSpace($minioPassword)) {
    throw "MINIO_USERNAME or MINIO_PASSWORD is missing from .env"
}

# Map the MinIO credential values to the standard AWS environment variable names
# expected by the S3A credential provider.
$env:AWS_ACCESS_KEY_ID = $minioUsername
$env:AWS_SECRET_ACCESS_KEY = $minioPassword

# Check if the Spark job file exists
$jobFile = Join-Path $projectRoot $JobPath

if (-not (Test-Path $jobFile)) {
    throw "Spark job not found at $jobFile"
}

# Path to the S3A configuration file
$s3aConfigFile = Join-Path $projectRoot "infrastructure\config\spark\s3a.conf"

# Check if the S3A configuration file exists
if (-not (Test-Path $s3aConfigFile)) {
    throw "S3A configuration file not found at $s3aConfigFile"
}

# Read the S3A configuration file and prepare the Spark submit arguments
$s3aProperties = Get-Content $s3aConfigFile |
    Where-Object {
        $_.Trim() -and -not $_.Trim().StartsWith("#")
    }

# Prepare the Spark submit arguments for S3A configuration
$sparkS3aConf = @()

# Loop through each property in the S3A configuration and create the corresponding Spark configuration arguments
foreach ($property in $s3aProperties) {
    $key, $value = $property -split "=", 2
    $sparkS3aConf += "--conf"
    $sparkS3aConf += "spark.hadoop.$($key.Trim())=$($value.Trim())"
}

# Prepare the Spark submit command with the provided arguments
docker compose exec `
    -T `
    spark-driver `
    spark-submit `
    --master spark://spark-master:7077 `
    $sparkS3aConf `
    "/workspace/$JobPath"