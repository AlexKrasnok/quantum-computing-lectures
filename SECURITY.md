# Security Policy

## Credentials

Never commit IBM Quantum tokens, API keys, passwords, private keys, `.env` files, or exported account configuration. Use the provider's supported credential store or an environment variable outside the repository.

If a credential is found in any notebook, output, attachment, Git commit, fork, or release artifact:

1. Revoke and rotate it immediately at the provider.
2. Remove it from the current files.
3. Purge it from Git history before making the repository public.
4. Assume cached clones and forks may still contain it.

## Reporting

Do not post a live credential in a public GitHub issue. Contact the repository owner privately and identify only the affected file and commit.
