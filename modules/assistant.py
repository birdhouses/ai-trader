import json
import time
from modules.capital_com_api import CapitalComAPI
from dotenv import load_dotenv
from openai import OpenAI
import os
from datetime import datetime

class Assistant:
    def __init__(self, capital_api_client):
        load_dotenv()
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.capital_api_client = capital_api_client

    def get_current_datetime(self):
        """Get the current UTC date and time in ISO format."""
        return datetime.utcnow().isoformat()

    def handle_requires_action(self, run_id, thread_id):
        initial_interval = 1
        max_interval = 3
        interval = initial_interval

        while True:
            run = self.openai_client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
            status = run.status

            if status == 'completed':
                messages = self.openai_client.beta.threads.messages.list(thread_id=thread_id)
                assistant_message = next(
                    (msg.content for msg in messages if msg.role == 'assistant'),
                    None
                )
                return assistant_message[0].text.value
            elif status in ['cancelled', 'failed', 'incomplete']:
                return None
            elif status == 'requires_action':
                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                tool_outputs = self.handle_tool_calls(tool_calls)
                self.openai_client.beta.threads.runs.submit_tool_outputs(thread_id=thread_id, run_id=run_id, tool_outputs=tool_outputs)

                return self.handle_requires_action(run_id, thread_id)

            time.sleep(interval)
            interval = min(interval * 2, max_interval)

    def handle_tool_calls(self, tool_calls):
        tool_outputs = []

        for tool in tool_calls:
            args = json.loads(tool.function.arguments)

            tool_name = tool.function.name
            output = None

            if tool_name == 'get_current_datetime':
                try:
                    output = self.get_current_datetime()
                except Exception as e:
                    output = str(e)
            elif tool_name == 'get_stock_data':
                try:
                    epic = args['epic']
                    resolution= args['resolution']
                    max= args['max']

                    output = self.capital_api_client.get_historical_prices(
                        epic,
                        resolution,
                        max
                    )
                    output = json.dumps(output, indent=4)
                except Exception as e:
                    print(f"Error retrieving stock data: {str(e)}")
                    output = "error retrieving stock data"

            if output is not None:
                tool_outputs.append({
                    'tool_call_id': tool.id,
                    'output': json.dumps(output)
                })
            else:
                tool_outputs.append({
                    'tool_call_id': tool.id,
                    'output': 'No output generated for this tool call.'
                })

        return tool_outputs

    def chat_with_assistant(self, assistant_id, question, thread_id=None):
        thread_id = 'skip'

        if thread_id and thread_id != 'skip':
            # Check for active runs and handle them before starting a new one
            active_runs = self.openai_client.beta.threads.runs.list(thread_id=thread_id, limit=1)
            if active_runs.data and active_runs.data[0].status == 'in_progress':
                run_id = active_runs.data[0].id
                print(f"Cancelling active run {run_id} on thread {thread_id}")
                self.openai_client.beta.threads.runs.cancel(thread_id=thread_id, run_id=run_id)

                # Wait for the run to cancel before proceeding
                initial_interval = 1
                max_interval = 3
                interval = initial_interval
                while True:
                    run_status = self.openai_client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id).status
                    if run_status == 'cancelled':
                        break
                    time.sleep(interval)
                    interval = min(interval * 2, max_interval)

            # Create a new message in the thread and start a new run
            self.openai_client.beta.threads.messages.create(thread_id=thread_id, role='user', content=question)
            run = self.openai_client.beta.threads.runs.create(thread_id=thread_id, assistant_id=assistant_id)
            run_id = run.id
        else:
            # Create a new thread and run if no thread exists
            response = self.openai_client.beta.threads.create_and_run(
                assistant_id=assistant_id,
                thread={"messages": [{"role": "user", "content": question}]}
            )
            run_id = response.id
            thread_id = response.thread_id

        return self.handle_requires_action(run_id, thread_id)
