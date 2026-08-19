# Release checklist

- [ ] Version and changelog updated
- [ ] Required pull requests reviewed and merged
- [ ] CI, DevSecOps, and documentation workflows green on `main`
- [ ] No unresolved HIGH or CRITICAL vulnerability
- [ ] Backup and restore procedure tested
- [ ] OAuth and privacy impact reviewed
- [ ] Database compatibility reviewed
- [ ] Production environment approval configured
- [ ] Tag points to the intended `main` commit
- [ ] GHCR AMD64 and ARM64 manifests published
- [ ] SBOM downloaded and inspected
- [ ] Provenance attestation verified
- [ ] Cosign signature verified by digest
- [ ] Smoke test completed from the released digest
- [ ] Release notes and rollback digest recorded
