*FIXME - SEE [Temporary_Guide_to_Early_Stage_Contributions.md](Temporary_Guide_to_Early_Stage_Contributions.md) for 
contributing this early in the project prior to the CI/CO pipeline being in place (below is just template/planning). 
In general the contributing pipeline spoken below is just empty a promises doc at the moment. Keep good common sense 
for now!. Fork the repo and do a pull requests as needed. For now, we'll tend to work on independent sections of the 
codebase of new files only to minimize merging issues. Add issues as needed but be precise about the error or 
recommended changes if the file ownership is not yours. Ask me questions :)*

# Contributing to Genie-Trader

Involvement from the trading community is a goal for this project. All help is welcome!
Developers can open issues on GitHub to discuss proposed enhancements/changes, or
to make bug reports.

It's a best practice to keep all discussions regarding changes to the codebase public.

To contribute, the following steps should be followed;

- Open an issue on GitHub to discuss your proposal.

- Once everyone is on the same page, take a fork of the `develop` branch (or ensure all upstream changes are merged).

- Install and setup pre-commit so that the pre-commit hook will be picked up on
  your local machine. This will automatically run various checks, auto-formatters
  and linting tools. Further information can be found here <https://pre-commit.com/>.

- It's recommended you install Redis using the default configuration, so that integration
  tests will pass on your machine.

- Open a pull request (PR) on the `develop` branch with a summary comment.

- The CI system will run the full test-suite over your code including all unit and integration tests, so please include appropriate tests
  with the PR.

- [Codacy](https://www.codacy.com/) will perform an automated code review. Please
  fix any issues which cause a failed check, and add the commit to your PR.

- You'll also be required to sign a standard Contributor License Agreement (CLA), which is
  administered automatically through CLAassisant.

- We will endeavour to review your code expeditiously, there may be some
  feedback on needed changes before merging.

## Tips

- Conform to the established coding practices, see _Coding Standards_ in the
  [Developer Guide](https://docs.Genie-Trader.codes/developer_guide/index.html).
- Keep PR's small and focused.
- Reference the related GitHub issue(s) in the PR comment.

Thank you for your interest in Genie-Trader!
