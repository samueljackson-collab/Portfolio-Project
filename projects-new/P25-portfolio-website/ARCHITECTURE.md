# Architecture

Stack: Next.js, Tailwind, CMS API (Contentful), Vercel deploy scripts.

Data/Control flow: Content updates pulled from CMS at build time, site built with incremental static regeneration, deployed to CDN with preview links.

Dependencies:
- Next.js, Tailwind, CMS API (Contentful), Vercel deploy scripts.
- Env/config: see README for required secrets and endpoints.
