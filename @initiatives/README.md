# Initiatives

This folder contains product initiatives and their associated documentation, PRDs, and rules.

## Structure

```
@initiatives/
├── personalization_input_flow/
│   └── PRD/
│       ├── PRD.md
│       └── JIRA_EPIC_FORMAT.md
├── create-epic-rule.mdc
└── create-user-story-task-rule.mdc
```

## Create Epic Rule

The `create-epic-rule.mdc` file contains a custom rule for creating JIRA Epics from PRDs.

### Usage

When you want to create a JIRA Epic from a PRD, simply say:
- "Create Epic"
- "Create Epic from PRD"
- Or reference the PRD file and request to create an Epic

The rule will automatically:
1. Extract content from the PRD
2. Format it using JIRA markup
3. Structure it with Summary, Description, Acceptance Criteria, and Definition of Done
4. Create the Epic in JIRA (requires project key, defaults to "SRCH")

### Required Information

- **Project Key**: The JIRA project key (e.g., "SRCH")
- **PRD File**: Path to the PRD file in the initiatives folder

### Epic Structure

The rule creates Epics with the following structure:
- **Summary**: Extracted from PRD title
- **Description**: Includes Context, User Problem, Hypothesis, Solution, Metrics, Scope, and Questions
- **Acceptance Criteria**: Organized by variants/flows and technical requirements
- **Definition of Done**: Comprehensive completion checklist

### Example

```
User: "@PRD.md Create Epic"
Assistant: [Reads PRD, formats content, creates Epic in JIRA]
Result: Epic created with ticket number (e.g., SRCH-1096)
```

## Create User Story and Task Rule

The `create-user-story-task-rule.mdc` file contains a custom rule for creating JIRA User Stories and Tasks from PRDs.

### Usage

When you want to create User Stories or Tasks from a PRD, simply say:
- "Create User Story"
- "Create Task"
- "Create Stories"
- "Create Tasks"
- Or reference the PRD file and request to create work items

### Required Information

- **Project Key**: The JIRA project key (e.g., "SRCH")
- **PRD File**: Path to the PRD file in the initiatives folder
- **Issue Type**: "Story" for User Stories, "Task" for Tasks
- **Epic** (Optional): Epic key (e.g., "SRCH-1096") if stories/tasks should be assigned to an Epic
  - If Epic is provided, stories/tasks will be created as children of the Epic
  - If Epic is not provided, stories/tasks will be created without a parent

### User Story Structure

The rule creates User Stories with the following structure:
- **Summary**: Headline with the goal
- **User Story**: "As a [user type], I want to [action], so that [benefit]" format
  - *Note: Adjust format if needed, or leave blank if it doesn't apply*
- **Description**: Content and description of what to do/implement
- **Acceptance Criteria**: Table format with columns:
  - **Name**: Name of the scenario
  - **Given**: Preconditions
  - **When**: Action
  - **Then**: Expected outcome
- **Definition of Done**: Comprehensive completion checklist

### Task Structure

The rule creates Tasks with the following structure:
- **Summary**: Headline with the goal
- **Description**: Content and description of what to do/implement
- **Acceptance Criteria**: Table format with columns (Name, Given, When, Then)
- **Definition of Done**: Comprehensive completion checklist
- **Note**: Tasks do NOT include the "User Story" field

### Acceptance Criteria Table Format

```
||Name||Given||When||Then||
|Scenario 1|User is on registration screen|User completes registration|Personalization screen appears|
|Scenario 2|User is on personalization screen|User selects preferences|Preferences are saved|
```

### Epic Assignment

- **With Epic**: "Create User Stories from @PRD.md under Epic SRCH-1096"
  - Stories/Tasks will be linked to the specified Epic
- **Without Epic**: "Create User Stories from @PRD.md"
  - Stories/Tasks will be created independently without a parent Epic

### Example

```
User: "@PRD.md Create User Stories under Epic SRCH-1096"
Assistant: [Reads PRD, breaks down into stories, creates User Stories in JIRA linked to Epic]
Result: Multiple User Stories created with ticket numbers (e.g., SRCH-1097, SRCH-1098) linked to Epic SRCH-1096
```

