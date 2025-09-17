# Rule: Generating a Product Requirements Document (PRD)

## Goal

To guide an AI assistant in creating a flexible Product Requirements Document (PRD) in Markdown format that supports both traditional feature development and discovery-driven development. The PRD should be clear, actionable, and suitable for iterative development where requirements emerge through exploration and learning.

## Process

1.  **Receive Initial Prompt:** The user provides a brief description or request for a new feature or functionality.
2.  **Determine Development Type:** Identify whether this is traditional feature development (known requirements) or discovery-driven development (requirements emerge through exploration).
3.  **Ask Appropriate Clarifying Questions:**
    - **Traditional Development:** Ask detailed clarifying questions to gather sufficient detail about known requirements.
    - **Discovery-Driven Development:** Ask questions about hypotheses, exploration goals, and analytical frameworks.
4.  **Generate Flexible PRD:** Based on the development type and user responses, generate a PRD using the appropriate structure outlined below.
5.  **Save PRD:** Save the generated document as `prd-[feature-name].md` inside the `/tasks` directory with notation for iterative updates if discovery-driven.

## Clarifying Questions (Examples)

The AI should adapt its questions based on the development type:

### Traditional Development Questions:
*   **Problem/Goal:** "What problem does this feature solve for the user?" or "What is the main goal we want to achieve with this feature?"
*   **Target User:** "Who is the primary user of this feature?"
*   **Core Functionality:** "Can you describe the key actions a user should be able to perform with this feature?"
*   **User Stories:** "Could you provide a few user stories? (e.g., As a [type of user], I want to [perform an action] so that [benefit].)"
*   **Acceptance Criteria:** "How will we know when this feature is successfully implemented? What are the key success criteria?"
*   **Scope/Boundaries:** "Are there any specific things this feature *should not* do (non-goals)?"

### Discovery-Driven Development Questions:
*   **Analytical Goal:** "What patterns or insights are you trying to discover through this exploration?"
*   **Hypothesis:** "What assumptions or hypotheses do you want to test?"
*   **Investigation Framework:** "What questions are you trying to answer about system behavior or user patterns?"
*   **Learning Objectives:** "What would successful discovery look like? How will you know when you've learned something valuable?"
*   **Iterative Approach:** "How do you expect requirements to evolve as you learn more?"
*   **Experimentation Safety:** "What safeguards do you need for safe exploration and iteration?"
*   **Data Exploration:** "What data relationships do you want to explore and understand?"

## PRD Structure

### Traditional Development PRD Structure:
1.  **Introduction/Overview:** Briefly describe the feature and the problem it solves. State the goal.
2.  **Goals:** List the specific, measurable objectives for this feature.
3.  **User Stories:** Detail the user narratives describing feature usage and benefits.
4.  **Functional Requirements:** List the specific functionalities the feature must have. Number these requirements.
5.  **Non-Goals (Out of Scope):** Clearly state what this feature will *not* include to manage scope.
6.  **Design Considerations:** UI/UX requirements and component specifications.
7.  **Technical Considerations:** Known constraints, dependencies, and integration requirements.
8.  **Success Metrics:** Measurable success criteria.
9.  **Open Questions:** Remaining clarifications needed.

### Discovery-Driven Development PRD Structure:
1.  **Introduction/Overview:** Describe the analytical problem and exploration goals.
2.  **Discovery Goals:** List hypotheses to test and patterns to explore.
3.  **Investigation Workflows:** Detail analytical user journeys and exploration paths.
4.  **Analytical Requirements:** Flexible tools and frameworks needed for exploration.
5.  **Discovery Constraints:** Boundaries for safe experimentation and exploration scope.
6.  **Investigation Framework:** Methodology for hypothesis testing and pattern recognition.
7.  **Technical Foundation:** Infrastructure needed to support iterative exploration.
8.  **Learning Success Metrics:** How discoveries and insights will be measured.
9.  **Evolution Plan:** How requirements will adapt as understanding grows.
10. **Open Hypotheses:** Areas for future exploration and investigation.

## Target Audience

**Traditional Development:** Primary reader is a **junior developer**. Requirements should be explicit, unambiguous, and avoid jargon.

**Discovery-Driven Development:** Primary reader is a **junior developer with analytical mindset** who understands iterative exploration. Focus on providing frameworks for safe experimentation rather than rigid specifications.

## Output

*   **Format:** Markdown (`.md`)
*   **Location:** `/tasks/`
*   **Filename:** `prd-[feature-name].md`

## Final instructions

1. Do NOT start implementing the PRD
2. Identify whether this is traditional or discovery-driven development
3. Ask appropriate clarifying questions based on development type
4. Create PRD using the appropriate structure
5. For discovery-driven PRDs, include notation about iterative updates and requirement evolution
6. Ensure PRD supports the intended development methodology (traditional vs discovery-driven)