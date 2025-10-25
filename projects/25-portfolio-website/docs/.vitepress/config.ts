import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'Portfolio Documentation',
  description: 'Enterprise portfolio with 25 projects',
  themeConfig: {
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Wiki.js Guide', link: '/wikijs' }
    ],
    sidebar: [
      {
        text: 'Projects',
        items: [
          { text: 'Project 1 - AWS Infrastructure', link: '/projects/aws-infrastructure' },
          { text: 'Project 6 - MLOps Platform', link: '/projects/mlops' }
        ]
      }
    ]
  }
})
