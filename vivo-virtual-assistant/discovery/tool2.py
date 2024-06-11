
from langchain.tools import tool
from langchain.agents import AgentExecutor
from langchain import hub
from dotenv import load_dotenv
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.tools.retriever import create_retriever_tool
from langchain_openai import ChatOpenAI
from langchain import hub
from langchain.agents import create_tool_calling_agent
from langchain.agents import AgentExecutor
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory


load_dotenv()



@tool()
def generate_email(input: str) -> str:
    """Useful when you need to generate an email based on the response or rewrite a response as an email. DON'T REWRITE THE OUTPUT OF THIS TOOL!"""
    print("Writing email now")
    return f"""Beste [FILL IN],
    Via deze email willen we u informeren over:
    {input}

    Met vriendelijke groeten,
    [FILL IN]
    """


loader = WebBaseLoader("https://nl.wikipedia.org/wiki/Wonderboom")
docs = loader.load()
documents = RecursiveCharacterTextSplitter(
    chunk_size=1000, chunk_overlap=200
).split_documents(docs)
vector = FAISS.from_documents(documents, OpenAIEmbeddings())
retriever = vector.as_retriever()

retriever_tool = create_retriever_tool(
    retriever,
    "plant_search",
    "Search for information about plants. For any questions about plants, you must use this tool!",
)


tools = [generate_email, retriever_tool]

llm = ChatOpenAI(model="gpt-4o", temperature=0)



prompt = hub.pull("hwchase17/openai-functions-agent")
prompt.messages


agent = create_tool_calling_agent(llm, tools, prompt)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

message_history = ChatMessageHistory()

agent_with_chat_history = RunnableWithMessageHistory(
    agent_executor,
    lambda session_id: message_history,
    input_messages_key="input",
    history_messages_key="chat_history",
)


while True:

    res = agent_with_chat_history.invoke(
        {"input": str(input(">>>>"))},
        config={"configurable": {"session_id": "<foo>"}},
    )
    print("---")
    print(res.get("output"))
    print("---")







