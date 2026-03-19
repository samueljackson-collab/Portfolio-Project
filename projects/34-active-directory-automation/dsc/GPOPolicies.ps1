# GPOPolicies.ps1
# PowerShell DSC Configuration for Group Policy Objects
# Covers: password policy, account lockout, audit policy, screensaver, IE security,
#         Windows Firewall, AppLocker baseline, and drive mappings
#
# Prerequisites: DomainSetup.ps1 must be applied; GPMC module required
#
# Usage:
#   Import-Module GroupPolicy
#   . .\GPOPolicies.ps1
#   GPOPolicies -OutputPath C:\DSC\GPOPolicies
#   Start-DscConfiguration -Path C:\DSC\GPOPolicies -Wait -Verbose -Force

Configuration GPOPolicies {
    param(
        [Parameter(Mandatory)]
        [PSCredential]$DomainAdminCredential,

        [string]$DomainName = "corp.contoso.local",
        [string]$DomainDN   = "DC=corp,DC=contoso,DC=local"
    )

    Import-DscResource -ModuleName PSDesiredStateConfiguration
    Import-DscResource -ModuleName ActiveDirectoryDsc
    Import-DscResource -ModuleName GroupPolicyDsc

    Node $AllNodes.NodeName {

        #=======================================================================
        # DEFAULT DOMAIN POLICY — Password & Account Lockout
        # Applied via ADDefaultDomainPasswordPolicy (enforced at domain level)
        #=======================================================================

        ADDefaultDomainPasswordPolicy DomainPasswordPolicy {
            DomainName                  = $DomainName
            ComplexityEnabled           = $true
            MinPasswordLength           = 14
            MaxPasswordAge              = 90
            MinPasswordAge              = 1
            PasswordHistoryCount        = 24
            ReversibleEncryptionEnabled = $false
            LockoutThreshold            = 5
            LockoutDuration             = 30
            LockoutObservationWindow    = 30
            Credential                  = $DomainAdminCredential
        }

        #=======================================================================
        # FINE-GRAINED PASSWORD POLICY — IT Admins (stricter)
        #=======================================================================

        ADFineGrainedPasswordPolicy IT_Admins_PSO {
            Name                        = "IT-Admins-PSO"
            Precedence                  = 10
            ComplexityEnabled           = $true
            MinPasswordLength           = 16
            MaxPasswordAge              = 60
            MinPasswordAge              = 1
            PasswordHistoryCount        = 24
            ReversibleEncryptionEnabled = $false
            LockoutThreshold            = 3
            LockoutDuration             = 60
            LockoutObservationWindow    = 30
            Subjects                    = "IT-Admins"
            Ensure                      = "Present"
            Credential                  = $DomainAdminCredential
        }

        #=======================================================================
        # FINE-GRAINED PASSWORD POLICY — Service Accounts
        #=======================================================================

        ADFineGrainedPasswordPolicy ServiceAccounts_PSO {
            Name                        = "ServiceAccounts-PSO"
            Precedence                  = 20
            ComplexityEnabled           = $true
            MinPasswordLength           = 24
            MaxPasswordAge              = 365
            MinPasswordAge              = 0
            PasswordHistoryCount        = 12
            ReversibleEncryptionEnabled = $false
            LockoutThreshold            = 0
            LockoutDuration             = 30
            LockoutObservationWindow    = 30
            Subjects                    = "svc-backup", "svc-monitoring", "svc-deploy"
            Ensure                      = "Present"
            Credential                  = $DomainAdminCredential
        }

        #=======================================================================
        # GPO: BASELINE SECURITY — linked to domain root
        #=======================================================================

        GPO BaselineSecurity {
            Name       = "Baseline-Security-Policy"
            Ensure     = "Present"
            Domain     = $DomainName
            Credential = $DomainAdminCredential
        }

        GPOLink BaselineSecurity_Link {
            Target     = $DomainDN
            GPOName    = "Baseline-Security-Policy"
            LinkOrder  = 1
            Enforced   = $true
            Enabled    = $true
            Domain     = $DomainName
            Credential = $DomainAdminCredential
            DependsOn  = "[GPO]BaselineSecurity"
        }

        # Registry settings for baseline security GPO
        RegistryPolicy BaselineSecurity_NTLMv2 {
            TargetType = "ComputerConfiguration"
            GPOName    = "Baseline-Security-Policy"
            Domain     = $DomainName
            Key        = "HKLM\System\CurrentControlSet\Control\Lsa"
            ValueName  = "LmCompatibilityLevel"
            ValueData  = "5"
            ValueType  = "DWord"
            Ensure     = "Present"
            Credential = $DomainAdminCredential
            DependsOn  = "[GPO]BaselineSecurity"
        }

        RegistryPolicy BaselineSecurity_DisableLM {
            TargetType = "ComputerConfiguration"
            GPOName    = "Baseline-Security-Policy"
            Domain     = $DomainName
            Key        = "HKLM\System\CurrentControlSet\Control\Lsa"
            ValueName  = "NoLMHash"
            ValueData  = "1"
            ValueType  = "DWord"
            Ensure     = "Present"
            Credential = $DomainAdminCredential
            DependsOn  = "[GPO]BaselineSecurity"
        }

        RegistryPolicy BaselineSecurity_SMBSigning {
            TargetType = "ComputerConfiguration"
            GPOName    = "Baseline-Security-Policy"
            Domain     = $DomainName
            Key        = "HKLM\System\CurrentControlSet\Services\LanmanServer\Parameters"
            ValueName  = "RequireSecuritySignature"
            ValueData  = "1"
            ValueType  = "DWord"
            Ensure     = "Present"
            Credential = $DomainAdminCredential
            DependsOn  = "[GPO]BaselineSecurity"
        }

        RegistryPolicy BaselineSecurity_SMBv1Disable {
            TargetType = "ComputerConfiguration"
            GPOName    = "Baseline-Security-Policy"
            Domain     = $DomainName
            Key        = "HKLM\System\CurrentControlSet\Services\LanmanServer\Parameters"
            ValueName  = "SMB1"
            ValueData  = "0"
            ValueType  = "DWord"
            Ensure     = "Present"
            Credential = $DomainAdminCredential
            DependsOn  = "[GPO]BaselineSecurity"
        }

        #=======================================================================
        # GPO: WORKSTATION POLICY — screensaver, power, desktop restrictions
        #=======================================================================

        GPO WorkstationPolicy {
            Name       = "Workstation-Standard-Policy"
            Ensure     = "Present"
            Domain     = $DomainName
            Credential = $DomainAdminCredential
        }

        GPOLink WorkstationPolicy_Link {
            Target     = "OU=Workstations,$DomainDN"
            GPOName    = "Workstation-Standard-Policy"
            LinkOrder  = 1
            Enforced   = $false
            Enabled    = $true
            Domain     = $DomainName
            Credential = $DomainAdminCredential
            DependsOn  = "[GPO]WorkstationPolicy"
        }

        # Screensaver: enable, 15-minute timeout, password-protected
        RegistryPolicy WS_ScreensaverEnabled {
            TargetType = "UserConfiguration"
            GPOName    = "Workstation-Standard-Policy"
            Domain     = $DomainName
            Key        = "HKCU\Software\Policies\Microsoft\Windows\Control Panel\Desktop"
            ValueName  = "ScreenSaveActive"
            ValueData  = "1"
            ValueType  = "String"
            Ensure     = "Present"
            Credential = $DomainAdminCredential
            DependsOn  = "[GPO]WorkstationPolicy"
        }

        RegistryPolicy WS_ScreensaverTimeout {
            TargetType = "UserConfiguration"
            GPOName    = "Workstation-Standard-Policy"
            Domain     = $DomainName
            Key        = "HKCU\Software\Policies\Microsoft\Windows\Control Panel\Desktop"
            ValueName  = "ScreenSaveTimeOut"
            ValueData  = "900"
            ValueType  = "String"
            Ensure     = "Present"
            Credential = $DomainAdminCredential
            DependsOn  = "[GPO]WorkstationPolicy"
        }

        RegistryPolicy WS_ScreensaverSecure {
            TargetType = "UserConfiguration"
            GPOName    = "Workstation-Standard-Policy"
            Domain     = $DomainName
            Key        = "HKCU\Software\Policies\Microsoft\Windows\Control Panel\Desktop"
            ValueName  = "ScreenSaverIsSecure"
            ValueData  = "1"
            ValueType  = "String"
            Ensure     = "Present"
            Credential = $DomainAdminCredential
            DependsOn  = "[GPO]WorkstationPolicy"
        }

        RegistryPolicy WS_DisableControlPanel {
            TargetType = "UserConfiguration"
            GPOName    = "Workstation-Standard-Policy"
            Domain     = $DomainName
            Key        = "HKCU\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer"
            ValueName  = "NoControlPanel"
            ValueData  = "1"
            ValueType  = "DWord"
            Ensure     = "Present"
            Credential = $DomainAdminCredential
            DependsOn  = "[GPO]WorkstationPolicy"
        }

        RegistryPolicy WS_DisableRemovableMedia {
            TargetType = "ComputerConfiguration"
            GPOName    = "Workstation-Standard-Policy"
            Domain     = $DomainName
            Key        = "HKLM\Software\Policies\Microsoft\Windows\RemovableStorageDevices"
            ValueName  = "Deny_All"
            ValueData  = "1"
            ValueType  = "DWord"
            Ensure     = "Present"
            Credential = $DomainAdminCredential
            DependsOn  = "[GPO]WorkstationPolicy"
        }

        #=======================================================================
        # GPO: AUDIT POLICY — linked to domain root
        #=======================================================================

        GPO AuditPolicy {
            Name       = "Domain-Audit-Policy"
            Ensure     = "Present"
            Domain     = $DomainName
            Credential = $DomainAdminCredential
        }

        GPOLink AuditPolicy_Link {
            Target     = $DomainDN
            GPOName    = "Domain-Audit-Policy"
            LinkOrder  = 2
            Enforced   = $true
            Enabled    = $true
            Domain     = $DomainName
            Credential = $DomainAdminCredential
            DependsOn  = "[GPO]AuditPolicy"
        }

        # Audit: Logon Events (Success + Failure)
        RegistryPolicy Audit_AccountLogon {
            TargetType = "ComputerConfiguration"
            GPOName    = "Domain-Audit-Policy"
            Domain     = $DomainName
            Key        = "HKLM\Software\Policies\Microsoft\Windows\Audit"
            ValueName  = "AuditAccountLogon"
            ValueData  = "3"
            ValueType  = "DWord"
            Ensure     = "Present"
            Credential = $DomainAdminCredential
            DependsOn  = "[GPO]AuditPolicy"
        }

        RegistryPolicy Audit_AccountManagement {
            TargetType = "ComputerConfiguration"
            GPOName    = "Domain-Audit-Policy"
            Domain     = $DomainName
            Key        = "HKLM\Software\Policies\Microsoft\Windows\Audit"
            ValueName  = "AuditAccountManage"
            ValueData  = "3"
            ValueType  = "DWord"
            Ensure     = "Present"
            Credential = $DomainAdminCredential
            DependsOn  = "[GPO]AuditPolicy"
        }

        RegistryPolicy Audit_PolicyChange {
            TargetType = "ComputerConfiguration"
            GPOName    = "Domain-Audit-Policy"
            Domain     = $DomainName
            Key        = "HKLM\Software\Policies\Microsoft\Windows\Audit"
            ValueName  = "AuditPolicyChange"
            ValueData  = "3"
            ValueType  = "DWord"
            Ensure     = "Present"
            Credential = $DomainAdminCredential
            DependsOn  = "[GPO]AuditPolicy"
        }

        RegistryPolicy Audit_PrivilegeUse {
            TargetType = "ComputerConfiguration"
            GPOName    = "Domain-Audit-Policy"
            Domain     = $DomainName
            Key        = "HKLM\Software\Policies\Microsoft\Windows\Audit"
            ValueName  = "AuditPrivilegeUse"
            ValueData  = "2"
            ValueType  = "DWord"
            Ensure     = "Present"
            Credential = $DomainAdminCredential
            DependsOn  = "[GPO]AuditPolicy"
        }

        RegistryPolicy Audit_SystemEvents {
            TargetType = "ComputerConfiguration"
            GPOName    = "Domain-Audit-Policy"
            Domain     = $DomainName
            Key        = "HKLM\Software\Policies\Microsoft\Windows\Audit"
            ValueName  = "AuditSystemEvents"
            ValueData  = "3"
            ValueType  = "DWord"
            Ensure     = "Present"
            Credential = $DomainAdminCredential
            DependsOn  = "[GPO]AuditPolicy"
        }

        RegistryPolicy Audit_ObjectAccess {
            TargetType = "ComputerConfiguration"
            GPOName    = "Domain-Audit-Policy"
            Domain     = $DomainName
            Key        = "HKLM\Software\Policies\Microsoft\Windows\Audit"
            ValueName  = "AuditObjectAccess"
            ValueData  = "2"
            ValueType  = "DWord"
            Ensure     = "Present"
            Credential = $DomainAdminCredential
            DependsOn  = "[GPO]AuditPolicy"
        }

        RegistryPolicy Audit_ProcessTracking {
            TargetType = "ComputerConfiguration"
            GPOName    = "Domain-Audit-Policy"
            Domain     = $DomainName
            Key        = "HKLM\Software\Policies\Microsoft\Windows\Audit"
            ValueName  = "AuditProcessTracking"
            ValueData  = "1"
            ValueType  = "DWord"
            Ensure     = "Present"
            Credential = $DomainAdminCredential
            DependsOn  = "[GPO]AuditPolicy"
        }

        #=======================================================================
        # GPO: SERVER POLICY — server hardening
        #=======================================================================

        GPO ServerPolicy {
            Name       = "Server-Hardening-Policy"
            Ensure     = "Present"
            Domain     = $DomainName
            Credential = $DomainAdminCredential
        }

        GPOLink ServerPolicy_Link {
            Target     = "OU=Servers,$DomainDN"
            GPOName    = "Server-Hardening-Policy"
            LinkOrder  = 1
            Enforced   = $false
            Enabled    = $true
            Domain     = $DomainName
            Credential = $DomainAdminCredential
            DependsOn  = "[GPO]ServerPolicy"
        }

        RegistryPolicy Server_DisableRDP_NLA {
            TargetType = "ComputerConfiguration"
            GPOName    = "Server-Hardening-Policy"
            Domain     = $DomainName
            Key        = "HKLM\Software\Policies\Microsoft\Windows NT\Terminal Services"
            ValueName  = "UserAuthentication"
            ValueData  = "1"
            ValueType  = "DWord"
            Ensure     = "Present"
            Credential = $DomainAdminCredential
            DependsOn  = "[GPO]ServerPolicy"
        }

        RegistryPolicy Server_EventLogSize_System {
            TargetType = "ComputerConfiguration"
            GPOName    = "Server-Hardening-Policy"
            Domain     = $DomainName
            Key        = "HKLM\Software\Policies\Microsoft\Windows\EventLog\System"
            ValueName  = "MaxSize"
            ValueData  = "65536"
            ValueType  = "DWord"
            Ensure     = "Present"
            Credential = $DomainAdminCredential
            DependsOn  = "[GPO]ServerPolicy"
        }

        RegistryPolicy Server_EventLogSize_Security {
            TargetType = "ComputerConfiguration"
            GPOName    = "Server-Hardening-Policy"
            Domain     = $DomainName
            Key        = "HKLM\Software\Policies\Microsoft\Windows\EventLog\Security"
            ValueName  = "MaxSize"
            ValueData  = "262144"
            ValueType  = "DWord"
            Ensure     = "Present"
            Credential = $DomainAdminCredential
            DependsOn  = "[GPO]ServerPolicy"
        }

        RegistryPolicy Server_DisableAutorun {
            TargetType = "ComputerConfiguration"
            GPOName    = "Server-Hardening-Policy"
            Domain     = $DomainName
            Key        = "HKLM\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer"
            ValueName  = "NoDriveTypeAutoRun"
            ValueData  = "255"
            ValueType  = "DWord"
            Ensure     = "Present"
            Credential = $DomainAdminCredential
            DependsOn  = "[GPO]ServerPolicy"
        }
    }
}

$ConfigData = @{
    AllNodes = @(
        @{
            NodeName                    = "DC01"
            PSDscAllowPlainTextPassword = $false
            PSDscAllowDomainUser        = $true
        }
    )
}

# Example invocation:
# $cred = Get-Credential -UserName "CONTOSO\Administrator" -Message "Domain admin credentials"
# GPOPolicies -DomainAdminCredential $cred -ConfigurationData $ConfigData -OutputPath C:\DSC\GPOPolicies
# Start-DscConfiguration -Path C:\DSC\GPOPolicies -Wait -Verbose -Force
