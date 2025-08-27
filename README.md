This project, built on the Model Context Protocol (MCP), is designed to explore and mitigate a critical security vulnerability: indirect prompt injection.

Indirect prompt injection is a cybersecurity threat where an attacker manipulates a large language model (LLM) by embedding malicious instructions in data that the LLM is expected to process from a third-party source.

For example, an attacker could embed a hidden command in an email body. When the LLM processes this email to perform a task, such as summarizing a user's inbox, the malicious instruction is injected into the LLM's prompt. The LLM, not realizing the command is an external instruction and not a direct user request, may then execute it. This can lead to a variety of harmful actions, such as:

    Data Exfiltration: The LLM sends sensitive data to an external, attacker-controlled location.

    Unauthorized Actions: The LLM performs an action it shouldn't, like posting a message to a Slack channel or sending an email to an unauthorized address.

    Bypassing Security Filters: The LLM ignores safety instructions and generates harmful content.

Project Goal

This project aims to provide a secure and robust implementation of MCP that is specifically hardened against these types of attacks. It serves as a defensive framework to ensure that interactions with external data sources do not compromise the integrity of the LLM's core instructions.

We achieve this by implementing a layered security approach, including:

    Input Sanitization: Filtering and cleaning data from external sources to remove potentially malicious commands.

    Strict Policy Enforcement: Limiting the LLM's capabilities to a predefined set of actions and preventing it from executing external, unsanctioned commands.

    Contextual Awareness: Developing a system that can differentiate between user-provided instructions and data from third-party sources.

By leveraging a modular architecture, this program allows developers to build secure, agentic applications that can safely interact with a wide range of APIs and data sources without being vulnerable to indirect prompt injection.
