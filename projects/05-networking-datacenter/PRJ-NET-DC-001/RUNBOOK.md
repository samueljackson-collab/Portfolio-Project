# Runbook — PRJ-NET-DC-001 (Active Directory Design & Automation)

## Overview

Production operations runbook for Active Directory infrastructure design, deployment, and automation using PowerShell DSC (Desired State Configuration) and Ansible. This runbook covers AD domain operations, infrastructure automation, configuration management, security hardening, disaster recovery, and troubleshooting procedures for enterprise datacenter Active Directory environments.

**System Components:**
- Active Directory Domain Services (AD DS)
- PowerShell Desired State Configuration (DSC)
- Ansible automation platform
- Group Policy management
- DNS and DHCP integration
- Certificate Services (AD CS)
- Federation Services (AD FS) - if applicable
- Backup and replication infrastructure

---

## SLOs/SLIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Domain Controller availability** | 99.9% | DC uptime monitoring |
| **Authentication success rate** | 99.95% | Successful Kerberos/NTLM authentications |
| **Replication latency** | < 15 minutes | Inter-site replication time |
| **GPO application time** | < 5 minutes | Group Policy refresh time |
| **Automation success rate** | 98% | DSC/Ansible configuration runs |
| **Backup completion rate** | 100% | System State backups |

---

## Dashboards & Alerts

### Dashboards

#### Domain Controller Health Dashboard
```powershell
# Quick DC health check
dcdiag /c /v | Out-File -FilePath "C:\Logs\dcdiag-$(Get-Date -Format 'yyyyMMdd-HHmm').log"

# Check replication status
repadmin /showrepl | Out-File -FilePath "C:\Logs\replication-$(Get-Date -Format 'yyyyMMdd-HHmm').log"

# Check FSMO roles
netdom query fsmo

# Check domain controller services
Get-Service -Name NTDS, DNS, KDC, W32Time | Format-Table Name, Status, StartType

# Check AD replication health
Get-ADReplicationPartnerMetadata -Target * |
    Select-Object Server, LastReplicationSuccess, LastReplicationResult |
    Format-Table -AutoSize
```

#### Active Directory Operations Dashboard
```powershell
# Check recent AD changes
Get-ADObject -Filter {whenChanged -gt $((Get-Date).AddDays(-1))} -IncludeDeletedObjects |
    Select-Object Name, whenChanged, ObjectClass

# Check locked accounts
Search-ADAccount -LockedOut | Select-Object Name, SamAccountName, LockedOut

# Check disabled accounts
Search-ADAccount -AccountDisabled | Measure-Object

# Check password expiration
Search-ADAccount -PasswordExpired | Select-Object Name, PasswordExpired

# Check recent failed login attempts
Get-EventLog -LogName Security -InstanceId 4625 -Newest 50 |
    Select-Object TimeGenerated, Message
```

#### Automation Status Dashboard
```bash
# Check Ansible playbook runs
ansible-playbook ad_operations.yml --check

# View DSC configuration status
ansible all -m win_shell -a "Get-DscConfigurationStatus | Select-Object Status, StartDate, Type"

# Check last automation run
ls -lht /var/log/ansible/ad-automation-*.log | head -5

# View DSC compliance
ansible windows_dcs -m win_shell -a "Test-DscConfiguration -Detailed"
```

### Alerts

| Severity | Condition | Response Time | Action |
|----------|-----------|---------------|--------|
| **P0** | Domain Controller down | Immediate | Restart DC, failover to backup |
| **P0** | AD replication failure > 1 hour | Immediate | Investigate and resolve replication |
| **P1** | Authentication failure rate > 1% | 30 minutes | Check DC health, investigate cause |
| **P1** | FSMO role holder down | 30 minutes | Seize roles if necessary |
| **P1** | DNS service failure | 30 minutes | Restart DNS, check zone health |
| **P2** | GPO not applying | 2 hours | Check GPO replication and inheritance |
| **P2** | Automation failure | 4 hours | Review logs, fix configuration |
| **P3** | Disk space low on DC | 24 hours | Clean logs, expand disk |

#### Alert Queries

**Check for Domain Controller failures:**
```powershell
# Check if DC is responding
Test-Connection -ComputerName DC01 -Count 2

# Check LDAP connectivity
$LDAP = New-Object DirectoryServices.DirectoryEntry("LDAP://DC01")
if ($LDAP.Name) { Write-Host "LDAP OK" } else { Write-Host "ALERT: LDAP FAILURE" }

# Check Kerberos
klist tickets
if ($LASTEXITCODE -ne 0) { Write-Host "ALERT: Kerberos authentication failed" }
```

**Monitor replication health:**
```powershell
# Check replication failures
$ReplErrors = repadmin /showrepl | Select-String "fail"
if ($ReplErrors) {
    Write-Host "ALERT: Replication failures detected"
    $ReplErrors
}

# Check replication latency
Get-ADReplicationPartnerMetadata -Target * |
    Where-Object { $_.LastReplicationSuccess -lt (Get-Date).AddMinutes(-30) } |
    ForEach-Object {
        Write-Host "ALERT: Replication delay on $($_.Server)"
    }
```

**Monitor authentication issues:**
```powershell
# Check failed authentication events (last hour)
$FailedAuth = Get-EventLog -LogName Security -After (Get-Date).AddHours(-1) |
    Where-Object {$_.InstanceID -eq 4625}
$FailedAuthCount = ($FailedAuth | Measure-Object).Count

if ($FailedAuthCount -gt 100) {
    Write-Host "ALERT: High authentication failure rate: $FailedAuthCount failures"
}
```

---

## Standard Operations

### Domain Controller Operations

#### Check Domain Controller Health
```powershell
# Comprehensive DC health check
dcdiag /c /v /e

# Check specific DC
dcdiag /s:DC01 /c /v

# Check replication topology
repadmin /replsummary

# Check DNS health
dcdiag /test:DNS /v

# Check SYSVOL replication
dfsrdiag ReplicationState /all
```

#### Restart Domain Controller Services
```powershell
# Restart NTDS (Active Directory Domain Services)
# WARNING: This will cause brief authentication disruption
Restart-Service NTDS -Force

# Restart DNS service
Restart-Service DNS -Force

# Restart KDC (Kerberos Key Distribution Center)
Restart-Service KDC -Force

# Restart Netlogon
Restart-Service Netlogon -Force

# Restart all critical AD services (use with caution)
'NTDS','DNS','KDC','Netlogon' | ForEach-Object {
    Restart-Service $_ -Force
    Start-Sleep -Seconds 5
}
```

#### Check and Manage FSMO Roles
```powershell
# View FSMO role holders
netdom query fsmo

# Or using PowerShell
Get-ADDomain | Select-Object InfrastructureMaster, PDCEmulator, RIDMaster
Get-ADForest | Select-Object SchemaMaster, DomainNamingMaster

# Transfer FSMO roles (graceful transfer)
Move-ADDirectoryServerOperationMasterRole -Identity "DC02" -OperationMasterRole SchemaMaster

# Seize FSMO roles (if holder is permanently down)
# WARNING: Only use if original holder cannot be recovered
Move-ADDirectoryServerOperationMasterRole -Identity "DC02" -OperationMasterRole PDCEmulator -Force
```

### Active Directory Management

#### User Account Management
```powershell
# Create new user
New-ADUser -Name "John Doe" -GivenName "John" -Surname "Doe" `
    -SamAccountName "jdoe" -UserPrincipalName "jdoe@contoso.com" `
    -Path "OU=Users,DC=contoso,DC=com" `
    -AccountPassword (ConvertTo-SecureString "P@ssw0rd!" -AsPlainText -Force) `
    -Enabled $true

# Modify user
Set-ADUser -Identity jdoe -Department "IT" -Title "Systems Administrator"

# Disable user account
Disable-ADAccount -Identity jdoe

# Unlock locked account
Unlock-ADAccount -Identity jdoe

# Reset password
Set-ADAccountPassword -Identity jdoe -NewPassword (ConvertTo-SecureString "NewP@ss123" -AsPlainText -Force) -Reset

# Force password change at next logon
Set-ADUser -Identity jdoe -ChangePasswordAtLogon $true
```

#### Group Management
```powershell
# Create security group
New-ADGroup -Name "IT-Admins" -GroupScope Global -GroupCategory Security `
    -Path "OU=Groups,DC=contoso,DC=com"

# Add user to group
Add-ADGroupMember -Identity "IT-Admins" -Members jdoe

# Remove user from group
Remove-ADGroupMember -Identity "IT-Admins" -Members jdoe -Confirm:$false

# List group members
Get-ADGroupMember -Identity "IT-Admins" | Select-Object Name, SamAccountName

# List user's group memberships
Get-ADPrincipalGroupMembership -Identity jdoe | Select-Object Name
```

#### Organizational Unit (OU) Management
```powershell
# Create OU
New-ADOrganizationalUnit -Name "IT Department" -Path "DC=contoso,DC=com"

# Move user to different OU
Move-ADObject -Identity "CN=John Doe,OU=Users,DC=contoso,DC=com" `
    -TargetPath "OU=IT Department,DC=contoso,DC=com"

# Protect OU from accidental deletion
Get-ADOrganizationalUnit -Identity "OU=IT Department,DC=contoso,DC=com" |
    Set-ADOrganizationalUnit -ProtectedFromAccidentalDeletion $true
```

### Group Policy Management

#### Create and Link GPO
```powershell
# Create new GPO
New-GPO -Name "Workstation Security Policy" -Comment "Security hardening for workstations"

# Link GPO to OU
New-GPLink -Name "Workstation Security Policy" -Target "OU=Workstations,DC=contoso,DC=com"

# Set GPO link order
Set-GPLink -Name "Workstation Security Policy" -Target "OU=Workstations,DC=contoso,DC=com" -Order 1

# Enforce GPO (no block inheritance)
Set-GPLink -Name "Workstation Security Policy" -Target "OU=Workstations,DC=contoso,DC=com" -Enforced Yes
```

#### GPO Operations
```powershell
# Force GPO update on local machine
gpupdate /force

# Force GPO update on remote computer
Invoke-Command -ComputerName Client01 -ScriptBlock { gpupdate /force }

# Generate GPO report
Get-GPOReport -Name "Workstation Security Policy" -ReportType Html -Path "C:\Reports\GPO-Report.html"

# Backup GPO
Backup-GPO -Name "Workstation Security Policy" -Path "C:\GPOBackups"

# Restore GPO
Restore-GPO -Name "Workstation Security Policy" -Path "C:\GPOBackups\{GUID}"

# Check GPO replication status
Get-GPO -All | ForEach-Object {
    $_ | Get-GPPermission -All | Select-Object GPO, Trustee, Permission
}
```

### DSC (Desired State Configuration) Operations

#### Deploy DSC Configuration
```powershell
# Create DSC configuration
Configuration ADConfiguration {
    param (
        [Parameter(Mandatory=$true)]
        [String]$DomainName
    )

    Import-DscResource -ModuleName PSDesiredStateConfiguration
    Import-DscResource -ModuleName ActiveDirectoryDsc

    Node 'DC01' {
        WindowsFeature AD-Domain-Services {
            Name = 'AD-Domain-Services'
            Ensure = 'Present'
        }

        ADDomain 'ContosoDomain' {
            DomainName = $DomainName
            Credential = $Credential
            DependsOn = '[WindowsFeature]AD-Domain-Services'
        }

        ADOrganizationalUnit 'ITDepartment' {
            Name = 'IT Department'
            Path = "DC=contoso,DC=com"
            Ensure = 'Present'
        }
    }
}

# Compile configuration
ADConfiguration -DomainName "contoso.com" -OutputPath "C:\DSC\ADConfig"

# Apply configuration
Start-DscConfiguration -Path "C:\DSC\ADConfig" -Wait -Verbose -Force
```

#### Check DSC Status
```powershell
# Get current DSC configuration status
Get-DscConfigurationStatus

# Test if system is in desired state
Test-DscConfiguration -Detailed

# Get DSC configuration
Get-DscConfiguration

# Get DSC local configuration manager settings
Get-DscLocalConfigurationManager
```

### Ansible Automation Operations

#### Run Ansible Playbooks
```bash
# Check AD domain status
ansible-playbook playbooks/ad_check_health.yml

# Deploy AD configuration
ansible-playbook playbooks/ad_deploy.yml --check  # Dry run
ansible-playbook playbooks/ad_deploy.yml  # Apply changes

# Create users from inventory
ansible-playbook playbooks/ad_create_users.yml -e "user_file=users.csv"

# Apply security hardening
ansible-playbook playbooks/ad_security_hardening.yml

# Run with specific tags
ansible-playbook playbooks/ad_operations.yml --tags "users,groups"
```

#### Ansible Ad-Hoc Commands
```bash
# Check DC connectivity
ansible windows_dcs -m win_ping

# Get AD domain info
ansible windows_dcs -m win_shell -a "Get-ADDomain | Select-Object Name, Forest, DomainMode"

# Check AD replication
ansible windows_dcs -m win_shell -a "repadmin /showrepl"

# Get domain controller list
ansible windows_dcs -m win_shell -a "Get-ADDomainController -Filter * | Select-Object Name, IPv4Address, Site"

# Restart AD service (use with caution)
ansible windows_dcs -m win_service -a "name=NTDS state=restarted"
```

### DNS Management

#### DNS Operations
```powershell
# Create DNS A record
Add-DnsServerResourceRecordA -Name "server01" -IPv4Address "192.168.1.100" -ZoneName "contoso.com"

# Create DNS PTR record
Add-DnsServerResourceRecordPtr -Name "100" -IPv4Address "192.168.1.100" -ZoneName "1.168.192.in-addr.arpa"

# Create DNS CNAME record
Add-DnsServerResourceRecordCName -Name "www" -HostNameAlias "webserver.contoso.com" -ZoneName "contoso.com"

# Delete DNS record
Remove-DnsServerResourceRecord -Name "server01" -RRType "A" -ZoneName "contoso.com" -Force

# Check DNS zone replication
Get-DnsServerZone | Select-Object ZoneName, ReplicationScope, IsDsIntegrated

# Force DNS replication
Sync-DnsServerZone -Name "contoso.com"
```

---

## Incident Response

### Detection

**Automated Detection:**
- SCOM/monitoring alerts
- Event log monitoring
- Replication health checks
- Service status monitors
- Automation failure notifications

**Manual Detection:**
```powershell
# Quick health check
dcdiag /c | Select-String "fail"

# Check event logs for errors
Get-EventLog -LogName "Directory Service" -EntryType Error -Newest 20

# Check replication
repadmin /replsummary | Select-String "fail\|error"

# Check DC services
Get-Service -Name NTDS, DNS, KDC | Where-Object {$_.Status -ne 'Running'}
```

### Triage

#### Severity Classification

### P0: Critical Domain Failure
- All domain controllers down
- Forest-wide authentication failure
- Schema master failure during schema changes
- Complete AD replication failure

### P1: Major Service Degradation
- Single DC down (multi-DC environment)
- FSMO role holder failure
- Site-wide authentication issues
- DNS service failure
- Replication failure > 1 hour

### P2: Service Impact
- GPO application failures
- Single OU authentication issues
- Replication latency 15-60 minutes
- Automation failures
- Non-critical service failures

### P3: Minor Issues
- Single user account issues
- GPO compliance warnings
- Low disk space warnings
- Performance degradation

### Incident Response Procedures

#### P0: Domain Controller Down

**Immediate Actions (0-5 minutes):**
```powershell
# 1. Verify DC is down
Test-Connection -ComputerName DC01 -Count 4

# 2. Check if other DCs are operational
Get-ADDomainController -Filter * | ForEach-Object {
    Test-Connection -ComputerName $_.HostName -Count 2 -ErrorAction SilentlyContinue
}

# 3. Check load on remaining DCs
Invoke-Command -ComputerName DC02 -ScriptBlock {
    Get-Counter '\Processor(_Total)\% Processor Time'
}

# 4. Attempt to connect to down DC console
# RDP, ILO, or physical access

# 5. Check DC services if accessible
Invoke-Command -ComputerName DC01 -ScriptBlock {
    Get-Service -Name NTDS, DNS, KDC | Select-Object Name, Status
} -ErrorAction SilentlyContinue
```

**Investigation (5-15 minutes):**
```powershell
# Check system event logs (if accessible)
Get-EventLog -ComputerName DC01 -LogName System -EntryType Error -Newest 50

# Check Directory Services event log
Get-EventLog -ComputerName DC01 -LogName "Directory Service" -EntryType Error -Newest 50

# Check disk space
Get-WmiObject -ComputerName DC01 -Class Win32_LogicalDisk |
    Select-Object DeviceID, @{Name="FreeGB";Expression={[math]::Round($_.FreeSpace/1GB,2)}}

# Check for recent Windows Updates
Get-HotFix -ComputerName DC01 | Sort-Object InstalledOn -Descending | Select-Object -First 10
```

**Mitigation:**
```powershell
# Option 1: Restart DC (if accessible)
Restart-Computer -ComputerName DC01 -Force

# Option 2: Force shutdown and start (via hypervisor/ILO)
# Use virtualization management tools or ILO/iDRAC

# Option 3: Restart critical services
Invoke-Command -ComputerName DC01 -ScriptBlock {
    Restart-Service NTDS -Force
    Start-Sleep -Seconds 10
    Restart-Service DNS -Force
}

# Option 4: Remove from rotation temporarily (if multi-DC)
# Update DNS SRV records or load balancer configuration

# Verify mitigation
Test-Connection -ComputerName DC01 -Count 2
dcdiag /s:DC01 /c
```

#### P1: AD Replication Failure

**Investigation:**
```powershell
# 1. Check replication status
repadmin /showrepl

# 2. Check replication queue
repadmin /queue

# 3. Check replication partners
repadmin /showreps

# 4. Force synchronization
repadmin /syncall /AdeP

# 5. Check for replication errors
Get-ADReplicationFailure -Target DC01 -Scope Domain

# 6. Check DNS configuration
nslookup -type=SRV _ldap._tcp.dc._msdcs.contoso.com

# 7. Check network connectivity between DCs
Test-NetConnection -ComputerName DC02 -Port 389  # LDAP
Test-NetConnection -ComputerName DC02 -Port 3268 # Global Catalog
Test-NetConnection -ComputerName DC02 -Port 445  # SMB
```

**Common Causes & Fixes:**

**DNS Issues:**
```powershell
# Verify DNS settings on DC
Get-DnsClientServerAddress

# Register DC in DNS
Register-DnsClient -Verbose

# Restart DNS service
Restart-Service DNS -Force

# Verify SRV records
nslookup -type=SRV _ldap._tcp.dc._msdcs.contoso.com
```

**Firewall Blocking Replication:**
```powershell
# Check firewall rules
Get-NetFirewallRule -DisplayName "*Active Directory*" | Select-Object DisplayName, Enabled

# Ensure required ports are open:
# TCP 389 (LDAP), 636 (LDAPS), 3268 (GC), 3269 (GC SSL)
# TCP 88 (Kerberos), 445 (SMB), 135 (RPC), Dynamic RPC ports

# Test port connectivity
Test-NetConnection -ComputerName DC02 -Port 389
Test-NetConnection -ComputerName DC02 -Port 445
```

**USN Rollback:**
```powershell
# Check for USN rollback (serious issue)
Get-EventLog -LogName "Directory Service" | Where-Object {$_.EventID -eq 2095}

# If USN rollback detected:
# - DO NOT force replication
# - Contact Microsoft Support
# - May require DC rebuild
```

**Mitigation:**
```powershell
# Force replication from specific DC
repadmin /replicate DC01 DC02 "DC=contoso,DC=com"

# Synchronize all naming contexts
repadmin /syncall /AdeP

# Push replication from this DC to all partners
repadmin /syncall /e /P

# Verify replication success
repadmin /showrepl | Select-String "Last attempt.*successful"

# Check replication latency
Get-ADReplicationPartnerMetadata -Target * |
    Select-Object Server, LastReplicationSuccess, LastReplicationResult
```

#### P1: FSMO Role Holder Failure

**Investigation:**
```powershell
# 1. Check current FSMO role holders
netdom query fsmo

# 2. Test connectivity to role holders
$FSMOHolders = @()
$FSMOHolders += (Get-ADDomain).InfrastructureMaster
$FSMOHolders += (Get-ADDomain).PDCEmulator
$FSMOHolders += (Get-ADDomain).RIDMaster
$FSMOHolders += (Get-ADForest).SchemaMaster
$FSMOHolders += (Get-ADForest).DomainNamingMaster

$FSMOHolders | ForEach-Object {
    Test-Connection -ComputerName $_ -Count 2 -ErrorAction SilentlyContinue
}

# 3. Determine which roles are on failed DC
# 4. Assess impact based on role
```

**Mitigation:**

**If DC can be recovered (graceful transfer):**
```powershell
# Transfer roles to another DC
Move-ADDirectoryServerOperationMasterRole -Identity "DC02" `
    -OperationMasterRole SchemaMaster, DomainNamingMaster, PDCEmulator, RIDMaster, InfrastructureMaster
```

**If DC cannot be recovered (seize roles):**
```powershell
# WARNING: Only seize roles if original holder is permanently dead
# and will NEVER come back online

# Seize all roles to DC02
Move-ADDirectoryServerOperationMasterRole -Identity "DC02" `
    -OperationMasterRole SchemaMaster, DomainNamingMaster, PDCEmulator, RIDMaster, InfrastructureMaster `
    -Force

# Verify role transfer
netdom query fsmo

# Metadata cleanup for failed DC (after seizing)
# Use ntdsutil to remove failed DC from AD
ntdsutil
metadata cleanup
connections
connect to server DC02
quit
select operation target
list domains
select domain 0
list sites
select site 0
list servers in site
select server 1  # Failed DC
quit
remove selected server
quit
quit
```

#### P2: GPO Not Applying

**Investigation:**
```powershell
# 1. Check GPO replication status
Get-GPO -All | ForEach-Object {
    $_.DisplayName
    (Get-GPOReport -Guid $_.Id -ReportType Xml).GPO.Computer.VersionDirectory
}

# 2. Check SYSVOL replication
dfsrdiag ReplicationState /all

# 3. Test GPO application on client
# On client machine:
gpresult /H gpresult.html
# Open gpresult.html in browser

# 4. Check for WMI filters
Get-GPO -Name "Workstation Security Policy" | Select-Object WmiFilter

# 5. Check GPO permissions
Get-GPPermission -Name "Workstation Security Policy" -All

# 6. Check for blocked inheritance
Get-GPInheritance -Target "OU=Workstations,DC=contoso,DC=com"
```

**Mitigation:**
```powershell
# Force SYSVOL replication
dfsrdiag SyncNow /RGName:"Domain System Volume" /Partner:DC02 /Time:1

# Reset GPO on client
Invoke-Command -ComputerName Client01 -ScriptBlock {
    Remove-Item -Path "C:\Windows\System32\GroupPolicy\*" -Recurse -Force
    gpupdate /force
}

# Restore GPO from backup if corrupted
Restore-GPO -Name "Workstation Security Policy" -Path "C:\GPOBackups\Latest"

# Check SYSVOL permissions
icacls C:\Windows\SYSVOL

# Fix GPO permissions
Set-GPPermission -Name "Workstation Security Policy" -TargetName "Domain Computers" -TargetType Group -PermissionLevel GpoApply
```

#### P2: Automation Failure (DSC/Ansible)

**DSC Configuration Failure Investigation:**
```powershell
# Check DSC status
Get-DscConfigurationStatus | Select-Object Status, Error, StartDate

# View detailed error
Get-DscConfigurationStatus | Select-Object -ExpandProperty ResourcesNotInDesiredState

# Check event logs
Get-WinEvent -LogName "Microsoft-Windows-Dsc/Operational" -MaxEvents 50

# Test configuration without applying
Test-DscConfiguration -Detailed
```

**DSC Mitigation:**
```powershell
# Reapply DSC configuration
Start-DscConfiguration -Path "C:\DSC\ADConfig" -Wait -Verbose -Force

# Reset LCM if corrupted
Remove-DscConfigurationDocument -Stage Current
Remove-DscConfigurationDocument -Stage Pending

# Reconfigure LCM
Set-DscLocalConfigurationManager -Path "C:\DSC\LCMConfig" -Force

# Verify fix
Test-DscConfiguration
Get-DscConfigurationStatus
```

**Ansible Failure Investigation:**
```bash
# Check Ansible connectivity
ansible windows_dcs -m win_ping

# Run playbook in check mode
ansible-playbook playbooks/ad_operations.yml --check -vvv

# Check Ansible logs
tail -100 /var/log/ansible/ad-automation.log

# Test WinRM connectivity
ansible windows_dcs -m win_shell -a "hostname"
```

**Ansible Mitigation:**
```bash
# Verify credentials
ansible-vault view group_vars/windows/vault.yml

# Test WinRM manually
curl --header "Content-Type: application/soap+xml;charset=UTF-8" \
    --data @winrm_test.xml \
    http://dc01.contoso.com:5985/wsman

# Rerun failed playbook
ansible-playbook playbooks/ad_operations.yml --start-at-task="Configure DNS" -vv

# Force fact gathering
ansible windows_dcs -m setup --tree /tmp/facts
```

### Post-Incident

**After Resolution:**
```powershell
# Document incident
$IncidentReport = @"
# AD Incident Report

**Date:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
**Severity:** P1
**Duration:** [duration]
**Affected Components:** [DC names, services, etc.]

## Timeline
- [Time]: Issue detected
- [Time]: Investigation started
- [Time]: Root cause identified
- [Time]: Fix implemented
- [Time]: Service restored

## Root Cause
[Detailed root cause analysis]

## Impact
- Authentication failures: [count]
- Affected users: [count]
- Replication lag: [time]

## Resolution
[How the issue was resolved]

## Prevention
- [ ] Add monitoring for [specific metric]
- [ ] Update documentation
- [ ] Implement redundancy
- [ ] Schedule preventive maintenance

## Lessons Learned
[Key takeaways]
"@

$IncidentReport | Out-File -FilePath "C:\Incidents\incident-$(Get-Date -Format 'yyyyMMdd-HHmm').md"

# Update health check baselines
dcdiag /c /v > "C:\Baselines\dcdiag-post-incident.log"
repadmin /showrepl > "C:\Baselines\replication-post-incident.log"
```

---

## Monitoring & Troubleshooting

### Essential Troubleshooting Commands

#### Active Directory Health Checks
```powershell
# Comprehensive health check
dcdiag /c /v /e /f:C:\Logs\dcdiag-full.log

# Test specific component
dcdiag /test:Replications
dcdiag /test:DNS
dcdiag /test:FSMOCheck
dcdiag /test:Services

# Check all DCs in forest
dcdiag /e

# Network connectivity test
dcdiag /test:Connectivity
```

#### Replication Diagnostics
```powershell
# Show replication status
repadmin /showrepl

# Show replication summary
repadmin /replsummary

# Check replication queue
repadmin /queue

# Show replication metadata for object
repadmin /showobjmeta "CN=John Doe,OU=Users,DC=contoso,DC=com"

# Force replication
repadmin /syncall /AdeP

# Show replication partners
repadmin /showreps
```

#### Performance Monitoring
```powershell
# Check NTDS performance counters
Get-Counter '\NTDS\*' | Format-Table -AutoSize

# Check LDAP performance
Get-Counter '\DirectoryServices(NTDS)\LDAP Client Sessions'
Get-Counter '\DirectoryServices(NTDS)\LDAP Searches/sec'

# Check disk performance
Get-Counter '\PhysicalDisk(*)\Avg. Disk sec/Read'
Get-Counter '\PhysicalDisk(*)\Avg. Disk sec/Write'

# Check memory usage
Get-Counter '\Memory\Available MBytes'
Get-Counter '\Process(lsass)\Working Set'
```

#### Database Maintenance
```powershell
# Check AD database integrity
ntdsutil "activate instance ntds" "files" "integrity" quit quit

# Get database info
ntdsutil "activate instance ntds" "files" "info" quit quit

# Compact database (offline)
# Stop AD DS service first
Stop-Service NTDS
ntdsutil "activate instance ntds" "files" "compact to C:\Temp" quit quit
# Replace old database with compacted one

# Check database size
Get-ChildItem "C:\Windows\NTDS\ntds.dit" | Select-Object Name, @{N="SizeGB";E={[math]::Round($_.Length/1GB,2)}}
```

### Common Issues & Solutions

#### Issue: "The specified domain either does not exist or could not be contacted"

**Symptoms:**
```powershell
PS> Get-ADUser -Identity jdoe
Get-ADUser : Unable to contact the server. This may be because this server does not exist,
it is currently down, or it does not have the Active Directory Web Services running.
```

**Diagnosis:**
```powershell
# Check if AD Web Services is running
Get-Service ADWS

# Check DNS resolution
nslookup contoso.com
nslookup -type=SRV _ldap._tcp.dc._msdcs.contoso.com

# Check network connectivity
Test-NetConnection -ComputerName DC01 -Port 389
```

**Solution:**
```powershell
# Start AD Web Services
Start-Service ADWS

# Register DNS records
Register-DnsClient
ipconfig /registerdns

# Restart Netlogon service
Restart-Service Netlogon

# Verify fix
Get-ADDomain
```

---

#### Issue: High CPU usage on domain controller

**Symptoms:**
- lsass.exe consuming > 80% CPU
- Slow authentication
- High LDAP response times

**Diagnosis:**
```powershell
# Check CPU usage
Get-Counter '\Processor(*)\% Processor Time'

# Check LDAP operations
Get-Counter '\DirectoryServices(NTDS)\LDAP Searches/sec'

# Check for inefficient LDAP queries
# Enable expensive search logging
Set-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Services\NTDS\Diagnostics" -Name "15 Field Engineering" -Value 5

# Check event log for expensive searches (Event ID 1644)
Get-EventLog -LogName "Directory Service" | Where-Object {$_.EventID -eq 1644}
```

**Solution:**
```powershell
# Add indexes for commonly searched attributes
# (Requires Schema Admin rights)
$SchemaNC = (Get-ADRootDSE).schemaNamingContext
$AttributeToIndex = "employeeID"
$Attribute = Get-ADObject -SearchBase $SchemaNC -Filter {lDAPDisplayName -eq $AttributeToIndex}
Set-ADObject -Identity $Attribute -Add @{searchFlags=1}

# Restart NTDS service to apply
Restart-Service NTDS -Force

# Disable expensive search logging after troubleshooting
Set-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Services\NTDS\Diagnostics" -Name "15 Field Engineering" -Value 0
```

---

#### Issue: SYSVOL not replicating

**Symptoms:**
- GPOs not applying to clients
- SYSVOL folder out of sync between DCs

**Diagnosis:**
```powershell
# Check DFSR state
dfsrdiag ReplicationState

# Check backlog
dfsrdiag Backlog /RGName:"Domain System Volume" /RFName:"SYSVOL Share" /SendingMember:DC01 /ReceivingMember:DC02

# Check DFSR event logs
Get-EventLog -LogName "DFS Replication" -EntryType Error -Newest 20
```

**Solution:**
```powershell
# Force DFSR synchronization
dfsrdiag SyncNow /RGName:"Domain System Volume" /Partner:DC02 /Time:1

# Restart DFSR service
Restart-Service DFSR

# If authoritative restore needed (DC01 is authoritative)
Stop-Service DFSR
Set-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Services\DFSR\Parameters\Backup/Restore\Process Security" -Name "Burflags" -Value 0xD2
Start-Service DFSR

# On non-authoritative DC (DC02)
Stop-Service DFSR
Set-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Services\DFSR\Parameters\Backup/Restore\Process Security" -Name "Burflags" -Value 0xD4
Start-Service DFSR

# Verify replication
dfsrdiag ReplicationState
```

---

## Disaster Recovery & Backups

### RPO/RTO

- **RPO** (Recovery Point Objective): 1 hour (hourly System State backups)
- **RTO** (Recovery Time Objective): 4 hours (full DC restore or promote new DC)

### Backup Strategy

**System State Backups:**
```powershell
# Install Windows Server Backup feature
Install-WindowsFeature Windows-Server-Backup

# Perform System State backup
wbadmin start systemstatebackup -backupTarget:E: -quiet

# Schedule daily System State backups
$Action = New-ScheduledTaskAction -Execute "wbadmin.exe" -Argument "start systemstatebackup -backupTarget:E: -quiet"
$Trigger = New-ScheduledTaskTrigger -Daily -At 2AM
Register-ScheduledTask -TaskName "Daily System State Backup" -Action $Action -Trigger $Trigger -User "SYSTEM"

# Verify backup
wbadmin get versions
```

**AD Database Backups:**
```powershell
# Full server backup (includes System State)
wbadmin start backup -backupTarget:E: -include:C: -allCritical -quiet

# Backup GPOs
Backup-GPO -All -Path "E:\GPO Backups\$(Get-Date -Format 'yyyy-MM-dd')"

# Export AD structure
csvde -f "E:\AD Backups\ad-export-$(Get-Date -Format 'yyyy-MM-dd').csv"

# Backup DNS zones
Export-DnsServerZone -Name "contoso.com" -FileName "contoso.com-$(Get-Date -Format 'yyyy-MM-dd').dns"
```

**Configuration Backups:**
```bash
# Backup Ansible configurations
tar -czf /backups/ansible-config-$(date +%Y%m%d).tar.gz \
    /etc/ansible/ playbooks/ inventory/

# Backup DSC configurations
tar -czf /backups/dsc-config-$(date +%Y%m%d).tar.gz \
    /var/lib/dsc/ /opt/dsc-configs/
```

### Disaster Recovery Procedures

#### Restore Domain Controller from Backup

**System State Restore (DC is bootable):**
```powershell
# 1. Restart DC in Directory Services Restore Mode (DSRM)
# - Reboot and press F8
# - Select "Directory Services Restore Mode"
# - Login with DSRM password

# 2. List available backups
wbadmin get versions

# 3. Restore System State
wbadmin start systemstaterecovery -version:MM/DD/YYYY-HH:MM -quiet

# 4. Restart normally
Restart-Computer

# 5. Mark restored DC as authoritative (if needed)
ntdsutil
activate instance ntds
authoritative restore
restore database
# or restore specific subtree:
restore subtree "OU=IT Department,DC=contoso,DC=com"
quit
quit

# 6. Verify restoration
dcdiag /c /v
repadmin /showrepl
```

#### Promote New Domain Controller

**Emergency DC Promotion (existing DC failed):**
```powershell
# 1. Prepare new server
Install-WindowsFeature AD-Domain-Services -IncludeManagementTools

# 2. Promote to Domain Controller
$Credential = Get-Credential
Install-ADDSDomainController -DomainName "contoso.com" -Credential $Credential -SafeModeAdministratorPassword (ConvertTo-SecureString "P@ssw0rd!" -AsPlainText -Force)

# 3. Verify promotion
Get-ADDomainController -Identity $env:COMPUTERNAME

# 4. Check replication
repadmin /replsummary

# 5. Transfer FSMO roles if needed
Move-ADDirectoryServerOperationMasterRole -Identity $env:COMPUTERNAME -OperationMasterRole SchemaMaster,DomainNamingMaster,PDCEmulator,RIDMaster,InfrastructureMaster -Force
```

#### Forest Recovery (Complete Disaster)

**Forest-Level Disaster Recovery:**
```powershell
# 1. Restore first DC in forest root domain (authoritative)
# Follow System State Restore procedure above

# 2. Clean metadata of all other DCs
# Use ntdsutil metadata cleanup to remove all failed DCs

# 3. Seize all FSMO roles to restored DC
Move-ADDirectoryServerOperationMasterRole -Identity $env:COMPUTERNAME `
    -OperationMasterRole SchemaMaster,DomainNamingMaster,PDCEmulator,RIDMaster,InfrastructureMaster -Force

# 4. Reset krbtgt password twice
# Important for Kerberos security
$krbtgt = Get-ADUser -Identity krbtgt
Set-ADAccountPassword -Identity $krbtgt -Reset -NewPassword (ConvertTo-SecureString "Complex_P@ssw0rd_1" -AsPlainText -Force)
# Wait for replication (if other DCs exist)
Set-ADAccountPassword -Identity $krbtgt -Reset -NewPassword (ConvertTo-SecureString "Complex_P@ssw0rd_2" -AsPlainText -Force)

# 5. Force replication
repadmin /syncall /AdeP

# 6. Gradually add other DCs
# Promote new DCs one by one
# Verify replication between each promotion

# 7. Restore GPOs
Restore-GPO -All -Path "E:\GPO Backups\Latest"

# 8. Comprehensive testing
dcdiag /c /v /e
```

---

## Maintenance Procedures

### Routine Maintenance

#### Daily Tasks
```powershell
# Health check
dcdiag /c | Out-File -Append -FilePath "C:\Logs\daily-health-$(Get-Date -Format 'yyyy-MM-dd').log"

# Replication check
repadmin /replsummary >> "C:\Logs\daily-health-$(Get-Date -Format 'yyyy-MM-dd').log"

# Check for locked accounts
Search-ADAccount -LockedOut | Select-Object Name, LockedOut

# Check disk space
Get-WmiObject Win32_LogicalDisk | Where-Object {$_.DriveType -eq 3} |
    Select-Object DeviceID, @{Name="FreeGB";Expression={[math]::Round($_.FreeSpace/1GB,2)}} |
    Where-Object {$_.FreeGB -lt 10}
```

#### Weekly Tasks
```powershell
# Full health check with logging
dcdiag /c /v > "C:\Logs\weekly-health-$(Get-Date -Format 'yyyy-MM-dd').log"

# Check event logs for errors
Get-EventLog -LogName "Directory Service" -EntryType Error -After (Get-Date).AddDays(-7) |
    Select-Object TimeGenerated, Message |
    Export-Csv "C:\Logs\weekly-errors-$(Get-Date -Format 'yyyy-MM-dd').csv"

# GPO compliance check
Get-GPOReport -All -ReportType Html -Path "C:\Reports\GPO-Report-$(Get-Date -Format 'yyyy-MM-dd').html"

# Backup all GPOs
Backup-GPO -All -Path "C:\GPOBackups\$(Get-Date -Format 'yyyy-MM-dd')"

# Check AD database size
Get-ChildItem "C:\Windows\NTDS\ntds.dit" |
    Select-Object Name, @{N="SizeGB";E={[math]::Round($_.Length/1GB,2)}}
```

#### Monthly Tasks
```powershell
# Comprehensive forest/domain health report
Get-ADForest | Out-File "C:\Reports\monthly-forest-$(Get-Date -Format 'yyyy-MM-dd').txt"
Get-ADDomain | Out-File -Append "C:\Reports\monthly-forest-$(Get-Date -Format 'yyyy-MM-dd').txt"

# Check for stale computer accounts (> 90 days)
$StaleDate = (Get-Date).AddDays(-90)
Search-ADAccount -ComputersOnly -AccountInactive -TimeSpan 90.00:00:00 |
    Export-Csv "C:\Reports\stale-computers-$(Get-Date -Format 'yyyy-MM-dd').csv"

# Check for expired accounts
Search-ADAccount -AccountExpired |
    Export-Csv "C:\Reports\expired-accounts-$(Get-Date -Format 'yyyy-MM-dd').csv"

# Database defragmentation analysis
ntdsutil "activate instance ntds" "files" "info" quit quit

# Review and rotate logs
Get-ChildItem C:\Logs -Filter "*.log" | Where-Object {$_.LastWriteTime -lt (Get-Date).AddMonths(-3)} | Remove-Item

# Update DSC/Ansible configurations
ansible-playbook playbooks/ad_monthly_maintenance.yml
```

---

## Quick Reference Card

### Most Common Operations
```powershell
# Health check
dcdiag /c

# Replication status
repadmin /showrepl

# Force replication
repadmin /syncall /AdeP

# Check FSMO roles
netdom query fsmo

# Restart AD services
Restart-Service NTDS -Force

# Create user
New-ADUser -Name "John Doe" -SamAccountName jdoe

# Unlock account
Unlock-ADAccount -Identity jdoe

# Force GPO update
gpupdate /force

# Check GPO application
gpresult /H gpresult.html
```

### Emergency Response
```powershell
# P0: DC down
Test-Connection -ComputerName DC01
Restart-Computer -ComputerName DC01 -Force

# P1: Replication failure
repadmin /showrepl | Select-String "fail"
repadmin /syncall /AdeP

# P1: FSMO role failure
netdom query fsmo
Move-ADDirectoryServerOperationMasterRole -Identity DC02 -OperationMasterRole PDCEmulator -Force

# P2: GPO not applying
dfsrdiag SyncNow /RGName:"Domain System Volume"
gpupdate /force
```

---

**Document Metadata:**
- **Version:** 1.0
- **Last Updated:** 2025-11-10
- **Owner:** Infrastructure & Datacenter Operations Team
- **Review Schedule:** Quarterly or after major incidents
- **Feedback:** Create issue or submit PR with updates
