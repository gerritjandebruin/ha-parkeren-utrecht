# Pre-Release Checklist for Parkeren Utrecht Integration

## ✅ Code Quality
- [x] All linting errors fixed (ruff check passes)
- [x] Code formatted (ruff format)
- [x] All imports properly organized
- [x] Type hints added
- [x] Docstrings added

## ✅ File Structure
- [x] `custom_components/parkeeractie/` exists in repo root
- [x] `manifest.json` is properly configured
- [x] `hacs.json` is properly configured
- [x] `strings.json` for translations
- [x] `services.yaml` for service definitions
- [x] `translations/` directory exists

## ✅ Documentation
- [x] `README.md` exists
- [x] `info.md` created for HACS
- [x] `PUBLISHING.md` guide created
- [ ] Add screenshots to README (optional)
- [ ] Add example automations

## 📝 Remaining Tasks

### 1. Clean Up Repository Structure
```bash
# Remove or gitignore the config/custom_components directory
# It's only for local testing, not for distribution
echo "config/" >> .gitignore
```

### 2. Update .gitignore
Make sure these are ignored:
```
__pycache__/
*.pyc
*.pyo
.pytest_cache/
.ruff_cache/
config/
!config/configuration.yaml
.vscode/
*.log
*.db
.HA_VERSION
```

### 3. Verify manifest.json version
Current version: 0.1.0 ✅

### 4. Test Installation
- [ ] Test installing via HACS custom repository
- [ ] Test manual installation
- [ ] Verify config flow works
- [ ] Verify sensors appear
- [ ] Test the start_parking_session service

### 5. Create GitHub Release
```bash
# 1. Commit all final changes
git add .
git commit -m "Release v0.1.0: Initial Parkeren Utrecht integration"
git push origin main

# 2. Create and push tag
git tag -a v0.1.0 -m "Release v0.1.0

Features:
- Monitor parking account balance
- Track remaining parking time
- Start parking sessions from Home Assistant
- Binary sensor for parking problems"

git push origin v0.1.0

# 3. Go to GitHub and create release from tag
```

### 6. Test as HACS Custom Repository
Have someone (or use another HA instance) test installing:
1. HACS → Integrations → ⋮ → Custom repositories
2. Add: `https://github.com/gerritjandebruin/ha-parkeren-utrecht`
3. Category: Integration
4. Install and verify

### 7. Get User Feedback
Before submitting to HACS default:
- [ ] Test with at least 2-3 users
- [ ] Fix any reported bugs
- [ ] Update documentation based on feedback

### 8. Submit to HACS Default (Optional)
When ready for wider distribution:
1. Go to https://github.com/hacs/default
2. Fork the repository
3. Edit `custom_components/integration`
4. Add line: `gerritjandebruin/ha-parkeren-utrecht`
5. Create Pull Request
6. Address review feedback

### 9. Promote Your Integration
- [ ] Post on Home Assistant Community Forum
- [ ] Post on Reddit r/homeassistant
- [ ] Share on Discord
- [ ] Tweet about it (if applicable)

## Quick Commands Reference

```bash
# Check for linting issues
uvx ruff check custom_components/parkeeractie/

# Format code
uvx ruff format custom_components/parkeeractie/

# Create release
git tag -a v0.1.0 -m "Initial release"
git push origin v0.1.0

# Update to new version
# 1. Update version in manifest.json
# 2. Commit changes
# 3. Create new tag
git tag -a v0.1.1 -m "Bug fixes"
git push origin v0.1.1
```

## Support & Maintenance

After release, plan to:
- Monitor GitHub issues regularly
- Release bug fixes promptly
- Test with new Home Assistant versions
- Keep dependencies updated
- Respond to user questions

## Success Metrics

Track:
- GitHub stars
- Number of installs (via HACS if accepted)
- Issues opened/closed
- Community feedback

## Next Version Planning

Ideas for v0.2.0:
- [ ] Add more sensors (active sessions, permits)
- [ ] Add ability to stop parking sessions
- [ ] Add permit management
- [ ] Improve error handling
- [ ] Add unit tests
- [ ] Add config option for scan interval

---

Good luck with your release! 🎉
