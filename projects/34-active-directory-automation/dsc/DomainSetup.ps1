# DomainSetup.ps1
# PowerShell DSC Configuration for Active Directory Domain Controller setup
# Configures: AD DS, DNS, RSAT, Domain, OU Structure, Sites, and base settings
#
# Usage:
#   $cred = Get-Credential
#   . .\DomainSetup.ps1
#   DomainController -DomainAdminCredential $cred -OutputPath C:\DSC\DomainSetup
#   Start-DscConfiguration -Path C:\DSC\DomainSetup -Wait -Verbose -Force

Configuration DomainController {
    param(
        [Parameter(Mandatory)]
        [PSCredential]$DomainAdminCredential,

        [string]$DomainName            = "corp.contoso.local",
        [string]$DomainNetBIOSName     = "CONTOSO",
        [string]$DatabasePath          = "C:\Windows\NTDS",
        [string]$LogPath               = "C:\Windows\NTDS",
        [string]$SysvolPath            = "C:\Windows\SYSVOL",
        [string]$SiteName              = "HQ-Site",
        [string]$SiteSubnet            = "192.168.10.0/24"
    )

    Import-DscResource -ModuleName PSDesiredStateConfiguration
    Import-DscResource -ModuleName ActiveDirectoryDsc
    Import-DscResource -ModuleName NetworkingDsc
    Import-DscResource -ModuleName ComputerManagementDsc

    Node $AllNodes.NodeName {

        #-----------------------------------------------------------------------
        # Local Configuration Manager settings
        #-----------------------------------------------------------------------
        LocalConfigurationManager {
            RebootNodeIfNeeded   = $true
            ActionAfterReboot    = "ContinueConfiguration"
            ConfigurationMode    = "ApplyAndAutoCorrect"
            RefreshMode          = "Push"
        }

        #-----------------------------------------------------------------------
        # Windows Features
        #-----------------------------------------------------------------------
        WindowsFeature ADDS {
            Name   = "AD-Domain-Services"
            Ensure = "Present"
        }

        WindowsFeature DNS {
            Name      = "DNS"
            Ensure    = "Present"
            DependsOn = "[WindowsFeature]ADDS"
        }

        WindowsFeature RSAT_ADDS {
            Name      = "RSAT-ADDS"
            Ensure    = "Present"
            DependsOn = "[WindowsFeature]ADDS"
        }

        WindowsFeature RSAT_AD_Tools {
            Name      = "RSAT-AD-Tools"
            Ensure    = "Present"
            DependsOn = "[WindowsFeature]ADDS"
        }

        WindowsFeature RSAT_DNS {
            Name      = "RSAT-DNS-Server"
            Ensure    = "Present"
            DependsOn = "[WindowsFeature]DNS"
        }

        WindowsFeature RSAT_GPMC {
            Name      = "GPMC"
            Ensure    = "Present"
            DependsOn = "[WindowsFeature]ADDS"
        }

        WindowsFeature DFSNamespace {
            Name      = "FS-DFS-Namespace"
            Ensure    = "Present"
            DependsOn = "[WindowsFeature]ADDS"
        }

        WindowsFeature DFSReplication {
            Name      = "FS-DFS-Replication"
            Ensure    = "Present"
            DependsOn = "[WindowsFeature]ADDS"
        }

        #-----------------------------------------------------------------------
        # Network adapter static IP (assumes single NIC named "Ethernet")
        #-----------------------------------------------------------------------
        NetIPAddress StaticIP {
            InterfaceAlias = "Ethernet"
            IPAddress      = $Node.IPAddress
            PrefixLength   = 24
            AddressFamily  = "IPv4"
        }

        DnsServerAddress SetDNS {
            InterfaceAlias = "Ethernet"
            AddressFamily  = "IPv4"
            Address        = "127.0.0.1"
            DependsOn      = "[NetIPAddress]StaticIP"
        }

        #-----------------------------------------------------------------------
        # Domain creation
        #-----------------------------------------------------------------------
        ADDomain CreateDomain {
            DomainName                    = $DomainName
            DomainNetBIOSName             = $DomainNetBIOSName
            Credential                    = $DomainAdminCredential
            SafemodeAdministratorPassword = $DomainAdminCredential
            DatabasePath                  = $DatabasePath
            LogPath                       = $LogPath
            SysvolPath                    = $SysvolPath
            ForestMode                    = "WinThreshold"
            DomainMode                    = "WinThreshold"
            DependsOn                     = "[WindowsFeature]ADDS", "[DnsServerAddress]SetDNS"
        }

        WaitForADDomain WaitForDomain {
            DomainName           = $DomainName
            Credential           = $DomainAdminCredential
            RestartCount         = 2
            WaitTimeout          = 600
            WaitForValidCredentials = $true
            DependsOn            = "[ADDomain]CreateDomain"
        }

        #-----------------------------------------------------------------------
        # AD Sites and Services
        #-----------------------------------------------------------------------
        ADReplicationSite HQSite {
            Name      = $SiteName
            Ensure    = "Present"
            DependsOn = "[WaitForADDomain]WaitForDomain"
        }

        ADReplicationSubnet HQSubnet {
            Name        = $SiteSubnet
            Site        = $SiteName
            Description = "HQ LAN subnet"
            DependsOn   = "[ADReplicationSite]HQSite"
        }

        ADReplicationSiteLink DefaultLink {
            Name                          = "DEFAULTIPSITELINK"
            SitesIncluded                 = $SiteName
            Cost                          = 100
            ReplicationFrequencyInMinutes = 15
            OptionChangeNotification      = $true
            DependsOn                     = "[ADReplicationSite]HQSite"
        }

        #-----------------------------------------------------------------------
        # Top-level Organizational Units
        #-----------------------------------------------------------------------
        ADOrganizationalUnit OU_IT {
            Name        = "IT"
            Path        = "DC=corp,DC=contoso,DC=local"
            Description = "Information Technology department"
            Ensure      = "Present"
            DependsOn   = "[WaitForADDomain]WaitForDomain"
        }

        ADOrganizationalUnit OU_HR {
            Name        = "HR"
            Path        = "DC=corp,DC=contoso,DC=local"
            Description = "Human Resources department"
            Ensure      = "Present"
            DependsOn   = "[WaitForADDomain]WaitForDomain"
        }

        ADOrganizationalUnit OU_Finance {
            Name        = "Finance"
            Path        = "DC=corp,DC=contoso,DC=local"
            Description = "Finance department"
            Ensure      = "Present"
            DependsOn   = "[WaitForADDomain]WaitForDomain"
        }

        ADOrganizationalUnit OU_Operations {
            Name        = "Operations"
            Path        = "DC=corp,DC=contoso,DC=local"
            Description = "Operations department"
            Ensure      = "Present"
            DependsOn   = "[WaitForADDomain]WaitForDomain"
        }

        ADOrganizationalUnit OU_ServiceAccounts {
            Name        = "ServiceAccounts"
            Path        = "DC=corp,DC=contoso,DC=local"
            Description = "Managed and standard service accounts"
            Ensure      = "Present"
            DependsOn   = "[WaitForADDomain]WaitForDomain"
        }

        ADOrganizationalUnit OU_Servers {
            Name        = "Servers"
            Path        = "DC=corp,DC=contoso,DC=local"
            Description = "Server computer objects"
            Ensure      = "Present"
            DependsOn   = "[WaitForADDomain]WaitForDomain"
        }

        ADOrganizationalUnit OU_Workstations {
            Name        = "Workstations"
            Path        = "DC=corp,DC=contoso,DC=local"
            Description = "Workstation computer objects"
            Ensure      = "Present"
            DependsOn   = "[WaitForADDomain]WaitForDomain"
        }

        ADOrganizationalUnit OU_Security {
            Name        = "Security"
            Path        = "DC=corp,DC=contoso,DC=local"
            Description = "Security groups and distribution lists"
            Ensure      = "Present"
            DependsOn   = "[WaitForADDomain]WaitForDomain"
        }

        #-----------------------------------------------------------------------
        # Sub-OUs under IT
        #-----------------------------------------------------------------------
        ADOrganizationalUnit OU_IT_Admins {
            Name        = "Admins"
            Path        = "OU=IT,DC=corp,DC=contoso,DC=local"
            Description = "IT Administrators"
            Ensure      = "Present"
            DependsOn   = "[ADOrganizationalUnit]OU_IT"
        }

        ADOrganizationalUnit OU_IT_HelpDesk {
            Name        = "Help-Desk"
            Path        = "OU=IT,DC=corp,DC=contoso,DC=local"
            Description = "Help Desk technicians"
            Ensure      = "Present"
            DependsOn   = "[ADOrganizationalUnit]OU_IT"
        }

        ADOrganizationalUnit OU_IT_DevOps {
            Name        = "DevOps"
            Path        = "OU=IT,DC=corp,DC=contoso,DC=local"
            Description = "DevOps and automation engineers"
            Ensure      = "Present"
            DependsOn   = "[ADOrganizationalUnit]OU_IT"
        }

        #-----------------------------------------------------------------------
        # Sub-OUs under Servers
        #-----------------------------------------------------------------------
        ADOrganizationalUnit OU_Servers_App {
            Name        = "AppServers"
            Path        = "OU=Servers,DC=corp,DC=contoso,DC=local"
            Description = "Application servers"
            Ensure      = "Present"
            DependsOn   = "[ADOrganizationalUnit]OU_Servers"
        }

        ADOrganizationalUnit OU_Servers_Web {
            Name        = "WebServers"
            Path        = "OU=Servers,DC=corp,DC=contoso,DC=local"
            Description = "Web/IIS servers"
            Ensure      = "Present"
            DependsOn   = "[ADOrganizationalUnit]OU_Servers"
        }

        ADOrganizationalUnit OU_Servers_DB {
            Name        = "DBServers"
            Path        = "OU=Servers,DC=corp,DC=contoso,DC=local"
            Description = "Database servers"
            Ensure      = "Present"
            DependsOn   = "[ADOrganizationalUnit]OU_Servers"
        }

        ADOrganizationalUnit OU_Servers_File {
            Name        = "FileServers"
            Path        = "OU=Servers,DC=corp,DC=contoso,DC=local"
            Description = "File and print servers"
            Ensure      = "Present"
            DependsOn   = "[ADOrganizationalUnit]OU_Servers"
        }

        #-----------------------------------------------------------------------
        # AD Recycle Bin
        #-----------------------------------------------------------------------
        ADOptionalFeature RecycleBin {
            FeatureName                       = "Recycle Bin Feature"
            EnterpriseAdministratorCredential = $DomainAdminCredential
            ForestFQDN                        = $DomainName
            DependsOn                         = "[WaitForADDomain]WaitForDomain"
        }

        #-----------------------------------------------------------------------
        # Default Domain Password Policy
        #-----------------------------------------------------------------------
        ADDefaultDomainPasswordPolicy PasswordPolicy {
            DomainName                  = $DomainName
            ComplexityEnabled           = $true
            MinPasswordLength           = 12
            MaxPasswordAge              = 90
            MinPasswordAge              = 1
            PasswordHistoryCount        = 24
            ReversibleEncryptionEnabled = $false
            LockoutThreshold            = 5
            LockoutDuration             = 30
            LockoutObservationWindow    = 30
            DependsOn                   = "[WaitForADDomain]WaitForDomain"
        }

        #-----------------------------------------------------------------------
        # KDS Root Key (required for gMSA accounts)
        #-----------------------------------------------------------------------
        ADKDSKey KDSKey {
            Ensure           = "Present"
            EffectiveTime    = "1/1/1970 00:00:00"
            AllowUnsafeEffectiveTime = $true
            DependsOn        = "[WaitForADDomain]WaitForDomain"
        }
    }
}

# Configuration data — update NodeName and IPAddress per environment
$ConfigData = @{
    AllNodes = @(
        @{
            NodeName                    = "DC01"
            IPAddress                   = "192.168.10.10"
            PSDscAllowPlainTextPassword = $false
            PSDscAllowDomainUser        = $true
        }
    )
}

# Example invocation (comment out in production; use a deployment wrapper)
# $cred = Get-Credential -UserName "Administrator" -Message "Enter domain admin password"
# DomainController -DomainAdminCredential $cred -ConfigurationData $ConfigData -OutputPath "C:\DSC\DomainSetup"
# Start-DscConfiguration -Path "C:\DSC\DomainSetup" -Wait -Verbose -Force
