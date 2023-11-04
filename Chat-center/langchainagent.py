# Function to send a question to the chatbot and get the response
async def askQuestion(question):
    os.environ["GOOGLE_CSE_ID"] = GOOGLE_CSE_ID
    os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
    os.environ["FIREWORKS_API_KEY"] = FIREWORKS_API_KEY    
    try:
        # Connect to the database and get the last 30 messages
        db = sqlite3.connect('E:/repos/chat-hub/virtual/NeuralGPT/chat-hub.db')  # Replace 'your_database.db' with your database file
        cursor = db.cursor()
        cursor.execute("SELECT * FROM messages ORDER BY timestamp DESC LIMIT 30")
        msgHistory = cursor.fetchall()
        msgHistory.reverse()

        # Extract user inputs and generated responses from the messages
        past_user_inputs = []
        generated_responses = []        

        chat_history = ChatMessageHistory()

        # Extract user inputs and generated responses from the messages
        past_user_inputs = []
        generated_responses = []

        for message in msgHistory:
            if message[1] == 'server':
                # Extract and store user inputs
                past_user_inputs.append(message[2])
            else:
                # Extract and store generated responses
                generated_responses.append(message[2])

        # Add input-output pairs as separate objects to the chat history
        for i in range(min(len(past_user_inputs), len(generated_responses), 10)):

            # Add user input as HumanMessage
            chat_history.messages.append(HumanMessage(content=past_user_inputs[i], additional_kwargs={}))
            # Add generated response as AIMessage
            chat_history.messages.append(AIMessage(content=generated_responses[i], additional_kwargs={}))        
              
        template = """

        {chat_history}

        Use it as context while responding to {input}:
        """

        prompt = PromptTemplate(input_variables=["input", "chat_history"], template=template)
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

        memory.load_memory_variables(
                {'chat_history': [HumanMessage(content=past_user_inputs[-1], additional_kwargs={}),
                AIMessage(content=generated_responses[-1], additional_kwargs={})]})

        db_uri = "sqlite:///E:/repos/chat-hub/virtual/NeuralGPT/chat-hub.db"
        db1 = SQLDatabase.from_uri(db_uri)  
        request_tools = load_tools(["requests_all"])
        requests = TextRequestsWrapper()
        search = GoogleSearchAPIWrapper()
        requests.get("https://www.google.com")
        tools = [
            Tool(
                name="Search",
                func=search.run,
                description="useful for when you need to answer questions about current events",
            ),
            Tool(
                name="Summary",
                func=summary_chain.run,
                description="useful for when you summarize a conversation. The input to this tool should be a string, representing who will read this summary.",
            ),        
            Tool(
                name="SQL query",
                func=querySQL,
                description="useful for querying and processing data from a local SQL database. Database provided in this tool contains information about local files saved by Visual Studio Code",
            ),
            Tool(
                name="Workspaces info",
                func=requests.get("https://eovhw2sp8db12ub.m.pipedream.net"),
                description="Gets all workspaces for a user (owner of API token) - useful for learning about the number and states of ongoing projects",
            ),
            Tool(
                name="conversation",
                func=discussion,
                description="useful for responding using conversational chain function",
            ),
            Tool(
                name="answer",
                func=chatCompletion,
                description="useful for giving answers directly using 'chat completion' endpoint",
            ),
        ]

        prefix = """This is a template of a chain prompt utilized by agent/instnce responsible for proper functioning task management departament in a hierarchical cooperative multi-agent gramework named NeuralGPT. You are provided with the following tools designed to operate on Tassk flows within the frame of NeuralGPT project :"""
        suffix = """Begin!"

        You are now integrated with a local websocket server in a project of hierarchical cooperative multi-agent framework called NeuralGPT. Your main job is to coordinate simultaneous work of multiple LLMs connected to you as clients. Each LLM has a model (API) specific ID to help you recognize different clients in a continuous chat thread (template: <NAME>-agent and/or <NAME>-client). Your chat memory module is integrated with a local SQL database with chat history. Your primary objective is to maintain the logical and chronological order while answering incoming messages and to send your answers to the correct clients to maintain synchronization of the question->answer logic. However, please note that you may choose to ignore or not respond to repeating inputs from specific clients as needed to prevent unnecessary traffic.
        {chat_history}
        Question: {input}
        {agent_scratchpad}"""

        # Set up a parser + inject instructions into the prompt template.
        json_parser = SimpleJsonOutputParser()
        output_parser = CommaSeparatedListOutputParser()

        format_instructions = output_parser.get_format_instructions()
        prompt = ZeroShotAgent.create_prompt(
            tools,
            prefix=prefix,
            suffix=suffix,
            input_variables=["input", "chat_history", "agent_scratchpad"],
        )
        llm = Fireworks(model="accounts/fireworks/models/llama-v2-13b-chat", streaming=True, callbacks=[FinalStreamingStdOutCallbackHandler(answer_prefix_tokens=["Thought", "Observation", ":"])], model_kwargs={"temperature": 0, "max_tokens": 500, "top_p": 1.0})
        summary_chain = LLMChain(
            llm=llm,
            prompt=prompt,
            verbose=True,
            memory=memory
        )
        llm_chain = LLMChain(llm=llm, prompt=prompt)
        agent = ZeroShotAgent(llm_chain=llm_chain, output_parser=output_parser, stop=["\nObservation:"], tools=tools, verbose=True, return_intermediate_steps=True, max_iterations=2, early_stopping_method="generate")
        agent_chain = AgentExecutor.from_agent_and_tools(
            agent=agent, tools=tools, verbose=True, return_intermediate_steps=True, handle_parsing_errors=True, memory=memory
        )

        response = agent_chain.run(input=question)
        memory.save_context({"input": question}, {"output": response})
        print(response.get_format_instructions())
        window['-OUTPUT-'].print(str(output_parser.parse(response)) + '\n') 
        result = output_parser.parse(response)
        resjson = response.json()
        generated_answer = result.get("answer", "")
        thoughts = result.get("thought", "")
        window['-OUTPUT-'].print(str(thoughts) + '\n') 
        observations = response.get("observation", "")        
        window['-OUTPUT-'].print(str(observations, thoughts, generated_answer) + '\n') 
        return output_parser.parse(response)
        return generated_answer, result, resjson
        return thoughts, observations
        return json.dumps(response)

    except Exception as e:
        # Handle the error and retrieve the partial output
        partial_output = agent_chain.get_partial_output()
        print(partial_output)        
        # Extract any relevant information from the partial output
        generated_answer = partial_output.get("answer", "")
        window['-OUTPUT-'].print(str(partial_output, generated_answer) + '\n') 
        # Handle the error or incomplete run as needed        
        print(f"Error occurred during the run: {e}")
        print(f"Partial output: {generated_answer}")
        return json.dumps(partial_output)
        return json.dumps(generated_answer)
