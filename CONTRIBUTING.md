# Contributing to Jarvis

:+1::tada: Thanks for taking the time to contribute! :tada::+1:

The following is a set of guidelines for contributing to Jarvis, which is hosted in its [GitHub repo](https://github.com/sukeesh/Jarvis). These are mostly guidelines, and not rules. Use your best judgment, and feel free to propose changes to this document in a pull request.

### Short Version

* PRs are accepted :)
* We follow [PEP 8](https://pep8.org/) formatting ([official PEP 8](https://www.python.org/dev/peps/pep-0008/)). Before making a pull request ensure that your code is according to PEP 8 standards
* If you have some ideas for new features but don't have the time to implement them, please open an issue with the tag new_feature
* Don't forget to comment and add docstrings to your code where needed!

### Table Of Contents

[How Can I Contribute?](#how-can-i-contribute)
  * [Reporting Bugs](#reporting-bugs)
  * [Suggesting Enhancements](#suggesting-enhancements)
  * [Adding documentation](#adding-documentation)
  * [Beginners: Your First Contribution](#beginners-your-first-contribution)
  * [Pull Requests](#pull-requests)

[Styleguides](#styleguides)
  * [Git Commit Messages](#git-commit-messages)
  * [Python Styleguide](#python-styleguide)
  * [Documentation Styleguide](#documentation-styleguide)

## How Can I Contribute?

### Reporting Bugs

Here's some guidelines to help maintainers and the community understand your report :pencil:, reproduce the behavior :computer: :computer:, and find related reports :mag_right:.

Before creating bug reports, please check [this list](#before-submitting-a-bug-report) as you may find that you don't need to create one. When you are creating a bug report, please [include as many details as possible](#how-do-i-submit-a-good-bug-report).

> **Note:** If you find a **Closed** issue that seems like it is the same problem you're experiencing, open a new issue and try and link to the original issue.

#### Before Submitting A Bug Report

* Read the README and the documentation to check if you missed something.
* Check if you can reproduce the problem in the latest version of Jarvis.
* **Perform a quick search in [issues](https://github.com/sukeesh/Jarvis/issues)** to see if the bug has already been reported. If it has **and the issue is still open**, add a comment to the existing issue instead of opening a new one.

#### How Do I Submit A Good Bug Report?

Bugs are recorded as [issues](https://guides.github.com/features/issues/).
Explain the problem and include details to help maintainers reproduce the problem, and to help contributers fix it:

* **Use a clear and descriptive title** for the issue to identify the problem
* **Describe the steps which produce the problem** in as much detail as possible
* **Describe what was wrong** with the behavior you observed
* **Explain which behavior you expected to see instead and why**
* **Can you reliably reproduce the issue?** If not, provide details about how often the problem happens and under which conditions it normally happens
* Include details about your configuration and environment. What OS are you using? What command line program was Jarvis running in? The more detail the better

### Suggesting Enhancements and Features

Following these guidelines helps maintainers and the community understand your suggestion :pencil: and find related suggestions :mag_right:.

Before creating feature suggestions, please check [this list](#before-submitting-a-feature-suggestion). You may find that you don't need to create one. When creating a suggestion, [include as many details as possible](#how-do-i-suggest-a-feature).

#### Before Submitting A Feature Suggestion

* **Check if that feature already exists**
* **Check if you have the latest version** of Jarvis
* **Perform a [quick search](https://github.com/sukeesh/Jarvis/issues)** to see if the feature/enhancement has already been suggested. If it has, add a comment to the existing issue instead of opening a new one.

#### How Do I Submit A Feature Suggestion?

Enhancement suggestions are tracked as GitHub [issues](https://guides.github.com/features/issues/).

* **Use a clear and descriptive title** for the issue to identify the suggestion
* **Use the tag new_feature** in the issue
* **Provide a description of the suggested feature**

### Adding Documentation

Every project benefits from having better documentation! With this in mind, Pull Requests that address documentation are welcome! 

These contributions can be in many forms:

* Added/Improved docstrings and comments for functions/classes
* Added/Improved markdown files (README, CONTRIBUTING etc) that help visitors navigate the repository

### Beginners: Your First Contribution

These are the steps to take to successfully contribute code to the Jarvis repo:

1. **Find a potential contribution that you want to make**. You can do this by either going throught the existing [list of issues](https://github.com/sukeesh/Jarvis/issues) and picking one, or by opening a new issue.
2. **Assign it to yourself by commenting on the issue** and saying that you will fix it.
> **Note:** Remember to periodically comment an update on the issue to let everyone know that you're still working on it, or else someone else may take up the same issue.
3. **Fork the main branch** so you have a repository on your Github called your_username/Jarvis.
4. **Make commits to this forked repository**. You can clone this repository onto your computer and then push your commits to it, or take the less popular approach and make your commits directly in the forked Github repo.
5. **After finishing all your commits**, [squash](https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&cad=rja&uact=8&ved=2ahUKEwjIoemS1Y30AhWzyIsBHWprDJYQFnoECAQQAw&url=https%3A%2F%2Fdocs.github.com%2Fen%2Fdesktop%2Fcontributing-and-collaborating-using-github-desktop%2Fmanaging-commits%2Fsquashing-commits&usg=AOvVaw0NwD3KXuURsZVEN7oK_bW2) them into a single commit if there's too many repetitive ones.
6. **In the forked repository, click on 'Pull Requests' and then make a new pull request**. Make sure that you are comparing your repo, your_username/Jarvis to the main repo sukeesh/Jarvis.
7. **Submit the pull request**. Refer to the [pull requests](#pull-requests) section below to see details about them.

Congratulations! You've just made your first pull request!

### Pull Requests

Please follow these steps to have your contribution merged asap:

1. Follow the [styleguides](#styleguides)
2. [Squash](https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&cad=rja&uact=8&ved=2ahUKEwjIoemS1Y30AhWzyIsBHWprDJYQFnoECAQQAw&url=https%3A%2F%2Fdocs.github.com%2Fen%2Fdesktop%2Fcontributing-and-collaborating-using-github-desktop%2Fmanaging-commits%2Fsquashing-commits&usg=AOvVaw0NwD3KXuURsZVEN7oK_bW2) your commits into a single one if there's a lot of repetitive, similar commits.

While the prerequisites above must be satisfied prior to having your pull request reviewed, the reviewer(s) may ask you to complete additional design work, tests, or other changes before your pull request can be ultimately accepted.

## Styleguides

### Git Commit Messages

Follow common practices as described very well [here](https://chris.beams.io/posts/git-commit/).

Here's a quick summary:
* **Write the first line of your commit in the imperative tense**, not past tense.
* Write concise one line commits where possible.
* Write a body wherever needed.
* Make a commit for every **logical change**.

##### Example:

If you fixed a bug regarding Jarvis's speech, you'd phrase it: 

'Fix bug regarding Jarvis speech' ✔️

'Fixed bug for speech' ❌

'Fixes speech' ❌

### Python Styleguide

1. Most importantly, when contributing to a file, follow the existing convention.
2. If you're creating a new script follow the official [styleguide](#official-styleguide).

##### Official Styleguide 

Python Code: [PEP 8](https://pep8.org/)

### Documentation Styleguide

Python Comments and Docstrings: [Google Guidelines](https://google.github.io/styleguide/pyguide.html#s3.8.1-comments-in-doc-strings)

Markdown files: Follow the convention used in existing markdown files in the repository.



