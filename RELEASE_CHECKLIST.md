# Release checklist

VERSION is canonical. PATCH covers installation/docs/validation/compatibility; MINOR adds routing capabilities; MAJOR changes incompatible layout/behavior. Never move or overwrite a published tag or its release assets.

1. Select VERSION, update the latest CHANGELOG entry, and match the README repository version. The release page, not a working-tree version heading, establishes publication status.
2. Run source validation, unit tests, and git diff --check. Build with `python scripts/package_runtime.py`; optionally assert the version with --version.
3. Verify the ZIP and sidecars with the builder's --verify option. Inspect its nine allowlisted members, one top-level folder, extracted-runtime validation, manifest, and checksum. Review content as well as absence of .env, .env.*, *.pem, *.key, credentials*, token*, secrets*, developer files, and linked paths. Do not claim filename filtering proves secret absence.
4. Review and commit source changes only. Never commit dist/. Push the intended branch, confirm a clean tree, and verify the successful Validate skill run belongs to that exact commit.
5. Check remote tags and GitHub Releases for the version. If either already exists, stop and report the collision. Never force-push tags or replace existing release assets.
6. Create an annotated vVERSION tag on the CI-verified commit and push only that new tag. Confirm its remote target. Do not tag a dirty checkout or a different commit.
7. Create **Adaptive Model Router vVERSION** with concise release notes from the matching CHANGELOG. Use gh release create with --verify-tag, --title, and --notes-file. Attach the locally verified versioned ZIP and SHA-256 sidecar; the manifest may also be attached for provenance. Publish only after validation, tests, packaging, extracted-package checks, and checksum generation succeed.
8. Confirm the published release page, tag/commit, title, and asset names/sizes. Download the published ZIP and checksum into a temporary directory and compare the bytes/hash against the verified local artifact. Do not overwrite v0.2.0 or any prior release.

This project intentionally uses a manual release step after CI instead of a tag-triggered publisher. Ordinary branch pushes and PRs validate but never release. If permissions are unavailable, report **prepared but not published**, identify the verified commit/artifacts, and perform these remaining steps manually. No release API or network access is needed for a local build.

## Reproducibility

Build from the exact tagged source with Python 3.13+ and the standard library. UTF-8 LF normalization, sorted names, fixed timestamps/permissions, and ZIP_STORED entries make output independent of checkout newlines, file mtimes, and zlib versions. The generated external manifest records all file hashes; hosts do not consume it. Development-only README links are rewritten to the matching tag; runtime references remain relative and are validated after extraction.
