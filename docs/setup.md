# Environment Setup

This portfolio repository is documentation-first and does not currently ship any
runtime services. The previous Python dependencies `apscheduler` and `redis`
were removed because there is no code that uses them.

## Prerequisites

A Python 3.10+ interpreter is sufficient if you would like to work inside a
virtual environment for future tooling.

## Installing Dependencies

The `requirements.txt` file is intentionally comment-only to reflect that the
project has no runtime dependencies right now. Running `pip install -r requirements.txt`
will succeed without installing any packages.

## Next Steps

If you add tooling that needs packages later, document the additions in
`requirements.txt` and update this guide accordingly.
