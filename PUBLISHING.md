# Publishing Your Parkeren Utrecht Integration

## Publishing Options

### Option 1: HACS Default Repository (Most Popular) ⭐

To get your integration into the official HACS default repository:

#### Prerequisites:
✅ GitHub repository with proper structure (you have this)
✅ `manifest.json` with all required fields (you have this)
✅ `hacs.json` file (you have this)
✅ `README.md` documentation (you have this)
✅ `info.md` for HACS display (you have this)
✅ Code passes linting (you have this)

#### Steps:
1. **Tag a release on GitHub:**
   ```bash
   git tag -a v0.1.0 -m "Initial release"
   git push origin v0.1.0
   ```

2. **Submit to HACS:**
   - Go to https://github.com/hacs/default
   - Fork the repository
   - Add your integration to `custom_components/integration` file:
     ```
     gerritjandebruin/ha-parkeren-utrecht
     ```
   - Create a Pull Request
   - Wait for review and approval (usually takes a few days)

3. **Requirements for HACS acceptance:**
   - At least one release tag
   - Valid `manifest.json`
   - Valid `hacs.json`
   - README with documentation
   - Working integration
   - Pass all HACS validation checks

### Option 2: HACS Custom Repository (Quick Start)

Users can install immediately without waiting for HACS approval:

**Users install by:**
1. In HACS → Integrations → ⋮ (three dots) → Custom repositories
2. Add: `https://github.com/gerritjandebruin/ha-parkeren-utrecht`
3. Category: Integration
4. Click Add

### Option 3: Manual Installation

Users download and copy files manually:
1. Download the repository
2. Copy `custom_components/parkeeractie` to their HA config
3. Restart Home Assistant

## Pre-Publication Checklist

Before publishing, ensure:

- [ ] Code is in the root `custom_components/` directory (not nested in `config/`)
- [ ] All tests pass
- [ ] Linting passes (✅ you have this)
- [ ] `manifest.json` is complete and valid
- [ ] Version number is set in `manifest.json`
- [ ] README has clear installation instructions
- [ ] Documentation for all features
- [ ] License file (MIT recommended)
- [ ] `.gitignore` excludes unnecessary files
- [ ] Create a GitHub release with changelog

## Current Repository Structure Issues

Your code is currently in two places:
1. `custom_components/parkeeractie/` ✅ Correct for distribution
2. `config/custom_components/parkeeractie/` ❌ For local testing only

**Action needed:** Ensure the main `custom_components/` directory is what gets published.

## Next Steps

1. **Move final code to root custom_components:**
   ```bash
   # Copy from config to root if needed
   rsync -av config/custom_components/parkeeractie/ custom_components/parkeeractie/
   ```

2. **Create a GitHub release:**
   ```bash
   # Commit all changes
   git add .
   git commit -m "Prepare v0.1.0 release"
   git push origin main
   
   # Create and push tag
   git tag -a v0.1.0 -m "Initial release - Parkeren Utrecht integration"
   git push origin v0.1.0
   ```

3. **Create release on GitHub:**
   - Go to your repo on GitHub
   - Click "Releases" → "Create a new release"
   - Select tag v0.1.0
   - Title: "v0.1.0 - Initial Release"
   - Add release notes (features, known issues)
   - Publish release

4. **Test installation:**
   - Add as HACS custom repository
   - Install and verify it works
   - Get feedback from a few users

5. **Submit to HACS (optional):**
   - Once stable and tested
   - Follow HACS submission process above

## Documentation Best Practices

Update your README.md with:
- Clear description of what the integration does
- Screenshots (optional but helpful)
- Installation instructions (HACS + Manual)
- Configuration examples
- Service documentation with examples
- Troubleshooting section
- Link to Parkeeractie Utrecht website

## Promotion

Once published:
- Post on Home Assistant Community Forum
- Post on Reddit r/homeassistant
- Share on Home Assistant Discord
- Add to your GitHub profile

## Maintenance

After publishing:
- Monitor GitHub issues
- Respond to user questions
- Release bug fixes and new features
- Keep dependencies updated
- Test with new HA versions

## Additional Resources

- [HACS Documentation](https://hacs.xyz/)
- [HA Integration Development](https://developers.home-assistant.io/)
- [HA Brand Guidelines](https://www.home-assistant.io/developers/documentation/create_integration/)

Good luck with your integration! 🚀
