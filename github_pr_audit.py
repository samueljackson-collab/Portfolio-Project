#!/usr/bin/env python3
"""
GitHub PR Audit Tool
====================

Audits all open PRs across your GitHub repositories and generates
a comprehensive report with categorization and recommended actions.

Prerequisites:
    - GitHub CLI (gh) installed and authenticated
    - Python 3.7+

Usage:
    python github_pr_audit.py [--username USERNAME] [--output-dir DIR]

Output:
    - pr_audit_report.json  (machine-readable)
    - pr_audit_report.csv   (spreadsheet-friendly)
    - pr_audit_summary.md   (human-readable summary)
    - pr_resolution_plan.md (step-by-step action plan)
"""

import subprocess
import json
import csv
import os
import sys
from datetime import datetime, timezone
from collections import defaultdict
from typing import Dict, List, Optional, Tuple
import argparse

#===============================================================================
# Configuration
#===============================================================================

CATEGORY_PRIORITIES = {
    'MERGE': 1,    # Highest priority - quick wins
    'CLOSE': 2,    # Second - cleanup
    'REBASE': 3,   # Third - fix conflicts
    'UPDATE': 4,   # Fourth - address issues
    'REVIEW': 5,   # Fifth - assess
    'DRAFT': 6,    # Lowest - work in progress
}

CATEGORY_COLORS = {
    'MERGE': '🟢',
    'UPDATE': '🟡',
    'REBASE': '🔴',
    'CLOSE': '⚫',
    'REVIEW': '🔵',
    'DRAFT': '⚪',
}

#===============================================================================
# Helper Functions
#===============================================================================

def run_gh_command(args: List[str]) -> Optional[str]:
    """Run a GitHub CLI command and return output."""
    try:
        result = subprocess.run(
            ['gh'] + args,
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None

def check_dependencies() -> bool:
    """Check if required dependencies are installed."""
    # Check gh CLI
    if run_gh_command(['--version']) is None:
        print("❌ GitHub CLI (gh) is not installed.")
        print("   Install from: https://cli.github.com/")
        return False

    # Check authentication
    if run_gh_command(['auth', 'status']) is None:
        print("❌ GitHub CLI is not authenticated.")
        print("   Run: gh auth login")
        return False

    print("✅ All dependencies satisfied")
    return True

def get_username() -> Optional[str]:
    """Get the authenticated user's username."""
    result = run_gh_command(['api', 'user', '--jq', '.login'])
    return result

def get_repositories(username: str) -> List[str]:
    """Get all repositories for a user."""
    # Try user's own repos first
    result = run_gh_command([
        'repo', 'list', username,
        '--limit', '500',
        '--json', 'nameWithOwner',
        '--jq', '.[].nameWithOwner'
    ])

    if result:
        repos = [r.strip() for r in result.split('\n') if r.strip()]
        if repos:
            return repos

    # Fallback to repos user has access to
    result = run_gh_command([
        'api', 'user/repos',
        '--paginate',
        '--jq', '.[].full_name'
    ])

    if result:
        return [r.strip() for r in result.split('\n') if r.strip()]

    return []

def get_open_prs(repo: str) -> List[Dict]:
    """Get all open PRs for a repository."""
    result = run_gh_command([
        'pr', 'list',
        '--repo', repo,
        '--state', 'open',
        '--json', 'number,title,author,createdAt,isDraft,mergeable,reviewDecision,statusCheckRollup,url,headRefName,baseRefName,additions,deletions,changedFiles',
        '--limit', '500'
    ])

    if result:
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return []
    return []

def calculate_age_days(created_at: str) -> int:
    """Calculate the age of a PR in days."""
    try:
        created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        return (now - created).days
    except ValueError:
        return 0

def get_ci_status(status_checks: Optional[List]) -> str:
    """Determine overall CI status from status checks."""
    if not status_checks:
        return 'NONE'

    conclusions = [check.get('conclusion', 'PENDING') for check in status_checks]

    if all(c == 'SUCCESS' for c in conclusions if c):
        return 'SUCCESS'
    if any(c == 'FAILURE' for c in conclusions):
        return 'FAILURE'
    if any(c == 'ERROR' for c in conclusions):
        return 'ERROR'
    if any(c in ('PENDING', None, '') for c in conclusions):
        return 'PENDING'
    return 'UNKNOWN'

def categorize_pr(pr_data: Dict) -> Tuple[str, str]:
    """Categorize a PR and return (category, action_description)."""
    age_days = pr_data.get('age_days', 0)
    mergeable = pr_data.get('mergeable', 'UNKNOWN')
    ci_status = pr_data.get('ci_status', 'UNKNOWN')
    is_draft = pr_data.get('isDraft', False)
    review_decision = pr_data.get('reviewDecision', '')

    # Draft PRs
    if is_draft:
        return 'DRAFT', 'Draft PR - complete work or convert to ready for review'

    # Ready to merge
    if (review_decision == 'APPROVED' and
        ci_status == 'SUCCESS' and
        mergeable == 'MERGEABLE'):
        return 'MERGE', 'Ready to merge - approved, CI passing, no conflicts'

    # Has conflicts
    if mergeable == 'CONFLICTING':
        return 'REBASE', 'Has conflicts - rebase on main branch'

    # CI failing
    if ci_status in ('FAILURE', 'ERROR'):
        return 'UPDATE', 'CI failing - fix test failures or build errors'

    # Very old PRs (>90 days)
    if age_days > 90:
        return 'CLOSE', f'Stale ({age_days} days old) - review and close if obsolete'

    # Changes requested
    if review_decision == 'CHANGES_REQUESTED':
        return 'UPDATE', 'Changes requested - address review feedback'

    # Old PRs (>30 days)
    if age_days > 30:
        return 'REVIEW', f'Aging ({age_days} days) - assess and prioritize'

    # Needs review
    if review_decision in ('REVIEW_REQUIRED', '', None):
        return 'REVIEW', 'Awaiting review - request reviewers or self-review'

    return 'REVIEW', 'Needs assessment - review and decide next action'

def process_pr(pr: Dict, repo: str) -> Dict:
    """Process a single PR and enrich with computed fields."""
    age_days = calculate_age_days(pr.get('createdAt', ''))
    ci_status = get_ci_status(pr.get('statusCheckRollup'))

    pr_data = {
        'pr_number': pr.get('number'),
        'repository': repo,
        'title': pr.get('title', ''),
        'author': pr.get('author', {}).get('login', 'unknown'),
        'created_at': pr.get('createdAt', ''),
        'age_days': age_days,
        'isDraft': pr.get('isDraft', False),
        'mergeable': pr.get('mergeable', 'UNKNOWN'),
        'ci_status': ci_status,
        'reviewDecision': pr.get('reviewDecision', ''),
        'url': pr.get('url', ''),
        'head_branch': pr.get('headRefName', ''),
        'base_branch': pr.get('baseRefName', ''),
        'additions': pr.get('additions', 0),
        'deletions': pr.get('deletions', 0),
        'changed_files': pr.get('changedFiles', 0),
    }

    category, action = categorize_pr(pr_data)
    pr_data['category'] = category
    pr_data['action'] = action
    pr_data['priority'] = CATEGORY_PRIORITIES.get(category, 99)

    return pr_data

#===============================================================================
# Report Generation
#===============================================================================

def generate_json_report(prs: List[Dict], output_path: str):
    """Generate JSON report."""
    with open(output_path, 'w') as f:
        json.dump(prs, f, indent=2, default=str)
    print(f"📄 JSON report: {output_path}")

def generate_csv_report(prs: List[Dict], output_path: str):
    """Generate CSV report."""
    if not prs:
        return

    fieldnames = [
        'pr_number', 'repository', 'title', 'author', 'created_at',
        'age_days', 'category', 'action', 'isDraft', 'mergeable',
        'ci_status', 'reviewDecision', 'changed_files', 'url'
    ]

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(prs)

    print(f"📊 CSV report: {output_path}")

def generate_summary_report(prs: List[Dict], output_path: str, username: str):
    """Generate markdown summary report."""
    # Count by category
    by_category = defaultdict(list)
    for pr in prs:
        by_category[pr['category']].append(pr)

    # Count by repository
    by_repo = defaultdict(list)
    for pr in prs:
        by_repo[pr['repository']].append(pr)

    with open(output_path, 'w') as f:
        f.write("# GitHub PR Audit Report\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n")
        f.write(f"**User:** {username}  \n")
        f.write(f"**Total Open PRs:** {len(prs)}\n\n")
        f.write("---\n\n")

        # Summary table
        f.write("## Summary by Category\n\n")
        f.write("| Category | Count | % | Action Required |\n")
        f.write("|----------|-------|---|------------------|\n")

        for cat in ['MERGE', 'UPDATE', 'REBASE', 'CLOSE', 'REVIEW', 'DRAFT']:
            count = len(by_category.get(cat, []))
            pct = (count / len(prs) * 100) if prs else 0
            emoji = CATEGORY_COLORS.get(cat, '⚪')
            actions = {
                'MERGE': 'Merge immediately',
                'UPDATE': 'Fix issues, then merge',
                'REBASE': 'Resolve conflicts first',
                'CLOSE': 'Close if obsolete',
                'REVIEW': 'Assess and decide',
                'DRAFT': 'Complete or convert'
            }
            f.write(f"| {emoji} {cat} | {count} | {pct:.1f}% | {actions.get(cat, '')} |\n")

        f.write("\n---\n\n")

        # By repository
        f.write("## PRs by Repository\n\n")
        f.write("| Repository | Open PRs | Oldest (days) |\n")
        f.write("|------------|----------|---------------|\n")

        for repo in sorted(by_repo.keys(), key=lambda r: -len(by_repo[r])):
            repo_prs = by_repo[repo]
            oldest = max(pr['age_days'] for pr in repo_prs)
            f.write(f"| {repo} | {len(repo_prs)} | {oldest} |\n")

        f.write("\n---\n\n")

        # Quick wins (MERGE ready)
        if by_category['MERGE']:
            f.write("## 🟢 Quick Wins - Ready to Merge\n\n")
            f.write("These PRs are approved, passing CI, and have no conflicts:\n\n")
            f.write("| PR | Repository | Title | Age |\n")
            f.write("|----|------------|-------|-----|\n")
            for pr in sorted(by_category['MERGE'], key=lambda x: x['age_days'], reverse=True):
                f.write(f"| [#{pr['pr_number']}]({pr['url']}) | {pr['repository']} | {pr['title'][:50]}{'...' if len(pr['title']) > 50 else ''} | {pr['age_days']}d |\n")
            f.write("\n```bash\n# Merge all ready PRs:\n")
            for pr in by_category['MERGE']:
                f.write(f"gh pr merge {pr['pr_number']} --repo {pr['repository']} --merge --delete-branch\n")
            f.write("```\n\n")

        # Stale PRs
        if by_category['CLOSE']:
            f.write("## ⚫ Stale PRs - Review for Closure\n\n")
            f.write("These PRs are >90 days old and may be obsolete:\n\n")
            f.write("| PR | Repository | Title | Age | Author |\n")
            f.write("|----|------------|-------|-----|--------|\n")
            for pr in sorted(by_category['CLOSE'], key=lambda x: -x['age_days']):
                f.write(f"| [#{pr['pr_number']}]({pr['url']}) | {pr['repository']} | {pr['title'][:40]}{'...' if len(pr['title']) > 40 else ''} | {pr['age_days']}d | {pr['author']} |\n")
            f.write("\n")

        # Conflicts
        if by_category['REBASE']:
            f.write("## 🔴 PRs with Conflicts\n\n")
            f.write("These PRs need to be rebased on main:\n\n")
            f.write("| PR | Repository | Title | Branch |\n")
            f.write("|----|------------|-------|--------|\n")
            for pr in by_category['REBASE']:
                f.write(f"| [#{pr['pr_number']}]({pr['url']}) | {pr['repository']} | {pr['title'][:40]}{'...' if len(pr['title']) > 40 else ''} | {pr['head_branch']} |\n")
            f.write("\n")

    print(f"📋 Summary report: {output_path}")

def generate_resolution_plan(prs: List[Dict], output_path: str):
    """Generate detailed PR resolution plan."""
    # Sort by priority then age
    sorted_prs = sorted(prs, key=lambda x: (x['priority'], -x['age_days']))

    # Group by category
    by_category = defaultdict(list)
    for pr in sorted_prs:
        by_category[pr['category']].append(pr)

    with open(output_path, 'w') as f:
        f.write("# PR Resolution Plan\n\n")
        f.write(f"**Total PRs to Process:** {len(prs)}\n\n")
        f.write("---\n\n")

        # Phase 1: Merge
        f.write("## Phase 1: Quick Wins (MERGE)\n\n")
        f.write("**Estimated Time:** 5 minutes per PR\n\n")
        if by_category['MERGE']:
            for i, pr in enumerate(by_category['MERGE'], 1):
                f.write(f"### {i}. PR #{pr['pr_number']} - {pr['repository']}\n")
                f.write(f"**Title:** {pr['title']}\n")
                f.write(f"**URL:** {pr['url']}\n")
                f.write("**Action:**\n```bash\n")
                f.write(f"gh pr merge {pr['pr_number']} --repo {pr['repository']} --merge --delete-branch\n")
                f.write("```\n\n")
        else:
            f.write("*No PRs ready to merge.*\n\n")

        # Phase 2: Close stale
        f.write("## Phase 2: Cleanup Stale (CLOSE)\n\n")
        f.write("**Estimated Time:** 2 minutes per PR (review + close)\n\n")
        if by_category['CLOSE']:
            for i, pr in enumerate(by_category['CLOSE'], 1):
                f.write(f"### {i}. PR #{pr['pr_number']} - {pr['repository']}\n")
                f.write(f"**Title:** {pr['title']}\n")
                f.write(f"**Age:** {pr['age_days']} days\n")
                f.write(f"**Author:** {pr['author']}\n")
                f.write("**Decision:** [ ] Keep  [ ] Close\n")
                f.write("**Action if closing:**\n```bash\n")
                f.write(f"gh pr close {pr['pr_number']} --repo {pr['repository']} --comment \"Closing as stale. Please reopen if still needed.\"\n")
                f.write("```\n\n")
        else:
            f.write("*No stale PRs to review.*\n\n")

        # Phase 3: Rebase
        f.write("## Phase 3: Resolve Conflicts (REBASE)\n\n")
        f.write("**Estimated Time:** 15-30 minutes per PR\n\n")
        if by_category['REBASE']:
            for i, pr in enumerate(by_category['REBASE'], 1):
                f.write(f"### {i}. PR #{pr['pr_number']} - {pr['repository']}\n")
                f.write(f"**Title:** {pr['title']}\n")
                f.write(f"**Branch:** {pr['head_branch']} → {pr['base_branch']}\n")
                f.write("**Action:**\n```bash\n")
                f.write(f"gh pr checkout {pr['pr_number']} --repo {pr['repository']}\n")
                f.write(f"git fetch origin {pr['base_branch']}\n")
                f.write(f"git rebase origin/{pr['base_branch']}\n")
                f.write("# Resolve conflicts if any\n")
                f.write("git push --force-with-lease\n")
                f.write("```\n\n")
        else:
            f.write("*No PRs with conflicts.*\n\n")

        # Phase 4: Update
        f.write("## Phase 4: Address Issues (UPDATE)\n\n")
        f.write("**Estimated Time:** 30-60 minutes per PR\n\n")
        if by_category['UPDATE']:
            for i, pr in enumerate(by_category['UPDATE'], 1):
                f.write(f"### {i}. PR #{pr['pr_number']} - {pr['repository']}\n")
                f.write(f"**Title:** {pr['title']}\n")
                f.write(f"**Issue:** {pr['action']}\n")
                f.write(f"**CI Status:** {pr['ci_status']}\n")
                f.write(f"**Review Status:** {pr['reviewDecision']}\n")
                f.write(f"**URL:** {pr['url']}\n")
                f.write("**TODO:**\n")
                f.write("- [ ] Review CI logs\n")
                f.write("- [ ] Address review comments\n")
                f.write("- [ ] Update code\n")
                f.write("- [ ] Re-request review\n\n")
        else:
            f.write("*No PRs needing updates.*\n\n")

        # Phase 5: Review
        f.write("## Phase 5: Assess Remaining (REVIEW)\n\n")
        if by_category['REVIEW']:
            for i, pr in enumerate(by_category['REVIEW'], 1):
                f.write(f"### {i}. PR #{pr['pr_number']} - {pr['repository']}\n")
                f.write(f"**Title:** {pr['title']}\n")
                f.write(f"**Age:** {pr['age_days']} days\n")
                f.write("**Decision:** [ ] Merge  [ ] Update  [ ] Close  [ ] Defer\n\n")
        else:
            f.write("*No PRs pending review.*\n\n")

        # Phase 6: Drafts
        f.write("## Phase 6: Draft PRs\n\n")
        if by_category['DRAFT']:
            for i, pr in enumerate(by_category['DRAFT'], 1):
                f.write(f"### {i}. PR #{pr['pr_number']} - {pr['repository']}\n")
                f.write(f"**Title:** {pr['title']}\n")
                f.write("**Decision:** [ ] Complete  [ ] Mark Ready  [ ] Close\n\n")
        else:
            f.write("*No draft PRs.*\n\n")

    print(f"📝 Resolution plan: {output_path}")

#===============================================================================
# Main
#===============================================================================

def main():
    parser = argparse.ArgumentParser(description='Audit GitHub PRs')
    parser.add_argument('--username', '-u', help='GitHub username (default: authenticated user)')
    parser.add_argument(
        '--output-dir',
        '-o',
        default=f'./github_audit_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
        help='Output directory'
    )
    args = parser.parse_args()

    print("\n" + "=" * 50)
    print("  GitHub PR Audit Tool")
    print("=" * 50 + "\n")

    # Check dependencies
    if not check_dependencies():
        sys.exit(1)

    # Get username
    username = args.username or get_username()
    if not username:
        print("❌ Could not determine GitHub username")
        sys.exit(1)

    print(f"👤 Auditing PRs for: {username}")

    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    print(f"📁 Output directory: {args.output_dir}")

    # Get repositories
    print("\n🔍 Fetching repositories...")
    repos = get_repositories(username)
    print(f"   Found {len(repos)} repositories")

    # Process all PRs
    all_prs = []
    print("\n📥 Fetching PRs...")

    for i, repo in enumerate(repos, 1):
        print(f"   [{i}/{len(repos)}] {repo}", end='\r')
        prs = get_open_prs(repo)
        for pr in prs:
            processed = process_pr(pr, repo)
            all_prs.append(processed)

    print(f"\n\n✅ Found {len(all_prs)} open PRs across {len(repos)} repositories\n")

    # Generate reports
    print("📊 Generating reports...")
    generate_json_report(all_prs, os.path.join(args.output_dir, 'pr_audit_report.json'))
    generate_csv_report(all_prs, os.path.join(args.output_dir, 'pr_audit_report.csv'))
    generate_summary_report(all_prs, os.path.join(args.output_dir, 'pr_audit_summary.md'), username)
    generate_resolution_plan(all_prs, os.path.join(args.output_dir, 'pr_resolution_plan.md'))

    # Print summary
    by_category = defaultdict(list)
    for pr in all_prs:
        by_category[pr['category']].append(pr)

    print("\n" + "=" * 50)
    print("  Summary")
    print("=" * 50)
    print(f"\n  Total Open PRs: {len(all_prs)}\n")

    for cat in ['MERGE', 'UPDATE', 'REBASE', 'CLOSE', 'REVIEW', 'DRAFT']:
        count = len(by_category.get(cat, []))
        emoji = CATEGORY_COLORS.get(cat, '⚪')
        print(f"  {emoji} {cat:8} {count:4}")

    print(f"\n📂 All reports saved to: {args.output_dir}/")
    print("\n💡 Next step: Review pr_resolution_plan.md for action items\n")

if __name__ == '__main__':
    main()
