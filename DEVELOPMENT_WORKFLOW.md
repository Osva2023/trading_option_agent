# Development Workflow - Git Branch Strategy

## 🌳 Branch Structure

```
main (production-ready)
└── dev (development branch)
    ├── feature/new-feature
    ├── feature/bug-fix
    └── feature/enhancement
```

## 📋 Workflow Rules

### **Main Branch (`main`)**
- ✅ **Production-ready code only**
- ✅ **No direct commits** - only merges from dev
- ✅ **Always stable and tested**
- ✅ **Tagged releases**

### **Development Branch (`dev`)**
- ✅ **Active development**
- ✅ **Feature integration**
- ✅ **Testing ground**
- ✅ **Regular commits allowed**

### **Feature Branches (`feature/*`)**
- ✅ **One feature per branch**
- ✅ **Branch from dev**
- ✅ **Merge back to dev when complete**
- ✅ **Delete after merge**

---

## 🚀 Development Workflow

### **1. Start New Feature**
```bash
# Switch to dev branch
git checkout dev
git pull origin dev

# Create feature branch
git checkout -b feature/your-feature-name

# Work on your feature...
```

### **2. Commit Changes**
```bash
# Stage changes
git add .

# Commit with clear message
git commit -m "feat: add new feature description"

# Push feature branch
git push -u origin feature/your-feature-name
```

### **3. Merge Feature to Dev**
```bash
# Switch to dev
git checkout dev
git pull origin dev

# Merge feature branch
git merge feature/your-feature-name

# Push dev
git push origin dev

# Delete feature branch
git branch -d feature/your-feature-name
git push origin --delete feature/your-feature-name
```

### **4. Release to Main (When Ready)**
```bash
# Switch to main
git checkout main
git pull origin main

# Merge dev to main
git merge dev

# Tag release
git tag -a v1.0.0 -m "Release v1.0.0"

# Push main and tags
git push origin main --tags
```

---

## 📝 Commit Message Convention

Use conventional commits:

```
feat: add new feature
fix: resolve bug
docs: update documentation
style: format code
refactor: restructure code
test: add tests
chore: maintenance tasks
```

---

## 🔄 Daily Workflow

### **Morning: Start Work**
```bash
git checkout dev
git pull origin dev
git checkout -b feature/daily-task
```

### **Throughout Day: Regular Commits**
```bash
git add .
git commit -m "feat: implement X functionality"
git push
```

### **Evening: Merge to Dev**
```bash
git checkout dev
git merge feature/daily-task
git push origin dev
```

---

## 🛠️ Useful Commands

### **Check Status**
```bash
git status                    # Current status
git branch -a                 # All branches
git log --oneline -5          # Recent commits
```

### **Switch Branches**
```bash
git checkout main             # Switch to main
git checkout dev              # Switch to dev
git checkout -b feature/new   # Create and switch to feature
```

### **Sync with Remote**
```bash
git pull origin dev           # Pull latest dev
git push origin dev           # Push dev changes
```

### **Clean Up**
```bash
git branch -d feature/old     # Delete local branch
git push origin --delete feature/old  # Delete remote branch
```

---

## ⚠️ Important Rules

1. **Never commit directly to main**
2. **Always pull before pushing**
3. **Test before merging to main**
4. **Delete feature branches after merge**
5. **Use clear commit messages**

---

## 🎯 Current Status

- ✅ **main**: Production-ready (initial commit)
- ✅ **dev**: Development branch (ready for features)
- ✅ **GitHub**: Both branches pushed and tracked

---

## 🚀 Next Steps

1. **Start developing**: `git checkout dev`
2. **Create features**: `git checkout -b feature/your-feature`
3. **Merge when ready**: Follow the workflow above
4. **Release to main**: When features are complete and tested

---

**Happy coding!** 🎉

---

*Last Updated: March 10, 2026*
