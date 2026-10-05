# Public release checklist

The repository is private until this list is done. Based on the public-release notes of [KingKongRobotics/jumper](https://github.com/KingKongRobotics/jumper/blob/main/docs/PUBLIC_RELEASE.md).

- [ ] **Clean history.** Publish a reviewed snapshot as a fresh single commit. Do not publish the internal history: earlier commits still contain files and names that were removed from the current tree.
- [ ] **Publication rights for every image.** Only our own renders. No third-party or reference photos (the photo-comparison images were removed from `docs/images/`; check `experiments/history/` again before release).
- [ ] **Licences.** Review `LICENSE` and `NOTICE` against what ships. Resolve the eye-firmware TODO in `NOTICE` (Waveshare demo terms).
- [ ] **No private data.** Grep tracked files and binary metadata (`.blend`, `.png`, `.mp4`) for emails, addresses, phone numbers, tokens and absolute paths.
- [ ] **Commit identity.** Use the GitHub noreply address for the public commit author.
- [ ] **Large files.** Keep every file < 100 MB and list the files > 25 MB in the README. Move big sources to Releases or LFS later, documenting the extra download step in the same change.
- [ ] **After publishing.** Add a description and topics, protect `main`, and only add release tags for tested versions.
