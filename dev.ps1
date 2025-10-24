param(
    [ValidateSet("up", "down", "logs")]
    [string]$Command = "up"
)

switch ($Command) {
    "up" { docker-compose up --build }
    "down" { docker-compose down }
    "logs" { docker-compose logs -f }
}
