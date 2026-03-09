#!/usr/bin/env bats

@test "docker_cleanup help" {
  run ./scripts/docker_cleanup.sh --help
  [ "$status" -eq 0 ]
  [[ "$output" == *"Usage"* ]]
}

@test "disk_monitor help" {
  run ./scripts/disk_monitor.sh --help
  [ "$status" -eq 0 ]
  [[ "$output" == *"Usage"* ]]
}
