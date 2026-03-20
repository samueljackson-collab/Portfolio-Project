# UsersAndGroups.ps1
# PowerShell DSC Configuration for AD users, security groups, and memberships
# Creates 20 sample users across IT, HR, Finance, Operations OUs
# Creates 5 security groups with membership assignments
#
# Prerequisites: DomainSetup.ps1 must have run successfully
#
# Usage:
#   $cred = Get-Credential
#   . .\UsersAndGroups.ps1
#   UsersAndGroups -DomainAdminCredential $cred -OutputPath C:\DSC\UsersAndGroups
#   Start-DscConfiguration -Path C:\DSC\UsersAndGroups -Wait -Verbose -Force

Configuration UsersAndGroups {
    param(
        [Parameter(Mandatory)]
        [PSCredential]$DomainAdminCredential,

        [Parameter(Mandatory)]
        [PSCredential]$DefaultUserPassword,

        [string]$DomainName    = "corp.contoso.local",
        [string]$DomainDN      = "DC=corp,DC=contoso,DC=local"
    )

    Import-DscResource -ModuleName PSDesiredStateConfiguration
    Import-DscResource -ModuleName ActiveDirectoryDsc

    Node $AllNodes.NodeName {

        #=======================================================================
        # SECURITY GROUPS
        #=======================================================================

        ADGroup IT_Admins {
            GroupName        = "IT-Admins"
            GroupScope       = "Global"
            Category         = "Security"
            Path             = "OU=IT,$DomainDN"
            Description      = "IT Administrators with elevated domain rights"
            Ensure           = "Present"
            Credential       = $DomainAdminCredential
        }

        ADGroup HelpDesk {
            GroupName        = "Help-Desk"
            GroupScope       = "Global"
            Category         = "Security"
            Path             = "OU=IT,$DomainDN"
            Description      = "Level 1 and Level 2 Help Desk staff"
            Ensure           = "Present"
            Credential       = $DomainAdminCredential
        }

        ADGroup HR_Users {
            GroupName        = "HR-Users"
            GroupScope       = "Global"
            Category         = "Security"
            Path             = "OU=HR,$DomainDN"
            Description      = "Human Resources department users"
            Ensure           = "Present"
            Credential       = $DomainAdminCredential
        }

        ADGroup Finance_Users {
            GroupName        = "Finance-Users"
            GroupScope       = "Global"
            Category         = "Security"
            Path             = "OU=Finance,$DomainDN"
            Description      = "Finance department users"
            Ensure           = "Present"
            Credential       = $DomainAdminCredential
        }

        ADGroup DevOps_Team {
            GroupName        = "DevOps-Team"
            GroupScope       = "Global"
            Category         = "Security"
            Path             = "OU=IT,$DomainDN"
            Description      = "DevOps engineers with CI/CD and infrastructure access"
            Ensure           = "Present"
            Credential       = $DomainAdminCredential
        }

        ADGroup Operations_Users {
            GroupName        = "Operations-Users"
            GroupScope       = "Global"
            Category         = "Security"
            Path             = "OU=Operations,$DomainDN"
            Description      = "Operations department users"
            Ensure           = "Present"
            Credential       = $DomainAdminCredential
        }

        ADGroup VPN_Users {
            GroupName        = "VPN-Users"
            GroupScope       = "Universal"
            Category         = "Security"
            Path             = "OU=Security,$DomainDN"
            Description      = "Users permitted to connect via VPN"
            Ensure           = "Present"
            Credential       = $DomainAdminCredential
        }

        ADGroup Remote_Desktop_Users {
            GroupName        = "Remote-Desktop-Users"
            GroupScope       = "Universal"
            Category         = "Security"
            Path             = "OU=Security,$DomainDN"
            Description      = "Users with remote desktop access to servers"
            Ensure           = "Present"
            Credential       = $DomainAdminCredential
        }

        #=======================================================================
        # IT DEPARTMENT USERS (OU=Admins,OU=IT)
        #=======================================================================

        ADUser jsmith {
            UserName              = "jsmith"
            GivenName             = "John"
            Surname               = "Smith"
            DisplayName           = "John Smith"
            UserPrincipalName     = "jsmith@corp.contoso.local"
            Path                  = "OU=Admins,OU=IT,$DomainDN"
            Department            = "IT"
            Title                 = "Senior Systems Administrator"
            EmailAddress          = "jsmith@contoso.local"
            OfficePhone           = "555-0101"
            Company               = "Contoso Corporation"
            Enabled               = $true
            Password              = $DefaultUserPassword
            PasswordNeverExpires  = $false
            ChangePasswordAtLogon = $true
            Ensure                = "Present"
            Credential            = $DomainAdminCredential
        }

        ADUser mmartinez {
            UserName              = "mmartinez"
            GivenName             = "Maria"
            Surname               = "Martinez"
            DisplayName           = "Maria Martinez"
            UserPrincipalName     = "mmartinez@corp.contoso.local"
            Path                  = "OU=Admins,OU=IT,$DomainDN"
            Department            = "IT"
            Title                 = "Network Administrator"
            EmailAddress          = "mmartinez@contoso.local"
            OfficePhone           = "555-0102"
            Company               = "Contoso Corporation"
            Enabled               = $true
            Password              = $DefaultUserPassword
            PasswordNeverExpires  = $false
            ChangePasswordAtLogon = $true
            Ensure                = "Present"
            Credential            = $DomainAdminCredential
        }

        ADUser rchen {
            UserName              = "rchen"
            GivenName             = "Robert"
            Surname               = "Chen"
            DisplayName           = "Robert Chen"
            UserPrincipalName     = "rchen@corp.contoso.local"
            Path                  = "OU=DevOps,OU=IT,$DomainDN"
            Department            = "IT"
            Title                 = "DevOps Engineer"
            EmailAddress          = "rchen@contoso.local"
            OfficePhone           = "555-0103"
            Company               = "Contoso Corporation"
            Enabled               = $true
            Password              = $DefaultUserPassword
            PasswordNeverExpires  = $false
            ChangePasswordAtLogon = $true
            Ensure                = "Present"
            Credential            = $DomainAdminCredential
        }

        ADUser apatel {
            UserName              = "apatel"
            GivenName             = "Anita"
            Surname               = "Patel"
            DisplayName           = "Anita Patel"
            UserPrincipalName     = "apatel@corp.contoso.local"
            Path                  = "OU=DevOps,OU=IT,$DomainDN"
            Department            = "IT"
            Title                 = "DevOps Engineer"
            EmailAddress          = "apatel@contoso.local"
            OfficePhone           = "555-0104"
            Company               = "Contoso Corporation"
            Enabled               = $true
            Password              = $DefaultUserPassword
            PasswordNeverExpires  = $false
            ChangePasswordAtLogon = $true
            Ensure                = "Present"
            Credential            = $DomainAdminCredential
        }

        # Help Desk users
        ADUser twilson {
            UserName              = "twilson"
            GivenName             = "Tyler"
            Surname               = "Wilson"
            DisplayName           = "Tyler Wilson"
            UserPrincipalName     = "twilson@corp.contoso.local"
            Path                  = "OU=Help-Desk,OU=IT,$DomainDN"
            Department            = "IT"
            Title                 = "Help Desk Technician II"
            EmailAddress          = "twilson@contoso.local"
            OfficePhone           = "555-0105"
            Company               = "Contoso Corporation"
            Enabled               = $true
            Password              = $DefaultUserPassword
            PasswordNeverExpires  = $false
            ChangePasswordAtLogon = $true
            Ensure                = "Present"
            Credential            = $DomainAdminCredential
        }

        ADUser lnguyen {
            UserName              = "lnguyen"
            GivenName             = "Linh"
            Surname               = "Nguyen"
            DisplayName           = "Linh Nguyen"
            UserPrincipalName     = "lnguyen@corp.contoso.local"
            Path                  = "OU=Help-Desk,OU=IT,$DomainDN"
            Department            = "IT"
            Title                 = "Help Desk Technician I"
            EmailAddress          = "lnguyen@contoso.local"
            OfficePhone           = "555-0106"
            Company               = "Contoso Corporation"
            Enabled               = $true
            Password              = $DefaultUserPassword
            PasswordNeverExpires  = $false
            ChangePasswordAtLogon = $true
            Ensure                = "Present"
            Credential            = $DomainAdminCredential
        }

        #=======================================================================
        # HR DEPARTMENT USERS (OU=HR)
        #=======================================================================

        ADUser adavis {
            UserName              = "adavis"
            GivenName             = "Amanda"
            Surname               = "Davis"
            DisplayName           = "Amanda Davis"
            UserPrincipalName     = "adavis@corp.contoso.local"
            Path                  = "OU=HR,$DomainDN"
            Department            = "Human Resources"
            Title                 = "HR Manager"
            EmailAddress          = "adavis@contoso.local"
            OfficePhone           = "555-0201"
            Company               = "Contoso Corporation"
            Enabled               = $true
            Password              = $DefaultUserPassword
            PasswordNeverExpires  = $false
            ChangePasswordAtLogon = $true
            Ensure                = "Present"
            Credential            = $DomainAdminCredential
        }

        ADUser kjohnson {
            UserName              = "kjohnson"
            GivenName             = "Karen"
            Surname               = "Johnson"
            DisplayName           = "Karen Johnson"
            UserPrincipalName     = "kjohnson@corp.contoso.local"
            Path                  = "OU=HR,$DomainDN"
            Department            = "Human Resources"
            Title                 = "HR Specialist"
            EmailAddress          = "kjohnson@contoso.local"
            OfficePhone           = "555-0202"
            Company               = "Contoso Corporation"
            Enabled               = $true
            Password              = $DefaultUserPassword
            PasswordNeverExpires  = $false
            ChangePasswordAtLogon = $true
            Ensure                = "Present"
            Credential            = $DomainAdminCredential
        }

        ADUser bthompson {
            UserName              = "bthompson"
            GivenName             = "Brian"
            Surname               = "Thompson"
            DisplayName           = "Brian Thompson"
            UserPrincipalName     = "bthompson@corp.contoso.local"
            Path                  = "OU=HR,$DomainDN"
            Department            = "Human Resources"
            Title                 = "Recruiter"
            EmailAddress          = "bthompson@contoso.local"
            OfficePhone           = "555-0203"
            Company               = "Contoso Corporation"
            Enabled               = $true
            Password              = $DefaultUserPassword
            PasswordNeverExpires  = $false
            ChangePasswordAtLogon = $true
            Ensure                = "Present"
            Credential            = $DomainAdminCredential
        }

        ADUser slee {
            UserName              = "slee"
            GivenName             = "Sophia"
            Surname               = "Lee"
            DisplayName           = "Sophia Lee"
            UserPrincipalName     = "slee@corp.contoso.local"
            Path                  = "OU=HR,$DomainDN"
            Department            = "Human Resources"
            Title                 = "HR Coordinator"
            EmailAddress          = "slee@contoso.local"
            OfficePhone           = "555-0204"
            Company               = "Contoso Corporation"
            Enabled               = $true
            Password              = $DefaultUserPassword
            PasswordNeverExpires  = $false
            ChangePasswordAtLogon = $true
            Ensure                = "Present"
            Credential            = $DomainAdminCredential
        }

        #=======================================================================
        # FINANCE DEPARTMENT USERS (OU=Finance)
        #=======================================================================

        ADUser mwhite {
            UserName              = "mwhite"
            GivenName             = "Michael"
            Surname               = "White"
            DisplayName           = "Michael White"
            UserPrincipalName     = "mwhite@corp.contoso.local"
            Path                  = "OU=Finance,$DomainDN"
            Department            = "Finance"
            Title                 = "Finance Director"
            EmailAddress          = "mwhite@contoso.local"
            OfficePhone           = "555-0301"
            Company               = "Contoso Corporation"
            Enabled               = $true
            Password              = $DefaultUserPassword
            PasswordNeverExpires  = $false
            ChangePasswordAtLogon = $true
            Ensure                = "Present"
            Credential            = $DomainAdminCredential
        }

        ADUser jrobinson {
            UserName              = "jrobinson"
            GivenName             = "Jennifer"
            Surname               = "Robinson"
            DisplayName           = "Jennifer Robinson"
            UserPrincipalName     = "jrobinson@corp.contoso.local"
            Path                  = "OU=Finance,$DomainDN"
            Department            = "Finance"
            Title                 = "Senior Accountant"
            EmailAddress          = "jrobinson@contoso.local"
            OfficePhone           = "555-0302"
            Company               = "Contoso Corporation"
            Enabled               = $true
            Password              = $DefaultUserPassword
            PasswordNeverExpires  = $false
            ChangePasswordAtLogon = $true
            Ensure                = "Present"
            Credential            = $DomainAdminCredential
        }

        ADUser dgarcia {
            UserName              = "dgarcia"
            GivenName             = "David"
            Surname               = "Garcia"
            DisplayName           = "David Garcia"
            UserPrincipalName     = "dgarcia@corp.contoso.local"
            Path                  = "OU=Finance,$DomainDN"
            Department            = "Finance"
            Title                 = "Financial Analyst"
            EmailAddress          = "dgarcia@contoso.local"
            OfficePhone           = "555-0303"
            Company               = "Contoso Corporation"
            Enabled               = $true
            Password              = $DefaultUserPassword
            PasswordNeverExpires  = $false
            ChangePasswordAtLogon = $true
            Ensure                = "Present"
            Credential            = $DomainAdminCredential
        }

        ADUser cwalker {
            UserName              = "cwalker"
            GivenName             = "Christine"
            Surname               = "Walker"
            DisplayName           = "Christine Walker"
            UserPrincipalName     = "cwalker@corp.contoso.local"
            Path                  = "OU=Finance,$DomainDN"
            Department            = "Finance"
            Title                 = "Accounts Payable Specialist"
            EmailAddress          = "cwalker@contoso.local"
            OfficePhone           = "555-0304"
            Company               = "Contoso Corporation"
            Enabled               = $true
            Password              = $DefaultUserPassword
            PasswordNeverExpires  = $false
            ChangePasswordAtLogon = $true
            Ensure                = "Present"
            Credential            = $DomainAdminCredential
        }

        #=======================================================================
        # OPERATIONS DEPARTMENT USERS (OU=Operations)
        #=======================================================================

        ADUser phall {
            UserName              = "phall"
            GivenName             = "Patrick"
            Surname               = "Hall"
            DisplayName           = "Patrick Hall"
            UserPrincipalName     = "phall@corp.contoso.local"
            Path                  = "OU=Operations,$DomainDN"
            Department            = "Operations"
            Title                 = "Operations Manager"
            EmailAddress          = "phall@contoso.local"
            OfficePhone           = "555-0401"
            Company               = "Contoso Corporation"
            Enabled               = $true
            Password              = $DefaultUserPassword
            PasswordNeverExpires  = $false
            ChangePasswordAtLogon = $true
            Ensure                = "Present"
            Credential            = $DomainAdminCredential
        }

        ADUser nyoung {
            UserName              = "nyoung"
            GivenName             = "Nancy"
            Surname               = "Young"
            DisplayName           = "Nancy Young"
            UserPrincipalName     = "nyoung@corp.contoso.local"
            Path                  = "OU=Operations,$DomainDN"
            Department            = "Operations"
            Title                 = "Operations Analyst"
            EmailAddress          = "nyoung@contoso.local"
            OfficePhone           = "555-0402"
            Company               = "Contoso Corporation"
            Enabled               = $true
            Password              = $DefaultUserPassword
            PasswordNeverExpires  = $false
            ChangePasswordAtLogon = $true
            Ensure                = "Present"
            Credential            = $DomainAdminCredential
        }

        ADUser skorea {
            UserName              = "skorea"
            GivenName             = "Samuel"
            Surname               = "Korea"
            DisplayName           = "Samuel Korea"
            UserPrincipalName     = "skorea@corp.contoso.local"
            Path                  = "OU=Operations,$DomainDN"
            Department            = "Operations"
            Title                 = "Logistics Coordinator"
            EmailAddress          = "skorea@contoso.local"
            OfficePhone           = "555-0403"
            Company               = "Contoso Corporation"
            Enabled               = $true
            Password              = $DefaultUserPassword
            PasswordNeverExpires  = $false
            ChangePasswordAtLogon = $true
            Ensure                = "Present"
            Credential            = $DomainAdminCredential
        }

        ADUser emorris {
            UserName              = "emorris"
            GivenName             = "Elena"
            Surname               = "Morris"
            DisplayName           = "Elena Morris"
            UserPrincipalName     = "emorris@corp.contoso.local"
            Path                  = "OU=Operations,$DomainDN"
            Department            = "Operations"
            Title                 = "Supply Chain Analyst"
            EmailAddress          = "emorris@contoso.local"
            OfficePhone           = "555-0404"
            Company               = "Contoso Corporation"
            Enabled               = $true
            Password              = $DefaultUserPassword
            PasswordNeverExpires  = $false
            ChangePasswordAtLogon = $true
            Ensure                = "Present"
            Credential            = $DomainAdminCredential
        }

        ADUser fanderson {
            UserName              = "fanderson"
            GivenName             = "Frank"
            Surname               = "Anderson"
            DisplayName           = "Frank Anderson"
            UserPrincipalName     = "fanderson@corp.contoso.local"
            Path                  = "OU=Operations,$DomainDN"
            Department            = "Operations"
            Title                 = "Warehouse Supervisor"
            EmailAddress          = "fanderson@contoso.local"
            OfficePhone           = "555-0405"
            Company               = "Contoso Corporation"
            Enabled               = $true
            Password              = $DefaultUserPassword
            PasswordNeverExpires  = $false
            ChangePasswordAtLogon = $true
            Ensure                = "Present"
            Credential            = $DomainAdminCredential
        }

        ADUser vtaylor {
            UserName              = "vtaylor"
            GivenName             = "Victoria"
            Surname               = "Taylor"
            DisplayName           = "Victoria Taylor"
            UserPrincipalName     = "vtaylor@corp.contoso.local"
            Path                  = "OU=Operations,$DomainDN"
            Department            = "Operations"
            Title                 = "Operations Coordinator"
            EmailAddress          = "vtaylor@contoso.local"
            OfficePhone           = "555-0406"
            Company               = "Contoso Corporation"
            Enabled               = $true
            Password              = $DefaultUserPassword
            PasswordNeverExpires  = $false
            ChangePasswordAtLogon = $true
            Ensure                = "Present"
            Credential            = $DomainAdminCredential
        }

        #=======================================================================
        # SERVICE ACCOUNTS (OU=ServiceAccounts)
        #=======================================================================

        ADUser svc_backup {
            UserName              = "svc-backup"
            GivenName             = "Backup"
            Surname               = "Service"
            DisplayName           = "SVC Backup Agent"
            UserPrincipalName     = "svc-backup@corp.contoso.local"
            Path                  = "OU=ServiceAccounts,$DomainDN"
            Department            = "IT"
            Description           = "Veeam/Windows Server Backup service account"
            Enabled               = $true
            Password              = $DefaultUserPassword
            PasswordNeverExpires  = $true
            ChangePasswordAtLogon = $false
            Ensure                = "Present"
            Credential            = $DomainAdminCredential
        }

        ADUser svc_monitoring {
            UserName              = "svc-monitoring"
            GivenName             = "Monitoring"
            Surname               = "Service"
            DisplayName           = "SVC Monitoring Agent"
            UserPrincipalName     = "svc-monitoring@corp.contoso.local"
            Path                  = "OU=ServiceAccounts,$DomainDN"
            Department            = "IT"
            Description           = "Prometheus / PRTG read-only monitoring service account"
            Enabled               = $true
            Password              = $DefaultUserPassword
            PasswordNeverExpires  = $true
            ChangePasswordAtLogon = $false
            Ensure                = "Present"
            Credential            = $DomainAdminCredential
        }

        ADUser svc_deploy {
            UserName              = "svc-deploy"
            GivenName             = "Deploy"
            Surname               = "Service"
            DisplayName           = "SVC Deployment Agent"
            UserPrincipalName     = "svc-deploy@corp.contoso.local"
            Path                  = "OU=ServiceAccounts,$DomainDN"
            Department            = "IT"
            Description           = "Ansible / CI-CD deployment service account"
            Enabled               = $true
            Password              = $DefaultUserPassword
            PasswordNeverExpires  = $true
            ChangePasswordAtLogon = $false
            Ensure                = "Present"
            Credential            = $DomainAdminCredential
        }

        #=======================================================================
        # GROUP MEMBERSHIP ASSIGNMENTS
        #=======================================================================

        ADGroupMember IT_Admins_Members {
            GroupName        = "IT-Admins"
            MembersToInclude = @("jsmith", "mmartinez")
            Credential       = $DomainAdminCredential
            DependsOn        = "[ADGroup]IT_Admins", "[ADUser]jsmith", "[ADUser]mmartinez"
        }

        ADGroupMember HelpDesk_Members {
            GroupName        = "Help-Desk"
            MembersToInclude = @("twilson", "lnguyen")
            Credential       = $DomainAdminCredential
            DependsOn        = "[ADGroup]HelpDesk", "[ADUser]twilson", "[ADUser]lnguyen"
        }

        ADGroupMember DevOps_Members {
            GroupName        = "DevOps-Team"
            MembersToInclude = @("rchen", "apatel")
            Credential       = $DomainAdminCredential
            DependsOn        = "[ADGroup]DevOps_Team", "[ADUser]rchen", "[ADUser]apatel"
        }

        ADGroupMember HR_Members {
            GroupName        = "HR-Users"
            MembersToInclude = @("adavis", "kjohnson", "bthompson", "slee")
            Credential       = $DomainAdminCredential
            DependsOn        = "[ADGroup]HR_Users", "[ADUser]adavis", "[ADUser]kjohnson", "[ADUser]bthompson", "[ADUser]slee"
        }

        ADGroupMember Finance_Members {
            GroupName        = "Finance-Users"
            MembersToInclude = @("mwhite", "jrobinson", "dgarcia", "cwalker")
            Credential       = $DomainAdminCredential
            DependsOn        = "[ADGroup]Finance_Users", "[ADUser]mwhite", "[ADUser]jrobinson", "[ADUser]dgarcia", "[ADUser]cwalker"
        }

        ADGroupMember Operations_Members {
            GroupName        = "Operations-Users"
            MembersToInclude = @("phall", "nyoung", "skorea", "emorris", "fanderson", "vtaylor")
            Credential       = $DomainAdminCredential
            DependsOn        = "[ADGroup]Operations_Users", "[ADUser]phall", "[ADUser]nyoung", "[ADUser]skorea", "[ADUser]emorris", "[ADUser]fanderson", "[ADUser]vtaylor"
        }

        ADGroupMember VPN_Members {
            GroupName        = "VPN-Users"
            MembersToInclude = @("jsmith", "mmartinez", "rchen", "apatel", "mwhite", "adavis")
            Credential       = $DomainAdminCredential
            DependsOn        = "[ADGroup]VPN_Users"
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
# $domainCred = Get-Credential -UserName "CONTOSO\Administrator" -Message "Domain admin"
# $userPass   = Get-Credential -UserName "NewUser" -Message "Default user password (username field ignored)"
# UsersAndGroups -DomainAdminCredential $domainCred -DefaultUserPassword $userPass `
#                -ConfigurationData $ConfigData -OutputPath C:\DSC\UsersAndGroups
# Start-DscConfiguration -Path C:\DSC\UsersAndGroups -Wait -Verbose -Force
