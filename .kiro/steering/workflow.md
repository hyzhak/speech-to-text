# Development Workflow

## GitHub + Git Flow Process

Follow this step-by-step process for every task implementation to ensure consistent development practices and proper documentation.

**⚠️ CRITICAL: Each step must be completed in sequential order. Do not skip steps or jump ahead to completion. Wait for each step to fully complete before proceeding to the next step. This workflow is designed to prevent errors and ensure quality.**

### Task Implementation Steps

1. **Create GitHub Issue**
   - Create a new GitHub issue for the task (unless it already exists)
   - Assign the issue to yourself
   - Use clear, descriptive title and detailed description
   - Add appropriate labels (bug, feature, enhancement, etc.)

2. **Prepare Local Environment**
   - Confirm you are on the main branch: `git branch`
   - Pull recent changes: `git pull origin main`
   - Ensure no conflicts or uncommitted changes: `git status`

3. **Create Feature Branch**
   - Follow git flow naming convention: `feature/issue-number-brief-description`
   - Example: `feature/123-add-whisper-model-support`
   - Create and switch to branch: `git checkout -b feature/123-add-whisper-model-support`

4. **Implementation and Testing**
   - Implement the required functionality
   - Write or update tests as needed
   - Follow project conventions and architecture patterns
   - Test locally to ensure everything works

5. **Document Progress**
   - Add comments to the GitHub issue throughout implementation
   - Include:
     - Knowledge discovered during implementation
     - Challenges faced and how they were resolved
     - Technical decisions made and reasoning
     - Any useful information for future reference
   - Update comments regularly, not just at the end

6. **Commit Changes**
   - Follow conventional commit format: https://www.conventionalcommits.org/en/v1.0.0/
   - Include reference to GitHub issue
   - You can add emoji to the commit message to indicate the type of change
   - Examples:
     - `feat: 🗣️ add Whisper model integration (#123)`
     - `fix: 📻 resolve audio format validation issue (#124)`
     - `docs: 📗 update API documentation for new endpoints (#125)`

7. **Push Branch**
   - Push feature branch to GitHub: `git push origin feature/123-add-whisper-model-support`

8. **Create Pull Request**
   - Create PR from feature branch to main
   - Use descriptive title and detailed description
   - Reference the GitHub issue: "Closes #123"
   - Add any additional context or testing notes

9. **Request Copilot Review (if enabled)**
   - If your repository has GitHub Copilot PR review enabled, trigger the Copilot review on the PR
   - If Copilot review is not enabled, proceed to manual review or follow your team's standard review process
   - Wait for automated review to complete before proceeding to next step

10. **Wait for Validation**
    - Wait for GitHub Actions to complete
    - Ensure all CI/CD checks pass
    - Review any automated feedback

11. **Respond to Feedback**
    - React to each comment with appropriate emoji (👍, ❤️, 👀, 👎, etc.)
    - Add sub-comments addressing each point
    - Engage constructively with all feedback
    - Ask clarifying questions if needed

12. **Implement Fixes**
    - Make necessary changes based on feedback
    - Commit fixes following conventional commit format
    - Push updated changes: `git push origin feature/123-add-whisper-model-support`

13. **Repeat Review Process**
    - **MANDATORY**: Return to step 9 if ANY changes were made after review
    - **DO NOT PROCEED** until all feedback is addressed and no new comments appear
    - Continue this cycle until review process is complete

14. **Merge When Ready**
    - **ONLY PROCEED** when ALL previous steps are complete
    - Ensure PR has passed all validations
    - Ensure all comments are addressed
    - **VERIFY** no pending reviews or feedback
    - Squash and merge the PR when approved
    - Delete the feature branch on GitHub

15. **Clean Up Local Environment**
    - Switch back to main branch: `git checkout main`
    - Pull merged changes: `git pull origin main`
    - Delete local feature branch: `git branch -d feature/123-add-whisper-model-support`

16. **Complete Task**
    - Verify the issue is automatically closed by the merge
    - Add final comment to issue if needed
    - Task is now complete

## Commit Message Format

Use conventional commits with issue references:

```
<type>[optional scope]: <description> (#issue-number)

[optional body]

[optional footer(s)]
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples
```
feat: 🔊 add audio format validation service (#45)
fix: 🧠 resolve memory leak in Whisper model loading (#46)
docs: 📗 update README with Docker setup instructions (#47)
test: 🧪 add integration tests for CLI interface (#48)
```

## Branch Naming Convention

- Feature branches: `feature/issue-number-brief-description`
- Bug fixes: `fix/issue-number-brief-description`
- Documentation: `docs/issue-number-brief-description`
- Hotfixes: `hotfix/issue-number-brief-description`

## Best Practices

- Keep commits atomic and focused
- Write clear, descriptive commit messages
- Document decisions and challenges in issue comments
- Respond to all PR feedback professionally
- Test thoroughly before pushing
- Keep feature branches up to date with main
- Use meaningful branch names that reflect the work being done