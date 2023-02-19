# How to Contribute

:tada: Fist off, thank you very much that you want to contribute! :tada:

Please help to keep the project maintainable, easy to contribute to, and more secure by following this guide.

## The Contribution Process

If you want to contribute to the project, making a fork and pull request:

1. Create your own fork.
2. Clone the fork locally.
3. Make changes in your local clone.
4. Push the changes from local to your fork.
5. Create a [GitHub Pull Request](https://github.com/roamingthings/spyglass/pulls) when your submission is ready to
   to be deployed into the project.
6. A [reviewer](contributors.md) that is ready to review your submission will assign themselves to the Pull Request on
   GitHub. The review process aims at checking the submission for defects, completeness and overall fit into the
   general architecture
   of the project.
7. After a successful review the Pull Request will be 'approved' on GitHub and will be committed to the main branch by
   a [contributor](contributors.md).

## About the Review Process

Every contribution to Spyglass will be reviewed before it is merged into the main branch. The review aims to check for
defects and to ensure that the submission follows the general style and architecture of the project.

It is understood that there is not a single 'best way' to accomplish a task. Therefore, it is not intended to discuss
if the submission is the 'best' implementation.

Most of the time you will receive feedback from the review. Please be prepared to provide more information or details
and update your submission, if required.

Common aspects that a review looks for:

1. Are there any defects and is the submission ready to be widely distributed?
2. Does the submission provide real additional value to the project that will improve what users will get out of the
   software?
3. Does the submission include automated tests (e.g. unit test) when applicable that will ensure that the implementation
   does what it
   is intended to do?
4. Is the copyright of the submission clear, compatible with the project and non-gratuitous?
5. Commits well formatted, cover a single topic and independent?
6. Is the documentation updated to reflect the changes?
7. Does the implementation follow the general style of the project?

## Format of Commit Messages

The header of the commit should be conformal with [conventional commits](https://www.conventionalcommits.org) and the
description should be contained in the commit message body.

```
<type>: lowercase, present form, short summary (the 'what' of the change)

Optional, more detailed explanation of what the commit does (the 'why' and 'how').

Signed-off-by: My Name <myemail@example.org>
```

The `<type>` may be one of the following list:

* `feat` - A new feature
* `fix` - A bug fix
* `test` - Adding a new test or improve an existing one
* `docs` - Changes or additions to the documentation
* `refactor` - Refactoring of the code or other project elements
* `chore` - Other modifications that do not modify implementation, test or documentations

It is important to have a "Signed-off-by" line on each commit to certify that you agree to the
[developer certificate of origin](developer-certificate-of-origin.md). Depending on your IDE or editor you can
automatically add this submission line with each commit.
It has to contain your real name (please don't use pseudonyms) and contain a current email address. Unfortunately, we
cannot accept anonymous submissions.

You can use `git commit -s` to sign off a commit.

## Format of the Pull Request

The pull request title and description will help the contributors to describe the change that is finally merged into
the main branch. Each submission will be squashed into a single commit before the merge.

This project follows the [Conventional Commits specification](https://www.conventionalcommits.org) to help to easily
understand the intention and change of a commit.

When crating the pull request we ask you to use the following guideline:

The title of the pull request has the following format:

```
<type>: lowercase, present form, short summary (the 'what' of the change)
```

If your submission does introduce a breaking change please add `BREAKING CHANGE` to the beginning of the description.

Similar to a commit the description describes the overall change of the submission and include a `Signed-off-by` line
at the end:

```
Describe what the submission changes.

What is its intention?

What benefit does it bring to the project?

Signed-off-by: My Name <myemail@example.org>
```
