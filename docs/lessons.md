# Lessons Learned

## Test Driven Development

- ALWAYS write tests before implementing functionality. This helps ensure the code meets requirements and avoids unnecessary complexity.
- When implementing a new feature, first write a failing test that describes the desired behavior.
- Tests should be specific and focused on one piece of functionality.
- After implementing changes, run the full test suite and code quality checks to catch any regressions.
- Test classes should be at the root level of the test file, not nested within other test classes, to ensure proper test discovery and organization.
- When running pytest for a specific test class, use the format `pytest path/to/test.py::TestClassName -v`
- For efficiency, run only the specific tests you need:
  - For a single test: `pytest path/to/test.py::TestClass::test_name`
  - For a test in a nested class: `pytest path/to/test.py::TestClass::TestNestedClass::test_name`
  - For a parameterized test: `pytest path/to/test.py::test_name`
- Structure tests with explicit comments to improve readability:
  ```python
  def test_something(self):
      # Arrange - set up test data and conditions
      
      # Act - perform the action being tested
      
      # Assert - verify the results
  ```

## Code Quality

- Avoid code duplication in error handling paths. When you see similar error handling repeated, consider consolidating the logic:
  1. Collect all items to process up front
  2. Use a single loop to handle common operations and error cases
  3. Consolidate status messages or logging
- Keep docstrings focused on interface behavior, not implementation details
- Never make changes unrelated to the current task or failing test
- Keep a clear separation between interface documentation (docstrings) and implementation notes (comments)
- Run pre-commit checks after making changes to ensure code quality and formatting standards are met
- Never include type information in docstrings when it's already present in type annotations
- ALWAYS run pre-commit checks after any code changes are considered complete:
  1. Run `uv run pre-commit run --all-files`
  2. If any checks modify files, run the checks again to ensure everything is clean
  3. Never consider a change complete until all pre-commit checks pass
- Use `contextlib.suppress` instead of empty try-except blocks:
  ```python
  # Instead of:
  try:
      do_something()
  except SomeError:
      pass
      
  # Use:
  from contextlib import suppress
  with suppress(SomeError):
      do_something()
  ```
- Display user feedback messages:
  1. Use present tense ("Removing..." not "Removed...")
  2. Show messages as soon as possible, don't wait until after the operation
  3. Use a flag like `first_removal` to ensure messages are shown exactly once

## Configuration Management

- When modifying configuration files like `pyproject.toml`, always consider the impact on existing configurations:
  1. Check if a configuration exists before modifying it
  2. Don't overwrite existing configurations unless explicitly requested
  3. Handle empty or invalid configurations gracefully
  4. Use appropriate functions from `pyproject.core` to manage configuration values
- Keep configuration behavior consistent and avoid special cases:
  1. Document configuration behavior in docstrings
  2. Add test cases to verify behavior
  3. Handle edge cases like empty lists or missing configurations
  4. Prefer simple, uniform behavior over complex special cases
