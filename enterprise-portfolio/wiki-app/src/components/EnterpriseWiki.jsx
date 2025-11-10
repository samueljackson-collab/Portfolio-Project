import React, { useState } from 'react';
import { Book, Server, GitBranch, TestTube, Network, ChevronRight, FileText, Code, Shield, Activity, CheckCircle } from 'lucide-react';

const EnterpriseWiki = () => {
  const [selectedRole, setSelectedRole] = useState('sde');
  const [selectedWeek, setSelectedWeek] = useState(1);

  const roles = {
    sde: {
      title: 'System Development Engineer',
      icon: Server,
      color: 'blue',
      description: 'Infrastructure, automation, and system reliability',
      weeks: 8
    },
    devops: {
      title: 'DevOps Engineer',
      icon: GitBranch,
      color: 'green',
      description: 'CI/CD, GitOps, and deployment automation',
      weeks: 6
    },
    qa: {
      title: 'QA Engineer III',
      icon: TestTube,
      color: 'purple',
      description: 'Testing strategy, automation, and quality assurance',
      weeks: 6
    },
    architect: {
      title: 'Solutions Architect',
      icon: Network,
      color: 'orange',
      description: 'System design, architecture patterns, and trade-offs',
      weeks: 8
    }
  };

  // Color class mapping for Tailwind CSS
  const colorClasses = {
    blue: {
      bg: 'bg-blue-600',
      hover: 'hover:bg-blue-700',
      bgAlt: 'bg-blue-600'
    },
    green: {
      bg: 'bg-green-600',
      hover: 'hover:bg-green-700',
      bgAlt: 'bg-green-600'
    },
    purple: {
      bg: 'bg-purple-600',
      hover: 'hover:bg-purple-700',
      bgAlt: 'bg-purple-600'
    },
    orange: {
      bg: 'bg-orange-600',
      hover: 'hover:bg-orange-700',
      bgAlt: 'bg-orange-600'
    }
  };

  const roleContent = {
    sde: {
      overview: {
        responsibilities: [
          'Design and implement highly available infrastructure',
          'Automate infrastructure provisioning with Terraform',
          'Implement monitoring and observability solutions',
          'Ensure system reliability and performance',
          'Manage multi-region deployments'
        ],
        skills: [
          'Infrastructure as Code (Terraform, CloudFormation)',
          'Cloud Platforms (AWS, Azure, GCP)',
          'Container Orchestration (Kubernetes, ECS)',
          'Monitoring & Observability (Prometheus, Grafana)',
          'Scripting (Python, Bash, Go)'
        ]
      },
      weeks: [
        {
          number: 1,
          title: 'Infrastructure Foundations',
          topics: [
            'Terraform AWS Setup',
            'VPC Design & Implementation',
            'Multi-AZ Architecture',
            'Security Groups & NACLs'
          ],
          deliverables: [
            'Complete VPC infrastructure',
            'Bastion host setup',
            'Network diagram',
            'Security documentation'
          ]
        },
        {
          number: 2,
          title: 'Compute & Load Balancing',
          topics: [
            'EC2 Auto Scaling Groups',
            'Application Load Balancer',
            'Launch Templates',
            'Health Checks'
          ],
          deliverables: [
            'Auto-scaling configuration',
            'ALB with SSL',
            'Health check endpoints',
            'Scaling policies'
          ]
        },
        {
          number: 3,
          title: 'Database & Storage',
          topics: [
            'RDS PostgreSQL Multi-AZ',
            'ElastiCache Redis Cluster',
            'S3 Buckets & Policies',
            'Database Backups'
          ],
          deliverables: [
            'Production database',
            'Cache configuration',
            'Backup strategy',
            'Recovery procedures'
          ]
        },
        {
          number: 4,
          title: 'Container Orchestration',
          topics: [
            'EKS Cluster Setup',
            'Node Groups Configuration',
            'Pod Security Policies',
            'Network Policies'
          ],
          deliverables: [
            'Production EKS cluster',
            'RBAC configuration',
            'Network policies',
            'Security scanning'
          ]
        },
        {
          number: 5,
          title: 'Monitoring & Observability',
          topics: [
            'Prometheus Setup',
            'Grafana Dashboards',
            'AlertManager Configuration',
            'Log Aggregation (ELK)'
          ],
          deliverables: [
            'Complete monitoring stack',
            'Custom dashboards',
            'Alert rules',
            'Log retention policies'
          ]
        },
        {
          number: 6,
          title: 'Event-Driven Architecture',
          topics: [
            'SQS Queue Configuration',
            'SNS Topics & Subscriptions',
            'EventBridge Rules',
            'Lambda Functions'
          ],
          deliverables: [
            'Message queue setup',
            'Event processing',
            'Dead letter queues',
            'Monitoring integration'
          ]
        },
        {
          number: 7,
          title: 'Disaster Recovery',
          topics: [
            'Backup Automation',
            'Cross-Region Replication',
            'Failover Procedures',
            'DR Testing'
          ],
          deliverables: [
            'DR plan documentation',
            'Automated backups',
            'Failover runbooks',
            'Test results'
          ]
        },
        {
          number: 8,
          title: 'Security Hardening',
          topics: [
            'IAM Policies & Roles',
            'Secrets Management',
            'Security Scanning',
            'Compliance Auditing'
          ],
          deliverables: [
            'Security baseline',
            'Secrets rotation',
            'Audit reports',
            'Compliance documentation'
          ]
        }
      ]
    },
    devops: {
      overview: {
        responsibilities: [
          'Design and maintain CI/CD pipelines',
          'Implement GitOps workflows',
          'Automate deployment processes',
          'Manage configuration as code',
          'Ensure zero-downtime deployments'
        ],
        skills: [
          'CI/CD Tools (GitHub Actions, GitLab CI, Jenkins)',
          'GitOps (ArgoCD, Flux)',
          'Configuration Management (Ansible, Chef)',
          'Container Technologies (Docker, Kubernetes)',
          'Scripting & Automation'
        ]
      },
      weeks: [
        {
          number: 1,
          title: 'CI/CD Pipeline Setup',
          topics: [
            'GitHub Actions Workflows',
            'Multi-stage Pipelines',
            'Security Scanning',
            'Artifact Management'
          ],
          deliverables: [
            'Complete CI pipeline',
            'Security gates',
            'Test automation',
            'Build optimization'
          ]
        },
        {
          number: 2,
          title: 'GitOps Implementation',
          topics: [
            'ArgoCD Installation',
            'Application Manifests',
            'Automated Sync',
            'Rollback Strategies'
          ],
          deliverables: [
            'ArgoCD setup',
            'GitOps repository',
            'Sync policies',
            'Rollback procedures'
          ]
        },
        {
          number: 3,
          title: 'Configuration Management',
          topics: [
            'Ansible Playbooks',
            'Inventory Management',
            'Role Development',
            'Vault Integration'
          ],
          deliverables: [
            'Ansible repository',
            'Server configuration',
            'Secret management',
            'Deployment automation'
          ]
        },
        {
          number: 4,
          title: 'Container Registry',
          topics: [
            'Registry Setup',
            'Image Scanning',
            'Vulnerability Management',
            'Image Signing'
          ],
          deliverables: [
            'Container registry',
            'Scanning pipeline',
            'Security policies',
            'Image lifecycle'
          ]
        },
        {
          number: 5,
          title: 'Deployment Strategies',
          topics: [
            'Blue-Green Deployments',
            'Canary Releases',
            'Rolling Updates',
            'Feature Flags'
          ],
          deliverables: [
            'Deployment manifests',
            'Traffic management',
            'Rollback automation',
            'Feature flag system'
          ]
        },
        {
          number: 6,
          title: 'Pipeline Optimization',
          topics: [
            'Build Caching',
            'Parallel Execution',
            'Resource Optimization',
            'Cost Management'
          ],
          deliverables: [
            'Optimized pipelines',
            'Performance metrics',
            'Cost analysis',
            'Best practices guide'
          ]
        }
      ]
    },
    qa: {
      overview: {
        responsibilities: [
          'Design comprehensive test strategies',
          'Implement test automation frameworks',
          'Perform security and performance testing',
          'Establish quality gates',
          'Lead testing best practices'
        ],
        skills: [
          'Test Automation (Cypress, Playwright, Selenium)',
          'API Testing (Postman, REST Assured)',
          'Performance Testing (K6, JMeter)',
          'Security Testing (OWASP ZAP, Burp Suite)',
          'Test Strategy & Planning'
        ]
      },
      weeks: [
        {
          number: 1,
          title: 'Test Framework Setup',
          topics: [
            'Jest Configuration',
            'Cypress Setup',
            'Test Structure',
            'Code Coverage'
          ],
          deliverables: [
            'Unit test framework',
            'E2E test suite',
            'Coverage reports',
            'Testing guidelines'
          ]
        },
        {
          number: 2,
          title: 'API Testing',
          topics: [
            'REST API Testing',
            'GraphQL Testing',
            'Contract Testing',
            'Mock Services'
          ],
          deliverables: [
            'API test suite',
            'Contract tests',
            'Mock server setup',
            'Test data management'
          ]
        },
        {
          number: 3,
          title: 'E2E Testing',
          topics: [
            'User Flow Testing',
            'Cross-browser Testing',
            'Mobile Testing',
            'Visual Regression'
          ],
          deliverables: [
            'E2E test scenarios',
            'Browser matrix',
            'Visual tests',
            'Test reports'
          ]
        },
        {
          number: 4,
          title: 'Performance Testing',
          topics: [
            'Load Testing',
            'Stress Testing',
            'Spike Testing',
            'Endurance Testing'
          ],
          deliverables: [
            'Performance test suite',
            'Load profiles',
            'Performance benchmarks',
            'Optimization recommendations'
          ]
        },
        {
          number: 5,
          title: 'Security Testing',
          topics: [
            'OWASP Top 10',
            'Penetration Testing',
            'Vulnerability Scanning',
            'Security Reports'
          ],
          deliverables: [
            'Security test plan',
            'Vulnerability reports',
            'Remediation tracking',
            'Security baseline'
          ]
        },
        {
          number: 6,
          title: 'CI/CD Integration',
          topics: [
            'Automated Testing',
            'Quality Gates',
            'Test Reporting',
            'Failure Analysis'
          ],
          deliverables: [
            'CI test integration',
            'Quality metrics',
            'Automated reports',
            'Failure handling'
          ]
        }
      ]
    },
    architect: {
      overview: {
        responsibilities: [
          'Design scalable system architectures',
          'Make technology decisions',
          'Define architecture patterns',
          'Ensure security and compliance',
          'Lead technical reviews'
        ],
        skills: [
          'System Design & Architecture Patterns',
          'Cloud Architecture (AWS, Azure, Multi-cloud)',
          'Microservices & Event-driven Architecture',
          'Security & Compliance',
          'Technical Leadership'
        ]
      },
      weeks: [
        {
          number: 1,
          title: 'Architecture Fundamentals',
          topics: [
            'Design Principles',
            'Architecture Patterns',
            'Trade-off Analysis',
            'System Requirements'
          ],
          deliverables: [
            'Architecture principles',
            'Pattern catalog',
            'Decision framework',
            'Requirements template'
          ]
        },
        {
          number: 2,
          title: 'Microservices Design',
          topics: [
            'Service Boundaries',
            'API Gateway Patterns',
            'Service Mesh',
            'Data Management'
          ],
          deliverables: [
            'Service architecture',
            'API specifications',
            'Data flow diagrams',
            'Integration patterns'
          ]
        },
        {
          number: 3,
          title: 'Event-Driven Architecture',
          topics: [
            'Event Sourcing',
            'CQRS Pattern',
            'Message Brokers',
            'Event Choreography'
          ],
          deliverables: [
            'Event architecture',
            'Message schemas',
            'Event flows',
            'Consistency patterns'
          ]
        },
        {
          number: 4,
          title: 'Scalability Patterns',
          topics: [
            'Horizontal Scaling',
            'Caching Strategies',
            'Database Sharding',
            'CDN Integration'
          ],
          deliverables: [
            'Scaling strategy',
            'Cache architecture',
            'Database design',
            'Performance plan'
          ]
        },
        {
          number: 5,
          title: 'Security Architecture',
          topics: [
            'Zero Trust Security',
            'Identity & Access',
            'Data Encryption',
            'Compliance Framework'
          ],
          deliverables: [
            'Security architecture',
            'IAM design',
            'Encryption strategy',
            'Compliance checklist'
          ]
        },
        {
          number: 6,
          title: 'Resilience Patterns',
          topics: [
            'Circuit Breakers',
            'Retry Policies',
            'Bulkheads',
            'Chaos Engineering'
          ],
          deliverables: [
            'Resilience patterns',
            'Fault tolerance',
            'Recovery procedures',
            'Testing strategy'
          ]
        },
        {
          number: 7,
          title: 'Multi-Region Architecture',
          topics: [
            'Global Load Balancing',
            'Data Replication',
            'Disaster Recovery',
            'Latency Optimization'
          ],
          deliverables: [
            'Multi-region design',
            'Replication strategy',
            'DR plan',
            'Performance metrics'
          ]
        },
        {
          number: 8,
          title: 'Cost Optimization',
          topics: [
            'Resource Optimization',
            'Reserved Capacity',
            'Right-sizing',
            'Cost Monitoring'
          ],
          deliverables: [
            'Cost architecture',
            'Optimization plan',
            'Budget forecasts',
            'Cost dashboards'
          ]
        }
      ]
    }
  };

  const currentRole = roles[selectedRole];
  const currentContent = roleContent[selectedRole];
  const RoleIcon = currentRole.icon;
  const selectedWeekData = currentContent.weeks.find(w => w.number === selectedWeek);
  const currentColors = colorClasses[currentRole.color];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 mb-8 shadow-2xl">
          <div className="flex items-center gap-4 mb-4">
            <Book className="w-12 h-12 text-white" />
            <h1 className="text-4xl font-bold text-white">Enterprise Portfolio Wiki</h1>
          </div>
          <p className="text-blue-100 text-lg">Complete learning paths for all technical roles</p>
        </div>

        <div className="grid lg:grid-cols-4 gap-6">
          {/* Role Selector */}
          <div className="lg:col-span-1">
            <div className="bg-slate-800 rounded-xl p-6 shadow-xl sticky top-4">
              <h2 className="text-xl font-bold text-white mb-4">Select Role</h2>
              <div className="space-y-3">
                {Object.entries(roles).map(([key, role]) => {
                  const Icon = role.icon;
                  const roleColors = colorClasses[role.color];
                  return (
                    <button
                      key={key}
                      onClick={() => {
                        setSelectedRole(key);
                        setSelectedWeek(1);
                      }}
                      className={`w-full p-4 rounded-lg transition-all ${
                        selectedRole === key
                          ? `${roleColors.bg} text-white shadow-lg scale-105`
                          : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <Icon className="w-6 h-6" />
                        <div className="text-left">
                          <div className="font-semibold">{role.title}</div>
                          <div className="text-xs opacity-80">{role.weeks} weeks</div>
                        </div>
                      </div>
                    </button>
                  );
                })}
              </div>

              {/* Progress Indicator */}
              <div className="mt-6 pt-6 border-t border-slate-700">
                <h3 className="text-sm font-semibold text-slate-400 mb-3">Your Progress</h3>
                <div className="space-y-2">
                  <div className="flex justify-between text-xs text-slate-400">
                    <span>Week {selectedWeek} of {currentRole.weeks}</span>
                    <span>{Math.round((selectedWeek / currentRole.weeks) * 100)}%</span>
                  </div>
                  <div className="w-full bg-slate-700 rounded-full h-2">
                    <div
                      className={`${currentColors.bg} h-2 rounded-full transition-all`}
                      style={{ width: `${(selectedWeek / currentRole.weeks) * 100}%` }}
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3">
            {/* Role Overview */}
            <div className="bg-slate-800 rounded-xl p-6 mb-6 shadow-xl">
              <div className="flex items-center gap-4 mb-4">
                <div className={`p-3 ${currentColors.bg} rounded-lg`}>
                  <RoleIcon className="w-8 h-8 text-white" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-white">{currentRole.title}</h2>
                  <p className="text-slate-400">{currentRole.description}</p>
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-6 mt-6">
                <div>
                  <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                    <CheckCircle className="w-5 h-5 text-green-500" />
                    Key Responsibilities
                  </h3>
                  <ul className="space-y-2">
                    {currentContent.overview.responsibilities.map((resp) => (
                      <li key={resp} className="text-slate-300 text-sm flex items-start gap-2">
                        <ChevronRight className="w-4 h-4 text-blue-500 mt-1 flex-shrink-0" />
                        {resp}
                      </li>
                    ))}
                  </ul>
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                    <Code className="w-5 h-5 text-purple-500" />
                    Core Skills
                  </h3>
                  <ul className="space-y-2">
                    {currentContent.overview.skills.map((skill) => (
                      <li key={skill} className="text-slate-300 text-sm flex items-start gap-2">
                        <ChevronRight className="w-4 h-4 text-purple-500 mt-1 flex-shrink-0" />
                        {skill}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>

            {/* Week Navigation */}
            <div className="bg-slate-800 rounded-xl p-6 mb-6 shadow-xl">
              <h3 className="text-xl font-bold text-white mb-4">Learning Path Timeline</h3>
              <div className="flex gap-2 overflow-x-auto pb-2">
                {currentContent.weeks.map((week) => (
                  <button
                    key={week.number}
                    onClick={() => setSelectedWeek(week.number)}
                    className={`px-4 py-2 rounded-lg whitespace-nowrap transition-all ${
                      selectedWeek === week.number
                        ? `${currentColors.bg} text-white shadow-lg`
                        : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                    }`}
                  >
                    Week {week.number}
                  </button>
                ))}
              </div>
            </div>

            {/* Week Content */}
            {selectedWeekData && (
              <div className="bg-slate-800 rounded-xl p-6 shadow-xl">
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h3 className="text-2xl font-bold text-white">Week {selectedWeekData.number}: {selectedWeekData.title}</h3>
                    <p className="text-slate-400 mt-1">Duration: 5-7 days</p>
                  </div>
                  <div className={`px-4 py-2 ${currentColors.bg} rounded-lg`}>
                    <span className="text-white font-semibold">In Progress</span>
                  </div>
                </div>

                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                      <FileText className="w-5 h-5 text-blue-500" />
                      Topics Covered
                    </h4>
                    <ul className="space-y-2">
                      {selectedWeekData.topics.map((topic, idx) => (
                        <li key={topic} className="flex items-start gap-2">
                          <div className={`w-6 h-6 rounded-full ${currentColors.bg} flex items-center justify-center flex-shrink-0 mt-0.5`}>
                            <span className="text-white text-xs font-bold">{idx + 1}</span>
                          </div>
                          <span className="text-slate-300">{topic}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <h4 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                      <CheckCircle className="w-5 h-5 text-green-500" />
                      Deliverables
                    </h4>
                    <ul className="space-y-2">
                      {selectedWeekData.deliverables.map((deliverable) => (
                        <li key={deliverable} className="flex items-start gap-2">
                          <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                          <span className="text-slate-300">{deliverable}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="mt-6 pt-6 border-t border-slate-700 flex gap-4">
                  <button
                    className={`flex-1 py-3 px-6 ${currentColors.bg} ${currentColors.hover} text-white rounded-lg font-semibold transition-colors`}
                    disabled
                    title="Coming soon"
                  >
                    View Detailed Guide
                  </button>
                  <button
                    className="py-3 px-6 bg-slate-700 text-white rounded-lg font-semibold hover:bg-slate-600 transition-colors"
                    disabled
                    title="Coming soon"
                  >
                    Access Resources
                  </button>
                </div>
              </div>
            )}

            {/* Quick Links */}
            <div className="grid md:grid-cols-3 gap-4 mt-6">
              <button
                className="bg-slate-800 rounded-xl p-4 hover:bg-slate-700 transition-colors text-left"
                disabled
                title="Coming soon"
              >
                <Code className="w-8 h-8 text-blue-500 mb-2" />
                <h4 className="font-semibold text-white">Code Examples</h4>
                <p className="text-sm text-slate-400">Full implementation samples</p>
              </button>
              <button
                className="bg-slate-800 rounded-xl p-4 hover:bg-slate-700 transition-colors text-left"
                disabled
                title="Coming soon"
              >
                <Activity className="w-8 h-8 text-green-500 mb-2" />
                <h4 className="font-semibold text-white">Live Demos</h4>
                <p className="text-sm text-slate-400">Interactive tutorials</p>
              </button>
              <button
                className="bg-slate-800 rounded-xl p-4 hover:bg-slate-700 transition-colors text-left"
                disabled
                title="Coming soon"
              >
                <Shield className="w-8 h-8 text-purple-500 mb-2" />
                <h4 className="font-semibold text-white">Best Practices</h4>
                <p className="text-sm text-slate-400">Industry standards</p>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EnterpriseWiki;
