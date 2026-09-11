# BundleProof

BundleProof catches broken Python desktop release artifacts before users download them.

It currently checks:

- required files and glob patterns;
- unexpectedly empty files;
- macOS `Info.plist` and its declared executable;
- executable permissions;
- the complete macOS bundle signature with `codesign --deep --strict`.

Output is available as readable text, JSON, or SARIF. BundleProof has no runtime dependencies and performs all checks locally.

## Install

```bash
python -m pip install bundleproof
```

Until the first PyPI release, install from GitHub:

```bash
python -m pip install git+https://github.com/ericz218/bundleproof.git
```

## Use

```bash
bundleproof check dist/MyApp.app \
  --require 'Contents/Resources/public_key.pem' \
  --require 'Contents/Resources/*.sql'
```

Exit status is nonzero when an error is found. Warnings, such as empty files, do not fail the check.

Machine-readable output:

```bash
bundleproof check dist/MyApp.app --format json
bundleproof check dist/MyApp.app --format sarif > bundleproof.sarif
```

## GitHub Actions

```yaml
- uses: ericz218/bundleproof@v0.1.0
  with:
    path: dist/MyApp.app
    require: Contents/Resources/public_key.pem Contents/Resources/schema.sql
```

Run the action on macOS when checking a macOS signature.

An example project test workflow is available at [`examples/ci.yml`](examples/ci.yml).

## Scope

Version 0.1 intentionally audits built artifacts rather than trying to infer every PyInstaller or Nuitka configuration. Planned rules are tracked in GitHub issues; contributions based on reproducible packaging failures are welcome.

## Contributing and security

See [CONTRIBUTING.md](CONTRIBUTING.md). Report vulnerabilities according to [SECURITY.md](SECURITY.md).

## License

MIT
