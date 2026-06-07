# Example feature file
# This is an example of Cucumber/Gherkin syntax
# Generated features will follow this structure

Feature: Example Web Testing
  As a QA engineer
  I want to test web applications
  So that I can ensure they work correctly

  Background:
    Given the browser is ready

  Scenario: Page loads successfully
    When I navigate to "https://example.com"
    Then the page title should not be empty
    And the page should have visible content

  Scenario: Visual appearance is correct
    When I navigate to "https://example.com"
    Then the page should have proper styling
    And text should be readable
    And images should load correctly

  Scenario: Interactive elements work
    When I navigate to "https://example.com"
    Then I should see interactive buttons
    And buttons should be clickable

  Scenario: No console errors
    When I navigate to "https://example.com"
    Then the browser console should have no errors
    And the page should be responsive
