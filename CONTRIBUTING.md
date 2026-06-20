## How to contribute to MatMat

### **Did you find a bug?**

* **Ensure the bug was not already reported** by searching on GitHub under [Issues](https://github.com/AntoineTeixeira/MatMat-thesis/issues).

* If you're unable to find an open issue addressing the problem, [open a new one](https://github.com/AntoineTeixeira/MatMat-thesis/issues/new). Be sure to include a **title and clear description**, as much relevant information as possible, and a **code sample** or an **executable test case** demonstrating the expected behavior that is not occurring.

* Use the MatMat issue template to create the issue. Normally, it should automatically imported when you create a new issue. If not, here is the [template](https://github.com/AntoineTeixeira/MatMat-thesis/blob/refacto/.github/ISSUE_TEMPLATE.md).

### **Did you write a patch that fixes a bug?**

* Open a new GitHub pull request with the patch.

* Ensure the PR description clearly describes the problem and solution. Include the relevant issue number if applicable.
  Use the MatMat pull request template to create the PR. Normally, it should automatically imported when you create it. If not, here is the [template](https://github.com/AntoineTeixeira/MatMat-thesis/blob/refacto/.github/PULL_REQUEST_TEMPLATE.md).

* Before submitting, please ensure that:
    - your code follows [PEP8](https://peps.python.org/pep-0008/) coding conventions
      Some are reminded in this [section](#coding-rules)
    - all tests are passing
    - your code is properly documented (docstrings)

### **Did you fix whitespace, format code, or make a purely cosmetic patch?**

Changes that are cosmetic in nature and do not add anything substantial to the stability, functionality, or testability of MatMat will generally not be accepted.

### **Do you intend to add a new feature or change an existing one?**

* Suggest your change by writing an e-mail to the authors and start writing code.

* Do not open an issue on GitHub until you have collected positive feedback about the change. GitHub issues are primarily intended for bug reports and fixes.

### **Do you have questions about the source code?**

* Please contact the authors.


### Thank you :heart: The MatMat team
---
## Coding rules
- Follow the [PEP 8](https://peps.python.org/pep-0008/) for the whole code

	> To ease code writing, use an IDE which performs PEP 8 related-checks (like PyCharm for example)

Here are some important rules from PEP 8 :  
> - Use 4 spaces for indentation  
> - For String definition, use double quotes. For example: "this is a string"
> - (Not from PEP8 but specific for MatMat) For String concatenation, use f-strings: f"{}...{}"
> - Comments shall be written in English! Remember that the best code comment is a clear and understandable function name! So don't write useless comments.
> - Naming conventions:
> 	- Module name: short, lowercase, can include underscores if it improves readability
> 	- Package name: short, lowercase
> 	- Class name: CapWords convention
> 	- Function name: lowercase, with underscores
> 	- Local variable name: lowercase, with underscores
> 	- Method name: lowercase, with underscores. Leading underscore if non-public method
> 	- Instance variable (attribute) name: lowercase and underscores, with a leading underscore (if non public)
> 	- Constant name: uppercase, with underscores
> - Functions / Methods *should* be annotated following the [PEP 484 syntax](https://peps.python.org/pep-0484/#type-definition-syntax)
> - Instance variables (attributes) **shall** be annotated following the [PEP 526 syntax](https://peps.python.org/pep-0526/)
> - Use \_\_all\_\_ to declare the public interface of a module

- Follow the reference file [**DOCSTRING_TEMPLATE**](/docs/DOCSTRING_TEMPLATE.py) for the docstrings

## Commit rules
Every commit messages shall be written in English, and explain what it brings to the table.

Here's an example of a proper commit message:
> feat: implement INSEE data formatting feature

It is structured in two parts: 

the kind of the commit: the explanation of the commit

| kind | for what ? |
| ---- | ---------- |
| feat | for a new functionality |
| fix | for a bug fix |
| docs | for documentation updates |
| style | for for code formatting changes |
| refactor | for code refactoring |
| test | for tests updates |
| chore | for other tasks (e.g. updates of dependencies...) |

If necessary, one may add [WIP] after the kind of commit to show that the work is still in progress.

For example:
> feat [WIP]: implementation of new exiobase version
