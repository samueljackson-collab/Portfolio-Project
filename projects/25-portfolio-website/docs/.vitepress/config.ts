import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'Sam Jackson - Enterprise Portfolio',
  description: 'Technical portfolio showcasing 25 enterprise-grade projects across Infrastructure, AI/ML, Security, and Emerging Technologies',

  head: [
    ['meta', { name: 'author', content: 'Sam Jackson' }],
    ['meta', { name: 'keywords', content: 'DevOps, Cloud Architecture, AWS, Kubernetes, Machine Learning, Cybersecurity, Portfolio' }]
  ],

  themeConfig: {
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Projects', link: '/projects/01-aws-infrastructure' },
      { text: 'Wiki.js Guide', link: '/wikijs' },
      {
        text: 'Categories',
        items: [
          { text: 'Infrastructure & DevOps', link: '/projects/01-aws-infrastructure' },
          { text: 'AI/ML & Data', link: '/projects/05-streaming' },
          { text: 'Security & Blockchain', link: '/projects/11-iot' },
          { text: 'Emerging Tech', link: '/projects/16-data-lake' },
          { text: 'Enterprise Systems', link: '/projects/21-quantum-crypto' }
        ]
      },
      { text: 'GitHub', link: 'https://github.com/samueljackson-collab/Portfolio-Project' }
    ],

    sidebar: [
      {
        text: '🏗️ Infrastructure & DevOps',
        collapsed: false,
        items: [
          { text: 'Project 1: AWS Infrastructure', link: '/projects/01-aws-infrastructure' },
          { text: 'Project 2: Database Migration', link: '/projects/02-database-migration' },
          { text: 'Project 3: Kubernetes CI/CD', link: '/projects/03-kubernetes-cicd' },
          { text: 'Project 4: DevSecOps Pipeline', link: '/projects/04-devsecops' }
        ]
      },
      {
        text: '🤖 AI/ML & Data Engineering',
        collapsed: false,
        items: [
          { text: 'Project 5: Real-time Streaming', link: '/projects/05-streaming' },
          { text: 'Project 6: MLOps Platform', link: '/projects/06-mlops' },
          { text: 'Project 7: Serverless Processing', link: '/projects/07-serverless' },
          { text: 'Project 8: AI Chatbot', link: '/projects/08-ai-chatbot' },
          { text: 'Project 9: Disaster Recovery', link: '/projects/09-disaster-recovery' },
          { text: 'Project 10: Blockchain Contracts', link: '/projects/10-blockchain' }
        ]
      },
      {
        text: '🔐 Security & Blockchain',
        collapsed: false,
        items: [
          { text: 'Project 11: IoT Analytics', link: '/projects/11-iot' },
          { text: 'Project 12: Quantum Computing', link: '/projects/12-quantum' },
          { text: 'Project 13: Cybersecurity SOAR', link: '/projects/13-cybersecurity' },
          { text: 'Project 14: Edge AI Inference', link: '/projects/14-edge-ai' },
          { text: 'Project 15: Real-time Collaboration', link: '/projects/15-collaboration' }
        ]
      },
      {
        text: '🚀 Emerging Technologies',
        collapsed: false,
        items: [
          { text: 'Project 16: Data Lake Analytics', link: '/projects/16-data-lake' },
          { text: 'Project 17: Multi-Cloud Mesh', link: '/projects/17-service-mesh' },
          { text: 'Project 18: GPU Computing', link: '/projects/18-gpu-computing' },
          { text: 'Project 19: K8s Operators', link: '/projects/19-k8s-operators' },
          { text: 'Project 20: Blockchain Oracle', link: '/projects/20-oracle' }
        ]
      },
      {
        text: '🏢 Enterprise Systems',
        collapsed: false,
        items: [
          { text: 'Project 21: Quantum-Safe Crypto', link: '/projects/21-quantum-crypto' },
          { text: 'Project 22: Autonomous DevOps', link: '/projects/22-autonomous-devops' },
          { text: 'Project 23: Monitoring Stack', link: '/projects/23-monitoring' },
          { text: 'Project 24: Report Generator', link: '/projects/24-report-generator' },
          { text: 'Project 25: Portfolio Website', link: '/projects/25-portfolio-website' }
        ]
      },
      {
        text: '📚 Guides & Resources',
        items: [
          { text: 'Wiki.js Setup Guide', link: '/wikijs' }
        ]
      }
    ],

    socialLinks: [
      { icon: 'github', link: 'https://github.com/samueljackson-collab' },
      { icon: 'linkedin', link: 'https://www.linkedin.com/in/sams-jackson' }
    ],

    footer: {
      message: 'Enterprise Technical Portfolio',
      copyright: 'Copyright © 2024 Sam Jackson'
    },

    search: {
      provider: 'local'
    },

    editLink: {
      pattern: 'https://github.com/samueljackson-collab/Portfolio-Project/edit/main/projects/25-portfolio-website/docs/:path',
      text: 'Edit this page on GitHub'
    }
  },

  markdown: {
    theme: {
      light: 'github-light',
      dark: 'github-dark'
    },
    lineNumbers: true
  }
})
