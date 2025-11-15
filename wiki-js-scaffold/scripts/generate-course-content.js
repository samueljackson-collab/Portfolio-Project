#!/usr/bin/env node
/**
 * Generate Complete Course Content Structure
 * Creates all 32 lessons for the GitHub Fundamentals course
 */

const fs = require('fs').promises;
const fsSync = require('fs');
const path = require('path');

const courseLessons = {
  '02-git-fundamentals': [
    { num: '01', title: 'Repository Basics', topics: ['init', 'clone', 'repository structure'] },
    { num: '02', title: 'Staging and Committing', topics: ['git add', 'git commit', 'staging area'] },
    { num: '03', title: 'Viewing History', topics: ['git log', 'git diff', 'commit history'] },
    { num: '04', title: 'Branching Fundamentals', topics: ['git branch', 'git checkout', 'branch strategy'] },
    { num: '05', title: 'Merging Changes', topics: ['git merge', 'merge conflicts', 'fast-forward'] },
    { num: '06', title: 'Remote Repositories', topics: ['git remote', 'git fetch', 'git pull'] },
    { num: '07', title: 'Pushing Changes', topics: ['git push', 'upstream branches', 'force push'] },
    { num: '08', title: 'Undoing Changes', topics: ['git reset', 'git revert', 'git restore'] }
  ],
  '03-documentation': [
    { num: '01', title: 'README Best Practices', topics: ['project description', 'installation', 'usage examples'] },
    { num: '02', title: 'Gitignore Files', topics: ['ignore patterns', 'common files', 'templates'] },
    { num: '03', title: 'Licenses and Contributing', topics: ['open source licenses', 'CONTRIBUTING.md', 'CODE_OF_CONDUCT'] }
  ],
  '04-real-world-projects': [
    { num: '01', title: 'Portfolio Setup', topics: ['github.io', 'pages', 'custom domain'] },
    { num: '02', title: 'Project Structure', topics: ['file organization', 'best practices', 'templates'] },
    { num: '03', title: 'Collaboration Workflow', topics: ['forking', 'pull requests', 'code review'] },
    { num: '04', title: 'Project Management', topics: ['issues', 'milestones', 'project boards'] },
    { num: '05', title: 'Deployment Basics', topics: ['GitHub Pages', 'Netlify', 'Vercel'] }
  ],
  '05-github-platform': [
    { num: '01', title: 'Issues and Discussions', topics: ['creating issues', 'labels', 'discussions'] },
    { num: '02', title: 'Pull Requests', topics: ['creating PRs', 'review process', 'merging'] },
    { num: '03', title: 'GitHub Actions', topics: ['CI/CD', 'workflows', 'automation'] },
    { num: '04', title: 'Security Features', topics: ['Dependabot', 'security advisories', 'secrets'] },
    { num: '05', title: 'Advanced GitHub', topics: ['wikis', 'releases', 'insights'] }
  ],
  '06-advanced-topics': [
    { num: '01', title: 'Git Rebase and History', topics: ['interactive rebase', 'squashing', 'history rewriting'] },
    { num: '02', title: 'Advanced Workflows', topics: ['Git Flow', 'trunk-based development', 'monorepos'] }
  ],
  '07-next-steps': [
    { num: '01', title: 'Contributing to Open Source', topics: ['finding projects', 'first contribution', 'best practices'] },
    { num: '02', title: 'Career Development', topics: ['portfolio building', 'interview prep', 'networking'] },
    { num: '03', title: 'Continuing Education', topics: ['resources', 'communities', 'advanced topics'] }
  ]
};

function generateLesson(section, lesson) {
  const { num, title, topics } = lesson;
  const topicList = topics.map(t => `- ${t}`).join('\n');

  return `# ${title}

## 📚 Overview

This lesson covers ${title.toLowerCase()}, an essential skill for effective Git and GitHub usage.

## 🎯 Learning Objectives

By the end of this lesson, you will be able to:

${topics.map(t => `- ✅ Understand and use ${t}`).join('\n')}
- ✅ Apply best practices
- ✅ Avoid common pitfalls
- ✅ Troubleshoot issues

## 📖 Core Concepts

### Key Topics

${topicList}

### Why This Matters

Understanding ${title.toLowerCase()} is crucial for:
- Professional development workflows
- Team collaboration
- Project management
- Career advancement

## 💻 Practical Examples

### Basic Usage

\`\`\`bash
# Example commands will be demonstrated
# Follow along and practice these examples
\`\`\`

### Real-World Scenario

A typical use case for ${title.toLowerCase()}:

1. Identify the need
2. Plan your approach
3. Execute the commands
4. Verify the results
5. Commit your changes

## 🔍 Deep Dive

### Understanding the Details

${topics.map(t => `**${t}**: Detailed explanation of ${t} and its applications.`).join('\n\n')}

### Common Use Cases

- Team collaboration scenarios
- Individual project workflows
- Open source contributions
- Production deployments

## 🛠️ Hands-On Practice

### Exercise 1: Basic Operations

Try these commands:

\`\`\`bash
# Practice exercise placeholder
# Actual commands specific to this topic
\`\`\`

### Exercise 2: Real-World Application

Apply what you've learned:

1. Set up your environment
2. Follow the steps
3. Observe the results
4. Reflect on the outcome

## 💡 Best Practices

### Do's ✅
- Follow established conventions
- Test before committing
- Document your changes
- Communicate with your team

### Don'ts ❌
- Skip testing
- Force push without coordination
- Ignore warnings
- Work directly on main branch

## 🐛 Troubleshooting

### Common Issues

**Problem**: Common error message
**Solution**: How to resolve it

**Problem**: Another common issue
**Solution**: Step-by-step resolution

### Getting Help

- Check official documentation
- Search Stack Overflow
- Ask in GitHub Discussions
- Review course materials

## 🎯 Key Takeaways

- ${topics[0]} is fundamental to Git workflows
- Practice regularly to build muscle memory
- Understand the why, not just the how
- Apply these skills to real projects

## ✅ Knowledge Check

Before moving on, ensure you can:

- [ ] Explain the concept in your own words
- [ ] Execute basic operations confidently
- [ ] Recognize when to use these skills
- [ ] Troubleshoot common issues

## 🚀 Next Steps

Continue your learning journey with the next lesson or practice these concepts in your own projects.

---

**Questions or feedback?** Open a discussion on GitHub!
`;
}

async function generateAllLessons() {
  console.log('🚀 Generating course content...\n');

  const contentDir = path.join(__dirname, '../content');
  let totalCreated = 0;

  for (const [section, lessons] of Object.entries(courseLessons)) {
    const sectionDir = path.join(contentDir, section);

    // Create directory if it doesn't exist
    if (!fsSync.existsSync(sectionDir)) {
      await fs.mkdir(sectionDir, { recursive: true });
    }

    console.log(`📁 Section: ${section}`);

    for (const lesson of lessons) {
      const filename = `${lesson.num}-${lesson.title.toLowerCase().replace(/\s+/g, '-')}.md`;
      const filepath = path.join(sectionDir, filename);

      // Skip if file already exists
      if (fsSync.existsSync(filepath)) {
        console.log(`  ⏭️  Skipped: ${filename} (already exists)`);
        continue;
      }

      const content = generateLesson(section, lesson);
      await fs.writeFile(filepath, content, 'utf8');
      console.log(`  ✅ Created: ${filename}`);
      totalCreated++;
    }

    console.log('');
  }

  console.log(`🎉 Course generation complete!`);
  console.log(`   Created: ${totalCreated} new lessons`);
  console.log(`   Total sections: ${Object.keys(courseLessons).length}`);
}

// Run if called directly
if (require.main === module) {
  generateAllLessons().catch(error => {
    console.error('❌ Error:', error.message);
    process.exit(1);
  });
}

module.exports = { generateAllLessons };
