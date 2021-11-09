# Contributing to Jarvis

:+1::tada: Thanks for taking the time to contribute! :tada::+1:

The following is a set of guidelines for contributing to Jarvis, which is hosted in its [GitHub repo](https://github.com/sukeesh/Jarvis). These are mostly guidelines, and not rules. Use your best judgment, and feel free to propose changes to this document in a pull request.

### Short Version

* PRs are accepted :)
* We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) formatting. Before making a pull request ensure that your code is according to PEP 8 standards
* If you have some ideas for new features but don't have the time to implement them, please open an issue with the tag new_feature
* Don't forget to comment and add docstrings to your code where needed!

### Table Of Contents

[What if I just have a question?](#what-if-i-just-have-a-question)

[How Can I Contribute?](#how-can-i-contribute)
  * [Reporting Bugs](#reporting-bugs)
  * [Suggesting Enhancements](#suggesting-enhancements)
  * [Beginners: Your First Contribution](#beginners-your-first-contribution)
  * [Pull Requests](#pull-requests)

[Styleguides](#styleguides)
  * [Git Commit Messages](#git-commit-messages)
  * [Python Styleguide](#python-styleguide)
  * [Documentation Styleguide](#documentation-styleguide)

[Additional Notes](#additional-notes)
  * [Issue and Pull Request Labels](#issue-and-pull-request-labels)


## What if I Just Have a Question?

> **Note:** Please don't file an issue just to ask a question. 
1. Read the README, and see if that answers you.
2. Read this whole document.
If you still have a question, search existing issues and you may find that there's a topic similar to that of your question. You can ask your question as a comment in that issue.

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

* **Check if that feature [already exists]() **
* **Check if you have the latest version** of Jarvis
* **Perform a [quick search](https://github.com/sukeesh/Jarvis/issues)** to see if the feature/enhancement has already been suggested. If it has, add a comment to the existing issue instead of opening a new one.

#### How Do I Submit A Feature Suggestion?

Enhancement suggestions are tracked as GitHub [issues](https://guides.github.com/features/issues/).

* **Use a clear and descriptive title** for the issue to identify the suggestion
* **Provide a description of the suggested feature**

### Your First Code Contribution

Unsure where to begin contributing to Atom? You can start by looking through these `beginner` and `help-wanted` issues:

* [Beginner issues][beginner] - issues which should only require a few lines of code, and a test or two.
* [Help wanted issues][help-wanted] - issues which should be a bit more involved than `beginner` issues.

Both issue lists are sorted by total number of comments. While not perfect, number of comments is a reasonable proxy for impact a given change will have.

If you want to read about using Atom or developing packages in Atom, the [Atom Flight Manual](https://flight-manual.atom.io) is free and available online. You can find the source to the manual in [atom/flight-manual.atom.io](https://github.com/atom/flight-manual.atom.io).

#### Local development

Atom Core and all packages can be developed locally. For instructions on how to do this, see the following sections in the [Atom Flight Manual](https://flight-manual.atom.io):

* [Hacking on Atom Core][hacking-on-atom-core]
* [Contributing to Official Atom Packages][contributing-to-official-atom-packages]

### Pull Requests

The process described here has several goals:

- Maintain Atom's quality
- Fix problems that are important to users
- Engage the community in working toward the best possible Atom
- Enable a sustainable system for Atom's maintainers to review contributions

Please follow these steps to have your contribution considered by the maintainers:

1. Follow all instructions in [the template](PULL_REQUEST_TEMPLATE.md)
2. Follow the [styleguides](#styleguides)
3. After you submit your pull request, verify that all [status checks](https://help.github.com/articles/about-status-checks/) are passing <details><summary>What if the status checks are failing?</summary>If a status check is failing, and you believe that the failure is unrelated to your change, please leave a comment on the pull request explaining why you believe the failure is unrelated. A maintainer will re-run the status check for you. If we conclude that the failure was a false positive, then we will open an issue to track that problem with our status check suite.</details>

While the prerequisites above must be satisfied prior to having your pull request reviewed, the reviewer(s) may ask you to complete additional design work, tests, or other changes before your pull request can be ultimately accepted.
