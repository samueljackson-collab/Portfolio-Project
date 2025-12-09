# P25 – Portfolio Website

Static Next.js/React site with CMS-backed content, global CDN, and Lighthouse budgets.

## Quick start
- Stack: Next.js, Tailwind, CMS API (Contentful), Vercel deploy scripts.
- Flow: Content updates pulled from CMS at build time, site built with incremental static regeneration, deployed to CDN with preview links.
- Run: npm run lint then npm run test
- Operate: Purge CDN cache on content updates, rotate CMS tokens, and monitor uptime/LCP via synthetic checks.
