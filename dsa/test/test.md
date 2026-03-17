● The 10 Commandments of pytest

  ---
  I. One test, one behavior
  Each test verifies exactly one thing. When it fails, you know immediately what broke.

  II. Name tests like sentences
  test_find_kth_returns_none_when_list_is_empty beats test_find_kth_2. A reader should understand the intent without reading the body.

  III. Thou shalt not mutate shared fixtures
  Fixtures are shared. If you do ll_base.tail.next = ll_base.head inside a test, you corrupt the list for other tests that use that fixture.
   Use a fresh object or a dedicated fixture for that scenario.

  IV. Use fixtures for repeated setup, inline for one-offs
  If 5 tests need a [2,3,4,5] list → fixture. If only one test needs an empty list → create it inline. Fixtures are not about cleanliness,
  they're about reuse.

  V. Parametrize to cover the input space
  When the same behavior should hold for multiple inputs, use @pytest.mark.parametrize. Don't write 5 identical tests with different
  hardcoded values.

  VI. Always test the edges
  Empty input, single element, k > length, None, zero, negative numbers. That's where bugs live.

  VII. Assert on what actually matters
  assert node.value == 4 is better than assert node is not None when you care about the value. Weak assertions let bugs through.

  VIII. Thou shalt not test implementation, only behavior
  Test what the function returns or does to its output — not how it does it internally. If you refactor the algorithm, the tests should
  still pass.

  IX. A failing test must be a useful message
  If a test fails and you can't tell what went wrong from the name + assertion alone, it needs work. Add context with assert x == y,
  "reason" when needed.

  X. Import what you test, test what you import
      If it's in the import block, there must be tests for it. Dead imports are a sign of dead coverage.
