# Python code linting slackbot - CodeOptimizer
Introducing CodeOptimizer – a robust Python-powered Slackbot designed to streamline your coding workflow. With a primary function of analyzing user-submitted Python code snippets in real-time, CodeOptimizer employs the capabilities of PyLint to perform static code analysis, ensuring adherence to coding best practices and highlighting potential issues. No longer do you need to leave your Slack conversation to evaluate the quality and standard of your code. Simply send your code to CodeOptimizer, and within moments, receive detailed linting feedback directly within Slack.

### Key Features
- **Real-time Analysis**: Quickly analyze Python code snippets without leaving your Slack environment.
- **Powered by PyLint**: Leverage the renowned static analysis tool, PyLint, for precise and comprehensive feedback.
- **Interactive Feedback**: Receive insightful suggestions, warnings, and error messages that help improve your code quality.
- **Ease of Use**: A user-friendly interface ensures that developers of all levels can benefit from CodeOptimizer.
Optimize your Python development process, uphold coding standards, and foster a culture of coding excellence with the CodeOptimizer.

### How to use
- Setup Slack
    - Login to slack and create workspace
    - Create slack app, give name and specify workspace
    - Add scope(s) to bot
    - Install app to workspace (need a channel for the same)
    - Add app to channel
- Handling messages (events)
    - In Slack API go to Event subscriptions
    - Enable events
    - Install [ngrok](https://ngrok.com/)
    - Get signing secret from Slack API (basic information)
    - To run ngrok: `ngrok http 5000`` (this will generate a public URL accessible via the internet and it points to flask server running on port 5000)
    - On Slack API page, we need to enter the request url which is `ngrok URL` + `/slack/events``
    - In subscribe to bot events, add the type of event (message.channels) that the slack app should react to. For example, if a message is sent to a channel where slackbot is present, it will be re-directed to the flask app (thanks to ngrok) so that the underlying logic can work with it.
    - Check for additional scopes that might be required to be added and then re-install the app in workspace.
- Start slackbot
    - Start flask server (port 5000)
    - Run ngrok: `ngrok http 5000``
    - Update public URL on slack API page
    - Re-install slack bot app in workspace (if required)    