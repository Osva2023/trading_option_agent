# Quick Git Branch Commands

## 🌳 Current Status
- ✅ **main**: Clean production branch
- ✅ **dev**: Active development branch
- ✅ **GitHub**: Both branches synced

## 🚀 Quick Start Development

### **Start Working**
```bash
# Switch to dev branch
git checkout dev
git pull origin dev

# Create feature branch
git checkout -b feature/your-feature-name
```

### **Daily Workflow**
```bash
# Make changes...
git add .
git commit -m "feat: your feature description"
git push
```

### **Merge to Dev**
```bash
# Switch to dev
git checkout dev
git pull origin dev

# Merge your feature
git merge feature/your-feature-name

# Push and clean up
git push origin dev
git branch -d feature/your-feature-name
git push origin --delete feature/your-feature-name
```

### **Release to Main (When Ready)**
```bash
git checkout main
git pull origin main
git merge dev
git push origin main
```

## 📋 Branch Status
```bash
git branch -a          # See all branches
git status             # Current status
git log --oneline -5   # Recent commits
```

## 🎯 Remember
- **main**: Production only (merge from dev)
- **dev**: Development (merge features here)
- **feature/* **: Individual features (delete after merge)

---
*See DEVELOPMENT_WORKFLOW.md for full guide*