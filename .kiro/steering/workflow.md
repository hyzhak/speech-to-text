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

11. **Evaluate and Respond to Feedback**
    - **Evaluate each Copilot comment for relevance and accuracy:**
      - **Accept**: Valid suggestions that improve code quality, clarity, or correctness
      - **Consider**: Suggestions that may be subjective but have merit (style preferences, alternative approaches)
      - **Reject**: Comments that are incorrect, irrelevant, or would worsen the code
      - **Clarify**: Comments that are unclear or need more context
    - **Assessment criteria:**
      - Does the suggestion fix an actual issue or improve functionality?
      - Is the suggestion consistent with project conventions and standards?
      - Would implementing the change benefit future maintainability?
      - Is the comment based on accurate understanding of the code context?
    - **Document your evaluation:**
      - React to each comment with appropriate emoji (👍 for accept, 👀 for considering, 👎 for reject)
      - Add sub-comments explaining your reasoning for each decision
      - For rejected suggestions, explain why they don't apply or are incorrect
      - For accepted suggestions, acknowledge and indicate you'll implement them

12. **Implement Accepted Changes**
    - **Only implement changes you evaluated as beneficial in step 11**
    - Make necessary changes based on accepted feedback
    - **Do not implement suggestions you determined were incorrect or irrelevant**
    - Group related changes into logical commits
    - Commit fixes following conventional commit format
    - Include reference to specific feedback addressed in commit message
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

## Evaluating Copilot Feedback

### Types of Feedback and How to Handle Them

**✅ Accept These Types:**
- Genuine bugs or security issues
- Syntax errors or typos
- Improvements to code clarity or readability
- Better variable/function naming suggestions
- Performance optimizations with clear benefits
- Adherence to established project conventions

**🤔 Consider These Types:**
- Style preferences that don't conflict with project standards
- Alternative implementation approaches
- Suggestions for additional error handling
- Documentation improvements
- Refactoring suggestions for better maintainability

**❌ Reject These Types:**
- Suggestions that break existing functionality
- Changes that conflict with project architecture decisions
- Overly opinionated style changes that don't improve clarity
- Suggestions based on misunderstanding of the code context
- Changes that would introduce unnecessary complexity
- Recommendations that contradict established project patterns

### Example Evaluation Process

```
Copilot Comment: "Consider using const instead of let for this variable"
Evaluation: ✅ Accept - Variable is never reassigned, const is more appropriate
Action: Implement change and respond with 👍

Copilot Comment: "This function should return a Promise"
Evaluation: ❌ Reject - Function is intentionally synchronous for this use case
Action: Respond with 👎 and explain: "Function needs to be synchronous for immediate validation"

Copilot Comment: "Consider adding error handling here"
Evaluation: 🤔 Consider - Good suggestion but need to evaluate if it fits the error handling strategy
Action: Respond with 👀 and comment: "Good point, will add try-catch consistent with other service methods"
```

## Best Practices

- Keep commits atomic and focused
- Write clear, descriptive commit messages
- Document decisions and challenges in issue comments
- Respond to all PR feedback professionally with clear reasoning
- Test thoroughly before pushing
- Keep feature branches up to date with main
- Use meaningful branch names that reflect the work being done
- **Evaluate all feedback critically - not all suggestions should be implemented**
- **Explain your reasoning when rejecting feedback to maintain good communication**