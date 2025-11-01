# 🔄 Development Workflow

We follow the Git Feature Branch Workflow to keep the codebase clean and organized.

## 1. Create a Feature Branch
```bash
# Update your main branch
git checkout main
git pull origin main

# Create a new feature branch
git checkout -b feature/your-feature-name

# Examples:
# feature/add-order-model
# feature/payment-integration
# bugfix/fix-user-validation
```

## 2. Make Your Changes
```bash
# Make your code changes
# Write tests for your changes
# Run tests locally to ensure they pass

pytest -v
```

## 3. Commit Your Changes
Follow conventional commit messages:
```bash
git add .
git commit -m "feat: add order model with CRUD operations

- Created Order model with SQLAlchemy
- Added order endpoints (GET, POST, PUT, DELETE)
- Implemented order status tracking
- Added 10 unit tests for order functionality"
```

## 4. Push Your Branch
```bash
git push origin feature/your-feature-name
```

## 5. Create a Pull Request

Go to GitHub repository
Click "Compare & pull request"
Fill in the PR template:

Title: Clear, descriptive title
Description: What changes were made and why
Testing: How you tested the changes
Screenshots: If UI changes



# PR Template:
## Changes
- Brief description of what changed

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] All tests pass locally
- [ ] Added new tests for new features
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated

## 6. Code Review

Wait for CI tests to pass ✅
Address review comments
Make requested changes
Push updates (they'll automatically update the PR)

## 7. Merge
Once approved:

Squash and merge (recommended for clean history)
Delete the feature branch after merging