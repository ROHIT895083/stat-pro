from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI

def create_agent(df):
    llm = ChatOpenAI(temperature=0)

    agent = create_pandas_dataframe_agent(
        llm=llm,
        df=df,
        verbose=True,
        allow_dangerous_code=False
    )

    return agent